import serial
import tkinter
from tkinter import messagebox  # 添加 messagebox 模組
from time import sleep
import threading
import queue
import pymysql as mysql
import datetime

# 創建數據隊列，用於線程間通信
data_queue = queue.Queue()

# 設定串口
SERIAL_PORT = '/dev/cu.usbserial-140'  # 修正串口名稱
ser = None
connect_status = False
condition = False

# 資料庫設定
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'djangodb'  # 使用已創建的 testt 資料庫
}

# 全局變量
temperature_threshold = 28.0  # 默認溫度閾值為 28.0°C
light_threshold = 2000      # 默認光線閾值為 2000 (數值越小表示光線越亮)

# 資料庫連接函數
def connect_to_database():
    try:
        conn = mysql.connect(**db_config)
        print("成功連接到資料庫")
        return conn
    except mysql.Error as e:
        print(f"資料庫連接錯誤: {e}")
        return None

# 創建資料表（如果不存在）
def create_tables():
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        # 溫濕度記錄表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dht_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            temperature FLOAT NOT NULL,
            humidity FLOAT NOT NULL,
            timestamp DATETIME NOT NULL
        )
        ''')
        
        # 光敏電阻記錄表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS light_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            light_level INT NOT NULL,
            timestamp DATETIME NOT NULL
        )
        ''')
        
        # 門狀態記錄表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS door_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            status VARCHAR(10) NOT NULL,
            trigger_type VARCHAR(20) NOT NULL,
            timestamp DATETIME NOT NULL
        )
        ''')
        
        conn.commit()
        print("資料表已創建或已存在")
        return True
    except mysql.Error as e:
        print(f"創建資料表錯誤: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# 儲存溫濕度記錄
def save_dht_record(temperature, humidity):
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        now = datetime.datetime.now()
        sql = "INSERT INTO dht_records (temperature, humidity, timestamp) VALUES (%s, %s, %s)"
        cursor.execute(sql, (temperature, humidity, now))
        conn.commit()
        print(f"已保存溫濕度記錄：溫度 {temperature}°C, 濕度 {humidity}%")
        return True
    except mysql.Error as e:
        print(f"保存溫濕度記錄錯誤: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# 儲存光照強度記錄
def save_light_record(light_level):
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        now = datetime.datetime.now()
        sql = "INSERT INTO light_records (light_level, timestamp) VALUES (%s, %s)"
        cursor.execute(sql, (light_level, now))
        conn.commit()
        print(f"已保存光照強度記錄：{light_level}")
        return True
    except mysql.Error as e:
        print(f"保存光照強度記錄錯誤: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# 儲存門狀態變更
def save_door_status(status, trigger_type):
    conn = connect_to_database()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        now = datetime.datetime.now()
        sql = "INSERT INTO door_records (status, trigger_type, timestamp) VALUES (%s, %s, %s)"
        cursor.execute(sql, (status, trigger_type, now))
        conn.commit()
        print(f"已保存門狀態變更：{status}，觸發類型：{trigger_type}")
        return True
    except mysql.Error as e:
        print(f"保存門狀態變更錯誤: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# 串口讀取線程
def serial_reader():
    global ser, connect_status
    while connect_status:
        try:
            if ser and ser.is_open and ser.in_waiting:
                data = ser.readline().decode('utf-8', errors='ignore').strip()
                if data:
                    print(f"收到數據: {data}")
                    data_queue.put(data)
            sleep(0.1)  # 短暫休眠，避免CPU使用率過高
        except Exception as e:
            print(f"讀取錯誤: {e}")
            sleep(1)

# 處理數據隊列
def process_queue():
    try:
        while not data_queue.empty():
            data = data_queue.get_nowait()
            process_response(data)
    except Exception as e:
        print(f"處理數據錯誤: {e}")
    finally:
        # 每100毫秒檢查一次隊列
        Tkwindow.after(100, process_queue)

# 串口發送指令
def SerialWrite(command):
    global ser
    if not ser or not ser.is_open:
        print("串口未連接")
        return None
        
    try:
        ser.write(command)  # 發送指令到 Arduino
        print(f"發送命令: {command}")
        return True
    except serial.SerialException as e:
        print(f"串口通信錯誤: {e}")
        return None

# 處理 Arduino 回應
def process_response(data):
    if data.startswith("STATUS:"):
        status = data.split(":")[1]
        print(f"收到狀態: {status}")
        if status == "Ready":
            LabelA.config(text="Arduino 已就緒！")
            buttonC.config(state='normal')      # 啟用溫濕度按鈕
            buttonOpen.config(state='normal')   # 啟用開門按鈕
            buttonClose.config(state='normal')  # 啟用關門按鈕
            buttonLight.config(state='normal')  # 啟用光照測量按鈕
            buttonAuto.config(state='normal')   # 啟用自動控制按鈕
            # 顯示連接成功的訊息框
            messagebox.showinfo("連接成功", "Arduino 已成功連接！\n\n現在可以使用溫濕度感測、光照測量和門控制等功能。")
    
    elif data.startswith("DHT:"):
        print("收到溫濕度數據")
        if data == "DHT:Error":
            print("溫濕度讀取錯誤")
            LabelA.config(text="溫濕度感測器讀取錯誤！")
        else:
            try:
                values = data.split(":")[1].split(",")
                humidity = float(values[0])
                temperature = float(values[1])
                print(f"溫度: {temperature}°C, 濕度: {humidity}%")
                
                # 更新溫濕度顯示
                dht_label.config(text=f"溫度: {temperature}°C\n濕度: {humidity}%")
                
                # 只有當溫度超過閾值時才保存數據
                if temperature > temperature_threshold:
                    # 儲存溫濕度數據到資料庫
                    save_dht_record(temperature, humidity)
                    LabelA.config(text=f"溫度 {temperature}°C 超過閾值 {temperature_threshold}°C！\n數據已保存到資料庫")
                    print(f"溫度 {temperature}°C 超過閾值 {temperature_threshold}°C，數據已保存")
                    
                    # 顯示警告對話框
                    messagebox.showwarning("溫度警告", f"溫度 {temperature}°C 超過閾值 {temperature_threshold}°C！\n系統已自動將數據上傳至資料庫。")
                else:
                    LabelA.config(text=f"溫度 {temperature}°C 未超過閾值 {temperature_threshold}°C\n數據未保存")
                    print(f"溫度 {temperature}°C 未超過閾值 {temperature_threshold}°C，數據未保存")
            except Exception as e:
                print(f"解析溫濕度數據錯誤: {e}")
                print(f"原始數據: {data}")
                LabelA.config(text="數據格式錯誤！")
    
    elif data.startswith("LIGHT:"):
        print("收到光照數據")
        try:
            light_level = int(data.split(":")[1])
            print(f"光照強度: {light_level}")
            
            # 更新光照強度顯示
            light_label.config(text=f"光照強度: {light_level}")
            
            # 保存光照強度數據到資料庫
            save_light_record(light_level)
            
            if light_level < light_threshold:
                LabelA.config(text=f"測得光照強度 {light_level} 小於閾值 {light_threshold}\n觸發開門操作（環境較暗）")
            else:
                LabelA.config(text=f"測得光照強度 {light_level}（環境較亮）")
        except Exception as e:
            print(f"解析光照數據錯誤: {e}")
            print(f"原始數據: {data}")
            LabelA.config(text="光照數據格式錯誤！")
    
    elif data.startswith("DOOR:"):
        status = data.split(":")[1]
        print(f"門狀態: {status}")
        
        if status == "Open":
            door_label.config(text="門狀態: 開啟", bg="green", fg="white")
            
            # 判斷觸發類型 (溫度或光照)
            if "ALERT" in data_queue.queue:
                save_door_status("Open", "Temperature")
            else:
                save_door_status("Open", "Light")
        elif status == "Close":
            door_label.config(text="門狀態: 關閉", bg="red", fg="white")
            save_door_status("Close", "Auto")
    
    elif data.startswith("ALERT:"):
        alert_message = data.split(":")[1]
        print(f"警報: {alert_message}")
        
        # 顯示警告對話框
        messagebox.showwarning("系統警報", alert_message)
        LabelA.config(text=f"警報: {alert_message}")
    
    # 更新界面
    LabelA.update()

# 發送 'c' 指令（讀取 DHT11 溫濕度感測器數據）
def SendCmdC():
    global condition, ser
    if not ser or not ser.is_open:
        LabelA.config(text="串口未連接！")
        return
        
    SerialWrite(b'c\n')  # 發送 'c' 指令，添加換行符
    LabelA.config(text="正在讀取溫濕度...")

# 發送開門指令
def SendOpenDoor():
    global ser
    if not ser or not ser.is_open:
        LabelA.config(text="串口未連接！")
        return
        
    SerialWrite(b'open\n')  # 發送開門指令
    LabelA.config(text="發送開門命令...")

# 發送關門指令
def SendCloseDoor():
    global ser
    if not ser or not ser.is_open:
        LabelA.config(text="串口未連接！")
        return
        
    SerialWrite(b'close\n')  # 發送關門指令
    LabelA.config(text="發送關門命令...")

# 發送檢查光照和溫度指令
def SendCheckLight():
    global ser
    if not ser or not ser.is_open:
        LabelA.config(text="串口未連接！")
        return
        
    SerialWrite(b'check\n')  # 發送檢查命令
    LabelA.config(text="讀取光照和溫度中...")

# 切換自動控制模式
def ToggleAutoControl():
    global ser
    if not ser or not ser.is_open:
        LabelA.config(text="串口未連接！")
        return
    
    if buttonAuto.cget('text') == "自動控制:開":
        SerialWrite(b'auto:off\n')  # 關閉自動控制
        buttonAuto.config(text="自動控制:關")
        LabelA.config(text="已關閉自動控制模式")
    else:
        SerialWrite(b'auto:on\n')  # 開啟自動控制
        buttonAuto.config(text="自動控制:開")
        LabelA.config(text="已開啟自動控制模式")

# 發送設置溫度閾值指令
def UpdateTemperatureThreshold(value):
    global temperature_threshold, ser
    temperature_threshold = float(value)
    threshold_label.config(text=f"溫度閾值: {temperature_threshold}°C")
    
    if ser and ser.is_open:
        cmd = f'temp:{temperature_threshold}\n'.encode()
        SerialWrite(cmd)
        print(f"發送溫度閾值設置: {temperature_threshold}°C")

# 發送設置光照閾值指令
def UpdateLightThreshold(value):
    global light_threshold, ser
    light_threshold = int(value)
    light_threshold_label.config(text=f"光照閾值: {light_threshold}")
    
    if ser and ser.is_open:
        cmd = f'light:{light_threshold}\n'.encode()
        SerialWrite(cmd)
        print(f"發送光照閾值設置: {light_threshold}")

# 查看資料庫記錄
def ViewDatabase():
    # 打開新視窗顯示資料庫記錄
    db_window = tkinter.Toplevel(Tkwindow)
    db_window.title("資料庫記錄")
    db_window.minsize(800, 600)
    
    # 創建 Notebook (選項卡)
    import tkinter.ttk as ttk
    notebook = ttk.Notebook(db_window)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)
    
    # 溫濕度記錄選項卡
    dht_frame = tkinter.Frame(notebook)
    notebook.add(dht_frame, text='溫濕度記錄')
    
    # 光照記錄選項卡
    light_frame = tkinter.Frame(notebook)
    notebook.add(light_frame, text='光照記錄')
    
    # 門狀態記錄選項卡
    door_frame = tkinter.Frame(notebook)
    notebook.add(door_frame, text='門狀態記錄')
    
    # 顯示溫濕度記錄
    dht_listbox = tkinter.Listbox(dht_frame, width=80, height=20)
    dht_listbox.pack(padx=10, pady=10, fill='both', expand=True)
    
    # 顯示光照記錄
    light_listbox = tkinter.Listbox(light_frame, width=80, height=20)
    light_listbox.pack(padx=10, pady=10, fill='both', expand=True)
    
    # 顯示門狀態記錄
    door_listbox = tkinter.Listbox(door_frame, width=80, height=20)
    door_listbox.pack(padx=10, pady=10, fill='both', expand=True)
    
    # 讀取記錄並顯示
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        
        # 獲取溫濕度記錄
        try:
            cursor.execute("SELECT temperature, humidity, timestamp FROM dht_records ORDER BY timestamp DESC LIMIT 100")
            for i, (temperature, humidity, timestamp) in enumerate(cursor.fetchall()):
                dht_listbox.insert(tkinter.END, f"{timestamp} - 溫度: {temperature}°C, 濕度: {humidity}%")
        except mysql.Error as e:
            dht_listbox.insert(tkinter.END, f"獲取溫濕度記錄時出錯: {e}")
        
        # 獲取光照記錄
        try:
            cursor.execute("SELECT light_level, timestamp FROM light_records ORDER BY timestamp DESC LIMIT 100")
            for i, (light_level, timestamp) in enumerate(cursor.fetchall()):
                light_listbox.insert(tkinter.END, f"{timestamp} - 光照強度: {light_level}")
        except mysql.Error as e:
            light_listbox.insert(tkinter.END, f"獲取光照記錄時出錯: {e}")
        
        # 獲取門狀態記錄
        try:
            cursor.execute("SELECT status, trigger_type, timestamp FROM door_records ORDER BY timestamp DESC LIMIT 100")
            for i, (status, trigger_type, timestamp) in enumerate(cursor.fetchall()):
                door_listbox.insert(tkinter.END, f"{timestamp} - 門狀態: {status}, 觸發類型: {trigger_type}")
        except mysql.Error as e:
            door_listbox.insert(tkinter.END, f"獲取門狀態記錄時出錯: {e}")
        
        cursor.close()
        conn.close()
    else:
        tkinter.Label(db_window, text="無法連接到資料庫").pack()

# 連接 Arduino
def Serial_Connect():
    global ser, connect_status
    print('正在連接 Arduino..........')
    LabelA.config(text='正在連接 Arduino..........')
    LabelA.update_idletasks()
    
    # 如果串口已經打開，先關閉
    if ser and ser.is_open:
        connect_status = False
        sleep(1)  # 給讀取線程時間退出
        ser.close()
        sleep(1)  # 等待串口完全關閉
    
    try:
        ser = serial.Serial(SERIAL_PORT, 115200, timeout=0.5)
        print("串口打開成功")
        # 啟動讀取線程
        connect_status = True
        threading.Thread(target=serial_reader, daemon=True).start()
        
        # 初始化按鈕狀態
        buttonC.config(state='normal')
        buttonOpen.config(state='normal')
        buttonClose.config(state='normal')
        buttonLight.config(state='normal')
        buttonAuto.config(state='normal')
        buttonStart.config(state='disabled')
        
        # 發送初始命令
        SerialWrite(b'\n')
        LabelA.config(text='Arduino 已連接！等待狀態...')
        
        return True
        
    except serial.SerialException as e:
        print(f"串口連接錯誤: {e}")
        LabelA.config(text='串口連接失敗！請檢查設備連接')
        return False

# 退出程式
def Exit():
    global ser, connect_status
    print('退出程式....')
    LabelA.config(text='退出程式...')
    LabelA.update_idletasks()
    
    # 停止讀取線程
    connect_status = False
    sleep(1)
    
    try:
        if ser and ser.is_open:
            SerialWrite(b'\x1b\n')  # 發送 ESC 碼 (0x1B) 來通知 Arduino 停止
            ser.close()
    except serial.SerialException as e:
        print(f"關閉串口時發生錯誤: {e}")
    finally:
        Tkwindow.destroy()

# 初始化資料庫
def init_database():
    create_tables()

# 創建 Tkinter 視窗
Tkwindow = tkinter.Tk()
Tkwindow.title('ESP32 溫度監控與車門控制系統')
Tkwindow.minsize(700, 500)

# 創建主框架
main_frame = tkinter.Frame(Tkwindow)
main_frame.pack(fill='both', expand=True, padx=10, pady=10)

# 左側面板 - 狀態顯示
left_panel = tkinter.Frame(main_frame, borderwidth=2, relief='groove')
left_panel.pack(side=tkinter.LEFT, fill='both', expand=True, padx=5, pady=5)

# 右側面板 - 控制選項
right_panel = tkinter.Frame(main_frame, borderwidth=2, relief='groove')
right_panel.pack(side=tkinter.RIGHT, fill='both', expand=True, padx=5, pady=5)

# 顯示 Arduino 狀態的標籤
LabelA = tkinter.Label(left_panel, bg='white', fg='black', text='請按 "連接" 開始', width=30, height=3)
LabelA.pack(side=tkinter.TOP, padx=10, pady=10, fill='x')

# 添加溫濕度顯示區域
dht_frame = tkinter.Frame(left_panel, borderwidth=2, relief='groove')
dht_frame.pack(side=tkinter.TOP, padx=10, pady=5, fill='x')

dht_label = tkinter.Label(dht_frame, text="溫度: --°C\n濕度: --%", height=2)
dht_label.pack(pady=5)

# 添加光照強度顯示區域
light_frame = tkinter.Frame(left_panel, borderwidth=2, relief='groove')
light_frame.pack(side=tkinter.TOP, padx=10, pady=5, fill='x')

light_label = tkinter.Label(light_frame, text="光照強度: --", height=1)
light_label.pack(pady=5)

# 添加門狀態顯示區域
door_frame = tkinter.Frame(left_panel, borderwidth=2, relief='groove')
door_frame.pack(side=tkinter.TOP, padx=10, pady=5, fill='x')

door_label = tkinter.Label(door_frame, text="車門狀態: 關閉", height=1, bg="red", fg="white")
door_label.pack(pady=5, fill='x')

# 添加溫度閾值滑桿
threshold_frame = tkinter.Frame(right_panel, borderwidth=2, relief='groove')
threshold_frame.pack(side=tkinter.TOP, fill='x', padx=10, pady=5)

threshold_title = tkinter.Label(threshold_frame, text="溫度設定", font=("Arial", 10, "bold"))
threshold_title.pack(side=tkinter.TOP, pady=2)

threshold_label = tkinter.Label(threshold_frame, text=f"溫度閾值: {temperature_threshold}°C", width=15)
threshold_label.pack(side=tkinter.TOP, padx=5, pady=2)

threshold_slider = tkinter.Scale(threshold_frame, from_=0, to=50, orient='horizontal', 
                               length=200, resolution=0.5, command=UpdateTemperatureThreshold)
threshold_slider.set(temperature_threshold)
threshold_slider.pack(side=tkinter.TOP, padx=5, pady=2)

# 添加光照閾值滑桿
light_threshold_frame = tkinter.Frame(right_panel, borderwidth=2, relief='groove')
light_threshold_frame.pack(side=tkinter.TOP, fill='x', padx=10, pady=5)

light_threshold_title = tkinter.Label(light_threshold_frame, text="光照設定", font=("Arial", 10, "bold"))
light_threshold_title.pack(side=tkinter.TOP, pady=2)

light_threshold_label = tkinter.Label(light_threshold_frame, text=f"光照閾值: {light_threshold}", width=15)
light_threshold_label.pack(side=tkinter.TOP, padx=5, pady=2)

light_threshold_slider = tkinter.Scale(light_threshold_frame, from_=0, to=4095, orient='horizontal', 
                                     length=200, resolution=50, command=UpdateLightThreshold)
light_threshold_slider.set(light_threshold)
light_threshold_slider.pack(side=tkinter.TOP, padx=5, pady=2)

# 控制按鈕區
control_frame = tkinter.Frame(right_panel, borderwidth=2, relief='groove')
control_frame.pack(side=tkinter.TOP, fill='x', padx=10, pady=5)

control_title = tkinter.Label(control_frame, text="控制選項", font=("Arial", 10, "bold"))
control_title.pack(side=tkinter.TOP, pady=2)

# 上排按鈕
top_buttons_frame = tkinter.Frame(control_frame)
top_buttons_frame.pack(side=tkinter.TOP, fill='x', padx=5, pady=2)

# 讀取 DHT11 溫濕度按鈕
buttonC = tkinter.Button(top_buttons_frame, text='讀取溫濕度', width=10, command=SendCmdC, state='disabled')
buttonC.pack(side=tkinter.LEFT, padx=5, pady=5)

# 檢查光照按鈕
buttonLight = tkinter.Button(top_buttons_frame, text='讀取光照', width=10, command=SendCheckLight, state='disabled')
buttonLight.pack(side=tkinter.LEFT, padx=5, pady=5)

# 下排按鈕
bottom_buttons_frame = tkinter.Frame(control_frame)
bottom_buttons_frame.pack(side=tkinter.TOP, fill='x', padx=5, pady=2)

# 開門按鈕
buttonOpen = tkinter.Button(bottom_buttons_frame, text='開門', width=10, command=SendOpenDoor, state='disabled')
buttonOpen.pack(side=tkinter.LEFT, padx=5, pady=5)

# 關門按鈕
buttonClose = tkinter.Button(bottom_buttons_frame, text='關門', width=10, command=SendCloseDoor, state='disabled')
buttonClose.pack(side=tkinter.LEFT, padx=5, pady=5)

# 自動控制按鈕
buttonAuto = tkinter.Button(control_frame, text='自動控制:開', width=15, command=ToggleAutoControl, state='disabled')
buttonAuto.pack(side=tkinter.TOP, padx=5, pady=5)

# 底部按鈕
bottom_frame = tkinter.Frame(Tkwindow)
bottom_frame.pack(side=tkinter.BOTTOM, fill='x', padx=10, pady=10)

# 查看資料庫按鈕
buttonDB = tkinter.Button(bottom_frame, text='查看記錄', width=10, command=ViewDatabase)
buttonDB.pack(side=tkinter.LEFT, padx=5)

# 連接 Arduino 按鈕
buttonStart = tkinter.Button(bottom_frame, text='連接', width=10, command=Serial_Connect)
buttonStart.pack(side=tkinter.RIGHT, padx=5)

# 退出按鈕
buttonEnd = tkinter.Button(bottom_frame, text='退出', width=10, command=Exit)
buttonEnd.pack(side=tkinter.RIGHT, padx=5)

# 初始化資料庫
init_database()

# 啟動數據處理
Tkwindow.after(100, process_queue)

# 開始 Tkinter 事件迴圈
Tkwindow.mainloop()