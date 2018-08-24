from django.urls import path

from .views import RoomListAPIView

app_name = 'api'

urlpatterns = [
    path('', RoomListAPIView.as_view(), name='list')
]
