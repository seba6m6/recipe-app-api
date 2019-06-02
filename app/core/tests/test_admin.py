from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin  = get_user_model().objects.create_superuser('seb@wp.pl', '123')
        self.client.force_login(self.admin)

        self.user = get_user_model().objects.create_user(
            'test@wp.pl',
            '123',
            name='testinio'
        )

    def test_user_listed(self):
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
