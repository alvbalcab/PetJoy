from django.db import models


class DatosEmpresa(models.Model):
    """Información de la empresa/tienda"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=300)
    ciudad = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    logo = models.ImageField(upload_to='empresa/', blank=True, null=True)
    
    # Redes sociales
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    
    # Configuración de envío
    envio_gratuito_desde = models.DecimalField(max_digits=10, decimal_places=2, default=50.00, 
                                                help_text="Importe mínimo para envío gratuito")
    coste_envio_estandar = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    
    # Impuestos
    iva_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=21.00)
    
    class Meta:
        verbose_name = 'Datos de Empresa'
        verbose_name_plural = 'Datos de Empresa'
    
    def __str__(self):
        return self.nombre
    
    @classmethod
    def get_datos(cls):
        """Obtiene los datos de la empresa (singleton)"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
