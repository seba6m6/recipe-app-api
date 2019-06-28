import os
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')

def create_upload_image_url(recipe_id):
    """Returns a url for image upload of the recipe"""
    return reverse('recipe:recipe-image-upload', args=[recipe_id, ])

def create_detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id, ])


def create_sample_tag(user, name='Side Dish'):
    """Creating a sample Tag"""
    return Tag.objects.create(user=user, name=name)


def create_sample_ingredient(user, name='Pickle'):
    """Creating a sample Ingredient"""
    return Ingredient.objects.create(user=user, name=name)


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

    def test_viewing_recipe_detail(self):
        """Tests for viewing a recipe detail"""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        recipe.ingredients.add(create_sample_ingredient(user=self.user))

        recipe_url = create_detail_url(recipe.id)

        res = self.client.get(recipe_url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating a basic Recipe"""
        payload = {"title": "Vietnamese Cake",
                   "time_minutes": 45,
                   "price": 5.00}

        res = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_creating_recipe_with_tags(self):
        tag1 = create_sample_tag(user=self.user, name="Light")
        tag2 = create_sample_tag(user=self.user, name="Spicy")

        payload = {
            "title": "Spicy Chicken",
            "time_minutes": 45,
            "price": 6.77,
            "tags": [tag1.id, tag2.id]
        }
        res = self.client.post(RECIPE_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        self.assertEqual(tags.count(), 2)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_creating_recipe_with_ingredients(self):
        """Testing creating Recipe with Ingredients"""
        ingredient1 = create_sample_ingredient(user=self.user, name="Paprika")
        ingredient2 = create_sample_ingredient(user=self.user, name="Salad")

        payload = {
            "title": "Green Salad",
            "time_minutes": 34,
            "price": 4.66,
            "ingredients": [ingredient1.id, ingredient2.id]
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_recipe_update(self):
        """Testing an partial update with patch"""
        recipe = create_sample_recipe(user=self.user)
        recipe.tags.add(create_sample_tag(user=self.user))
        new_tag = create_sample_tag(user=self.user, name="Lourd")

        payload = {
            "title": "Russian Borsch",
            "time_minutes": 70,
            'tags': [new_tag.id, ]
        }
        recipe_url = create_detail_url(recipe.id)
        self.client.patch(recipe_url, payload)
        recipe.refresh_from_db()
        tags = recipe.tags.all()
        self.assertEqual(payload['title'], recipe.title)
        self.assertEqual(payload['time_minutes'], payload['time_minutes'])
        self.assertIn(new_tag, tags)
        self.assertEqual(len(tags), 1)

    def test_full_update(self):
        """Testing updating with put"""
        recipe = create_sample_recipe(user=self.user)
        recipe.ingredients.add(create_sample_ingredient(
            user=self.user,
            name='Fries'
        ))
        payload = {
            "title": "New Cuisine",
            "price": 5.00,
            "time_minutes": 90
        }
        recipe_url = create_detail_url(recipe.id)
        self.client.put(recipe_url, payload)
        recipe.refresh_from_db()
        ingredients = recipe.ingredients.all()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(len(ingredients), 0)


class RecipeImageAPI(TestCase):
    """Tests with the Recipe image upload"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='seba@wp.pl',
            password='correctpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_sample_recipe(
            user=self.user,
            title="Chiling salad"
        )
    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Tests uploading an image to Recipe API"""
        url = create_upload_image_url(self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            image = Image.new("RGB", (10, 10))
            image.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format="multipart")

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_invalid_image_field(self):
        """Test with uploading invalid image field"""
        url = create_upload_image_url(self.recipe.id)

        res = self.client.post(url, {"image": "not_image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
