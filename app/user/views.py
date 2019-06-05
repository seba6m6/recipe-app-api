from rest_framework import generics
from user.serializers import UserSerializer

class UserCreateAPI(generics.CreateAPIView):
    """Creating an User base of a User serializer class"""
    serializer_class = UserSerializer
