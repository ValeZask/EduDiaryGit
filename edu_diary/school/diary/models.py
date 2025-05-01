from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Class(models.Model):
    number = models.PositiveSmallIntegerField(verbose_name='Номер класса')
    letter = models.CharField(max_length=1, verbose_name='Буква класса')
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='classes_taught',
        verbose_name='Классный руководитель',
        limit_choices_to={'role': 'teacher'}
    )
    academic_year = models.CharField(max_length=9, verbose_name='Учебный год')

    class Meta:
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'
        unique_together = ('number', 'letter', 'academic_year')

    def __str__(self):
        return f"{self.number}{self.letter} ({self.academic_year})"

class Subject(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название предмета')
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subjects_taught',
        verbose_name='Учитель',
        limit_choices_to={'role': 'teacher'}
    )
    description = models.TextField(null=True, blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

    def __str__(self):
        return self.name

class Schedule(models.Model):
    DAYS_OF_WEEK = (
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
        (7, 'Воскресенье'),
    )

    classroom = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Класс'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Предмет'
    )
    day_of_week = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK, verbose_name='День недели')
    start_time = models.TimeField(verbose_name='Время начала')
    end_time = models.TimeField(verbose_name='Время окончания')
    room = models.CharField(max_length=10, null=True, blank=True, verbose_name='Кабинет')

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'
        unique_together = ('classroom', 'day_of_week', 'start_time')

    def __str__(self):
        return f"{self.subject} ({self.classroom}) - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

class Grade(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='Ученик',
        limit_choices_to={'role': 'student'}
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name='Предмет'
    )
    value = models.PositiveSmallIntegerField(
        choices=((2, '2'), (3, '3'), (4, '4'), (5, '5')),
        verbose_name='Оценка'
    )
    date = models.DateField(verbose_name='Дата')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'
        unique_together = ('student', 'subject', 'date')

    def __str__(self):
        return f"{self.student.full_name}: {self.subject} - {self.value} ({self.date})"