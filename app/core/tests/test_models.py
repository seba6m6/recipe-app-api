from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating new user with a email is successful"""
        email = 'seba@wp.pl'
        password = '1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_mail_normalized(self):
        """Tests that the email for the new user is normalized"""
        email = "test12@WP.PL"
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_user_has_provided_email(self):
        """Tests that user has provided an email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test1234')

    def test_successfuly_created_superuser(self):
        """Tests that the superuser was created successfuly"""
        email = "seba@WP.pl"
        user = get_user_model().objects.create_superuser(email, '1234')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
