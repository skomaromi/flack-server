from django.urls import path

from .views import UploadAPIView, FileListAPIView

app_name = 'api'

urlpatterns = [
    path('', FileListAPIView.as_view(), name='list'),
    path('upload/', UploadAPIView.as_view(), name='upload')
]
