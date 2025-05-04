from django.contrib import admin
from .homepage.models import Project, ProjectMember, ProjectTask, Event, StudentEvent
from .diary.models import Class, Subject, Schedule, Grade

admin.site.register(StudentEvent)
admin.site.register(Project)
admin.site.register(ProjectMember)
admin.site.register(ProjectTask)
admin.site.register(Event)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(Schedule)
admin.site.register(Grade)
