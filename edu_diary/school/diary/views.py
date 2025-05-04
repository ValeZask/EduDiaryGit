from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from datetime import datetime, timedelta
from django.utils.dateparse import parse_date
from django.contrib.auth import get_user_model
from .models import Schedule, Grade, Class, Subject
from .serializers import ScheduleSerializer, GradeSerializer, LessonSerializer  # Добавили LessonSerializer
from users.permissions import IsTeacher
from users.custom_auth import CsrfExemptSessionAuthentication

User = get_user_model()


class ScheduleView(generics.GenericAPIView):
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        print(f"User: {user}, Role: {user.role}")

        if user.role == 'student':
            profile = user.profile
            print(f"Student Profile: class_number={profile.class_number}, class_letter={profile.class_letter}")
            # Вместо поиска Class, напрямую фильтруем Schedule по данным из Profile
            if profile.class_number and profile.class_letter:
                return Schedule.objects.filter(
                    classroom__number=profile.class_number,
                    classroom__letter=profile.class_letter
                )
            return Schedule.objects.none()

        elif user.role == 'parent':
            student_parent = user.parent_students.first()
            print(f"Parent Student: {student_parent}")
            if not student_parent:
                return Schedule.objects.none()
            student = student_parent.student
            profile = student.profile
            print(f"Parent's Student Profile: class_number={profile.class_number}, class_letter={profile.class_letter}")
            if profile.class_number and profile.class_letter:
                return Schedule.objects.filter(
                    classroom__number=profile.class_number,
                    classroom__letter=profile.class_letter
                )
            return Schedule.objects.none()

        elif user.role == 'teacher':
            subjects = Subject.objects.filter(teacher=user)
            print(f"Teacher Subjects: {subjects}")
            return Schedule.objects.filter(subject__in=subjects)

        return Schedule.objects.none()

    def validate_overlapping_lessons(self, queryset, start_date, end_date):
        for schedule in queryset:
            overlapping = Schedule.objects.filter(
                classroom=schedule.classroom,
                day_of_week=schedule.day_of_week,
                start_time__lt=schedule.end_time,
                end_time__gt=schedule.start_time
            ).exclude(id=schedule.id)
            if overlapping.exists():
                raise serializers.ValidationError(
                    f"Урок {schedule.subject} пересекается с другим уроком в {schedule.get_day_of_week_display()}."
                )

    @extend_schema(
        tags=["Дневник"],
        summary="Получение расписания на неделю",
        description="Возвращает расписание уроков на указанную неделю, сгруппированное по дням с датами. Доступно для учеников, родителей и учителей.",
        parameters=[
            OpenApiParameter(name='start_date',
                             description='Начало недели (ГГГГ-ММ-ДД), если не указано — текущая неделя', type=str,
                             required=False),
            OpenApiParameter(name='direction', description='Переключение недели: next/prev', type=str, required=False),
            OpenApiParameter(name='student_id',
                             description='ID ученика (для учителей, чтобы видеть оценки конкретного ученика)', type=int,
                             required=False),
        ],
        responses={
            200: OpenApiResponse(description="Расписание на неделю"),
            400: OpenApiResponse(description="Некорректные параметры"),
            401: OpenApiResponse(description="Неавторизован"),
        }
    )
    def get(self, request, *args, **kwargs):
        start_date_str = request.query_params.get('start_date')
        direction = request.query_params.get('direction')
        student_id = request.query_params.get('student_id')

        if start_date_str:
            start_date = parse_date(start_date_str)
            if not start_date:
                return Response(
                    {"detail": "Некорректный формат даты. Используйте ГГГГ-ММ-ДД"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            start_date = datetime.today().date()
            start_date -= timedelta(days=start_date.weekday())

        if direction:
            if direction == 'next':
                start_date += timedelta(days=7)
            elif direction == 'prev':
                start_date -= timedelta(days=7)
            else:
                return Response(
                    {"detail": "Параметр direction должен быть 'next' или 'prev'"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        end_date = start_date + timedelta(days=6)

        queryset = self.get_queryset().filter(
            day_of_week__range=[start_date.weekday() + 1, end_date.weekday() + 1]
        )

        try:
            self.validate_overlapping_lessons(queryset, start_date, end_date)
        except serializers.ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        result = []

        current_date = start_date
        for i in range(7):
            day_index = current_date.weekday()
            day_name = days[day_index]
            day_schedules = queryset.filter(day_of_week=day_index + 1)
            lessons_serializer = LessonSerializer(
                day_schedules,
                many=True,
                context={'request': request, 'date': current_date, 'student_id': student_id}
            )
            result.append({
                "day": day_name,
                "date": str(current_date.day),
                "lessons": lessons_serializer.data
            })
            current_date += timedelta(days=1)

        months = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        month_year = f"{months[start_date.month - 1]} {start_date.year}"

        response = {
            "schedule": result,
            "week_info": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "next_week_start": (start_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                "prev_week_start": (start_date - timedelta(days=7)).strftime("%Y-%m-%d"),
                "month_year": month_year
            }
        }

        return Response(response)

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
        value = request.data.get('value')

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

        # Проверка, что оценка в допустимом диапазоне
        try:
            value = int(value)
            if value not in [2, 3, 4, 5]:
                return Response(
                    {"detail": "Оценка должна быть в диапазоне от 2 до 5"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError):
            return Response(
                {"detail": "Оценка должна быть числом"},
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
            defaults={'value': value, 'comment': request.data.get('comment', '')}
        )

        if not created:
            serializer = self.get_serializer(grade, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(self.get_serializer(grade).data, status=status.HTTP_201_CREATED)