from django.urls import path

from .views import UploadAPIView

app_name = 'api'

urlpatterns = [
    path('upload/', UploadAPIView.as_view(), name='upload')
]
