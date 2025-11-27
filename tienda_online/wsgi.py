"""Configuración WSGI para `tienda_online`.

Exponemos la variable `application` que el servidor WSGI utiliza para
iniciar la aplicación Django. Mantiene la configuración estándar generada
por `django-admin startproject`.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_online.settings')

application = get_wsgi_application()
