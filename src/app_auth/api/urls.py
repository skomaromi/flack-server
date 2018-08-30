from django.urls import path

from .views import (
    LoginAPIView,
    RegisterAPIView,
    UserExistsAPIView,
    UserListAPIView
)

app_name = 'api'

urlpatterns = [
    path('users/', UserListAPIView.as_view(), name='users'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('user-exists/', UserExistsAPIView.as_view(), name='user-exists'),
    path('register/', RegisterAPIView.as_view(), name='register')
]
