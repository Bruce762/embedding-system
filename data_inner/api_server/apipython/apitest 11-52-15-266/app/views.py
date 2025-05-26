from django.shortcuts import render, redirect
from .models import dht  # 從models.py載入需要的資料表
#（新增）
from django.conf import settings
from django.http import FileResponse, Http404
import os

# 上傳資料
def sensor_upload(request):
    if request.method == 'POST':
        temp = request.POST.get('temperature')
        hum = request.POST.get('humidity')
        dht.objects.create(temperature=temp, humidity=hum)
        return redirect('sensor_list')
    return render(request, 'sensor_upload.html')
# 查詢資料
def sensor_data(request):
    data = dht.objects.all().order_by('-recorded_at')
    return render(request, 'sensor_data.html', {'data': data})
# 圖片下載（新增）
def image_download(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    raise Http404("圖片不存在")
# 上傳圖片（新增）
def image_upload(request):
    # 若找不到 media 資料夾，自動建立
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

    # 列出所有檔案名稱
    files = os.listdir(settings.MEDIA_ROOT)
    return render(request, 'image_upload.html', {
        'files': files,
        'message': message
    })