from django.urls import path
from .views import createUser
from django.urls import path, include


urlpatterns= [
    path("register/", createUser, name="register"),
    
]