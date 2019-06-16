from rest_framework import generics, authentication, permissions
from user.serializers import UserSerializer, AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


class UserCreateAPI(generics.CreateAPIView):
    """Creating an User base of a User serializer class"""
    serializer_class = UserSerializer


class TokenCreateAPI(ObtainAuthToken):
    """Creating a Token for authenticating when
    user makes request to the API"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserManageAPI(generics.RetrieveUpdateAPIView):
    """Retrieve an authenticated user and updating his profile"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Getting and returning an user object"""
        return self.request.user

