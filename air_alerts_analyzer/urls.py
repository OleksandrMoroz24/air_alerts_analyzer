from django.contrib import admin
from django.urls import path
from alerts.views import region_alerts_analytics

urlpatterns = [
    path('alerts-analytics/', region_alerts_analytics, name='region_alerts_analytics'),
    path('admin/', admin.site.urls)
]
