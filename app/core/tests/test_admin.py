"""Unit Tests for Django Admin Mods"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client


class AdminSiteTests(TestCase):
    """Test Django Admin"""

    def setUp(self):
        self.client = Client()
        self.superuser = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='testpass123'
        )

        self.client.force_login(self.superuser)

        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='testpass123',
            name='Test User'
        )

    def test_listing_users(self):
        """Test that users are listed on the page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_edit_user_page(self):
        """Test the edit user page is accessible."""

        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user(self):
        """Test create user page is accessible."""

        url = reverse('admin:core_user_add')

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
