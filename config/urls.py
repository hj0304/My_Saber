# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('analysis/', include('analysis.urls')),
    path('', include('core.urls')),  #(메인 주소 접속 시 core로 보냄)
    path('simulation/', include('simulation.urls')),
]