from django.urls import path
from django.contrib import admin
from . import views

admin.site.site_header = 'Insights Agent'
admin.site.index_title = 'Site Administration'
admin.site.site_title = 'Insights Agent Administration'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:project_id>/', views.show, name='show'),
]
