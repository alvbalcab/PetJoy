from django.contrib import admin
from .models import DatosEmpresa


@admin.register(DatosEmpresa)
class DatosEmpresaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'telefono', 'ciudad']
    
    def has_add_permission(self, request):
        # Solo permitir un registro
        return not DatosEmpresa.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar
        return False
