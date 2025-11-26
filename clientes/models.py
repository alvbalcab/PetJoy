from django.db import models
from django.contrib.auth.models import AbstractUser


class Cliente(AbstractUser):
    """Cliente extendido del modelo User de Django"""
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=300, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=10, blank=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def __str__(self):
        return self.email or self.username
    
    def nombre_completo(self):
        """Retorna el nombre completo del cliente"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
