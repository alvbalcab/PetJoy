from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuración de la app `core`.

    Contiene utilidades y modelos compartidos por el proyecto, como los
    datos de la empresa y ajustes globales.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
