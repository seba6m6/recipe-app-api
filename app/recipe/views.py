from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


from core.models import Tag, Ingredient, Recipe
from recipe import serializers


class BasicRecipeAttrViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):

    """Manage objects in database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(BasicRecipeAttrViewSet):

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BasicRecipeAttrViewSet):

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage Recipe objects in the database"""

    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def _string_params_to_int(self, string_params):
        return [int(param) for param in string_params.split(',')]

    def get_queryset(self):
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tags_id = self._string_params_to_int(tags)
            queryset = queryset.filter(tags__id__in=tags_id)
        if ingredients:
            ingredients_id = self._string_params_to_int(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_id)
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):

        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        elif self.action == 'image_upload':
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a Recipe in db"""
        return serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='image-upload')
    def image_upload(self, request, pk=None):
        """Uploading an image"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )



