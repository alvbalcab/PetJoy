from django.contrib import admin
from .models import Categoria, Marca, Producto, ImagenProducto, TallaProducto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1


class TallaProductoInline(admin.TabularInline):
    model = TallaProducto
    extra = 3


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'marca', 'precio', 'precio_oferta', 'stock', 'esta_disponible', 'es_destacado']
    list_filter = ['categoria', 'marca', 'esta_disponible', 'es_destacado', 'genero']
    search_fields = ['nombre', 'descripcion']
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ImagenProductoInline, TallaProductoInline]
    list_editable = ['precio', 'precio_oferta', 'stock', 'esta_disponible', 'es_destacado']
