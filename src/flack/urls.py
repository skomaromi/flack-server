"""flack URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .views import dashboard

schema_view = get_schema_view(
    openapi.Info(
        title="API Reference",
        default_version='v1',
    ),
)

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('admin/', admin.site.urls),
    path('api/', schema_view.with_ui('swagger')),
    path('api/auth/', include('app_auth.api.urls', namespace='auth-api')),
    path('api/rooms/', include('app_rooms.api.urls', namespace='room-api')),
    path('api/messages/', include('app_messages.api.urls', namespace='message-api')),
    path('api/files/', include('app_files.api.urls', namespace='file-api')),
]
