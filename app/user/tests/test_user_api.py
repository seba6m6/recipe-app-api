from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create_user')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**kwargs):
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTest(TestCase):
    """Test for creating an public user"""

    def setUp(self):
        self.client = APIClient()

    def test_user_created_successfuly(self):
        payload = {"email": "batianm@outlook.com",
                   "name": "Basti",
                   "password": "seba123"}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn("password", res.data)

    def test_user_already_exists(self):
        payload = {"email": "batianm@outlook.com",
                   "name": "Basti",
                   "password": "seba123"}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(
            res.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_password_is_too_short(self):
        payload = {"email": "batianm@outlook.com",
                   "name": "Basti",
                   "password": "se"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(
            res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload["email"]
            ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {"email": "batianm@outlook.com",
                   "name": "Basti",
                   "password": "seba6m6"}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if the invalid
        credentials are given"""
        create_user(email='test@wp.pl', password="testpass")
        payload = {'email': 'test@wp.pl', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exist"""
        payload = {'email': 'test@wp.pl', 'password': 'testpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test that token is not created if the
        required fields are missing"""
        res = self.client.post(TOKEN_URL, {'email': 'test@wp.pl',
                                           'password': ''
                                           })
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITest(TestCase):
    """Test API request that require authentication"""

    def setUp(self):
        self.user = create_user(
            email="seba@wp.pl",
            password="haslopass",
            name="Sebastian"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_successfully(self):
        """Test retrieving a logged in user  """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_no_post_allowed(self):
        """Test that post method is not allowed"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_updating_authorized_user(self):
        payload = {
            'name': 'NewSebastian',
            'password': 'newhaslopass'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
