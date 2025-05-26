"""gameApi URL Configuration

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
from app import views as app_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', app_views.upload_data, name='upload'),
    # 有了這個 name='upload'，您可以在程式碼的任何地方通過名稱引用這個 URL，而不需要硬編碼路徑。
    # 這在以下情況特別有用：
    # 如果您需要修改 URL 路徑（例如從 upload/ 變成 data/upload/），只需更改 urlpatterns 中的定義，所有使用 name 引用的地方都會自動更新
    # 在模板中可以寫 {% url 'upload' %} 而不是硬編碼 URL
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# 這行程式碼的作用是讓 Django 在開發環境中能夠提供媒體文件的訪問
# settings.MEDIA_URL 定義了媒體文件的 URL 前綴，例如 '/media/'
# settings.MEDIA_ROOT 定義了媒體文件在系統中的實際存儲位置
# static() 函數會將這兩個設定結合，創建合適的 URL pattern 來處理媒體文件的請求
# 這樣當有人訪問 /media/xxxx.jpg 時，Django 就會去 MEDIA_ROOT 目錄下尋找並提供對應的文件
