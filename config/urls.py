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
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
# router.register(r'surveys', views.SurveyViewSet)
router.register(r'data_entries', views.DataEntryViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/send_access_code', views.send_access_code, name='send_access_code'),
    path('api/check_access_code', views.check_access_code, name='check_access_code'),
    path('api/resend_access_code', views.resend_access_code, name='resend_access_code'),
    path('api/surveys', views.surveys, name='surveys'),
    path('api/logout', views.logout, name='logout'),
    path('api/current_user', views.current_user, name='current_user'),
    path('', include('pages.urls')),
]

# Cruft
# path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
# path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
# path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
# path('projects/', include('projects.urls')),
# path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
