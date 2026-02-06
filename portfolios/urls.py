"""
URL configuration for portfolios app - Dashboard routes.
"""
from django.urls import path
from portfolios.views import DashboardSiteView

urlpatterns = [
    path('site/', DashboardSiteView.as_view(), name='dashboard-site'),
]
