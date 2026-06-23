from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm

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


# Инлайн-классы

class CommentInline(admin.TabularInline):
    # Модель/форма CommentInline

    model = Comment
    extra = 0
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'text', 'is_internal', 'created_at')


class AttachmentInline(admin.TabularInline):
    # Модель/форма AttachmentInline

    model = Attachment
    extra = 0
    readonly_fields = ('uploaded_by', 'file_size', 'uploaded_at')
    fields = ('file', 'original_filename', 'uploaded_by', 'file_size', 'uploaded_at')


# Администрирование моделей

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Модель/форма UserAdmin

    form = CustomUserChangeForm

    list_display = ('username', 'last_name', 'first_name', 'role', 'department', 'is_active')
    list_filter = ('role', 'is_active', 'department')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('last_name', 'first_name')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'patronymic', 'phone', 'department', 'avatar', 'bio'),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'first_name', 'last_name', 'patronymic', 'email',
                       'phone', 'department'),
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    # Модель/форма DepartmentAdmin

    list_display = ('name', 'email', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    # Модель/форма TicketCategoryAdmin

    list_display = ('name', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TicketStatus)
class TicketStatusAdmin(admin.ModelAdmin):
    # Модель/форма TicketStatusAdmin

    list_display = ('name', 'slug', 'color', 'is_closed', 'order')
    list_filter = ('is_closed',)
    list_editable = ('order', 'color')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TicketPriority)
class TicketPriorityAdmin(admin.ModelAdmin):
    # Модель/форма TicketPriorityAdmin

    list_display = ('name', 'slug', 'color', 'level')
    list_editable = ('level', 'color')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    # Модель/форма TicketAdmin

    list_display = ('__str__', 'author', 'category', 'status', 'priority',
                    'assignee', 'created_at')
    list_filter = ('status', 'priority', 'category', 'department', 'created_at')
    search_fields = ('title', 'description', 'author__username', 'author__last_name')
    raw_id_fields = ('author', 'assignee')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'closed_at')
    inlines = [CommentInline, AttachmentInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'category', 'priority'),
        }),
        ('Назначение', {
            'fields': ('author', 'assignee', 'department', 'status'),
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'closed_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # Модель/форма CommentAdmin

    list_display = ('ticket', 'author', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('text', 'author__username')
    raw_id_fields = ('ticket', 'author')


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    # Модель/форма AttachmentAdmin

    list_display = ('original_filename', 'ticket', 'uploaded_by', 'file_size', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('original_filename',)
    raw_id_fields = ('ticket', 'comment', 'uploaded_by')


@admin.register(FAQArticle)
class FAQArticleAdmin(admin.ModelAdmin):
    # Модель/форма FAQArticleAdmin

    list_display = ('question', 'category', 'is_published', 'order', 'created_at')
    list_filter = ('is_published', 'category')
    search_fields = ('question', 'answer')
    list_editable = ('is_published', 'order')


@admin.register(KnowledgeBaseArticle)
class KnowledgeBaseArticleAdmin(admin.ModelAdmin):
    # Модель/форма KnowledgeBaseArticleAdmin

    list_display = ('title', 'category', 'author', 'is_published', 'views_count', 'created_at')
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    # Модель/форма FeedbackAdmin

    list_display = ('subject', 'name', 'email', 'is_processed', 'created_at')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('subject', 'message', 'name', 'email')
    list_editable = ('is_processed',)
    readonly_fields = ('created_at',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    # Модель/форма ActivityLogAdmin

    list_display = ('action_type', 'user', 'ticket', 'created_at')
    list_filter = ('action_type', 'created_at')
    search_fields = ('description', 'user__username')
    readonly_fields = ('user', 'ticket', 'action_type', 'description', 'created_at')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
