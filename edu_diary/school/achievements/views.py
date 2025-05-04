from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from users.models import User
from .serializers import StudentWithAchievementsSerializer
from drf_spectacular.utils import extend_schema


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    max_page_size = 100

@extend_schema(
    summary="Список учеников с достижениями",
    description="Фильтрация по имени (search), по категории (achievements__category), с пагинацией (page).",
    responses=StudentWithAchievementsSerializer(many=True)
)
class StudentAchievementsSummaryView(ListAPIView):
    serializer_class = StudentWithAchievementsSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['full_name']
    filterset_fields = ['achievements__category']

    def get_queryset(self):
        return User.objects.filter(role="student").distinct()