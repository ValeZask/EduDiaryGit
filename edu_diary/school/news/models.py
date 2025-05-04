from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название категории')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

class News(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    content = models.TextField(
        verbose_name='Содержание'
    )
    image = models.ImageField(
        upload_to='news_images/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    publish_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='news_articles',
        verbose_name='Автор'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='news_items'
    )

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-publish_date']

    def __str__(self):
        return self.title
