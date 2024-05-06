from django.db import models


class Alerts(models.Model):
    alertid = models.AutoField(primary_key=True)
    regionid = models.ForeignKey(
        "Regions", models.DO_NOTHING, db_column="regionid", blank=True, null=True
    )
    starttime = models.DateTimeField(blank=True, null=True)
    endtime = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    alerttype = models.TextField(blank=True, null=True)
    iscontinue = models.BooleanField(blank=True, null=True)

    class Meta:
        db_table = "alerts"


class Regions(models.Model):
    regionid = models.IntegerField(primary_key=True)
    regionname = models.TextField()
    regiontype = models.TextField()

    class Meta:
        db_table = "regions"
