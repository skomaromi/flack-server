from django.urls import path

from .views import MessageListAPIView

app_name = 'api'

urlpatterns = [
    path('', MessageListAPIView.as_view(), name='list')
]
