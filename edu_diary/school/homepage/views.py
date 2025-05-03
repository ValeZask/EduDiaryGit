from rest_framework import generics, permissions
from users.models import User
from .serializers import StudentSerializer

from .models import Event, Project, ProjectMember, ProjectTask, StudentEvent
from .serializers import (
    EventSerializer, ProjectSerializer, ProjectMemberSerializer,
    ProjectTaskSerializer, StudentEventSerializer
)

from drf_spectacular.utils import extend_schema

class MyChildrenListView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Список детей текущего родителя",
        description="Возвращает список всех студентов, прикреплённых к родителю",
        responses={200: StudentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.role != 'parent':
            return User.objects.none()
        return User.objects.filter(
            role='student',
            student_parents__parent=user
        ).distinct()


@extend_schema(
    summary="Список всех событий",
    responses={200: EventSerializer(many=True)}
)
class EventListAPIView(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


@extend_schema(
    summary="Список всех проектов",
    responses={200: ProjectSerializer(many=True)}
)
class ProjectListAPIView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


@extend_schema(
    summary="Список участников всех проектов",
    responses={200: ProjectMemberSerializer(many=True)}
)
class ProjectMemberListAPIView(generics.ListAPIView):
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer


@extend_schema(
    summary="Список задач всех проектов",
    responses={200: ProjectTaskSerializer(many=True)}
)
class ProjectTaskListAPIView(generics.ListAPIView):
    queryset = ProjectTask.objects.all()
    serializer_class = ProjectTaskSerializer


@extend_schema(
    summary="Список событий учеников",
    responses={200: StudentEventSerializer(many=True)}
)
class StudentEventListAPIView(generics.ListAPIView):
    queryset = StudentEvent.objects.all()
    serializer_class = StudentEventSerializer
