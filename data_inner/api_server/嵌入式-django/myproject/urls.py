"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from testapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 感測器數據相關路由
    path('sensor/upload/', views.sensor_upload, name='sensor_upload'),
    path('sensor/data/', views.sensor_data, name='sensor_data'),
    
    # 圖片上傳下載路由
    path('image/upload/', views.image_upload, name='image_upload'),
    path('image/download/<str:filename>/', views.image_download, name='image_download'),
    
    # 串口監控相關路由
    path('serial/monitor/', views.serial_monitor_status, name='serial_monitor_status'),
    path('serial/monitor/status/', views.serial_monitor_status, name='serial_monitor_status_api'),
    path('serial/monitor/control/', views.serial_monitor_control, name='serial_monitor_control'),
    path('serial/monitor/data/', views.serial_monitor_data, name='serial_monitor_data'),
    
    # API 路由
    path('api/sensor/', views.sensor_upload, name='esp32_data_upload'),  # ESP32 專用API端點
    path('api/dht/', views.api_get_all_dht_data, name='api_get_all_dht_data'),
    path('api/dht/create/', views.api_create_dht_data, name='api_create_dht_data'),
    path('api/dht/latest/', views.api_get_latest_dht_data, name='api_get_latest_dht_data'),
    path('api/dht/<int:record_id>/delete/', views.api_delete_dht_data, name='api_delete_dht_data'),
]

# 添加媒體文件的URL配置
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
