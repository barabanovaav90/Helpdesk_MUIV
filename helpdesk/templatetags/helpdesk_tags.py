
from django import template

register = template.Library()


@register.filter(name='file_size_format')
def file_size_format(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return '0 Б'

    if value < 1024:
        return f'{value} Б'
    elif value < 1024 * 1024:
        return f'{value / 1024:.1f} КБ'
    elif value < 1024 * 1024 * 1024:
        return f'{value / (1024 * 1024):.1f} МБ'
    else:
        return f'{value / (1024 * 1024 * 1024):.1f} ГБ'


@register.filter(name='status_badge_class')
def status_badge_class(status):
    if hasattr(status, 'is_closed') and status.is_closed:
        return 'badge-closed'
    return 'badge-open'


@register.filter(name='role_display')
def role_display(role_value):
    roles = {
        'CLIENT': 'Клиент',
        'SUPPORT': 'Саппорт',
        'ADMIN': 'Администратор',
    }
    return roles.get(role_value, role_value)


@register.simple_tag
def active_link(request, url_name, *args):
    from django.urls import reverse
    try:
        url = reverse(url_name, args=args)
        if request.path == url:
            return 'active'
    except Exception:
        pass
    return ''

from django.utils.safestring import mark_safe
import markdown

@register.filter(name='markdown_format')
def markdown_format(text):
    if not text:
        return ""
    html = markdown.markdown(text, extensions=['extra', 'nl2br'])
    return mark_safe(html)
