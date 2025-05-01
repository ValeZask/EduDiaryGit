import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edu_diary.settings')
django.setup()

from users.models import User, Profile, StudentParent
from school.diary.models import Class, Subject, Schedule, Grade

def populate_data():
    User.objects.all().delete()
    Profile.objects.all().delete()
    StudentParent.objects.all().delete()
    Class.objects.all().delete()
    Subject.objects.all().delete()
    Schedule.objects.all().delete()
    Grade.objects.all().delete()

    teacher = User.objects.create_user(
        email='teacher@example.com',
        username='teacher',
        password='pass123',
        full_name='Teacher',
        role='teacher'
    )
    student = User.objects.create_user(
        email='student@example.com',
        username='student',
        password='pass123',
        full_name='Student',
        role='student'
    )
    parent = User.objects.create_user(
        email='parent@example.com',
        username='parent',
        password='pass123',
        full_name='Parent',
        role='parent'
    )

    Profile.objects.create(user=teacher)
    Profile.objects.create(user=student, class_number=7, class_letter='Б')
    Profile.objects.create(user=parent)

    StudentParent.objects.create(student=student, parent=parent)

    classroom = Class.objects.create(
        number=7,
        letter='Б',
        teacher=teacher,
        academic_year='2024-2025'
    )

    subject = Subject.objects.create(
        name='Алгебра',
        teacher=teacher
    )

    Schedule.objects.create(
        classroom=classroom,
        subject=subject,
        day_of_week=1,
        start_time='08:00:00',
        end_time='08:45:00',
        room='101'
    )
    Schedule.objects.create(
        classroom=classroom,
        subject=subject,
        day_of_week=2,
        start_time='08:50:00',
        end_time='09:35:00',
        room='102'
    )

    Grade.objects.create(
        student=student,
        subject=subject,
        value=4,
        date='2025-03-03',
        comment='Хорошая работа'
    )
    Grade.objects.create(
        student=student,
        subject=subject,
        value=5,
        date='2025-03-04',
        comment='Отличная работа'
    )

    print("Тестовые данные успешно добавлены!")

if __name__ == '__main__':
    populate_data()