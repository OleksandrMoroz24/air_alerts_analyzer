from django.db import models


class Region(models.Model):
    regionId = models.AutoField(primary_key=True)
    regionName = models.TextField()
    regionType = models.TextField()

    def __str__(self):
        return self.regionName


class Alert(models.Model):
    alertId = models.AutoField(primary_key=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, db_column='regionId')
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    duration = models.DurationField()
    alertType = models.TextField()
    isContinue = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.alertType} from {self.startTime} to {self.endTime}"
