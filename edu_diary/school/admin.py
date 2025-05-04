from django.contrib import admin
from .diary.models import Class, Subject, Schedule, Grade


admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(Schedule)
admin.site.register(Grade)
