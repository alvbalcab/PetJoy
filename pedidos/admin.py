from django.contrib import admin
from .models import Pedido, ItemPedido, Carrito, ItemCarrito


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ['nombre_producto', 'talla', 'cantidad', 'precio_unitario', 'total']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['numero_pedido', 'nombre_cliente', 'email_cliente', 'fecha_creacion', 'estado', 'total', 'metodo_pago']
    list_filter = ['estado', 'metodo_pago', 'fecha_creacion']
    search_fields = ['numero_pedido', 'nombre_cliente', 'apellidos_cliente', 'email_cliente', 'telefono_cliente']
    readonly_fields = ['numero_pedido', 'fecha_creacion', 'subtotal', 'total']
    inlines = [ItemPedidoInline]
    list_editable = ['estado']
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'cliente', 'fecha_creacion', 'estado')
        }),
        ('Datos del Cliente', {
            'fields': ('nombre_cliente', 'apellidos_cliente', 'email_cliente', 'telefono_cliente')
        }),
        ('Dirección de Envío', {
            'fields': ('direccion_envio', 'ciudad_envio', 'codigo_postal_envio')
        }),
        ('Información Financiera', {
            'fields': ('subtotal', 'impuestos', 'coste_entrega', 'descuento', 'total', 'metodo_pago')
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )


class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'cantidad_items', 'total', 'fecha_actualizacion']
    search_fields = ['cliente__username', 'cliente__email']
    inlines = [ItemCarritoInline]
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
