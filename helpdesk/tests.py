from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Department, TicketCategory, TicketStatus, TicketPriority

class HelpdeskViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testclient',
            password='password123',
            role=User.Role.CLIENT
        )
        self.admin = User.objects.create_superuser(
            username='testadmin',
            password='password123',
            role=User.Role.ADMIN
        )

    def test_public_pages(self):
        pages = [
            'home', 'about', 'faq', 'knowledge_base', 'contacts', 
            'feedback', 'privacy_policy', 'terms', 'register', 'login'
        ]
        for page in pages:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200, f"Page {page} failed")

    def test_private_pages_redirect(self):
        pages = ['dashboard', 'ticket_list', 'ticket_create', 'profile', 'profile_edit']
        for page in pages:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 302, f"Page {page} should redirect if not logged in")

    def test_private_pages_logged_in(self):
        self.client.login(username='testclient', password='password123')
        pages = ['dashboard', 'ticket_list', 'ticket_create', 'profile', 'profile_edit']
        for page in pages:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200, f"Page {page} failed for client")

    def test_admin_pages_logged_in(self):
        self.client.login(username='testadmin', password='password123')
        pages = [
            'admin_dashboard', 'admin_user_list', 'admin_category_list', 
            'admin_reports', 'admin_feedback_list', 'admin_activity_log'
        ]
        for page in pages:
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 200, f"Admin page {page} failed for admin")
