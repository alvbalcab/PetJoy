from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'telefono', 'ciudad', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'ciudad']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telefono']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('telefono', 'direccion', 'ciudad', 'codigo_postal')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('email', 'telefono', 'direccion', 'ciudad', 'codigo_postal')}),
    )
