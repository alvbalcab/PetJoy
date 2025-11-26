"""
Script para probar el carrito
Ejecutar con: python manage.py shell < test_carrito.py
"""

from django.contrib.sessions.backends.db import SessionStore
from pedidos.carrito import Carrito
from productos.models import Producto

print("🛒 Probando el carrito...")
print()

# Crear una sesión de prueba
session = SessionStore()
session.create()

class FakeRequest:
    def __init__(self, session):
        self.session = session

request = FakeRequest(session)

# Crear carrito
carrito = Carrito(request)
print(f"✅ Carrito creado")
print(f"📊 Items en carrito: {len(carrito)}")
print()

# Obtener primer producto
producto = Producto.objects.first()
if not producto:
    print("❌ No hay productos. Ejecuta primero: python personalizar_petjoy.py")
    exit()

print(f"📦 Producto de prueba: {producto.nombre}")
print(f"💰 Precio: {producto.precio}€")
print()

# Agregar producto
print("➕ Agregando producto al carrito...")
carrito.agregar(producto=producto, cantidad=2)
print(f"✅ Producto agregado")
print(f"📊 Items en carrito: {len(carrito)}")
print()

# Mostrar contenido del carrito
print("📋 Contenido del carrito:")
for item in carrito:
    print(f"  - {item['producto'].nombre}")
    print(f"    Cantidad: {item['cantidad']}")
    print(f"    Precio unitario: {item['precio']}€")
    print(f"    Total: {item['total']}€")
print()

# Totales
print("💵 Totales:")
print(f"  Subtotal: {carrito.obtener_precio_total()}€")
print(f"  Envío: {carrito.obtener_coste_envio()}€")
print(f"  IVA: {carrito.obtener_impuestos()}€")
print(f"  TOTAL: {carrito.obtener_total_final()}€")
print()

print("✅ ¡El carrito funciona correctamente!")
print()
print("🌐 Ahora prueba en el navegador:")
print("1. python manage.py runserver")
print("2. Ve a: http://127.0.0.1:8000/productos/")
print("3. Agrega un producto")
print("4. Ve al carrito: http://127.0.0.1:8000/pedidos/carrito/")
