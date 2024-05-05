from django_q.models import Schedule

Schedule.objects.create(func='alerts.db_updater.schedule_alerts_fetching', schedule_type=Schedule.MINUTES)
# schedule('alerts.db_updater.schedule_alerts_fetching', schedule_type='I', minutes=5, repeats=-1)
