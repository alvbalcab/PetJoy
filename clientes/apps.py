from django.apps import AppConfig


class ClientesConfig(AppConfig):
    """Configuración de la app `clientes`.

    Define la configuración para la aplicación que gestiona los clientes
    y la autenticación personalizada del proyecto.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clientes'
