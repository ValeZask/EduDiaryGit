from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
from django.contrib.auth import get_user_model
from .models import Schedule, Grade, Class, Subject
from .serializers import ScheduleSerializer, GradeSerializer
from users.permissions import IsTeacher
from users.custom_auth import CsrfExemptSessionAuthentication

User = get_user_model()

class ScheduleView(generics.GenericAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            profile = user.profile
            user_class = Class.objects.filter(
                number=profile.class_number,
                letter=profile.class_letter
            ).first()
            return Schedule.objects.filter(classroom=user_class)

        elif user.role == 'parent':
            student_parent = user.parent_students.first()
            if not student_parent:
                return Schedule.objects.none()
            student = student_parent.student
            profile = student.profile
            user_class = Class.objects.filter(
                number=profile.class_number,
                letter=profile.class_letter
            ).first()
            return Schedule.objects.filter(classroom=user_class)

        elif user.role == 'teacher':
            subjects = Subject.objects.filter(teacher=user)
            return Schedule.objects.filter(subject__in=subjects)

        return Schedule.objects.none()

    @extend_schema(
        tags=["Дневник"],
        summary="Получение расписания на неделю",
        description="Возвращает расписание уроков на указанную неделю, сгруппированное по дням. Доступно для учеников, родителей и учителей.",
        parameters=[
            OpenApiParameter(name='start_date', description='Начало недели (ГГГГ-ММ-ДД)', type=str, required=True),
            OpenApiParameter(name='end_date', description='Конец недели (ГГГГ-ММ-ДД)', type=str, required=True),
        ],
        responses={
            200: OpenApiResponse(description="Расписание на неделю", examples={
                "application/json": {
                    "Пн": [{"subject": "Алгебра", "start_time": "08:00:00", "end_time": "08:45:00", "grade": 4}],
                    "Вт": [{"subject": "Рус.яз", "start_time": "08:50:00", "end_time": "09:35:00", "grade": 5}],
                }
            }),
            400: OpenApiResponse(description="Некорректные даты"),
            401: OpenApiResponse(description="Неавторизован"),
        }
    )
    def get(self, request, *args, **kwargs):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not start_date_str or not end_date_str:
            return Response(
                {"detail": "Не указаны start_date или end_date"},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        if not start_date or not end_date:
            return Response(
                {"detail": "Некорректный формат даты. Используйте ГГГГ-ММ-ДД"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if start_date > end_date:
            return Response(
                {"detail": "start_date должна быть раньше end_date"},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.get_queryset().filter(
            day_of_week__range=[start_date.weekday() + 1, end_date.weekday() + 1]
        )

        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        result = {day: [] for day in days[start_date.weekday():end_date.weekday() + 1]}

        current_date = start_date
        while current_date <= end_date:
            day_name = days[current_date.weekday()]
            day_schedules = queryset.filter(day_of_week=current_date.weekday() + 1)
            serializer = self.get_serializer(
                day_schedules,
                many=True,
                context={'request': request, 'date': current_date}
            )
            result[day_name] = serializer.data
            current_date += timedelta(days=1)

        return Response(result)

class GradeCreateUpdateView(generics.GenericAPIView):
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    authentication_classes = [CsrfExemptSessionAuthentication]

    @extend_schema(
        tags=["Дневник"],
        summary="Создание/обновление оценки",
        description="Позволяет учителю выставить или обновить оценку ученику за предмет. Доступно только учителям.",
        responses={
            201: OpenApiResponse(response=GradeSerializer, description="Оценка создана"),
            200: OpenApiResponse(response=GradeSerializer, description="Оценка обновлена"),
            400: OpenApiResponse(description="Некорректные данные"),
            403: OpenApiResponse(description="Доступ запрещен"),
        }
    )
    def post(self, request, *args, **kwargs):
        student_id = request.data.get('student')
        subject_id = request.data.get('subject')
        date_str = request.data.get('date')

        if not all([student_id, subject_id, date_str]):
            return Response(
                {"detail": "Не указаны student, subject или date"},
                status=status.HTTP_400_BAD_REQUEST
            )

        date = parse_date(date_str)
        if not date:
            return Response(
                {"detail": "Некорректный формат даты. Используйте ГГГГ-ММ-ДД"},
                status=status.HTTP_400_BAD_REQUEST
            )

        student = User.objects.filter(id=student_id, role='student').first()
        subject = Subject.objects.filter(id=subject_id, teacher=request.user).first()

        if not student or not subject:
            return Response(
                {"detail": "Ученик или предмет не найдены, или вы не преподаете этот предмет"},
                status=status.HTTP_400_BAD_REQUEST
            )

        grade, created = Grade.objects.get_or_create(
            student=student,
            subject=subject,
            date=date,
            defaults={'value': request.data.get('value'), 'comment': request.data.get('comment', '')}
        )

        if not created:
            serializer = self.get_serializer(grade, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(self.get_serializer(grade).data, status=status.HTTP_201_CREATED)