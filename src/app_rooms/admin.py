from django.contrib import admin

from .models import Room
from .forms import RoomModelForm


class RoomModelAdmin(admin.ModelAdmin):
    form = RoomModelForm


admin.site.register(Room, RoomModelAdmin)
