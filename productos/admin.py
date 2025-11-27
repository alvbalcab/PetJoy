"""Configuración del panel de administración para el catálogo de productos.

Contiene admin personalizados para `Categoria`, `Marca` y `Producto`,
además de inlines para imágenes y tallas del producto.
"""

from django.contrib import admin
from .models import Categoria, Marca, Producto, ImagenProducto, TallaProducto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Admin para `Categoria`.

    Muestra campos de nombre y descripción y permite búsqueda por nombre.
    """
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    """Admin para `Marca`.

    Muestra la lista de marcas y permite búsqueda rápida.
    """
    list_display = ['nombre']
    search_fields = ['nombre']


class ImagenProductoInline(admin.TabularInline):
    """Inline para gestionar imágenes relacionadas a un `Producto`."""
    model = ImagenProducto
    extra = 1


class TallaProductoInline(admin.TabularInline):
    """Inline para gestionar tallas y stock de un `Producto`."""
    model = TallaProducto
    extra = 3


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Admin para `Producto` con configuraciones de búsqueda y ediciones."""
    list_display = ['nombre', 'categoria', 'marca', 'precio', 'precio_oferta', 'stock', 'esta_disponible', 'es_destacado']
    list_filter = ['categoria', 'marca', 'esta_disponible', 'es_destacado', 'genero']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ImagenProductoInline, TallaProductoInline]
    list_editable = ['precio', 'precio_oferta', 'stock', 'esta_disponible', 'es_destacado']
