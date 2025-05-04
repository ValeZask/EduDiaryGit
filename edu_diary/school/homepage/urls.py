from django.urls import path
from . import views
app_name = 'homepage'

urlpatterns = [
    path('parent_children/', views.MyChildrenListView.as_view()),
    path('event/', views.EventListAPIView.as_view()),
    path('project/', views.ProjectListAPIView.as_view()),
    path('project_member/', views.ProjectMemberListAPIView.as_view()),
    path('project_task/', views.ProjectTaskListAPIView.as_view()),
    path('student_event/', views.StudentEventListAPIView.as_view()),

]