from django.apps import AppConfig


class CustomAdminConfig(AppConfig):
    """Configuración de la app `custom_admin`.

    Define la app que contiene formularios y utilidades para personalizar
    la interfaz administrativa si se requiere.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_admin'
