# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # 빈 문자열('')이 메인 주소를 의미함
]