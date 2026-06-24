from django.urls import path
from . import views

urlpatterns = [
    # ── Публичные страницы ──────────────────────────────────────────
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('faq/', views.faq_view, name='faq'),
    path('knowledge-base/', views.knowledge_base_view, name='knowledge_base'),
    path('knowledge-base/<slug:slug>/', views.kb_article_detail_view, name='kb_article_detail'),
    path('contacts/', views.contacts_view, name='contacts'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('privacy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms/', views.terms_view, name='terms'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # ── Личный кабинет ──────────────────────────────────────────────
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('tickets/', views.ticket_list_view, name='ticket_list'),
    path('tickets/create/', views.ticket_create_view, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail_view, name='ticket_detail'),
    path('comment/<int:pk>/delete/', views.delete_comment_view, name='delete_comment'),
    path('attachment/<int:pk>/delete/', views.delete_attachment_view, name='delete_attachment'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    # ── Панель администратора ───────────────────────────────────────
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_user_list_view, name='admin_user_list'),
    path('admin-panel/categories/', views.admin_category_list_view, name='admin_category_list'),
    path('admin-panel/reports/', views.admin_reports_view, name='admin_reports'),
    path('admin-panel/feedback/', views.admin_feedback_list_view, name='admin_feedback_list'),
    path('admin-panel/activity/', views.admin_activity_log_view, name='admin_activity_log'),
]
