from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    AttachmentForm,
    CommentForm,
    FeedbackForm,
    LoginForm,
    ProfileEditForm,
    RegistrationForm,
    TicketForm,
    TicketStatusForm,
)
from .models import (
    ActivityLog,
    Attachment,
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
from .reports import generate_tickets_docx, generate_tickets_xlsx


# ══════════════════════════════════════════════════════════════════════
# ПУБЛИЧНЫЕ СТРАНИЦЫ (10+)
# ══════════════════════════════════════════════════════════════════════

def home_view(request):
    stats = {
        'tickets_total': Ticket.objects.count(),
        'tickets_resolved': Ticket.objects.filter(status__is_closed=True).count(),
        'faq_count': FAQArticle.objects.filter(is_published=True).count(),
        'kb_count': KnowledgeBaseArticle.objects.filter(is_published=True).count(),
    }
    recent_articles = KnowledgeBaseArticle.objects.filter(
        is_published=True
    ).order_by('-created_at')[:3]

    context = {
        'stats': stats,
        'recent_articles': recent_articles,
        'breadcrumbs': [('Главная', None)],
    }
    return render(request, 'public/home.html', context)


def about_view(request):
    context = {
        'breadcrumbs': [('Главная', '/'), ('О нас', None)],
    }
    return render(request, 'public/about.html', context)


def faq_view(request):
    articles = FAQArticle.objects.filter(is_published=True).select_related('category')
    category_slug = request.GET.get('category')

    if category_slug:
        articles = articles.filter(category__slug=category_slug)

    categories = TicketCategory.objects.filter(
        is_active=True,
        faq_articles__is_published=True,
    ).distinct()

    context = {
        'articles': articles,
        'categories': categories,
        'current_category': category_slug,
        'breadcrumbs': [('Главная', '/'), ('FAQ', None)],
    }
    return render(request, 'public/faq.html', context)


def knowledge_base_view(request):
    articles = KnowledgeBaseArticle.objects.filter(
        is_published=True
    ).select_related('category', 'author')

    query = request.GET.get('q', '')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    category_slug = request.GET.get('category')
    if category_slug:
        articles = articles.filter(category__slug=category_slug)

    categories = TicketCategory.objects.filter(
        is_active=True,
        kb_articles__is_published=True,
    ).distinct()

    context = {
        'articles': articles,
        'categories': categories,
        'query': query,
        'current_category': category_slug,
        'breadcrumbs': [('Главная', '/'), ('База знаний', None)],
    }
    return render(request, 'public/knowledge_base.html', context)


def kb_article_detail_view(request, slug):
    article = get_object_or_404(
        KnowledgeBaseArticle,
        slug=slug,
        is_published=True,
    )
    # Увеличение счётчика просмотров
    KnowledgeBaseArticle.objects.filter(pk=article.pk).update(
        views_count=article.views_count + 1
    )

    context = {
        'article': article,
        'breadcrumbs': [
            ('Главная', '/'),
            ('База знаний', '/knowledge-base/'),
            (article.title[:40], None),
        ],
    }
    return render(request, 'public/kb_article_detail.html', context)


def contacts_view(request):
    departments = Department.objects.filter(is_active=True)
    context = {
        'departments': departments,
        'breadcrumbs': [('Главная', '/'), ('Контакты', None)],
    }
    return render(request, 'public/contacts.html', context)


def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
            feedback.save()
            messages.success(request, 'Ваше обращение успешно отправлено! Мы свяжемся с вами в ближайшее время.')
            return redirect('feedback')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        form = FeedbackForm(initial=initial)

    context = {
        'form': form,
        'breadcrumbs': [('Главная', '/'), ('Обратная связь', None)],
    }
    return render(request, 'public/feedback.html', context)


def privacy_policy_view(request):
    context = {
        'breadcrumbs': [('Главная', '/'), ('Политика конфиденциальности', None)],
    }
    return render(request, 'public/privacy_policy.html', context)


def terms_view(request):
    context = {
        'breadcrumbs': [('Главная', '/'), ('Пользовательское соглашение', None)],
    }
    return render(request, 'public/terms.html', context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
            return redirect('dashboard')
    else:
        form = RegistrationForm()

    context = {
        'form': form,
        'breadcrumbs': [('Главная', '/'), ('Регистрация', None)],
    }
    return render(request, 'public/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
    else:
        form = LoginForm()

    context = {
        'form': form,
        'breadcrumbs': [('Главная', '/'), ('Вход', None)],
    }
    return render(request, 'public/login.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')


# ══════════════════════════════════════════════════════════════════════
# ЛИЧНЫЙ КАБИНЕТ (5+ страниц)
# ══════════════════════════════════════════════════════════════════════

@login_required
def dashboard_view(request):
    user = request.user

    if user.is_client:
        tickets = Ticket.objects.filter(author=user)
    else:
        tickets = Ticket.objects.filter(
            Q(author=user) | Q(assignee=user)
        )

    stats = {
        'total': tickets.count(),
        'open': tickets.filter(status__is_closed=False).count(),
        'closed': tickets.filter(status__is_closed=True).count(),
    }
    recent_tickets = tickets.select_related('status', 'priority', 'category')[:5]
    recent_activity = ActivityLog.objects.filter(
        Q(user=user) | Q(ticket__author=user)
    ).select_related('user', 'ticket')[:10]

    context = {
        'stats': stats,
        'recent_tickets': recent_tickets,
        'recent_activity': recent_activity,
        'breadcrumbs': [('Главная', '/'), ('Личный кабинет', None)],
    }
    return render(request, 'private/dashboard.html', context)


@login_required
def ticket_list_view(request):
    user = request.user

    if user.is_client:
        tickets = Ticket.objects.filter(author=user)
    elif user.is_support:
        show = request.GET.get('show', 'assigned')
        if show == 'all':
            tickets = Ticket.objects.all()
        else:
            tickets = Ticket.objects.filter(
                Q(assignee=user) | Q(assignee__isnull=True)
            )
    else:
        tickets = Ticket.objects.all()

    # Фильтрация
    status_slug = request.GET.get('status')
    if status_slug:
        tickets = tickets.filter(status__slug=status_slug)

    priority_slug = request.GET.get('priority')
    if priority_slug:
        tickets = tickets.filter(priority__slug=priority_slug)

    query = request.GET.get('q', '')
    if query:
        tickets = tickets.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    tickets = tickets.select_related('author', 'assignee', 'status', 'priority', 'category')

    context = {
        'tickets': tickets,
        'statuses': TicketStatus.objects.all(),
        'priorities': TicketPriority.objects.all(),
        'query': query,
        'current_status': status_slug,
        'current_priority': priority_slug,
        'breadcrumbs': [
            ('Главная', '/'),
            ('Личный кабинет', '/dashboard/'),
            ('Мои тикеты', None),
        ],
    }
    return render(request, 'private/ticket_list.html', context)


@login_required
def ticket_create_view(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        files = request.FILES.getlist('attachments')

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.author = request.user
            # Начальный статус — первый в порядке сортировки
            ticket.status = TicketStatus.objects.first()
            ticket.save()

            # Загрузка вложений
            for f in files:
                Attachment.objects.create(
                    ticket=ticket,
                    uploaded_by=request.user,
                    file=f,
                    original_filename=f.name,
                    file_size=f.size,
                )

            # Запись в журнал
            ActivityLog.objects.create(
                user=request.user,
                ticket=ticket,
                action_type=ActivityLog.ActionType.TICKET_CREATED,
                description=f'Создан тикет «{ticket.title}».',
            )

            messages.success(request, f'Тикет #{ticket.pk} успешно создан!')
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        form = TicketForm()

    context = {
        'form': form,
        'breadcrumbs': [
            ('Главная', '/'),
            ('Личный кабинет', '/dashboard/'),
            ('Мои тикеты', '/tickets/'),
            ('Новый тикет', None),
        ],
    }
    return render(request, 'private/ticket_create.html', context)


@login_required
def ticket_detail_view(request, pk):
    ticket = get_object_or_404(
        Ticket.objects.select_related(
            'author', 'assignee', 'category', 'status', 'priority', 'department'
        ),
        pk=pk,
    )

    # Проверка доступа: клиент видит только свои тикеты
    if request.user.is_client and ticket.author != request.user:
        messages.error(request, 'У вас нет доступа к этому тикету.')
        return redirect('ticket_list')

    comments = ticket.comments.select_related('author').order_by('created_at')
    if request.user.is_client:
        comments = comments.filter(is_internal=False)

    attachments = ticket.attachments.select_related('uploaded_by')

    # Обработка комментария
    comment_form = CommentForm()
    status_form = TicketStatusForm(initial={
        'status': ticket.status,
        'assignee': ticket.assignee,
    }) if not request.user.is_client else None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'comment':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                if not request.user.is_client:
                    comment.is_internal = request.POST.get('is_internal') == 'on'
                comment.save()

                # Загрузка вложений к комментарию
                files = request.FILES.getlist('attachments')
                for f in files:
                    Attachment.objects.create(
                        ticket=ticket,
                        comment=comment,
                        uploaded_by=request.user,
                        file=f,
                        original_filename=f.name,
                        file_size=f.size,
                    )

                ActivityLog.objects.create(
                    user=request.user,
                    ticket=ticket,
                    action_type=ActivityLog.ActionType.COMMENT_ADDED,
                    description=f'Добавлен комментарий к тикету #{ticket.pk}.',
                )
                messages.success(request, 'Комментарий добавлен.')
                return redirect('ticket_detail', pk=ticket.pk)

        elif action == 'update_status' and not request.user.is_client:
            status_form = TicketStatusForm(request.POST)
            if status_form.is_valid():
                new_status = status_form.cleaned_data['status']
                new_assignee = status_form.cleaned_data.get('assignee')

                old_status = ticket.status
                ticket.status = new_status
                if new_assignee:
                    ticket.assignee = new_assignee
                if new_status.is_closed:
                    ticket.closed_at = timezone.now()
                ticket.save()

                ActivityLog.objects.create(
                    user=request.user,
                    ticket=ticket,
                    action_type=ActivityLog.ActionType.STATUS_CHANGED,
                    description=f'Статус изменён: «{old_status}» → «{new_status}».',
                )
                messages.success(request, f'Статус тикета изменён на «{new_status}».')
                return redirect('ticket_detail', pk=ticket.pk)

    context = {
        'ticket': ticket,
        'comments': comments,
        'attachments': attachments,
        'comment_form': comment_form,
        'status_form': status_form,
        'breadcrumbs': [
            ('Главная', '/'),
            ('Личный кабинет', '/dashboard/'),
            ('Мои тикеты', '/tickets/'),
            (f'Тикет #{ticket.pk}', None),
        ],
    }
    return render(request, 'private/ticket_detail.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_comment_view(request, pk):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=pk)
        ticket_pk = comment.ticket.pk
        
        # Логируем действие
        ActivityLog.objects.create(
            user=request.user,
            ticket=comment.ticket,
            action_type=ActivityLog.ActionType.OTHER,
            description=f'Удалён комментарий пользователя {comment.author} к тикету #{ticket_pk}.',
        )
        
        # Физически удаляем файлы вложений, привязанных к комментарию
        for attachment in comment.attachments.all():
            if attachment.file:
                attachment.file.delete(save=False)
                
        comment.delete()
        messages.success(request, 'Комментарий и его вложения успешно удалены.')
        return redirect('ticket_detail', pk=ticket_pk)
    return redirect('home')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_attachment_view(request, pk):
    if request.method == 'POST':
        attachment = get_object_or_404(Attachment, pk=pk)
        ticket_pk = attachment.ticket.pk
        
        # Логируем действие
        ActivityLog.objects.create(
            user=request.user,
            ticket=attachment.ticket,
            action_type=ActivityLog.ActionType.OTHER,
            description=f'Удалено вложение «{attachment.original_filename}» из тикета #{ticket_pk}.',
        )
        
        # Физически удаляем файл
        if attachment.file:
            attachment.file.delete(save=False)
        attachment.delete()
        
        messages.success(request, 'Вложение успешно удалено.')
        return redirect('ticket_detail', pk=ticket_pk)
    return redirect('home')
@login_required
def profile_view(request):
    user = request.user
    tickets_count = Ticket.objects.filter(author=user).count()
    comments_count = Comment.objects.filter(author=user).count()

    context = {
        'profile_user': user,
        'tickets_count': tickets_count,
        'comments_count': comments_count,
        'breadcrumbs': [
            ('Главная', '/'),
            ('Личный кабинет', '/dashboard/'),
            ('Профиль', None),
        ],
    }
    return render(request, 'private/profile.html', context)


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)

    context = {
        'form': form,
        'breadcrumbs': [
            ('Главная', '/'),
            ('Личный кабинет', '/dashboard/'),
            ('Профиль', '/profile/'),
            ('Редактирование', None),
        ],
    }
    return render(request, 'private/profile_edit.html', context)


# ══════════════════════════════════════════════════════════════════════
# ПАНЕЛЬ АДМИНИСТРАТОРА (5+ страниц)
# ══════════════════════════════════════════════════════════════════════

def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.is_client:
            messages.error(request, 'У вас нет доступа к этому разделу.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    wrapper.__doc__ = view_func.__doc__
    return wrapper


@staff_required
def admin_dashboard_view(request):
    tickets = Ticket.objects.all()

    stats = {
        'total_tickets': tickets.count(),
        'open_tickets': tickets.filter(status__is_closed=False).count(),
        'closed_tickets': tickets.filter(status__is_closed=True).count(),
        'unassigned': tickets.filter(assignee__isnull=True, status__is_closed=False).count(),
        'total_users': User.objects.count(),
        'total_feedback': Feedback.objects.filter(is_processed=False).count(),
    }

    tickets_by_status = TicketStatus.objects.annotate(
        ticket_count=Count('tickets')
    )
    tickets_by_priority = TicketPriority.objects.annotate(
        ticket_count=Count('tickets')
    )
    recent_activity = ActivityLog.objects.select_related('user', 'ticket')[:15]

    context = {
        'stats': stats,
        'tickets_by_status': tickets_by_status,
        'tickets_by_priority': tickets_by_priority,
        'recent_activity': recent_activity,
        'breadcrumbs': [
            ('Главная', '/'),
            ('Панель управления', None),
        ],
    }
    return render(request, 'admin_panel/dashboard.html', context)


@staff_required
def admin_user_list_view(request):
    users = User.objects.all().select_related('department')

    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)

    query = request.GET.get('q', '')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'users': users,
        'query': query,
        'role_filter': role_filter,
        'roles': User.Role.choices,
        'breadcrumbs': [
            ('Главная', '/'),
            ('Панель управления', '/admin-panel/'),
            ('Пользователи', None),
        ],
    }
    return render(request, 'admin_panel/user_list.html', context)


@staff_required
def admin_category_list_view(request):
    context = {
        'categories': TicketCategory.objects.all(),
        'statuses': TicketStatus.objects.all(),
        'priorities': TicketPriority.objects.all(),
        'departments': Department.objects.all(),
        'breadcrumbs': [
            ('Главная', '/'),
            ('Панель управления', '/admin-panel/'),
            ('Справочники', None),
        ],
    }
    return render(request, 'admin_panel/category_list.html', context)


@staff_required
def admin_reports_view(request):
    if request.method == 'POST':
        report_format = request.POST.get('format', 'xlsx')
        tickets = Ticket.objects.select_related(
            'author', 'assignee', 'category', 'status', 'priority'
        ).order_by('-created_at')

        # Фильтры отчёта
        status_id = request.POST.get('status')
        if status_id:
            tickets = tickets.filter(status_id=status_id)

        priority_id = request.POST.get('priority')
        if priority_id:
            tickets = tickets.filter(priority_id=priority_id)

        now = timezone.now().strftime('%d-%m-%Y')

        if report_format == 'docx':
            buffer = generate_tickets_docx(tickets)
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            )
            response['Content-Disposition'] = f'attachment; filename="report_tickets_{now}.docx"'
        else:
            buffer = generate_tickets_xlsx(tickets)
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            )
            response['Content-Disposition'] = f'attachment; filename="report_tickets_{now}.xlsx"'

        return response

    context = {
        'statuses': TicketStatus.objects.all(),
        'priorities': TicketPriority.objects.all(),
        'breadcrumbs': [
            ('Главная', '/'),
            ('Панель управления', '/admin-panel/'),
            ('Отчёты', None),
        ],
    }
    return render(request, 'admin_panel/reports.html', context)


@staff_required
def admin_feedback_list_view(request):
    feedbacks = Feedback.objects.all().select_related('user')

    show = request.GET.get('show', 'new')
    if show == 'new':
        feedbacks = feedbacks.filter(is_processed=False)

    context = {
        'feedbacks': feedbacks,
        'show': show,
        'breadcrumbs': [
            ('Главная', '/'),
            ('Панель управления', '/admin-panel/'),
            ('Обращения', None),
        ],
    }
    return render(request, 'admin_panel/feedback_list.html', context)


@staff_required
def admin_activity_log_view(request):
    logs = ActivityLog.objects.select_related('user', 'ticket').order_by('-created_at')[:100]

    context = {
        'logs': logs,
        'breadcrumbs': [
            ('Главная', '/'),
            ('Панель управления', '/admin-panel/'),
            ('Журнал действий', None),
        ],
    }
    return render(request, 'admin_panel/activity_log.html', context)
