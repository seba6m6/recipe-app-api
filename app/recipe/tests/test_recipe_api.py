from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')

def create_sample_tag(user, title='Side Dish'):
    """Creating a sample Tag"""
    return Tag.objects.create(user=user, title=title)

def create_sample_recipe(user, **params):
    """Creating a sample Recipe"""

    defaults = {
        'title': 'Polish Soup',
        'time_minutes': 45,
        'price': 15.89
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPI(TestCase):
    """Tests publicly available Recipes"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Tests that login is required to access API"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeAPI(TestCase):
    """Test privately available API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='seba@wp.pl',
            password='correctpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_successsfully(self):
        """Tests that recipes are retrieved successfully"""
        create_sample_recipe(user=self.user)
        create_sample_recipe(user=self.user, title='Snack')

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPE_URL)

        self.assertEqual(serializer.data, res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieving_limited_to_request_user(self):
        """Tests that only recipes of request.user qre getting retrieved"""

        user2 = get_user_model().objects.create_user(
            email='waldek@wp.pl',
            password='correctpass'
        )
        recipe1 = create_sample_recipe(user=self.user)
        create_sample_recipe(user=user2)

        recipe = Recipe.objects.filter(user=self.user)

        serializer = RecipeSerializer(recipe, many=True)

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['title'], recipe1.title)
