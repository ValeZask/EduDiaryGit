from django.urls import path, include

urlpatterns = [
    path('diary/', include('school.diary.urls')),
    path('chat/', include('school.chat.urls')),
    path('homepage/', include('school.homepage.urls')),
    path('news/', include('school.news.urls')),
    path('achievements/', include('school.achievements.urls')),
]