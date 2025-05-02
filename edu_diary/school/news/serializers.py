from rest_framework import serializers
from .models import Category, News
from django.contrib.auth import get_user_model

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class NewsSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = News
        fields = [
            'id',
            'title',
            'content',
            'image',
            'publish_date',
            'author',
            'category',         # можно оставить, но убрать валидацию
            'category_detail'
        ]
        extra_kwargs = {
            'category': {'required': False}
        }
