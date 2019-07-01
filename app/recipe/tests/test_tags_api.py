from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Testing publicly available tags"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Tests privately available tags"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='seba@wp.pl',
            password='correctpass',
            name='Sebas'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags_list(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name="Meateater")
        Tag.objects.create(user=self.user, name="Vegan")

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_only_tags_for_authenticated_user(self):
        """Tests that only tags for authenticated user are being retrieved"""
        user2 = get_user_model().objects.create_user(
            email='user2@wp.pl',
            password='correctpass'
        )
        Tag.objects.create(user=user2,name="Foodie")
        tag = Tag.objects.create(user=self.user, name="Noodly")
        res = self.client.get(TAG_URL)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag(self):
        """Test creating a new Tag"""
        payload = {'name': 'Test Tag'}
        self.client.post(TAG_URL, payload)

        exists = Tag.objects.filter(user=self.user,
                                    name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_invalid_tag(self):
        """Test for creating a tag with invalid payload"""
        payload = {'name' : '',}
        res = self.client.post(TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_only_assigned_tags(self):
        """Test for retrieving only the tags that were assigned"""
        recipe = Recipe.objects.create(
            title="Pork in Wine",
            time_minutes=90,
            price=17.99,
            user=self.user
        )
        tag1 = Tag.object.create(
            name="Chilly",
            user=self.user
        )
        tag2 = Tag.objects.create(
            name="Hot&spicy",
            user=self.user
        )
        recipe.tags.add(tag1)
        res = self.client.get(TAG_URL, {"assigned_only": True})
        serialized_tag1 = TagSerializer(tag1)
        serialized_tag2 = TagSerializer(tag2)

        self.assertIn(serialized_tag1.data, res.data)
        self.assertNotIn(serialized_tag2.data, res.data)
        self.assertTrue(res.status_code, status.HTTP_200_OK)