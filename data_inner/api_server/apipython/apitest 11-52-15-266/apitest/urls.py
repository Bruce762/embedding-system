"""apitest URL Configuration

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
from django.urls import path
from app import views #從view載入所有api功能
#（新增）
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('sensor/upload/', views.sensor_upload, name='sensor_upload'), #剛剛view中的,
    path('sensor/list/', views.sensor_data, name='sensor_list'),
    path('sensor/data/', views.sensor_data, name='sensor_data'),
    #（新增）
    path('image/upload/', views.image_upload, name='image_upload'),
    path('image/download/<str:filename>/', views.image_download, name='image_download'),
    path('upload/', views.upload_data, name='upload'),
    path('data/', views.show_data, name='data')
]

#這行要放在所有程式的底下
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
