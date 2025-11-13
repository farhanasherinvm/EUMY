# course/urls.py (Example structure)

from django.urls import path
from .views import DashboardView

urlpatterns = [
    # Dashboard API
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
]