from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create_user')

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







