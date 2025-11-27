"""Context processors del paquete `pedidos`.

Proveen utilidades que se inyectan en el contexto de las plantillas,
por ejemplo el carrito de sesión para mostrar el número de items en la
barra de navegación y facilitar la experiencia de compra.
"""

from .carrito import Carrito as CarritoSesion


def carrito(request):
    """Context processor para hacer el carrito disponible en todas las plantillas.

    Retorna un diccionario con la clave `carrito` que contiene una instancia
    de `Carrito` vinculada a la sesión del `request`.
    """
    return {'carrito': CarritoSesion(request)}
