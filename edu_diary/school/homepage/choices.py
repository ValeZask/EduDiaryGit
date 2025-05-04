from django.db import models


class ProjectStatusEnum(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Активный'
    COMPLETED = 'COMPLETED', 'Завершённый'


class TaskStatusEnum(models.TextChoices):
    NEW = 'NEW', 'Новая'
    IN_PROGRESS = 'IN_PROGRESS', 'В процессе'
    DONE = 'DONE', 'Выполнена'


class ProjectPriorityEnum(models.TextChoices):
    LOW = 'LOW', 'Низкий'
    MEDIUM = 'MEDIUM', 'Средний'
    HIGH = 'HIGH', 'Высокий'


class MemberRoleEnum(models.TextChoices):
    OWNER = 'OWNER', 'Руководитель'
    DEVELOPER = 'DEVELOPER', 'Разработчик'
    DESIGNER = 'DESIGNER', 'Дизайнер'
    ANALYST = 'ANALYST', 'Аналитик'
