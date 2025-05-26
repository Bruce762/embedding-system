from django.urls import path
from . import views

urlpatterns = [
    # 現有的 URL 模式
    path('sensor/upload/', views.sensor_upload, name='sensor_upload'),
    path('sensor/data/', views.sensor_data, name='sensor_data'),
    path('image/upload/', views.image_upload, name='image_upload'),
    path('image/download/<str:filename>/', views.image_download, name='image_download'),
    path('serial/monitor/data/', views.serial_monitor_data, name='serial_monitor_data'),
    path('serial/monitor/control/', views.serial_monitor_control, name='serial_monitor_control'),
    path('serial/monitor/status/', views.serial_monitor_status, name='serial_monitor_status'),
    
    # 新增的 API 端點
    path('api/dht/', views.api_get_all_dht_data, name='api_get_all_dht_data'),
    path('api/dht/create/', views.api_create_dht_data, name='api_create_dht_data'),
    path('api/dht/latest/', views.api_get_latest_dht_data, name='api_get_latest_dht_data'),
    path('api/dht/<int:record_id>/delete/', views.api_delete_dht_data, name='api_delete_dht_data'),
] 