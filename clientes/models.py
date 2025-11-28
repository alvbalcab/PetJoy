"""Modelos del paquete `clientes`.

Define el modelo `Cliente` que extiende `AbstractUser` y añade campos
de contacto y dirección que se usan en registros y envíos.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class Cliente(AbstractUser):
    """Modelo Cliente con campos adicionales de contacto y dirección.

    Proporciona información extra necesaria para el proceso de compra y
    para mostrarla en el perfil del usuario."""
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=300, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def __str__(self):
        """Representación legible del cliente.

        Devuelve el email si existe, en caso contrario el username.
        """
        return self.email or self.username
    
    def nombre_completo(self):
        """Retorna el nombre completo del cliente.

        Combina `first_name` y `last_name`. Si ambos están vacíos se usa el
        `username` como valor por defecto.
        """
        return f"{self.first_name} {self.last_name}".strip() or self.username
