from django.urls import path
from .views import ScheduleView, GradeCreateUpdateView

app_name = 'diary'

urlpatterns = [
    path('schedule/', ScheduleView.as_view(), name='schedule'),
    path('grades/', GradeCreateUpdateView.as_view(), name='grades'),
]