from .carrito import Carrito as CarritoSesion


def carrito(request):
    """Context processor para hacer el carrito disponible en todas las plantillas"""
    return {'carrito': CarritoSesion(request)}
