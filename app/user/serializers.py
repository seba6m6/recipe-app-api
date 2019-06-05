from django.contrib.auth import get_user_model
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ('name', 'password', 'email')
        extra_kwargs = {'password': {
            "write_only": True,
            "min_length": 5
        }}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)