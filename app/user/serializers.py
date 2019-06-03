from django.contrib.auth import get_user_model
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ('name', 'password', 'email')
        extra_kwargs = {'password': {
            "read_only": True,
            "min_length": 5
        }}