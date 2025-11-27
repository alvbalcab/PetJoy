"""Módulo con la clase `Carrito` que encapsula la lógica del carrito de compra.

La clase gestiona el almacenamiento en la sesión, la adición/actualización de
productos, el cálculo de totales, impuestos y costes de envío.
"""

from decimal import Decimal
from django.conf import settings
from productos.models import Producto
from core.models import DatosEmpresa


class Carrito:
    """Carrito de compra basado en sesión"""
    
    def __init__(self, request):
        """Inicializar el carrito"""
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito
    
    def agregar(self, producto, cantidad=1, talla='', actualizar_cantidad=False):
        """Agregar un producto al carrito o actualizar su cantidad"""
        producto_id = str(producto.id)
        talla_key = f"{producto_id}_{talla}" if talla else producto_id
        
        if talla_key not in self.carrito:
            self.carrito[talla_key] = {
                'producto_id': producto_id,
                'cantidad': 0,
                'precio': str(producto.precio_actual()),
                'talla': talla,
            }
        
        if actualizar_cantidad:
            self.carrito[talla_key]['cantidad'] = cantidad
        else:
            self.carrito[talla_key]['cantidad'] += cantidad
        
        self.guardar()
    
    def guardar(self):
        """Marcar la sesión como modificada"""
        self.session.modified = True
    
    def eliminar(self, producto, talla=''):
        """Eliminar un producto del carrito"""
        producto_id = str(producto.id)
        talla_key = f"{producto_id}_{talla}" if talla else producto_id
        
        if talla_key in self.carrito:
            del self.carrito[talla_key]
            self.guardar()
    
    def __iter__(self):
        """Iterar sobre los items del carrito y obtener los productos de la BD"""
        productos_ids = [item['producto_id'] for item in self.carrito.values()]
        productos = Producto.objects.filter(id__in=productos_ids)
        carrito = self.carrito.copy()
        
        for producto in productos:
            for key, item in carrito.items():
                if item['producto_id'] == str(producto.id):
                    item['producto'] = producto
                    item['precio'] = Decimal(item['precio'])
                    item['total'] = item['precio'] * item['cantidad']
                    yield item
    
    def __len__(self):
        """Contar todos los items en el carrito"""
        return sum(item['cantidad'] for item in self.carrito.values())
    
    def obtener_precio_total(self):
        """Calcular el precio total del carrito"""
        return sum(Decimal(item['precio']) * item['cantidad'] for item in self.carrito.values())
    
    def obtener_coste_envio(self):
        """Calcular el coste de envío"""
        datos_empresa = DatosEmpresa.get_datos()
        total = self.obtener_precio_total()
        
        if total >= datos_empresa.envio_gratuito_desde:
            return Decimal('0.00')
        return datos_empresa.coste_envio_estandar
    
    def obtener_impuestos(self):
        """Calcular los impuestos"""
        datos_empresa = DatosEmpresa.get_datos()
        subtotal = self.obtener_precio_total()
        return (subtotal * datos_empresa.iva_porcentaje) / Decimal('100')
    
    def obtener_total_final(self):
        """Calcular el total final incluyendo envío e impuestos"""
        subtotal = self.obtener_precio_total()
        envio = self.obtener_coste_envio()
        impuestos = self.obtener_impuestos()
        return subtotal + envio + impuestos
    
    def limpiar(self):
        """Vaciar el carrito"""
        del self.session['carrito']
        self.guardar()
