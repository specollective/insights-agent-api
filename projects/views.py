from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.core import serializers
from .models import Project
from django.views.decorators.csrf import csrf_exempt
import json

# NOTE: Disabling csrf for this demo API
@csrf_exempt
def index(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode("utf-8"))
        title = data.get('title')
        description = data.get('description')
        project_data = {
          'title': title,
          'description': description,
        }
        project = Project.objects.create(**project_data)
        project_data['id'] = project.id
        return JsonResponse({ 'data': project_data })
    else:
        data = list(Project.objects.values())
        return JsonResponse({ 'data': data })

def show(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    data = {
      'title': project.title,
      'description': project.description,
    }
    return JsonResponse({ 'data': data })
