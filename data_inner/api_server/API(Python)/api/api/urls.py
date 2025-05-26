from django.contrib import admin
from django.urls import path
# from . import views           # 若檔案結構不同，請視情況修改匯入路徑
from ESP32_CAM import views    # 從 ESP32_CAM 應用程式引入 views
from django.views.generic.base import RedirectView
# from . import app_views     # 備註：下方註解路徑對應此行

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('G005/', views.G005, name='G005'),   # 上傳影像的路徑
    path('G004/', views.G004, name='G004'),   # 用來查看影像的路徑

    # path('upload/', app_views.upload_data, name='upload'),
    # path('data/', app_views.show_data, name='data'),
    # path('sensor/sensor_upload/', app_views.dht_upload, name='sensor_upload'),
    # path('sensor/sensor_data/', app_views.dht_data, name='sensor_data'),
    # path('image/upload/', app_views.image_upload, name='image_upload'),
    # path('image/download/<str:filename>/', app_views.image_download, name='image_download'),
]
