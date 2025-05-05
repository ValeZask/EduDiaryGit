from django.conf import settings

from django.db import models
from django.contrib.auth import get_user_model
from .choices import (
    ProjectStatusEnum,
    TaskStatusEnum,
    ProjectPriorityEnum,
    MemberRoleEnum
)

User = get_user_model()


def generate_project_code():
    last = Project.objects.order_by('-id').first()
    number = last.id + 1 if last else 1
    return f"PN{number:07d}"


class Project(models.Model):
    project_code = models.CharField("Код проекта", max_length=20, unique=True, editable=False)
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания", null=True, blank=True)
    status = models.CharField(
        "Статус", max_length=20,
        choices=ProjectStatusEnum.choices,
        default=ProjectStatusEnum.ACTIVE
    )
    priority = models.CharField(
        "Приоритет", max_length=10,
        choices=ProjectPriorityEnum.choices,
        default=ProjectPriorityEnum.MEDIUM
    )
    avatar = models.ImageField("Аватар проекта", upload_to='project_avatars/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.project_code:
            self.project_code = generate_project_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project_code} — {self.title}"

    @property
    def all_tasks(self):
        return self.tasks.all()

    @property
    def active_tasks(self):
        return self.tasks.filter(status__in=[TaskStatusEnum.NEW, TaskStatusEnum.IN_PROGRESS])

    @property
    def members(self):
        return self.project_members.all()

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-start_date']


class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_members')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role_in_project = models.CharField("Роль", max_length=20, choices=MemberRoleEnum.choices)

    def __str__(self):
        return f"{self.student} — {self.get_role_in_project_display()}"

    class Meta:
        verbose_name = "Участник проекта"
        verbose_name_plural = "Участники проекта"
        unique_together = ('project', 'student')


class ProjectTask(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField("Название задачи", max_length=255)
    description = models.TextField("Описание", blank=True)
    status = models.CharField("Статус", max_length=20, choices=TaskStatusEnum.choices, default=TaskStatusEnum.NEW)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    deadline = models.DateField("Срок выполнения", null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Задача проекта"
        verbose_name_plural = "Задачи проекта"
        ordering = ['-deadline']


class Event(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    date = models.DateField(verbose_name='Дата')
    time = models.TimeField(verbose_name='Время')
    location = models.CharField(max_length=255, verbose_name='Место проведения')

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organized_events',
        limit_choices_to={'role__in': ['teacher', 'admin']},
        verbose_name='Организатор'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'

    def __str__(self):
        return f"{self.title} - {self.date}"


class StudentEvent(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_events',
        limit_choices_to={'role': 'student'},
        verbose_name='Ученик'
    )
    title = models.CharField(max_length=255, verbose_name='Название события')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    date = models.DateField(verbose_name='Дата')

    class Meta:
        verbose_name = 'Недавние события детей'
        verbose_name_plural = 'Недавние события детей'

    def __str__(self):
        return f"{self.title} ({self.student.full_name})"