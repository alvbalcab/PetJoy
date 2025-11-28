from django.apps import AppConfig


class ProductosConfig(AppConfig):
    """Configuración de la app `productos` para Django.

    Define la configuración por defecto y el nombre de la aplicación.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'productos'
