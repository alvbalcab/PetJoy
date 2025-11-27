"""Configuración ASGI para `tienda_online`.

Expone la variable `application` que el servidor ASGI utilizará para
servir la aplicación Django. No modifica la lógica aportada por
`django.core.asgi.get_asgi_application()`.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_online.settings')

application = get_asgi_application()
