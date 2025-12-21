# analysis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('strong-second/', views.strong_second_view, name='strong_second'),
    path('pitcher-meta/', views.pitcher_meta_view, name='pitcher_meta'),
    path('relief-metrics/', views.relief_metrics_view, name='relief_metrics'),
    # 추가된 라인
    path('cost-effectiveness/', views.cost_effectiveness_view, name='cost_effectiveness'),
]