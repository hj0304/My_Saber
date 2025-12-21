# analysis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('strong-second/', views.strong_second_view, name='strong_second'),
    path('pitcher-meta/', views.pitcher_meta_view, name='pitcher_meta'),
]