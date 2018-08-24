from django.conf import settings
from django.db import models

from app_files.models import File
from app_rooms.models import Room


class Location(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()


class Message(models.Model):
    content = models.TextField()
    # TODO: maybe replace CASCADE with a nicer alternative
    # (like keeping the message, but indicating that the associated File was deleted)
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    location = models.OneToOneField(Location, on_delete=models.CASCADE, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)
