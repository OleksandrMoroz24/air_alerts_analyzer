# views.py
from django.shortcuts import render
from django.db.models import Count, Avg, Max
from .models import Alerts, Regions
from datetime import datetime


def region_alerts_analytics(request):
    context = {
        'regions': Regions.objects.all(),
        'count': None,
        'average_duration': None,
        'max_duration': None
    }

    if request.method == 'POST':
        region_id = request.POST.get('regionid')
        start_date_str = request.POST.get('startdate')
        end_date_str = request.POST.get('enddate')

        # Convert user input into datetime objects assuming input format is %Y-%m-%d (HTML5 date input format)
        start_datetime = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Adjust the end time to include the entire day
        end_datetime = end_datetime.replace(hour=23, minute=59, second=59)

        # Filter alerts based on the selected region and time period
        alerts = Alerts.objects.filter(
            regionid_id=region_id,
            starttime__gte=start_datetime,
            endtime__lte=end_datetime
        )

        # Calculate count, average duration, and maximum duration
        context['count'] = alerts.count()
        avg_duration = alerts.aggregate(Avg('duration'))['duration__avg']
        max_duration = alerts.aggregate(Max('duration'))['duration__max']
        context['average_duration'] = avg_duration and avg_duration.total_seconds() // 60  # Convert to minutes
        context['max_duration'] = max_duration and max_duration.total_seconds() // 60  # Convert to minutes

    return render(request, 'alerts_analytics.html', context)
