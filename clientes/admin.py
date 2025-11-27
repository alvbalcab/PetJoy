"""Registro y configuración del admin de Django para el modelo `Cliente`.

Contiene la clase `ClienteAdmin` que extiende `UserAdmin` para mostrar
campos adicionales (teléfono, dirección, ciudad, código postal) en la
interfaz de administración.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(UserAdmin):
    """Admin personalizado para el modelo `Cliente`.

    Añade campos adicionales en las vistas de detalle y creación para
    facilitar la gestión de información de envío y contacto del cliente.
    """
    list_display = ['username', 'email', 'first_name', 'last_name', 'telefono', 'ciudad', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'ciudad']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telefono']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('telefono', 'direccion', 'ciudad', 'codigo_postal')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('email', 'telefono', 'direccion', 'ciudad', 'codigo_postal')}),
    )
