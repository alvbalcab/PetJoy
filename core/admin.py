"""Admin para los datos de la empresa mostrados en varias partes del sitio."""

from django.contrib import admin
from .models import DatosEmpresa


@admin.register(DatosEmpresa)
class DatosEmpresaAdmin(admin.ModelAdmin):
    """Admin para `DatosEmpresa`.

    Limita la creación a un único registro y previene su eliminación desde
    la interfaz administrativa para proteger la configuración principal.
    """
    list_display = ['nombre', 'email', 'telefono', 'ciudad']
    
    def has_add_permission(self, request):
        # Solo permitir un registro
        return not DatosEmpresa.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar
        return False
