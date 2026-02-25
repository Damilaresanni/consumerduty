from django.urls import path
from . import views


urlpatterns = [
    path('forms/', views.general, name='general'),
    path('documents/', views.documents, name= 'documents')
]