from django.apps import AppConfig


class PedidosConfig(AppConfig):
    """Configuración de la app `pedidos`.

    Contiene la configuración básica de la aplicación que gestiona los
    pedidos y carritos en el proyecto.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pedidos'
