from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('acerca-de/', views.acerca_de, name='acerca_de'),
    path('contacto/', views.contacto, name='contacto'),
]
