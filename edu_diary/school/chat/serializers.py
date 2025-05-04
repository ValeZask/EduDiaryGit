from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Chat, ChatMessage, ChatParticipant

User = get_user_model()


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['__all__']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserShortSerializer(read_only=True)
    read_by = UserShortSerializer(many=True, read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'chat', 'message_content', 'created_at', 'read_by']
        read_only_fields = ['id', 'sender', 'created_at', 'read_by']


class ChatParticipantSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)

    class Meta:
        model = ChatParticipant
        fields = ['id', 'user', 'chat', 'last_read_message', 'unread_count', 'role']
        read_only_fields = ['id', 'last_read_message', 'unread_count']


class ChatSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'title', 'type', 'avatar', 'last_message_at', 'last_message', 'unread_count', 'participants']

    def get_last_message(self, obj):
        message = obj.get_last_message()
        if message:
            return ChatMessageSerializer(message).data
        return None

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.get_unread_count_for_user(user)

    def get_participants(self, obj):
        return ChatParticipantSerializer(obj.chat_participants.all(), many=True).data


