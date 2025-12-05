from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'), # Landing Page
    path('live/', views.live_dashboard, name='live_dashboard'), # New Separate Dashboard
    path('analyze/', views.analyze_transaction, name='analyze'),
    path('export/', views.export_fraud_report, name='export_report'),
]