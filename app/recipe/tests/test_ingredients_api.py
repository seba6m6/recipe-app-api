from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe
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

    def test_created_successfully(self):
        """Tests that ingredients were created successfully"""

        payload = {'name':"Cabbage"}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(name=payload['name']).exists()

        self.assertTrue(exists)

    def test_invalid_payload(self):
        """Tests that with invalid payload object is not created"""
        payload = {'name': ""}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_retrieving_assigned_ingredients(self):
        """Retrieving only the assigned ingredients"""
        recipe1 = Recipe.objects.create(
            title="Fish and chips",
            time_minutes=50,
            price=4.55,
            user=self.user
        )
        ingredient1 = Ingredient.objects.create(
            name="Fish",
            user=self.user
        )
        ingredient2 = Ingredient.objects.create(
            name="Meatball",
            user=self.user
        )
        recipe1.ingredients.add(ingredient1)

        res= self.client.get(INGREDIENT_URL, {"assigned_only": True})

        serialized_ingredient1= IngredientSerializer(ingredient1)
        serialized_ingredient2 = IngredientSerializer(ingredient2)

        self.assertIn(serialized_ingredient1.data, res.data)
        self.assertNotIn(serialized_ingredient2.data , res.data)
        self.assertTrue(res.status_code, status.HTTP_200_OK)