from django.contrib import admin
from .homepage.models import Project, ProjectMember, ProjectTask, Event, StudentEvent
from .diary.models import Class, Subject, Schedule, Grade
from .news.models import News, Category
from .achievements.models import Achievement, AchievementPlace, AchievementCategory
from .chat.models import Chat, ChatMessage, ChatParticipant

admin.site.register(StudentEvent)
admin.site.register(Project)
admin.site.register(ProjectMember)
admin.site.register(ProjectTask)
admin.site.register(Event)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(Schedule)
admin.site.register(Grade)
admin.site.register(News)
admin.site.register(Achievement)
admin.site.register(AchievementPlace)
admin.site.register(AchievementCategory)
admin.site.register(Chat)
admin.site.register(ChatMessage)
admin.site.register(ChatParticipant)
admin.site.register(Category)


