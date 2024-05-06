import requests
from django_q.tasks import schedule
from air_alerts_analyzer import settings
from django.db import IntegrityError
from .models import Alerts, Regions
from dateutil.parser import parse


def save_alerts(data):
    for entry in data:
        region_id = entry['regionId']
        region_name = entry['regionName']
        alarms = entry['alarms']

        # Перевіряємо та оновлюємо регіон, якщо потрібно
        region, created = Regions.objects.get_or_create(regionid=region_id, defaults={'regionname': region_name})

        for alarm in alarms:
            is_continue = alarm.get('isContinue', False)
            # Додаємо тільки ті тривоги, де isContinue = False
            if not is_continue:
                start_date = alarm['startDate']
                end_date = alarm['endDate']
                duration = calculate_duration(start_date, end_date)
                alert_type = alarm.get('alertType', 'UNKNOWN')

                # Спроба створення нового запису тривоги
                try:
                    Alerts.objects.update_or_create(
                        regionid=region,
                        starttime=start_date,
                        endtime=end_date,
                        duration=duration,
                        alerttype=alert_type,
                        iscontinue=is_continue
                    )
                except IntegrityError:
                    # Якщо запис вже існує, можемо оновити інформацію або пропустити
                    continue


def calculate_duration(start, end):
    # Перетворення стрічок ISO8601 на об'єкти datetime
    start_dt = parse(start)
    end_dt = parse(end)
    return end_dt - start_dt


def fetch_alerts_from_api(regionId):
    url = f'https://api.ukrainealarm.com/api/v3/alerts/regionHistory?regionId={regionId}'
    headers = {
        'Authorization': settings.ALERTS_API
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        save_alerts(data)
    else:
        print(f"Failed to fetch data: {response.status_code}")


def schedule_alerts_fetching():
    regions = Regions.objects.all()
    for region in regions:
        schedule('alerts.db_updater.fetch_alerts_from_api', regionId=str(region.regionid), schedule_type='O')
