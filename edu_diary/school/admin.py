from django.contrib import admin
from .achievements.models import Achievement, AchievementPlace, AchievementCategory



admin.site.register(Achievement)
admin.site.register(AchievementPlace)
admin.site.register(AchievementCategory)
