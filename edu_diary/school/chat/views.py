from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Chat, ChatMessage, ChatParticipant
from .serializers import ChatSerializer, ChatMessageSerializer
from django.utils.timezone import now
from django.db.models import Q

User = get_user_model()


class ChatListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Chat.objects.filter(chat_participants__user=self.request.user)

    def perform_create(self, serializer):
        chat = serializer.save()
        ChatParticipant.objects.create(
            chat=chat, user=self.request.user, role='admin'
        )

    @extend_schema(tags=["Чаты"], summary="Список/создание чатов",)

    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @extend_schema(tags=["Чаты"], summary="Создание чата")
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return ChatMessage.objects.filter(chat_id=chat_id)

    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        if not ChatParticipant.objects.filter(
            chat_id=chat_id,
            user=self.request.user
        ).exists():
            return Response(
                {"detail": "Вы не участник этого чата!"},
                status=status.HTTP_403_FORBIDDEN
            )

        message = serializer.save(
            sender=self.request.user,
            chat_id=chat_id
        )
        Chat.objects.filter(id=chat_id).update(last_message_at=now())

    @extend_schema(tags=["Сообщения"],summary="Получение сообщений в чате")
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    @extend_schema(tags=["Сообщения"], summary="Отправить сообщение")
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class UnreadMessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(
            chat__chat_participants__user=self.request.user,
            is_read=False
        ).exclude(sender=self.request.user)

    @extend_schema(tags=["Сообщения"], summary="Получить непрочитанные сообщения")
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)
