from django.db import models

class Project(models.Model):
    title = models.TextField()
    description = models.TextField()
