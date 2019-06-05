from django.urls import path, include
from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.UserCreateAPI.as_view(), name='create_user')
]