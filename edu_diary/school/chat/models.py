from django.db import models
from django.contrib.auth import get_user_model
from .choices import ChatTypeEnum, ChatParticipantRoleEnum

User = get_user_model()


class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Chat(TimeStamp):
    title = models.CharField(max_length=255)
    type = models.CharField(choices=ChatTypeEnum.choices, default=ChatTypeEnum.PRIVATE, max_length=8)
    avatar = models.ImageField(upload_to='media/chat_avatars/', blank=True, null=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"

    def __str__(self):
        return self.title

    def get_last_message(self):
        return self.messages.order_by('-created_at').first()

    def get_unread_count_for_user(self, user):
        participant = self.chat_participants.filter(user=user).first()
        if not participant:
            return 0
        return participant.unread_count


class ChatMessage(TimeStamp):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    message_content = models.TextField()
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender}: {self.message_content[:20]}"

    def mark_as_read_by(self, user):
        self.read_by.add(user)
        self.save()


class ChatParticipant(TimeStamp):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_participants')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_participants')
    last_read_message = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='last_read_by')
    unread_count = models.PositiveIntegerField(default=0)
    role = models.CharField(choices=ChatParticipantRoleEnum.choices, default=ChatParticipantRoleEnum.MEMBER,
                            max_length=7)

    class Meta:
        verbose_name = "Участник чата"
        verbose_name_plural = "Участники чата"
        unique_together = ['user', 'chat']

    def __str__(self):
        return f'{self.user} -> {self.chat}'

    def mark_messages_as_read(self):
        unread_messages = self.chat.messages.exclude(read_by=self.user).order_by('-created_at')

        if unread_messages.exists():
            self.last_read_message = unread_messages.first()

            for message in unread_messages:
                message.read_by.add(self.user)

            self.unread_count = 0
            self.save()

