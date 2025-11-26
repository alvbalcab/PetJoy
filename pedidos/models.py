from django.db import models
from django.conf import settings
from productos.models import Producto
import uuid


class Carrito(models.Model):
    """Carrito de compra para clientes registrados"""
    cliente = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carrito')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
    
    def __str__(self):
        return f"Carrito de {self.cliente.username}"
    
    def total(self):
        """Calcula el total del carrito"""
        return sum(item.total for item in self.items.all())
    
    def cantidad_items(self):
        """Cuenta la cantidad total de items en el carrito"""
        return sum(item.cantidad for item in self.items.all())


class ItemCarrito(models.Model):
    """Items del carrito"""
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    talla = models.CharField(max_length=10, blank=True)
    cantidad = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = 'Item de Carrito'
        verbose_name_plural = 'Items de Carrito'
        unique_together = ['carrito', 'producto', 'talla']
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
    
    @property
    def total(self):
        """Calcula el total del item"""
        return self.cantidad * self.producto.precio_actual()


class Pedido(models.Model):
    """Pedido realizado por un cliente"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('contrareembolso', 'Contrareembolso'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
    ]
    
    numero_pedido = models.CharField(max_length=100, unique=True, editable=False)
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    
    # Datos del cliente (se guardan por si es compra sin registro)
    nombre_cliente = models.CharField(max_length=200)
    apellidos_cliente = models.CharField(max_length=200)
    email_cliente = models.EmailField()
    telefono_cliente = models.CharField(max_length=20)
    
    # Dirección de envío
    direccion_envio = models.CharField(max_length=300)
    ciudad_envio = models.CharField(max_length=100)
    codigo_postal_envio = models.CharField(max_length=10)
    
    # Información del pedido
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coste_entrega = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Método de pago
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    
    # Notas adicionales
    notas = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido {self.numero_pedido}"
    
    def save(self, *args, **kwargs):
        if not self.numero_pedido:
            # Generar número de pedido único
            self.numero_pedido = str(uuid.uuid4().hex[:12]).upper()
        super().save(*args, **kwargs)


class ItemPedido(models.Model):
    """Items de un pedido"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    nombre_producto = models.CharField(max_length=300)  # Guardar por si se elimina el producto
    talla = models.CharField(max_length=10, blank=True)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedidos'
    
    def __str__(self):
        return f"{self.cantidad} x {self.nombre_producto}"
