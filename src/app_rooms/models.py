from django.conf import settings
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError


class Room(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='rooms')
    name = models.CharField(max_length=255, null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)


@receiver(m2m_changed, sender=Room.participants.through)
def validate_room_m2m(sender, instance, action, reverse, model, pk_set, using, *args, **kwargs):
    print("Room::m2m_changed event triggered")
    participants_count = instance.participants.count()

    if participants_count < 2:
        raise ValidationError("A room must contain at least 2 participants")
