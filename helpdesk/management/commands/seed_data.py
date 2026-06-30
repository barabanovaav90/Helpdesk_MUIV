
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from helpdesk.models import (
    ActivityLog,
    Comment,
    Department,
    FAQArticle,
    Feedback,
    KnowledgeBaseArticle,
    Ticket,
    TicketCategory,
    TicketPriority,
    TicketStatus,
    User,
)


class Command(BaseCommand):

    help = 'Заполняет базу данных тестовыми данными для Helpdesk-системы.'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Начинаем заполнение базы данных...\n')

        self._create_departments()
        self._create_categories()
        self._create_statuses()
        self._create_priorities()
        self._create_users()
        self._create_tickets()
        self._create_faq()
        self._create_kb_articles()
        self._create_feedback()

        self.stdout.write(self.style.SUCCESS('\n✅ База данных успешно заполнена тестовыми данными!'))

    def _create_departments(self):
        departments_data = [
            ('Техническая поддержка', 'Отдел технической поддержки пользователей', 'support@helpdesk.ru'),
            ('Отдел разработки', 'Разработка и сопровождение программного обеспечения', 'dev@helpdesk.ru'),
            ('Отдел продаж', 'Работа с клиентами и продажами', 'sales@helpdesk.ru'),
            ('Бухгалтерия', 'Финансовый учёт и отчётность', 'accounting@helpdesk.ru'),
            ('Отдел кадров', 'Управление персоналом', 'hr@helpdesk.ru'),
        ]
        for name, desc, email in departments_data:
            Department.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'email': email},
            )
        self.stdout.write(f'  📁 Отделы: {Department.objects.count()}')

    def _create_categories(self):
        categories_data = [
            ('Техническая проблема', 'tech-problem', 'Сбои, ошибки, неисправности в работе ПО'),
            ('Консультация', 'consultation', 'Вопросы по работе с системой'),
            ('Запрос на доступ', 'access-request', 'Предоставление или изменение прав доступа'),
            ('Запрос на изменение', 'change-request', 'Запросы на доработку или изменение функционала'),
            ('Жалоба', 'complaint', 'Жалобы на качество обслуживания'),
            ('Настройка оборудования', 'hardware-setup', 'Установка и настройка оборудования'),
            ('Безопасность', 'security', 'Вопросы информационной безопасности'),
        ]
        for name, slug, desc in categories_data:
            TicketCategory.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc},
            )
        self.stdout.write(f'  📂 Категории: {TicketCategory.objects.count()}')

    def _create_statuses(self):
        statuses_data = [
            ('Новый', 'new', '#17a2b8', False, 1),
            ('В работе', 'in-progress', '#ffc107', False, 2),
            ('Ожидает ответа клиента', 'waiting-client', '#fd7e14', False, 3),
            ('Ожидает ответа поддержки', 'waiting-support', '#6f42c1', False, 4),
            ('Решён', 'resolved', '#28a745', True, 5),
            ('Закрыт', 'closed', '#6c757d', True, 6),
        ]
        for name, slug, color, is_closed, order in statuses_data:
            TicketStatus.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'color': color,
                    'is_closed': is_closed,
                    'order': order,
                },
            )
        self.stdout.write(f'  🏷️  Статусы: {TicketStatus.objects.count()}')

    def _create_priorities(self):
        priorities_data = [
            ('Низкий', 'low', '#28a745', 1),
            ('Средний', 'medium', '#ffc107', 2),
            ('Высокий', 'high', '#fd7e14', 3),
            ('Критический', 'critical', '#dc3545', 4),
        ]
        for name, slug, color, level in priorities_data:
            TicketPriority.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'color': color, 'level': level},
            )
        self.stdout.write(f'  🔺 Приоритеты: {TicketPriority.objects.count()}')

    def _create_users(self):
        tech_dept = Department.objects.get(name='Техническая поддержка')
        dev_dept = Department.objects.get(name='Отдел разработки')

        # Администратор
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Александр',
                'last_name': 'Петров',
                'patronymic': 'Сергеевич',
                'email': 'admin@helpdesk.ru',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'department': tech_dept,
            },
        )
        if created:
            admin.set_password('admin123')
            admin.save()

        # Сотрудники поддержки
        support_data = [
            ('support1', 'Мария', 'Иванова', 'Александровна', 'support1@helpdesk.ru', tech_dept),
            ('support2', 'Дмитрий', 'Козлов', 'Владимирович', 'support2@helpdesk.ru', dev_dept),
        ]
        for uname, fname, lname, patron, email, dept in support_data:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'patronymic': patron,
                    'email': email,
                    'role': User.Role.SUPPORT,
                    'is_staff': True,
                    'department': dept,
                },
            )
            if created:
                user.set_password('support123')
                user.save()

        # Клиенты
        clients_data = [
            ('client1', 'Анна', 'Смирнова', 'Петровна', 'anna@example.ru', '+7 (999) 111-22-33'),
            ('client2', 'Игорь', 'Новиков', 'Дмитриевич', 'igor@example.ru', '+7 (999) 444-55-66'),
            ('client3', 'Елена', 'Федорова', 'Ивановна', 'elena@example.ru', '+7 (999) 777-88-99'),
        ]
        for uname, fname, lname, patron, email, phone in clients_data:
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'patronymic': patron,
                    'email': email,
                    'phone': phone,
                    'role': User.Role.CLIENT,
                },
            )
            if created:
                user.set_password('client123')
                user.save()

        self.stdout.write(f'  👥 Пользователи: {User.objects.count()}')

    def _create_tickets(self):
        if Ticket.objects.exists():
            self.stdout.write('  🎫 Тикеты уже существуют, пропускаем...')
            return

        clients = list(User.objects.filter(role=User.Role.CLIENT))
        supports = list(User.objects.filter(role__in=[User.Role.SUPPORT, User.Role.ADMIN]))
        categories = list(TicketCategory.objects.all())
        statuses = list(TicketStatus.objects.all())
        priorities = list(TicketPriority.objects.all())

        tickets_data = [
            ('Не удаётся войти в личный кабинет',
             'При попытке входа в систему отображается ошибка «Неверный пароль», '
             'хотя пароль точно правильный. Пробовал сбросить — не помогает.'),
            ('Медленная работа системы отчётов',
             'Формирование отчёта за квартал занимает более 10 минут. '
             'Раньше отчёт формировался за 30 секунд.'),
            ('Запрос на предоставление VPN-доступа',
             'Прошу предоставить VPN-доступ для удалённой работы. '
             'Необходимо подключение к серверу 192.168.1.100.'),
            ('Ошибка при загрузке документов',
             'При загрузке PDF-файлов размером более 5 МБ система выдаёт ошибку 413. '
             'Необходимо увеличить лимит загрузки.'),
            ('Настройка нового рабочего места',
             'Прошу настроить рабочее место для нового сотрудника в отделе продаж. '
             'Необходимо: ПК, монитор, доступ к CRM.'),
            ('Не работает принтер в кабинете 305',
             'Сетевой принтер HP LaserJet перестал печатать. '
             'Горит красный индикатор, на экране ошибка замятия бумаги.'),
            ('Обновление прав доступа к базе данных',
             'Необходимо расширить права на чтение таблиц финансовой отчётности '
             'для пользователя ivanov_ii.'),
            ('Жалоба на качество обслуживания',
             'Тикет #1234 не решается уже третью неделю. '
             'Прошу ускорить обработку обращения.'),
            ('Запрос на установку 1С:Бухгалтерия',
             'Прошу установить 1С:Бухгалтерия 8.3 на рабочий компьютер в бухгалтерии. '
             'Лицензия уже приобретена.'),
            ('Сбой электронной почты',
             'Не отправляются письма через корпоративную почту с 10:00. '
             'Входящие приходят, исходящие зависают в очереди.'),
        ]

        now = timezone.now()
        for i, (title, desc) in enumerate(tickets_data):
            ticket = Ticket.objects.create(
                title=title,
                description=desc,
                author=random.choice(clients),
                assignee=random.choice(supports) if i % 3 != 0 else None,
                category=random.choice(categories),
                status=random.choice(statuses),
                priority=random.choice(priorities),
            )
            # Обновляем дату для реалистичности
            Ticket.objects.filter(pk=ticket.pk).update(
                created_at=now - timedelta(days=random.randint(1, 30))
            )

            # Комментарии
            comments_texts = [
                ('Добрый день! Приняли ваше обращение в работу.', True),
                ('Спасибо за обращение! Уточните, пожалуйста, версию браузера.', False),
                ('Проблема воспроизведена на тестовом стенде. Ищем решение.', True),
            ]
            for j, (text, is_internal) in enumerate(comments_texts[:random.randint(1, 3)]):
                Comment.objects.create(
                    ticket=ticket,
                    author=random.choice(supports),
                    text=text,
                    is_internal=is_internal and j > 0,
                )

            # Запись в журнал
            ActivityLog.objects.create(
                user=ticket.author,
                ticket=ticket,
                action_type=ActivityLog.ActionType.TICKET_CREATED,
                description=f'Создан тикет «{ticket.title}».',
            )

        self.stdout.write(f'  🎫 Тикеты: {Ticket.objects.count()}')
        self.stdout.write(f'  💬 Комментарии: {Comment.objects.count()}')

    def _create_faq(self):
        if FAQArticle.objects.exists():
            self.stdout.write('  ❓ FAQ уже существуют, пропускаем...')
            return

        admin = User.objects.filter(role=User.Role.ADMIN).first()
        faq_data = [
            ('Как создать новый тикет?',
             'Для создания нового тикета перейдите в раздел «Мои тикеты» '
             'и нажмите кнопку «Новый тикет». Заполните все обязательные поля: '
             'тему, описание, категорию и приоритет. При необходимости '
             'приложите файлы.'),
            ('Как отслеживать статус обращения?',
             'Статус вашего обращения отображается в списке тикетов '
             'в личном кабинете. Вы также получите уведомление при '
             'изменении статуса.'),
            ('Какие форматы файлов поддерживаются?',
             'Система поддерживает загрузку файлов форматов: '
             'PDF, DOC, DOCX, XLS, XLSX, PNG, JPG, ZIP. '
             'Максимальный размер файла — 10 МБ.'),
            ('Как связаться с технической поддержкой?',
             'Вы можете связаться с нами через форму обратной связи, '
             'по электронной почте support@helpdesk.ru или по телефону '
             '+7 (800) 123-45-67 (пн-пт, 9:00–18:00).'),
            ('Как изменить пароль?',
             'Для изменения пароля перейдите в раздел «Профиль» → «Редактирование». '
             'Введите текущий и новый пароли. Пароль должен содержать '
             'не менее 8 символов.'),
            ('Сколько времени занимает обработка тикета?',
             'Среднее время ответа — 2 рабочих часа. Критические тикеты '
             'обрабатываются в первую очередь. Время полного решения '
             'зависит от сложности обращения.'),
        ]

        cat = TicketCategory.objects.first()
        for i, (question, answer) in enumerate(faq_data):
            FAQArticle.objects.create(
                question=question,
                answer=answer,
                category=cat,
                author=admin,
                order=i + 1,
            )

        self.stdout.write(f'  ❓ FAQ-статьи: {FAQArticle.objects.count()}')

    def _create_kb_articles(self):
        if KnowledgeBaseArticle.objects.exists():
            self.stdout.write('  📚 Статьи БЗ уже существуют, пропускаем...')
            return

        admin = User.objects.filter(role=User.Role.ADMIN).first()
        articles_data = [
            ('Руководство по началу работы с системой',
             'getting-started',
             '## Введение\n\nДобро пожаловать в систему Helpdesk! '
             'Это руководство поможет вам быстро начать работу.\n\n'
             '## Регистрация\n\n1. Перейдите на страницу регистрации.\n'
             '2. Заполните все обязательные поля.\n'
             '3. Подтвердите электронную почту.\n\n'
             '## Создание первого тикета\n\n'
             '1. Войдите в личный кабинет.\n'
             '2. Нажмите «Новый тикет».\n'
             '3. Опишите проблему как можно подробнее.'),
            ('Настройка VPN-подключения',
             'vpn-setup',
             '## Настройка VPN\n\n'
             'Для подключения к корпоративной сети удалённо '
             'необходимо настроить VPN-клиент.\n\n'
             '### Windows\n\n1. Скачайте OpenVPN клиент.\n'
             '2. Импортируйте конфигурационный файл.\n'
             '3. Введите учётные данные.\n\n'
             '### macOS\n\n1. Установите Tunnelblick.\n'
             '2. Перетащите .ovpn файл на значок программы.'),
            ('Правила безопасности при работе с системой',
             'security-rules',
             '## Правила информационной безопасности\n\n'
             '1. **Не передавайте** свои учётные данные третьим лицам.\n'
             '2. **Используйте** сложные пароли (не менее 8 символов).\n'
             '3. **Блокируйте** рабочую станцию при уходе.\n'
             '4. **Сообщайте** о подозрительных письмах в службу безопасности.\n'
             '5. **Не устанавливайте** стороннее ПО без согласования.'),
            ('Инструкция по работе с электронной почтой',
             'email-guide',
             '## Корпоративная почта\n\n'
             'Корпоративная электронная почта работает на базе Microsoft Exchange.\n\n'
             '### Настройка в Outlook\n\n'
             '1. Откройте Outlook.\n'
             '2. Перейдите в Файл → Настройка учётных записей.\n'
             '3. Введите ваш корпоративный e-mail.\n'
             '4. Outlook автоматически определит параметры сервера.'),
        ]

        cat = TicketCategory.objects.first()
        for title, slug, content in articles_data:
            KnowledgeBaseArticle.objects.create(
                title=title,
                slug=slug,
                content=content,
                category=cat,
                author=admin,
                views_count=random.randint(10, 150),
            )

        self.stdout.write(f'  📚 Статьи БЗ: {KnowledgeBaseArticle.objects.count()}')

    def _create_feedback(self):
        if Feedback.objects.exists():
            self.stdout.write('  📩 Обращения уже существуют, пропускаем...')
            return

        feedback_data = [
            ('Иван Сидоров', 'ivan@example.ru', 'Благодарность',
             'Хочу поблагодарить сотрудника Марию Иванову за оперативное '
             'решение моей проблемы. Отличная работа!'),
            ('Ольга Кузнецова', 'olga@example.ru', 'Предложение по улучшению',
             'Было бы удобно добавить возможность прикреплять скриншоты '
             'прямо из буфера обмена (Ctrl+V).'),
            ('Пётр Волков', 'petr@example.ru', 'Вопрос по тарифам',
             'Подскажите, пожалуйста, стоимость расширенной технической '
             'поддержки для организации с 50+ рабочими местами.'),
        ]

        for name, email, subject, message in feedback_data:
            Feedback.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )

        self.stdout.write(f'  📩 Обращения: {Feedback.objects.count()}')
