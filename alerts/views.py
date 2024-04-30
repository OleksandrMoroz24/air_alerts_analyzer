# views.py

from django.shortcuts import render
from django.db.models import Count, Avg, Max
from django.db.models.functions import ExtractWeekDay, ExtractHour
from .models import Alerts, Regions
from datetime import datetime

def region_alerts_analytics(request):
    regions = Regions.objects.all()
    selected_region = request.POST.get('regionid')
    start_date = request.POST.get('startdate') or datetime.now().strftime('%Y-%m-%d')  # default to today if not provided
    end_date = request.POST.get('enddate') or datetime.now().strftime('%Y-%m-%d')  # default to today if not provided
    chart_type = request.POST.get('charttype', 'hour')  # Default to 'hour'

    context = {
        'regions': regions,
        'selected_region': selected_region,
        'start_date': start_date,
        'end_date': end_date,
        'chart_type': chart_type,
        # Initialize other context variables here...
    }

    if request.method == 'POST':
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        end_datetime = end_datetime.replace(hour=23, minute=59, second=59)

        alerts = Alerts.objects.filter(
            regionid_id=selected_region,
            starttime__gte=start_datetime,
            endtime__lte=end_datetime
        ).order_by('-starttime')

        context['alerts'] = alerts
        context['count'] = alerts.count()
        context['average_duration'] = alerts.aggregate(Avg('duration'))['duration__avg']
        context['max_duration'] = alerts.aggregate(Max('duration'))['duration__max']
        context['chart_type'] = chart_type

        if chart_type == 'weekday':
            weekday_counts = alerts.annotate(weekday=ExtractWeekDay('starttime')).values('weekday').annotate(
                count=Count('alertid')).order_by('weekday')
            context['weekday_counts'] = {day['weekday']: day['count'] for day in weekday_counts}
        if chart_type == 'hour':
            hour_counts_query = alerts.annotate(hour=ExtractHour('starttime')).values('hour').annotate(
                count=Count('alertid')).order_by('hour')
            hour_counts = {hour['hour']: hour['count'] for hour in hour_counts_query}
            context['hour_counts_list'] = [hour_counts.get(hour, 0) for hour in range(24)]

    return render(request, 'alerts_analytics.html', context)
