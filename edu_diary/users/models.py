from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLES = (
        ('teacher', 'Учитель'),
        ('parent', 'Родитель'),
        ('student', 'Ученик'),
    )

    email = models.EmailField(unique=True, verbose_name='Email')
    full_name = models.CharField(max_length=255, verbose_name='Полное имя')
    role = models.CharField(max_length=10, choices=ROLES, verbose_name='Роль')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Аватар')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name', 'role']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    class_number = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Номер класса')
    class_letter = models.CharField(max_length=1, null=True, blank=True, verbose_name='Буква класса')
    phone = models.CharField(max_length=15, null=True, blank=True, verbose_name='Телефон')
    address = models.TextField(null=True, blank=True, verbose_name='Адрес')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f"Профиль {self.user.full_name}"
