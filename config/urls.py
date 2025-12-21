# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('analysis/', include('analysis.urls')),
    path('', include('core.urls')),  # 이 줄을 추가! (메인 주소 접속 시 core로 보냄)
]