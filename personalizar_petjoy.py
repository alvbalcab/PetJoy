"""
Script para personalizar la tienda como PetJoy - Juguetes para Mascotas
Ejecutar con: python personalizar_petjoy.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_online.settings')
django.setup()

from productos.models import Categoria, Marca, Producto
from core.models import DatosEmpresa
from django.contrib.auth import get_user_model

Cliente = get_user_model()

print("🐾 Personalizando tienda para PetJoy...")
print("=" * 50)

# 1. Actualizar datos de empresa
print("\n1️⃣ Actualizando datos de empresa...")
empresa = DatosEmpresa.objects.first()
if empresa:
    empresa.nombre = 'PetJoy'
    empresa.descripcion = 'La mejor tienda de juguetes para tus mascotas. Diversión garantizada para perros y gatos.'
    empresa.email = 'info@petjoy.com'
    empresa.telefono = '+34 900 123 456'
    empresa.direccion = 'Calle de los Animales, 123'
    empresa.ciudad = 'Madrid'
    empresa.codigo_postal = '28001'
    empresa.save()
    print("✅ Datos de empresa actualizados")

# 2. Actualizar categorías
print("\n2️⃣ Actualizando categorías...")
Categoria.objects.all().delete()

categorias_petjoy = [
    {
        'nombre': 'Juguetes para Perros',
        'descripcion': 'Pelotas, cuerdas, frisbees y más para tu mejor amigo'
    },
    {
        'nombre': 'Juguetes para Gatos',
        'descripcion': 'Ratones, plumas, rascadores y juguetes interactivos'
    },
    {
        'nombre': 'Juguetes Interactivos',
        'descripcion': 'Dispensadores de premios, puzzles y juegos de inteligencia'
    },
    {
        'nombre': 'Peluches y Mordedores',
        'descripcion': 'Suaves peluches y resistentes mordedores'
    },
    {
        'nombre': 'Accesorios de Juego',
        'descripcion': 'Lanzadores, varitas y accesorios para jugar'
    },
]

for cat_data in categorias_petjoy:
    Categoria.objects.create(**cat_data)
    print(f"✅ Categoría creada: {cat_data['nombre']}")

# 3. Actualizar marcas
print("\n3️⃣ Actualizando marcas...")
Marca.objects.all().delete()

marcas_petjoy = [
    'Kong',
    'Trixie',
    'Ferplast',
    'Catit',
    'Chuckit',
    'Petstages',
    'PetJoy Original'
]

for marca_nombre in marcas_petjoy:
    Marca.objects.create(nombre=marca_nombre)
    print(f"✅ Marca creada: {marca_nombre}")

# 4. Crear productos para mascotas
print("\n4️⃣ Creando productos para mascotas...")
Producto.objects.all().delete()

categorias = {cat.nombre: cat for cat in Categoria.objects.all()}
marcas = {marca.nombre: marca for marca in Marca.objects.all()}

productos_petjoy = [
    {
        'nombre': 'Pelota Kong Classic',
        'descripcion': 'Pelota resistente de caucho natural perfecta para perros. Ideal para lanzar, rebotar y rellenar con premios.',
        'precio': 12.99,
        'categoria': categorias.get('Juguetes para Perros'),
        'marca': marcas.get('Kong'),
        'stock': 50,
        'es_destacado': True,
        'color': 'Rojo',
        'material': 'Caucho natural',
    },
    {
        'nombre': 'Ratón de Juguete con Catnip',
        'descripcion': 'Ratoncito de peluche relleno de catnip orgánico. Vuelve locos a los gatos.',
        'precio': 5.99,
        'precio_oferta': 3.99,
        'categoria': categorias.get('Juguetes para Gatos'),
        'marca': marcas.get('Trixie'),
        'stock': 100,
        'es_destacado': True,
        'color': 'Gris',
        'material': 'Peluche con catnip',
    },
    {
        'nombre': 'Cuerda Trenzada XXL',
        'descripcion': 'Cuerda resistente de algodón trenzado. Perfecta para tirar y jugar. Limpia los dientes mientras juega.',
        'precio': 14.99,
        'categoria': categorias.get('Juguetes para Perros'),
        'marca': marcas.get('PetJoy Original'),
        'stock': 35,
        'color': 'Multicolor',
        'material': 'Algodón trenzado',
    },
    {
        'nombre': 'Varita Mágica con Plumas',
        'descripcion': 'Varita extensible con plumas naturales. El juguete favorito de todos los gatos.',
        'precio': 8.99,
        'precio_oferta': 6.99,
        'categoria': categorias.get('Juguetes para Gatos'),
        'marca': marcas.get('Catit'),
        'stock': 60,
        'es_destacado': True,
        'color': 'Varios',
        'material': 'Plástico y plumas',
    },
    {
        'nombre': 'Dispensador de Premios Inteligente',
        'descripcion': 'Juguete interactivo que dispensa premios. Estimula la inteligencia de tu mascota.',
        'precio': 24.99,
        'categoria': categorias.get('Juguetes Interactivos'),
        'marca': marcas.get('Trixie'),
        'stock': 25,
        'es_destacado': True,
        'color': 'Azul',
        'material': 'Plástico resistente',
    },
    {
        'nombre': 'Frisbee Flexible',
        'descripcion': 'Frisbee suave y flexible, perfecto para parques. No daña los dientes.',
        'precio': 11.99,
        'categoria': categorias.get('Juguetes para Perros'),
        'marca': marcas.get('Chuckit'),
        'stock': 40,
        'color': 'Naranja',
        'material': 'Goma flexible',
    },
    {
        'nombre': 'Peluche con Sonido',
        'descripcion': 'Adorable peluche con sonido que encantará a tu perro. Suave y resistente.',
        'precio': 9.99,
        'categoria': categorias.get('Peluches y Mordedores'),
        'marca': marcas.get('Petstages'),
        'stock': 55,
        'color': 'Varios',
        'material': 'Peluche con squeaker',
    },
    {
        'nombre': 'Túnel de Juego para Gatos',
        'descripcion': 'Túnel plegable con bolas colgantes. Horas de diversión garantizada.',
        'precio': 19.99,
        'precio_oferta': 15.99,
        'categoria': categorias.get('Juguetes para Gatos'),
        'marca': marcas.get('Ferplast'),
        'stock': 20,
        'es_destacado': True,
        'color': 'Gris',
        'material': 'Poliéster',
    },
    {
        'nombre': 'Lanzador de Pelotas',
        'descripcion': 'Lanzador ergonómico para tirar pelotas más lejos sin esfuerzo. Incluye 2 pelotas.',
        'precio': 16.99,
        'categoria': categorias.get('Accesorios de Juego'),
        'marca': marcas.get('Chuckit'),
        'stock': 30,
        'color': 'Verde/Azul',
        'material': 'Plástico',
    },
    {
        'nombre': 'Mordedor Dental',
        'descripcion': 'Mordedor con textura especial para limpiar dientes y masajear encías.',
        'precio': 7.99,
        'categoria': categorias.get('Peluches y Mordedores'),
        'marca': marcas.get('Kong'),
        'stock': 70,
        'color': 'Azul',
        'material': 'Caucho dental',
    },
]

for prod_data in productos_petjoy:
    prod = Producto.objects.create(**prod_data)
    print(f"✅ Producto creado: {prod.nombre}")

print("\n" + "=" * 50)
print("✅ ¡Personalización completada!")
print("\n🐾 PetJoy está listo:")
print(f"   - {Categoria.objects.count()} categorías")
print(f"   - {Marca.objects.count()} marcas")
print(f"   - {Producto.objects.count()} productos")
print("\n🚀 Inicia el servidor: python manage.py runserver")
print("🌐 Visita: http://127.0.0.1:8000/")
