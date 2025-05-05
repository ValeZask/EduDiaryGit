from django.urls import path
from .views import StudentAchievementsSummaryView

app_name = 'achievements'

urlpatterns = [
    path('summary/', StudentAchievementsSummaryView.as_view(), name='achievements-summary'),
]
