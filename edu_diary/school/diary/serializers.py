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
        return obj.start_time.strftime("%H:%M")  # Формат "8:00"

    def get_end_time(self, obj):
        return obj.end_time.strftime("%H:%M")    # Формат "8:45"

    def get_grade(self, obj):
        user = self.context['request'].user
        student = None
        date = self.context.get('date')

        if user.role == 'student':
            student = user
        elif user.role == 'parent':
            student_parent = user.parent_students.first()
            student = student_parent.student if student_parent else None

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