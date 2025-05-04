from rest_framework import serializers
from .models import Schedule, Grade, Subject
from django.contrib.auth import get_user_model

User = get_user_model()

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'value', 'date', 'comment']
        read_only_fields = ['id', 'date']

class LessonSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source='subject.name')
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['subject', 'start_time', 'end_time', 'grade']

    def get_start_time(self, obj):
        return obj.start_time.strftime("%H:%M")

    def get_end_time(self, obj):
        return obj.end_time.strftime("%H:%M")

    def get_grade(self, obj):
        user = self.context['request'].user
        date = self.context.get('date')
        student_id = self.context.get('student_id')  # Получаем student_id из контекста
        student = None

        if user.role == 'student':
            student = user
        elif user.role == 'parent':
            student_parent = user.parent_students.first()
            student = student_parent.student if student_parent else None
        elif user.role == 'teacher':
            if student_id:
                student = User.objects.filter(id=student_id, role='student').first()
            else:
                # Если student_id не указан, возвращаем None (или можно показать оценки всех учеников)
                return None

        if student and date:
            grade = Grade.objects.filter(
                student=student,
                subject=obj.subject,
                date=date
            ).first()
            return grade.value if grade else None
        return None


class ScheduleSerializer(serializers.Serializer):
    day = serializers.CharField()
    date = serializers.CharField()
    lessons = LessonSerializer(many=True)