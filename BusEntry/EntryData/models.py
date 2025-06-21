from django.db import models

# Create your models here.

class CustomUser(models.Model):
    name = models.CharField(max_length=100)
    user_id = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)  # hashed

    def __str__(self):
        return self.user_id

class Bus_Data(models.Model):
    date = models.DateField()
    shift = models.CharField(max_length=20)
    bus_no = models.CharField(max_length=10)
    out_kms = models.FloatField()
    in_kms = models.FloatField(null=True, blank=True)  # Allow null
    diff = models.FloatField(null=True, blank=True)    # Allow null
    soc = models.CharField(max_length=20, null=True, blank=True)
    soc_in = models.CharField(max_length=20, null=True, blank=True, default="Not Provided")
    time_of_submission = models.TimeField()
    IN_Time = models.TimeField(default="00:00:00")
    user_name= models.CharField(max_length=50 ,default="Admin")

    def __str__(self):
        return f"{self.date} - Bus {self.bus_no} ({self.shift})"
