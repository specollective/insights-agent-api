"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from rest_framework import routers
from api import views
from rest_framework_bulk.routes import BulkRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Initial routers
router = routers.DefaultRouter()
bulk_router = BulkRouter()

# Register regular routes
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Register bulk routes
bulk_router.register(r'data_entries', views.DataEntryViewSet)

# Set url patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include(bulk_router.urls)),
    path('api/send_magic_link', views.send_magic_link, name='send_magic_link'),
    path('api/confirm_magic_link', views.confirm_magic_link, name='confirm_magic_link'),
    path('api/send_access_code', views.send_access_code, name='send_access_code'),
    path('api/confirm_access_code', views.confirm_access_code, name='confirm_access_code'),
    path('api/surveys', views.surveys, name='surveys'), # is this already being used? change to survey_results?
    path('api/logout', views.logout, name='logout'),
    path('api/current_user', views.current_user, name='current_user'),
    path('', include('pages.urls')),
]
