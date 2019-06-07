from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.UserCreateAPI.as_view(), name='create_user'),
    path('token/', views.TokenCreateAPI.as_view(), name='token')
]
