from django.shortcuts import render, redirect
from .models import DHT, TestModel  # 從models.py載入DHT資料表
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
import os
from django.views.decorators.csrf import csrf_exempt
import json
from . import serial_monitor
import datetime
import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# 設置日誌
logger = logging.getLogger(__name__)

# Create your views here.

# API 端點：上傳溫濕度數據
@api_view(['POST'])
def sensor_upload(request):
    """API 端點：上傳溫濕度數據"""
    try:
        data = request.data
        temp = data.get('temperature')
        hum = data.get('humidity')
        
        if temp is None or hum is None:
            return Response({
                'status': 'error',
                'message': '溫度和濕度數據都是必需的'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            temp_float = float(temp)
            hum_float = float(hum)
        except ValueError:
            return Response({
                'status': 'error',
                'message': '溫度和濕度必須是有效的數字'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # 檢查最後一條記錄的 ID
        try:
            last_record = DHT.objects.latest('recorded_at')
            # 如果最後記錄的 ID 是 1，則使用 ID 2，否則使用 ID 1
            next_id = 2 if last_record.id == 1 else 1
        except DHT.DoesNotExist:
            # 如果沒有記錄，從 ID 1 開始
            next_id = 1
        
        # 獲取當前時間
        current_time = datetime.datetime.now()
        
        # 如果指定 ID 的記錄已存在，則刪除它，然後創建新記錄
        try:
            old_record = DHT.objects.get(id=next_id)
            old_record.delete()
        except DHT.DoesNotExist:
            pass
            
        # 創建新記錄
        dht_record = DHT.objects.create(
            id=next_id,
            temperature=temp_float,
            humidity=hum_float
            # recorded_at 會自動使用當前時間
        )
        
        return Response({
            'status': 'success',
            'data': {
                'id': dht_record.id,
                'temperature': dht_record.temperature,
                'humidity': dht_record.humidity,
                'recorded_at': dht_record.recorded_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f'Error saving sensor data: {str(e)}')
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# API 端點：獲取感測器數據
@api_view(['GET'])
def sensor_data(request):
    """API 端點：獲取所有感測器數據"""
    try:
        data = DHT.objects.all().order_by('-recorded_at')
        response_data = [{
            'id': record.id,
            'temperature': record.temperature,
            'humidity': record.humidity,
            'recorded_at': record.recorded_at.strftime('%Y-%m-%d %H:%M:%S')
        } for record in data]
        return Response({
            'status': 'success',
            'data': response_data
        })
    except Exception as e:
        logger.error(f'Error fetching sensor data: {str(e)}')
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 圖片上傳
def image_upload(request):
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT)
    message = ''
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        file_path = os.path.join(settings.MEDIA_ROOT, image.name)
        with open(file_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        message = '圖片已成功上傳！'

    # 列出所有圖片檔案
    image_files = os.listdir(settings.MEDIA_ROOT) if os.path.exists(settings.MEDIA_ROOT) else []
    return render(request, 'image_upload.html', {'files': image_files, 'message': message})

# 圖片下載
def image_download(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    raise Http404("圖片不存在")

# API 端點：串口監控數據上傳
@api_view(['POST'])
def serial_monitor_data(request):
    """API 端點：處理串口監控的溫濕度數據上傳"""
    try:
        data = request.data
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        
        if temperature is None or humidity is None:
            return Response({
                'status': 'error',
                'message': '溫度和濕度數據都是必需的'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            temp_float = float(temperature)
            hum_float = float(humidity)
        except ValueError:
            return Response({
                'status': 'error',
                'message': '溫度和濕度必須是有效的數字'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        dht_record = DHT.objects.create(
            temperature=temp_float,
            humidity=hum_float
        )
        
        return Response({
            'status': 'success',
            'data': {
                'id': dht_record.id,
                'temperature': temp_float,
                'humidity': hum_float,
                'recorded_at': dht_record.recorded_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f'Error saving serial monitor data: {str(e)}')
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# API 端點：串口監控控制
@api_view(['POST'])
def serial_monitor_control(request):
    """API 端點：控制串口監控的啟動和停止"""
    try:
        data = request.data
        action = data.get('action')
        
        if action not in ['start', 'stop', 'request_data']:
            return Response({
                'status': 'error',
                'message': '無效的操作，請使用 start、stop 或 request_data'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'start':
            port = data.get('port')
            if port:
                serial_monitor.set_serial_port(port)
            
            if serial_monitor.start_monitoring():
                return Response({
                    'status': 'success',
                    'message': '串口監控已啟動'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': '啟動串口監控失敗'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        elif action == 'stop':
            if serial_monitor.stop_monitoring():
                return Response({
                    'status': 'success',
                    'message': '串口監控已停止'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': '停止串口監控失敗'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        elif action == 'request_data':
            if serial_monitor.request_dht_data():
                return Response({
                    'status': 'success',
                    'message': '已請求 DHT 數據'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': '請求 DHT 數據失敗'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f'Error in serial monitor control: {str(e)}')
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# API 端點：獲取串口監控狀態
@api_view(['GET'])
def serial_monitor_status(request):
    """API 端點：獲取串口監控狀態"""
    try:
        latest_records = DHT.objects.all().order_by('-recorded_at')[:10]
        
        status_data = {
            'is_running': serial_monitor.is_running,
            'serial_port': serial_monitor.serial_port,
            'baud_rate': serial_monitor.baud_rate,
            'latest_records': [{
                'id': record.id,
                'temperature': record.temperature,
                'humidity': record.humidity,
                'recorded_at': record.recorded_at.strftime('%Y-%m-%d %H:%M:%S')
            } for record in latest_records],
            'has_records': latest_records.exists(),
            'server_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 檢查請求是否需要 JSON 回應
        if request.accepted_renderer.format == 'json':
            return Response({
                'status': 'success',
                'data': status_data
            })
        
        # 返回網頁模板
        return render(request, 'serial_monitor.html', status_data)
        
    except Exception as e:
        logger.error(f'Error fetching serial monitor status: {str(e)}')
        if request.accepted_renderer.format == 'json':
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return render(request, 'serial_monitor.html', {
            'error_message': str(e),
            'is_running': False,
            'serial_port': '',
            'baud_rate': 0,
            'latest_records': [],
            'has_records': False,
            'server_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

# 新增 API 端點
@api_view(['GET'])
def api_get_all_dht_data(request):
    """獲取所有 DHT 數據的 API"""
    try:
        dht_data = DHT.objects.all().order_by('-recorded_at')
        data = [{
            'id': record.id,
            'temperature': record.temperature,
            'humidity': record.humidity,
            'recorded_at': record.recorded_at.strftime('%Y-%m-%d %H:%M:%S')
        } for record in dht_data]
        return Response({'status': 'success', 'data': data})
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def api_create_dht_data(request):
    """創建新的 DHT 數據記錄的 API"""
    try:
        data = request.data
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        
        if temperature is None or humidity is None:
            return Response({
                'status': 'error',
                'message': '溫度和濕度數據都是必需的'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            temp_float = float(temperature)
            hum_float = float(humidity)
        except ValueError:
            return Response({
                'status': 'error',
                'message': '溫度和濕度必須是有效的數字'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 檢查最後一條記錄的 ID
        try:
            last_record = DHT.objects.latest('recorded_at')
            # 如果最後記錄的 ID 是 1，則使用 ID 2，否則使用 ID 1
            next_id = 2 if last_record.id == 1 else 1
        except DHT.DoesNotExist:
            # 如果沒有記錄，從 ID 1 開始
            next_id = 1
        
        # 獲取當前時間
        current_time = datetime.datetime.now()
        
        # 如果指定 ID 的記錄已存在，則刪除它，然後創建新記錄
        try:
            old_record = DHT.objects.get(id=next_id)
            old_record.delete()
        except DHT.DoesNotExist:
            pass
            
        # 創建新記錄
        dht_record = DHT.objects.create(
            id=next_id,
            temperature=temp_float,
            humidity=hum_float
            # recorded_at 會自動使用當前時間
        )
        
        return Response({
            'status': 'success',
            'data': {
                'id': dht_record.id,
                'temperature': dht_record.temperature,
                'humidity': dht_record.humidity,
                'recorded_at': dht_record.recorded_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def api_get_latest_dht_data(request):
    """獲取最新的 DHT 數據的 API"""
    try:
        latest_record = DHT.objects.latest('recorded_at')
        data = {
            'id': latest_record.id,
            'temperature': latest_record.temperature,
            'humidity': latest_record.humidity,
            'recorded_at': latest_record.recorded_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        return Response({'status': 'success', 'data': data})
    except DHT.DoesNotExist:
        return Response({
            'status': 'error',
            'message': '沒有找到任何記錄'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def api_delete_dht_data(request, record_id):
    """刪除指定的 DHT 數據記錄的 API"""
    try:
        record = DHT.objects.get(id=record_id)
        record.delete()
        return Response({
            'status': 'success',
            'message': f'成功刪除記錄 ID: {record_id}'
        })
    except DHT.DoesNotExist:
        return Response({
            'status': 'error',
            'message': f'找不到 ID 為 {record_id} 的記錄'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
