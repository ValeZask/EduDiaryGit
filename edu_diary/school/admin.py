from django.contrib import admin
from .homepage.models import Project, ProjectMember, ProjectTask, Event, StudentEvent

admin.site.register(StudentEvent)
admin.site.register(Project)
admin.site.register(ProjectMember)
admin.site.register(ProjectTask)
admin.site.register(Event)
