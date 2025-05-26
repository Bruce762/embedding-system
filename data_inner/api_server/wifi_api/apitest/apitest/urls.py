from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ 上傳與資料顯示功能（API & HTML）
    path('upload/', views.upload_data, name='upload'),
    path('data/', views.show_data, name='data'),

    # 其他功能
    path('sensor/upload/', views.sensor_upload, name='sensor_upload'),
    path('sensor/list/', views.sensor_data, name='sensor_list'),
    path('sensor/data/', views.sensor_data, name='sensor_data'),
    path('image/upload/', views.image_upload, name='image_upload'),
    path('image/download/<str:filename>/', views.image_download, name='image_download'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
