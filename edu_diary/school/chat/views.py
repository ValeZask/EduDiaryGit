from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Chat, ChatMessage, ChatParticipant
from .serializers import ChatSerializer, ChatMessageSerializer, ChatParticipantSerializer
from .choices import ChatParticipantRoleEnum
from users.custom_auth import CsrfExemptSessionAuthentication

@extend_schema_view(
    list=extend_schema(summary="Получить список чатов пользователя"),
    create=extend_schema(summary="Создать новый чат")
)
class ChatListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_queryset(self):
        return Chat.objects.filter(chat_participants__user=self.request.user).distinct()

@extend_schema(summary="Получить детали чата")
class ChatRetrieveView(generics.RetrieveAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]  # Добавляем

    def get_queryset(self):
        return Chat.objects.filter(chat_participants__user=self.request.user)

@extend_schema(summary="Поиск чатов по названию")
class ChatSearchView(generics.ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]  # Добавляем

    def get_queryset(self):
        search_query = self.request.query_params.get('search', '')
        return Chat.objects.filter(
            chat_participants__user=self.request.user,
            title__icontains=search_query
        ).distinct()

@extend_schema_view(
    list=extend_schema(summary="Получить сообщения чата"),
    create=extend_schema(summary="Отправить новое сообщение в чат")
)

class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id)
        if not ChatParticipant.objects.filter(chat=chat, user=self.request.user).exists():
            raise PermissionDenied("Вы не участник чата.")
        search_params = self.request.query_params.get('search')
        if search_params:
            return ChatMessage.objects.filter(chat_id=chat_id, message_content__icontains=search_params).order_by('-created_at')
        return ChatMessage.objects.filter(chat_id=chat_id).order_by('-created_at')

    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id)
        if not ChatParticipant.objects.filter(chat=chat, user=self.request.user).exists():
            raise PermissionDenied("Вы не участник чата.")
        # Передаем chat в serializer.save
        message = serializer.save(sender=self.request.user, chat=chat)
        chat.last_message_at = message.created_at
        chat.save()
        participants = ChatParticipant.objects.filter(chat=chat).exclude(user=self.request.user)
        for participant in participants:
            participant.unread_count += 1
            participant.save()

@extend_schema(summary="Получить список участников чата")
class ChatParticipantListView(generics.ListAPIView):
    serializer_class = ChatParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        chat = get_object_or_404(Chat, id=chat_id)
        if not ChatParticipant.objects.filter(chat=chat, user=self.request.user).exists():
            raise PermissionDenied("Вы не участник чата!")
        return ChatParticipant.objects.filter(chat_id=chat_id)

@extend_schema(summary="Отметить все сообщения в чате как прочитанные")
class MarkAllMessagesAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def post(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)
        participant = get_object_or_404(ChatParticipant, chat=chat, user=request.user)
        participant.mark_messages_as_read()
        return Response({"detail": "Все сообщения помечены как прочитанные."}, status=status.HTTP_200_OK)

@extend_schema(summary="Добавить нового участника в чат")
class AddChatParticipantView(generics.CreateAPIView):
    serializer_class = ChatParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_queryset(self):
        chat_id = self.kwargs.get('chat_id')
        return ChatParticipant.objects.filter(chat_id=chat_id)

    def perform_create(self, serializer):
        chat_id = self.kwargs.get('chat_id')
        chat = get_object_or_404(Chat, id=chat_id)
        users = serializer.validated_data['users']
        if not ChatParticipant.objects.filter(
                chat=chat,
                user=self.request.user,
                role=ChatParticipantRoleEnum.ADMIN
        ).exists():
            raise PermissionDenied("Только администратор чата может добавлять участников.")
        for user in users:
            if ChatParticipant.objects.filter(chat=chat, user=user).exists():
                raise ValidationError({"detail": f"Пользователь {user.username} уже в чате."})
        serializer.save(chat=chat, role=ChatParticipantRoleEnum.MEMBER)