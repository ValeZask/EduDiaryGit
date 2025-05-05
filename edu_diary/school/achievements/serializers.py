from rest_framework import serializers
from .models import Achievement


class StudentWithAchievementsSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    full_name = serializers.CharField()
    avatar = serializers.ImageField()
    class_number = serializers.IntegerField()
    achievements_count = serializers.IntegerField()
    participation_count = serializers.IntegerField()
    top_achievement = serializers.CharField()

    def to_representation(self, instance):
        achievements = Achievement.objects.filter(student=instance)
        return {
            "student_id": instance.id,
            "full_name": instance.full_name,
            "avatar": instance.avatar.url if instance.avatar else None,
            "class_number": instance.profile.class_number if hasattr(instance, 'profile') else None,
            "achievements_count": achievements.exclude(place__isnull=True).count(),
            "participation_count": achievements.count(),
            "top_achievement": achievements.order_by('place').first().title if achievements.exists() else None
        }