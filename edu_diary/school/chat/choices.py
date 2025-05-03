from django.db import models

class ChatTypeEnum(models.TextChoices):
    PRIVATE = ('private', 'Личный')
    GROUP = ('group', 'Групповой')


class ChatParticipantRoleEnum(models.TextChoices):
    ADMIN = ('admin', 'Администратор')
    MEMBER = ('member', 'Участник')