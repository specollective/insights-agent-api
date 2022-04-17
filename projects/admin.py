from django.contrib import admin
from .models import Project

admin.site.site_header = 'Insights Agent'
admin.site.index_title = 'Site Administration'
admin.site.site_title = 'Insights Agent Administration'
admin.site.register(Project)
