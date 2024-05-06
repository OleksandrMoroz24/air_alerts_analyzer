from django.contrib import admin
from django.urls import path
from alerts.views import region_alerts_analytics, get_chatgpt_analysis

urlpatterns = [
    path('alerts-analytics/', region_alerts_analytics, name='region_alerts_analytics'),
    path('get-chatgpt-analysis/', get_chatgpt_analysis, name='get_chatgpt_analysis'),
    path('admin/', admin.site.urls)
]
