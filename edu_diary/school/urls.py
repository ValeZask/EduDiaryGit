from django.urls import path, include

app_name = 'school'

urlpatterns = [
    path('diary/', include('school.diary.urls', namespace='diary')),
    path('chat/', include('school.chat.urls', namespace='chat')),
    path('homepage/', include('school.homepage.urls', namespace='homepage')),
    path('news/', include('school.news.urls', namespace='news')),
    path('achievements/', include('school.achievements.urls', namespace='achievements')),
]
