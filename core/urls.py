"""Rutas principales de la aplicación `core`.

Define rutas para la página de inicio, la página "acerca de" y el
formulario de contacto que usa la configuración en `DatosEmpresa`.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('acerca-de/', views.acerca_de, name='acerca_de'),
    path('contacto/', views.contacto, name='contacto'),
]
