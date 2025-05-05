from django.db import models
from users.models import User



class AchievementCategory(models.Model):
    name = models.CharField("Название категории", max_length=100)

    class Meta:
        verbose_name = "Категория достижения"
        verbose_name_plural = "Категории достижений"

    def __str__(self):
        return self.name


class AchievementPlace(models.Model):
    name = models.CharField("Название места", max_length=50)

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"

    def __str__(self):
        return self.name




class Achievement(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name="Студент"
    )
    title = models.CharField("Название достижения", max_length=255)
    description = models.TextField("Описание", null=True, blank=True)
    date = models.DateField("Дата")
    category = models.ForeignKey(
        AchievementCategory,
        on_delete=models.CASCADE,
        verbose_name="Категория"
    )
    place = models.ForeignKey(
        AchievementPlace,
        on_delete=models.CASCADE,
        verbose_name="Место"
    )

    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"

    def __str__(self):
        return f"{self.title} — {self.student.username}"
