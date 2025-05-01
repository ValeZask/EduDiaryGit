from rest_framework import serializers
from .models import Schedule, Grade, Subject
from django.contrib.auth import get_user_model

User = get_user_model()

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'value', 'date', 'comment']
        read_only_fields = ['id', 'date']

class ScheduleSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source='subject.name')
    grade = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['id', 'subject', 'start_time', 'end_time', 'room', 'grade']

    def get_grade(self, obj):
        user = self.context['request'].user
        student = None

        if user.role == 'student':
            student = user
        elif user.role == 'parent':
            student_parent = user.parent_students.first()
            student = student_parent.student if student_parent else None

        if student:
            grade = Grade.objects.filter(
                student=student,
                subject=obj.subject,
                date=self.context.get('date')
            ).first()
            return grade.value if grade else None
        return None
