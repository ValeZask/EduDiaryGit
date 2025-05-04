from rest_framework import serializers
from django.contrib.auth import get_user_model

from .choices import ChatParticipantRoleEnum
from .models import Chat, ChatMessage, ChatParticipant

User = get_user_model()


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'role']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserShortSerializer(read_only=True)
    read_by = UserShortSerializer(many=True, read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'chat', 'message_content', 'created_at', 'read_by']
        read_only_fields = ['id', 'sender', 'created_at', 'read_by']


class ChatParticipantSerializer(serializers.ModelSerializer):
        users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, write_only=True,
                                                   required=True)
        update_chat_type = serializers.SerializerMethodField()

        class Meta:
            model = ChatParticipant
            fields = ['id', 'users', 'chat', 'last_read_message', 'unread_count', 'role', 'update_chat_type']
            read_only_fields = ['id', 'last_read_message', 'unread_count', 'chat', 'role', 'update_chat_type']

        def get_update_chat_type(self, obj):
            return obj.chat.change_type()

        def create(self, validated_data):
            users = validated_data.pop('users')
            chat = validated_data.get('chat')
            role = validated_data.get('role', ChatParticipantRoleEnum.MEMBER)

            # Создаем список участников для всех пользователей
            participants = []
            for user in users:
                participant = ChatParticipant.objects.create(
                    chat=chat,
                    user=user,
                    role=role
                )
                participants.append(participant)

            # Обновляем тип чата
            chat.change_type()

            # Возвращаем первого созданного участника
            # или можно логически решить, какой участник должен быть возвращен
            return participants[0] if participants else None


class ChatSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=True
    )
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['id', 'users', 'title', 'type', 'avatar', 'last_message_at', 'last_message', 'unread_count', 'participants']

    def validate_users(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо указать хотя бы одного пользователя.")
        if self.context['request'].user in value:
            raise serializers.ValidationError("Вы не можете добавить себя в чат.")
        return value

    def get_last_message(self, obj):
        last_message = obj.get_last_message()
        if last_message:
            return ChatMessageSerializer(last_message).data
        return None

    def get_unread_count(self, obj):
        return obj.get_unread_count_for_user(self.context['request'].user)

    def get_participants(self, obj):
        participants = obj.chat_participants.all()
        return ChatParticipantSerializer(participants, many=True).data

    def create(self, validated_data):
        users = validated_data.pop('users')
        chat = Chat.objects.create(**validated_data)

        ChatParticipant.objects.create(
            chat=chat,
            user=self.context['request'].user,
            role=ChatParticipantRoleEnum.ADMIN
        )
        for user in users:
            ChatParticipant.objects.create(
                chat=chat,
                user=user,
                role=ChatParticipantRoleEnum.MEMBER
            )

        return chat



