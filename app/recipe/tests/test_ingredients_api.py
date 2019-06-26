from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientAPI(TestCase):
    """Publicly available Ingredients"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that we need login to access ingredient"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPI(TestCase):
    """Privately available Ingredients"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='seba@wp.pl',
            password='correctpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieving_ingredients(self):
        """Test retrieving list of ingredients"""

        Ingredient.objects.create(
            name='Carrot',
            user = self.user
        )
        Ingredient.objects.create(
            name="Leeche",
            user=self.user
        )
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_ingredients_limited_to_authorized_user(self):
        """Tests that API retrieves only ingredients of authorized user"""

        user2 = get_user_model().objects.create_user(
            email="waldi@wp.pl",
            password="correctpassword"
        )
        Ingredient.objects.create(
            user=user2,
            name='Tumeric'
        )
        ingredient = Ingredient.objects.create(
            user=self.user,
            name="Cheese"
        )
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)