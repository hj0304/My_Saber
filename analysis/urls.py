# analysis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('strong-second/', views.strong_second_view, name='strong_second'),
    path('pitcher-meta/', views.pitcher_meta_view, name='pitcher_meta'),
    path('relief-metrics/', views.relief_metrics_view, name='relief_metrics'),
    path('cost-effectiveness/', views.cost_effectiveness_view, name='cost_effectiveness'),
    path('sample-size/', views.sample_size_view, name='sample_size'),
]