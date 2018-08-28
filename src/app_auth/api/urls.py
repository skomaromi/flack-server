from django.urls import path

from .views import LoginAPIView, UserListAPIView

app_name = 'api'

urlpatterns = [
    path('users/', UserListAPIView.as_view(), name='users'),
    path('login/', LoginAPIView.as_view(), name='login')
]
