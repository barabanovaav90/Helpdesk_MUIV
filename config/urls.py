from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Настройка заголовков стандартной админки Django
admin.site.site_header = 'Helpdesk — Панель администратора'
admin.site.site_title = 'Helpdesk Админ'
admin.site.index_title = 'Управление системой'

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('helpdesk.urls')),
]

# Обслуживание медиафайлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
