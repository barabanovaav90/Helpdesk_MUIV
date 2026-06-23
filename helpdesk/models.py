from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone



class Department(models.Model):
    # Модель/форма Department

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Название отдела',
        help_text='Полное название отдела или подразделения.',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Описание',
        help_text='Краткое описание задач и зоны ответственности отдела.',
    )
    email = models.EmailField(
        blank=True,
        default='',
        verbose_name='Контактный e-mail',
        help_text='Общий почтовый адрес отдела.',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен',
        help_text='Снимите флаг, чтобы скрыть отдел из выбора.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    class Meta:
        verbose_name = 'Отдел'
        verbose_name_plural = 'Отделы'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name



class User(AbstractUser):
    # Модель/форма User

    class Role(models.TextChoices):
    # Модель/форма Role
        CLIENT = 'CLIENT', 'Клиент'
        SUPPORT = 'SUPPORT', 'Саппорт'
        ADMIN = 'ADMIN', 'Администратор'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT,
        verbose_name='Роль',
        help_text='Роль определяет уровень доступа пользователя в системе.',
    )
    patronymic = models.CharField(
        max_length=150,
        blank=True,
        default='',
        verbose_name='Отчество',
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Телефон',
        help_text='Контактный номер телефона.',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name='Отдел',
        help_text='Отдел, к которому прикреплён сотрудник.',
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Аватар',
        help_text='Фотография профиля пользователя.',
    )
    bio = models.TextField(
        blank=True,
        default='',
        verbose_name='О себе',
        help_text='Краткая информация о пользователе.',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']

    def __str__(self) -> str:
        full_name = f'{self.last_name} {self.first_name} {self.patronymic}'.strip()
        return full_name if full_name else self.username

    @property
    def short_name(self) -> str:
        parts = [self.last_name]
        if self.first_name:
            parts.append(f'{self.first_name[0]}.')
        if self.patronymic:
            parts.append(f'{self.patronymic[0]}.')
        return ' '.join(parts).strip() or self.username

    @property
    def is_client(self) -> bool:
        return self.role == self.Role.CLIENT

    @property
    def is_support(self) -> bool:
        return self.role == self.Role.SUPPORT

    @property
    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN



class TicketCategory(models.Model):
    # Модель/форма TicketCategory

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Название категории',
    )
    slug = models.SlugField(
        max_length=150,
        unique=True,
        verbose_name='URL-псевдоним',
        help_text='Латинский идентификатор для URL (заполняется автоматически).',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Описание',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна',
    )

    class Meta:
        verbose_name = 'Категория тикета'
        verbose_name_plural = 'Категории тикетов'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name



class TicketStatus(models.Model):
    # Модель/форма TicketStatus

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название статуса',
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='URL-псевдоним',
    )
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name='Цвет (HEX)',
        help_text='Цвет для отображения статуса в интерфейсе, например #28a745.',
    )
    is_closed = models.BooleanField(
        default=False,
        verbose_name='Является закрывающим',
        help_text='Отметьте, если данный статус означает завершение работы над тикетом.',
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Порядок сортировки',
    )

    class Meta:
        verbose_name = 'Статус тикета'
        verbose_name_plural = 'Статусы тикетов'
        ordering = ['order', 'name']

    def __str__(self) -> str:
        return self.name



class TicketPriority(models.Model):
    # Модель/форма TicketPriority

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название приоритета',
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='URL-псевдоним',
    )
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name='Цвет (HEX)',
        help_text='Цвет для визуального выделения приоритета.',
    )
    level = models.PositiveSmallIntegerField(
        default=0,
        unique=True,
        verbose_name='Числовой уровень',
        help_text='Чем выше число, тем выше приоритет.',
    )

    class Meta:
        verbose_name = 'Приоритет тикета'
        verbose_name_plural = 'Приоритеты тикетов'
        ordering = ['level']

    def __str__(self) -> str:
        return self.name



class Ticket(models.Model):
    # Модель/форма Ticket

    title = models.CharField(
        max_length=300,
        verbose_name='Тема обращения',
        help_text='Кратко опишите суть проблемы или вопроса.',
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Подробное описание обращения.',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tickets',
        verbose_name='Автор',
        help_text='Пользователь, создавший тикет.',
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name='Исполнитель',
        help_text='Сотрудник поддержки, назначенный на обработку тикета.',
    )
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='Категория',
    )
    status = models.ForeignKey(
        TicketStatus,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='Статус',
    )
    priority = models.ForeignKey(
        TicketPriority,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='Приоритет',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name='Отдел-исполнитель',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата закрытия',
    )

    class Meta:
        verbose_name = 'Тикет'
        verbose_name_plural = 'Тикеты'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'#{self.pk} — {self.title}'

    def close(self) -> None:
        self.closed_at = timezone.now()
        self.save(update_fields=['closed_at', 'updated_at'])

    @property
    def is_closed(self) -> bool:
        return self.status.is_closed



class Comment(models.Model):
    # Модель/форма Comment

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Тикет',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    is_internal = models.BooleanField(
        default=False,
        verbose_name='Внутренний комментарий',
        help_text='Внутренние комментарии видны только сотрудникам поддержки.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

    def __str__(self) -> str:
        preview = self.text[:50] + '…' if len(self.text) > 50 else self.text
        return f'Комментарий от {self.author} к тикету #{self.ticket_id}: {preview}'



class Attachment(models.Model):
    # Модель/форма Attachment

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Тикет',
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attachments',
        verbose_name='Комментарий',
        help_text='Если файл приложен к конкретному комментарию.',
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Загрузил',
    )
    file = models.FileField(
        upload_to='attachments/%Y/%m/%d/',
        verbose_name='Файл',
    )
    original_filename = models.CharField(
        max_length=255,
        verbose_name='Имя файла',
        help_text='Исходное имя файла при загрузке.',
    )
    file_size = models.PositiveIntegerField(
        default=0,
        verbose_name='Размер (байт)',
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки',
    )

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'
        ordering = ['-uploaded_at']

    def __str__(self) -> str:
        return f'{self.original_filename} (тикет #{self.ticket_id})'



class FAQArticle(models.Model):
    # Модель/форма FAQArticle

    question = models.CharField(
        max_length=500,
        verbose_name='Вопрос',
    )
    answer = models.TextField(
        verbose_name='Ответ',
    )
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faq_articles',
        verbose_name='Категория',
        help_text='Категория, к которой относится вопрос.',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faq_articles',
        verbose_name='Автор',
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликована',
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Порядок сортировки',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    class Meta:
        verbose_name = 'Статья FAQ'
        verbose_name_plural = 'Статьи FAQ'
        ordering = ['order', '-created_at']

    def __str__(self) -> str:
        return self.question[:80]



class KnowledgeBaseArticle(models.Model):
    # Модель/форма KnowledgeBaseArticle

    title = models.CharField(
        max_length=300,
        verbose_name='Заголовок',
    )
    slug = models.SlugField(
        max_length=300,
        unique=True,
        verbose_name='URL-псевдоним',
    )
    content = models.TextField(
        verbose_name='Содержание',
        help_text='Полный текст статьи. Поддерживается форматирование Markdown.',
    )
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kb_articles',
        verbose_name='Основная категория',
    )
    tags = models.ManyToManyField(
        TicketCategory,
        blank=True,
        related_name='tagged_kb_articles',
        verbose_name='Теги (категории)',
        help_text='Дополнительные категории для перекрёстной навигации.',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='kb_articles',
        verbose_name='Автор',
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликована',
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество просмотров',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления',
    )

    class Meta:
        verbose_name = 'Статья базы знаний'
        verbose_name_plural = 'Статьи базы знаний'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.title



class Feedback(models.Model):
    # Модель/форма Feedback

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks',
        verbose_name='Пользователь',
        help_text='Заполняется автоматически для авторизованных пользователей.',
    )
    name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Имя отправителя (для неавторизованных).',
    )
    email = models.EmailField(
        verbose_name='E-mail',
        help_text='Адрес для обратной связи.',
    )
    subject = models.CharField(
        max_length=300,
        verbose_name='Тема',
    )
    message = models.TextField(
        verbose_name='Сообщение',
    )
    is_processed = models.BooleanField(
        default=False,
        verbose_name='Обработано',
        help_text='Отметьте, когда обращение будет рассмотрено.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата отправки',
    )

    class Meta:
        verbose_name = 'Обращение (обратная связь)'
        verbose_name_plural = 'Обращения (обратная связь)'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.subject} — {self.name}'



class ActivityLog(models.Model):
    # Модель/форма ActivityLog

    class ActionType(models.TextChoices):
    # Модель/форма ActionType
        TICKET_CREATED = 'TICKET_CREATED', 'Тикет создан'
        TICKET_UPDATED = 'TICKET_UPDATED', 'Тикет обновлён'
        TICKET_CLOSED = 'TICKET_CLOSED', 'Тикет закрыт'
        STATUS_CHANGED = 'STATUS_CHANGED', 'Статус изменён'
        ASSIGNEE_CHANGED = 'ASSIGNEE_CHANGED', 'Исполнитель назначен'
        COMMENT_ADDED = 'COMMENT_ADDED', 'Комментарий добавлен'
        FILE_UPLOADED = 'FILE_UPLOADED', 'Файл загружен'
        OTHER = 'OTHER', 'Другое'

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name='Пользователь',
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name='Тикет',
    )
    action_type = models.CharField(
        max_length=20,
        choices=ActionType.choices,
        default=ActionType.OTHER,
        verbose_name='Тип действия',
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Описание',
        help_text='Подробное описание выполненного действия.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время',
    )

    class Meta:
        verbose_name = 'Запись журнала'
        verbose_name_plural = 'Журнал действий'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'[{self.get_action_type_display()}] {self.user} — {self.created_at:%d.%m.%Y %H:%M}'
