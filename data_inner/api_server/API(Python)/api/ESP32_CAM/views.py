from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings

@csrf_exempt
def G005(request):
    """
    處理上傳影像的視圖函數
    """
    if request.method == 'POST':
        # 讀取 body
        print(request.body)
        try:
            # 確保目錄存在
            media_dir = os.path.join(settings.BASE_DIR, 'cam_media')
            os.makedirs(media_dir, exist_ok=True)
            
            # 開啟寫檔位置，使用相對路徑
            file_path = os.path.join(media_dir, 'latest.jpg')
            with open(file_path, 'wb') as fh:
                fh.write(request.body)
            status = "OK"
        except Exception as e:
            status = "ERROR"
            print(f"ERROR: {str(e)}")
    return HttpResponse(status)

@csrf_exempt
def G004(request):
    """
    處理查看影像的視圖函數
    """
    if request.method == 'GET':
        try:
            # 使用相對路徑
            media_dir = os.path.join(settings.BASE_DIR, 'cam_media')
            file_path = os.path.join(media_dir, 'latest.jpg')
            
            if os.path.exists(file_path):
                return FileResponse(open(file_path, 'rb'), content_type='image/jpeg')
            else:
                return HttpResponse("No image found", status=404)
        except Exception as e:
            return HttpResponse(f"ERROR: {str(e)}", status=500)
    return HttpResponse("Method not allowed", status=405)
