from rest_framework import serializers
from .models import Chat, ChatMessage, ChatParticipant
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'chat', 'sender', 'message_content', 'is_read', 'created_at']


class ChatParticipantSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ChatParticipant
        fields = ['id', 'user', 'chat', 'role', 'unread_count', 'last_read_message']


class ChatSerializer(serializers.ModelSerializer):
    participants = ChatParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'title', 'type', 'avatar', 'last_message_at', 'participants']