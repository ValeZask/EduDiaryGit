from django.db import models
from django.contrib.auth import get_user_model

from .choices import ChatParticipantRoleEnum, ChatTypeEnum

User = get_user_model()

class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Chat(TimeStamp):
    title = models.CharField(max_length=255)
    type = models.CharField(choices=ChatTypeEnum.choices, default=ChatTypeEnum.PRIVATE,max_length=8)
    avatar = models.ImageField(upload_to='chat_avatars/', blank=True, null=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"

    def __str__(self):
        return self.title


class ChatMessage(TimeStamp):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    message_content = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender}: {self.message_content[:20]}"


class ChatParticipant(TimeStamp):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_participants')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_participants')
    last_read_message = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL, null=True, blank=True)
    unread_count = models.PositiveIntegerField(default=0)
    role = models.CharField(choices=ChatParticipantRoleEnum.choices, default=ChatParticipantRoleEnum.MEMBER, max_length=7)

    class Meta:
        verbose_name = "Участник чата"
        verbose_name_plural = "Участники чата"

    def __str__(self):
        return f'{self.user} -> {self.chat}'

