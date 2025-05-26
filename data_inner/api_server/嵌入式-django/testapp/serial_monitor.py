import serial
import time
import threading
import queue
from django.db import connection
from .models import DHT
import datetime
import logging
import traceback
import requests
import json
import os

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 創建數據隊列，用於線程間通信
data_queue = queue.Queue()

# 全局變量
serial_port = '/dev/cu.usbserial-1140'  # 根據您的實際串口設置
baud_rate = 115200
ser = None
is_running = False
monitor_thread = None

# JSON 文件路徑
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_file_path = os.path.join(BASE_DIR, 'data', 'dht.json')

# 上傳數據到 API
def upload_data_to_api(temperature, humidity):
    """上傳溫濕度數據到 API"""
    try:
        # 準備數據
        data = {
            'temperature': temperature,
            'humidity': humidity
        }
        
        # 發送 POST 請求到 API
        response = requests.post(
            'http://127.0.0.1:8080/api/dht/create/',  # 使用 8080 端口
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        # 檢查響應
        if response.status_code in [200, 201]:
            try:
                response_data = response.json()
                if response_data.get('status') == 'success':
                    logger.info(f"數據成功上傳到資料庫：{response_data}")
                    return True
                else:
                    logger.error(f"API 回應狀態不是 success: {response_data}")
                    return False
            except json.JSONDecodeError:
                logger.error("無法解析 API 回應的 JSON 數據")
                return False
        else:
            logger.error(f"API 回應狀態碼錯誤: {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"錯誤詳情: {error_data}")
            except:
                logger.error(f"原始錯誤回應: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"發送請求時發生錯誤: {e}")
        logger.error(traceback.format_exc())
        return False
    except Exception as e:
        logger.error(f"上傳數據時發生未知錯誤: {e}")
        logger.error(traceback.format_exc())
        return False

# 確保數據目錄存在
def ensure_data_directory():
    """確保數據目錄存在"""
    data_dir = os.path.dirname(json_file_path)
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir)
            logger.info(f"創建數據目錄：{data_dir}")
        except Exception as e:
            logger.error(f"創建數據目錄失敗：{e}")
            return False
    return True

# 保存數據到 JSON 文件
def save_to_json(temperature, humidity):
    """將溫濕度數據保存到 JSON 文件"""
    logger.info(f"準備寫入 JSON 檔案到：{json_file_path}")
    try:
        # 確保目錄存在
        if not ensure_data_directory():
            return False

        # 讀取現有數據（如果存在）
        existing_data = []
        if os.path.exists(json_file_path):
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
            except json.JSONDecodeError:
                logger.warning("現有的 JSON 文件格式不正確，將創建新文件")
                existing_data = []
            except Exception as e:
                logger.error(f"讀取現有 JSON 文件時發生錯誤: {e}")
                existing_data = []

        # 準備新數據
        new_data = {
            'temperature': temperature,
            'humidity': humidity,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 添加新數據到列表
        existing_data.append(new_data)

        # 只保留最新的 100 條記錄
        if len(existing_data) > 100:
            existing_data = existing_data[-100:]

        # 寫入 JSON 文件
        try:
            with open(json_file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"數據已保存到 JSON 文件：{json_file_path}")
            logger.info(f"當前數據：溫度={temperature}°C, 濕度={humidity}%")
            return True
        except Exception as e:
            logger.error(f"寫入 JSON 文件時發生錯誤: {e}")
            logger.error(f"文件路徑: {json_file_path}")
            logger.error(f"當前工作目錄: {os.getcwd()}")
            return False

    except Exception as e:
        logger.error(f"保存到 JSON 文件時發生錯誤: {e}")
        logger.error(traceback.format_exc())
        return False

# 初始化串口
def initialize_serial():
    global ser, is_running
    
    try:
        # 關閉之前的連接（如果有）
        if ser and ser.is_open:
            is_running = False
            time.sleep(1)  # 給讀取線程時間退出
            ser.close()
            time.sleep(1)  # 等待串口完全關閉
            
        # 打開新的連接
        ser = serial.Serial(serial_port, baud_rate, timeout=0.5)
        logger.info("串口連接成功")
        
        # 激活 Arduino
        ser.write(b'\n')
        time.sleep(0.5)
        logger.info("Arduino 已激活")
        
        return True
    except serial.SerialException as e:
        logger.error(f"串口連接錯誤: {e}")
        return False

# 串口數據讀取線程
def serial_reader():
    global ser, is_running
    logger.info("串口監控線程已啟動")
    
    while is_running:
        try:
            if ser and ser.is_open and ser.in_waiting:
                data = ser.readline().decode('utf-8', errors='ignore').strip()
                if data:
                    logger.info(f"serial_reader 收到資料並放入 queue：{data}")
                    data_queue.put(data)
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"串口讀取錯誤: {e}")
            time.sleep(1)
    
    logger.info("串口監控線程已結束")


# 處理數據線程
def process_data_thread():
    global is_running
    logger.info("數據處理線程已啟動")
    
    while is_running:
        try:
            try:
                data = data_queue.get(block=True, timeout=0.5)
                logger.info(f"process_data_thread 拿到資料：{data}")
                process_serial_data(data)
                data_queue.task_done()
            except queue.Empty:
                pass
        except Exception as e:
            logger.error(f"處理數據時錯誤: {e}")
            logger.error(traceback.format_exc())
        
        time.sleep(0.1)
    
    logger.info("數據處理線程已結束")


# 處理串口數據
def process_serial_data(data):
    if data.startswith("DHT:"):
        logger.info("process_serial_data 成功判斷是 DHT 資料")
        if data == "DHT:Error":
            logger.error("溫濕度讀取錯誤")
        else:
            try:
                values = data.split(":")[1].split(",")
                if len(values) >= 2:
                    humidity = float(values[0])
                    temperature = float(values[1])
                    logger.info(f"解析結果：溫度={temperature}°C, 濕度={humidity}%")

                    # 保存到 JSON 文件
                    logger.info("即將呼叫 save_to_json() 儲存至 JSON")
                    save_to_json(temperature, humidity)

                    # 直接保存到資料庫
                    logger.info("即將呼叫 save_to_dht_model() 儲存至資料庫")
                    if save_to_dht_model(temperature, humidity):
                        logger.info("數據已成功保存到資料庫")
                    else:
                        logger.error("數據保存到資料庫失敗")
                else:
                    logger.error(f"收到的溫濕度數據格式不正確: {data}")
            except Exception as e:
                logger.error(f"解析溫濕度數據錯誤: {e}")
                logger.error(f"原始數據: {data}")
                logger.error(traceback.format_exc())


# 保存數據到 Django 模型
def save_to_dht_model(temperature, humidity):
    try:
        from django.db import transaction
        
        # 使用事務來確保數據的完整性
        with transaction.atomic():
            # 創建 DHT 模型記錄
            dht_record = DHT(temperature=temperature, humidity=humidity)
            dht_record.save()
            
        logger.info(f"已保存溫濕度記錄：溫度 {temperature}°C, 濕度 {humidity}%")
        return True
    except Exception as e:
        logger.error(f"保存溫濕度記錄錯誤: {e}")
        logger.error(traceback.format_exc())  # 添加完整的錯誤堆疊跟蹤
        return False

# 發送讀取溫濕度命令
def request_dht_data():
    global ser
    if not ser or not ser.is_open:
        logger.error("串口未連接")
        return False
    
    try:
        # 發送讀取溫濕度命令
        ser.write(b'c\n')
        logger.info("已發送讀取溫濕度命令")
        return True
    except Exception as e:
        logger.error(f"發送命令錯誤: {e}")
        logger.error(traceback.format_exc())  # 添加完整的錯誤堆疊跟蹤
        return False

# 定期請求溫濕度數據的線程
def periodic_data_request():
    global is_running
    logger.info("定期請求數據線程已啟動")
    
    while is_running:
        try:
            # 每10秒請求一次數據
            request_dht_data()
            time.sleep(10)
        except Exception as e:
            logger.error(f"定期請求數據錯誤: {e}")
            time.sleep(5)  # 發生錯誤時等待較短時間再試
    
    logger.info("定期請求數據線程已結束")

# 啟動監控
def start_monitoring():
    global is_running, monitor_thread, process_thread, periodic_thread
    
    if is_running:
        logger.warning("監控已經在運行中")
        return False
    
    # 初始化串口連接
    if not initialize_serial():
        return False
    
    # 啟動監控
    is_running = True
    
    # 啟動串口讀取線程
    monitor_thread = threading.Thread(target=serial_reader, daemon=True)
    monitor_thread.start()
    
    # 啟動數據處理線程
    process_thread = threading.Thread(target=process_data_thread, daemon=True)
    process_thread.start()
    
    # 啟動定期請求數據線程
    periodic_thread = threading.Thread(target=periodic_data_request, daemon=True)
    periodic_thread.start()
    
    # 請求初始數據
    request_dht_data()
    
    logger.info("監控已啟動")
    return True

# 停止監控
def stop_monitoring():
    global is_running, ser
    
    if not is_running:
        logger.warning("監控未在運行")
        return False
    
    # 停止線程
    is_running = False
    time.sleep(1)
    
    # 關閉串口連接
    if ser and ser.is_open:
        try:
            ser.close()
            logger.info("串口已關閉")
        except Exception as e:
            logger.error(f"關閉串口錯誤: {e}")
            logger.error(traceback.format_exc())  # 添加完整的錯誤堆疊跟蹤
    
    logger.info("監控已停止")
    return True

# 設置串口號
def set_serial_port(port):
    global serial_port
    serial_port = port
    logger.info(f"串口設置為: {port}") 