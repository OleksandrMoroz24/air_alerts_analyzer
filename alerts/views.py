from django.shortcuts import render
from django.db.models import Count, Avg, Max
from django.db.models.functions import ExtractWeekDay, ExtractHour
from .models import Alerts, Regions
from datetime import datetime, timedelta

from .utils import check_active_alerts, analyze_report_with_openai, fetch_telegram_messages


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours} hours, {minutes} minutes" if hours else f"{minutes} minutes"

def region_alerts_analytics(request):
    regions = Regions.objects.all()
    selected_region = request.POST.get('regionid')
    region_name = regions.get(regionid=selected_region).regionname
    start_date = request.POST.get('startdate') or datetime.now().strftime('%Y-%m-%d')  # default to today if not provided
    end_date = request.POST.get('enddate') or datetime.now().strftime('%Y-%m-%d')  # default to today if not provided
    chart_type = request.POST.get('charttype', 'hour')  # Default to 'hour'

    active_alerts = False
    if selected_region:
        active_alerts = check_active_alerts(selected_region)

    context = {
        'regions': regions,
        'selected_region': selected_region,
        'region_name': region_name,
        'start_date': start_date,
        'end_date': end_date,
        'chart_type': chart_type,
        'active_alerts': active_alerts
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
        context['average_duration'] = format_timedelta(alerts.aggregate(Avg('duration'))['duration__avg'])
        context['max_duration'] = format_timedelta(alerts.aggregate(Max('duration'))['duration__max'])
        context['chart_type'] = chart_type

        weekday_counts = alerts.annotate(weekday=ExtractWeekDay('starttime')).values('weekday').annotate(
            count=Count('alertid')).order_by('weekday')
        context['weekday_counts'] = {day['weekday']: day['count'] for day in weekday_counts}

        hour_counts_query = alerts.annotate(hour=ExtractHour('starttime')).values('hour').annotate(
            count=Count('alertid')).order_by('hour')
        hour_counts = {hour['hour']: hour['count'] for hour in hour_counts_query}
        context['hour_counts_list'] = [hour_counts.get(hour, 0) for hour in range(24)]

        total_days = (end_datetime - datetime(2022, 2, 24, 0, 0, 0)).days + 1
        total_weeks = total_days / 7

        total_alerts = Alerts.objects.filter(
            regionid_id=selected_region,
            starttime__gte=datetime(2022, 2, 24, 0, 0, 0),
            endtime__lte=end_datetime
        ).count()

        weekly_frequency_all_time = total_alerts / total_weeks if total_weeks else 0

        last_month_start = end_datetime - timedelta(days=30)
        last_week_start = end_datetime - timedelta(days=7)

        total_alerts_last_month = Alerts.objects.filter(
            regionid_id=selected_region,
            starttime__gte=last_month_start,
            starttime__lte=end_datetime
        ).count()
        total_weeks_last_month = 4

        total_alerts_last_week = Alerts.objects.filter(
            regionid_id=selected_region,
            starttime__gte=last_week_start,
            starttime__lte=end_datetime
        ).count()
        total_weeks_last_week = 1

        weekly_frequency_last_month = total_alerts_last_month / total_weeks_last_month if total_weeks_last_month else 0
        weekly_frequency_last_week = total_alerts_last_week / total_weeks_last_week if total_weeks_last_week else 0

        context.update({
            'weekly_frequency_all_time': f"{weekly_frequency_all_time:.1f} alerts per week",
            'weekly_frequency_last_month': f"{weekly_frequency_last_month:.1f} alerts per week",
            'weekly_frequency_last_week': f"{weekly_frequency_last_week:.1f} alerts per week",
        })

        tg_messages = fetch_telegram_messages()
        message = (
            f"Сьогоднішня дата: {datetime.now()}, назва регіону {region_name}, наявність тривоги в регіоні {active_alerts},"
            f"частота тривог в тиждень за весь час: {weekly_frequency_all_time}, "
            f"частота тривог в тиждень за останній місяці: {weekly_frequency_last_month}, "
            f"частота тривог в тиждень за останній тиждень: {weekly_frequency_last_week}, "
            f"кількість тривог по дням тижня {weekday_counts}, "
            f"кількість тривог по годинам дня {hour_counts}, "
            f"останні повідомлення повітряних сил україни щодо тривог {tg_messages}"


        )
        chatgpt_report = analyze_report_with_openai(message)
        context['chatgpt_report'] = chatgpt_report

    return render(request, 'alerts_analytics.html', context)

