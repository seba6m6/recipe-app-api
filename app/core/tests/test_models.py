from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch

def create_sample_user(email="seba@wp.pl", password="correctpass"):
    """Creating a sample user for tests"""
    user = get_user_model().objects.create_user(email=email, password=password)

    return user

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

    def test_tag_str(self):
        tag = models.Tag.objects.create(
            user=create_sample_user(),
            name="Beefer"
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test that Ingredient model exists and return a name as a string"""
        ingredient = models.Ingredient.objects.create(
            name='Carrot',
            user=create_sample_user()
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Tests the string representation of Recipe"""
        recipe = models.Recipe.objects.create(
            user=create_sample_user(),
            title="Beefsteak",
            time_minutes=40,
            price=15.55
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_image_file_uuid(self, mock_uuid):
        """Check that the image is saved in the correct location"""
        test_uuid = 'unique-uuid'
        mock_uuid.return_value = test_uuid

        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/recipe/{test_uuid}.jpg'

        self.assertEqual(file_path, exp_path)

