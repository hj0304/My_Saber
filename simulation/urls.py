# simulation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('pitch-tunnel/', views.pitch_tunnel_view, name='pitch_tunnel'),
]