from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Video(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    path = models.CharField(max_length=100)
    datetime = models.DateField(blank=False, null=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.CharField(max_length=300)
    datetime = models.DateField(blank=False, null=False)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
