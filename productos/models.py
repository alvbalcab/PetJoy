import re

from django.db import models
from django.utils.text import slugify


class Categoria(models.Model):
    """Categoría de productos"""
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='categorias/', blank=True, null=True)
    icono_clase = models.CharField(
        max_length=50,
        default='bi-grid-3x3-gap', 
        help_text="Clase CSS del icono de Bootstrap (Ej: bi-bone)"
    )
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Marca(models.Model):
    """Marca de productos"""
    nombre = models.CharField(max_length=200, unique=True)
    imagen = models.ImageField(upload_to='marcas/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Producto principal"""
    GENERO_CHOICES = [
        ('hombre', 'Hombre'),
        ('mujer', 'Mujer'),
        ('unisex', 'Unisex'),
        ('nino', 'Niño/a'),
    ]
    
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, blank=True)
    color = models.CharField(max_length=100, blank=True)
    material = models.CharField(max_length=200, blank=True)
    stock = models.IntegerField(default=0)
    esta_disponible = models.BooleanField(default=True)
    es_destacado = models.BooleanField(default=False)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_imagen_url(self):
        """
        Retorna la url de la imagen
        """
        if self.imagenes.first():
            return self.imagenes.first().imagen.url
        nombre_limpio = slugify(self.nombre)
        nombre_limpio = nombre_limpio.replace('-','_')
        ruta_generada = f'img/{nombre_limpio}.jpg'
        return ruta_generada
    
    def precio_actual(self):
        """Retorna el precio actual considerando ofertas"""
        if self.precio_oferta and self.precio_oferta < self.precio:
            return self.precio_oferta
        return self.precio
    
    def tiene_oferta(self):
        """Verifica si el producto tiene oferta activa"""
        return self.precio_oferta and self.precio_oferta < self.precio
    
    def descuento_porcentaje(self):
        """Calcula el porcentaje de descuento"""
        if self.tiene_oferta():
            descuento = ((self.precio - self.precio_oferta) / self.precio) * 100
            return round(descuento)
        return 0


class ImagenProducto(models.Model):
    """Imágenes de productos"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/') # cuando suba una foot, Django la guarda dentro de productos/
    es_principal = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Productos'
    
    def __str__(self):
        return f"Imagen de {self.producto.nombre}"
    
    def save(self, *args, **kwargs):
        # Si es la primera imagen, marcarla como principal
        if not self.pk and not self.producto.imagenes.exists():
            self.es_principal = True
        # Si se marca como principal, desmarcar las demás
        if self.es_principal:
            ImagenProducto.objects.filter(producto=self.producto, es_principal=True).exclude(pk=self.pk).update(es_principal=False)
        super().save(*args, **kwargs)


class TallaProducto(models.Model):
    """Tallas disponibles para un producto"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='tallas')
    talla = models.CharField(max_length=10)
    stock = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Talla de Producto'
        verbose_name_plural = 'Tallas de Productos'
        unique_together = ['producto', 'talla']
    
    def __str__(self):
        return f"{self.producto.nombre} - Talla {self.talla}"
