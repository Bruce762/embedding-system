from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.shortcuts import render, redirect
from .models import sensor_data  # 載入你之前建立的 model
from datetime import datetime
import cv2
import os
from django.conf import settings
import numpy as np
import logging
import time                      # 新增：給鏡頭暖機用

logger = logging.getLogger(__name__)

# 接收 ESP32 傳來的資料
@csrf_exempt
def upload_data(request):
    """
    處理上傳的感測器數據和拍攝照片的視圖函數
    接收 POST 請求，包含距離和響應時間數據
    同時拍攝照片並保存
    """
    if request.method == 'POST':
        try:
            # 記錄接收到的請求信息
            logger.info(f"收到 POST 請求，Content-Type: {request.content_type}")
            logger.info(f"請求內容: {request.body.decode('utf-8')}")
            
            # 解析 JSON 數據
            data = json.loads(request.body)
            distance = data.get('distance')
            responseTime = data.get('responseTime')
            
            logger.info(f"解析後的數據 - distance: {distance}, responseTime: {responseTime}")

            if distance is not None and responseTime is not None:
                # === 拍照部分 ===
                # 初始化攝像頭，明確指定使用 AVFoundation 框架
                cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
                
                # 設定攝像頭為廣角模式
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # 設定較大的解析度以獲得更寬的視野
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                cap.set(cv2.CAP_PROP_ZOOM, 0.5)  # 設定較小的縮放值以獲得更廣的視角
                cap.set(cv2.CAP_PROP_FOCUS, 0)   # 設定較短的焦距
                logger.info("攝像頭已設定為廣角模式")
                
                # 嘗試啟用自動對焦（OpenCV ≥4.5 才有；若不支援會回傳 False）
                autofocus_enabled = cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
                logger.info(f"自動對焦設置狀態: {'成功' if autofocus_enabled else '不支援'}")

                # 讓鏡頭有 2 秒暖機時間，以便自動對焦完成
                warm_up_start = time.time()
                while time.time() - warm_up_start < 2:
                    cap.grab()      # 只抓取影格，不解析成畫面
                
                logger.info("攝像頭暖機完成")

                ret, frame = cap.read()  # ret: 是否成功獲取畫面, frame: 捕獲的圖像
                
                if ret:
                    # 如果需要的話，可以進行影像校正來減少廣角畸變
                    # 這裡使用簡單的方式來減少魚眼效果
                    height, width = frame.shape[:2]
                    camera_matrix = np.array([[width, 0, width/2],
                                           [0, height, height/2],
                                           [0, 0, 1]], dtype=np.float32)
                    dist_coeffs = np.zeros((4,1))
                    frame = cv2.undistort(frame, camera_matrix, dist_coeffs)
                
                cap.release()  # 立即釋放攝像頭資源

                if ret:  # 如果成功捕獲圖像
                    # === 建立儲存路徑 ===
                    # 根據當前日期建立目錄結構：media/sensor_images/年/月/日/
                    today = datetime.now()
                    media_path = os.path.join(settings.MEDIA_ROOT, 'sensor_images', 
                                            str(today.year), str(today.month), str(today.day))
                    # 確保目錄存在，不存在則創建
                    os.makedirs(media_path, exist_ok=True)
                    
                    logger.info(f"創建目錄: {media_path}")

                    # === 生成檔案名稱 ===
                    # 格式：image_年月日_時分秒.jpg
                    filename = f"image_{today.strftime('%Y%m%d_%H%M%S')}.jpg"
                    file_path = os.path.join(media_path, filename)
                    
                    logger.info(f"準備保存圖片到: {file_path}")

                    # === 保存圖片 ===
                    cv2.imwrite(file_path, frame)  # 將圖片保存到指定路徑
                    
                    logger.info("圖片保存成功")

                    # === 準備資料庫路徑 ===
                    # 構建相對路徑，用於存儲在資料庫中
                    relative_path = os.path.join('sensor_images', 
                                               str(today.year), str(today.month), 
                                               str(today.day), filename)
                    
                    try:
                        # === 創建資料庫記錄 ===
                        # 將數據和圖片路徑保存到資料庫
                        sensor_data.objects.create(
                            distance=distance,
                            responseTime=responseTime,
                            timestamp=today,
                            image=relative_path
                        )
                        logger.info("資料庫記錄創建成功")
                        return JsonResponse({"message": "資料和圖片接收成功"}, json_dumps_params={'ensure_ascii': False})
                    except Exception as db_error:
                        # 資料庫操作失敗的錯誤處理
                        logger.error(f"資料庫操作失敗: {str(db_error)}")
                        return JsonResponse({"error": f"資料庫操作失敗: {str(db_error)}"}, 
                                         status=400, json_dumps_params={'ensure_ascii': False})
                else:
                    # 拍照失敗的錯誤處理
                    logger.error("無法拍攝照片")
                    return JsonResponse({"error": "無法拍攝照片"}, 
                                     status=400, json_dumps_params={'ensure_ascii': False})

            else:
                # 數據不完整的錯誤處理
                logger.error("資料不完整")
                return JsonResponse({"error": "資料不完整"}, 
                                 status=400, json_dumps_params={'ensure_ascii': False})

        except json.JSONDecodeError as json_error:
            # JSON 解析錯誤的處理
            logger.error(f"JSON 解析失敗: {str(json_error)}")
            return JsonResponse(
                {"error": "JSON 格式錯誤", "detail": str(json_error)},
                status=400,
                json_dumps_params={'ensure_ascii': False}
            )
        except Exception as e:
            # 其他未預期錯誤的處理
            logger.error(f"處理失敗: {str(e)}")
            return JsonResponse(
                {"error": "處理失敗", "detail": str(e)},
                status=400,
                json_dumps_params={'ensure_ascii': False}
            )

    # 如果不是 POST 請求，返回錯誤
    return JsonResponse({"error": "只接受 POST 請求"}, status=405)
