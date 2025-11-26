# Ejemplos y Mejores Prácticas de Testing

## 📚 Contenido

1. [Ejemplos de Tests Unitarios](#ejemplos-de-tests-unitarios)
2. [Ejemplos de Tests de Integración](#ejemplos-de-tests-de-integración)
3. [Uso de Fixtures y Factories](#uso-de-fixtures-y-factories)
4. [Mocking y Patching](#mocking-y-patching)
5. [Testing de APIs](#testing-de-apis)
6. [Patrones Comunes](#patrones-comunes)

---

## 1. Ejemplos de Tests Unitarios

### Test de Modelo Simple

```python
from django.test import TestCase
from productos.models import Categoria

class CategoriaModelTest(TestCase):
    def test_crear_categoria(self):
        """Test: Crear una categoría"""
        categoria = Categoria.objects.create(
            nombre="Juguetes",
            descripcion="Juguetes para mascotas"
        )
        
        self.assertEqual(categoria.nombre, "Juguetes")
        self.assertIsNotNone(categoria.id)
```

### Test de Modelo con Relaciones

```python
from django.test import TestCase
from productos.models import Producto, Categoria, Marca

class ProductoRelacionesTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Juguetes")
        self.marca = Marca.objects.create(nombre="Kong")
    
    def test_producto_con_categoria_y_marca(self):
        """Test: Producto con relaciones"""
        producto = Producto.objects.create(
            nombre="Pelota Kong",
            precio=19.99,
            categoria=self.categoria,
            marca=self.marca
        )
        
        self.assertEqual(producto.categoria, self.categoria)
        self.assertEqual(producto.marca, self.marca)
        self.assertIn(producto, self.categoria.productos.all())
```

### Test de Métodos del Modelo

```python
from decimal import Decimal
from django.test import TestCase
from productos.models import Producto

class ProductoMetodosTest(TestCase):
    def test_precio_con_descuento(self):
        """Test: Cálculo de precio con descuento"""
        producto = Producto.objects.create(
            nombre="Producto Test",
            precio=Decimal("100.00"),
            precio_oferta=Decimal("75.00")
        )
        
        # Verificar precio actual
        self.assertEqual(producto.precio_actual(), Decimal("75.00"))
        
        # Verificar descuento
        self.assertEqual(producto.descuento_porcentaje(), 25)
        
        # Verificar que tiene oferta
        self.assertTrue(producto.tiene_oferta())
```

### Test de Validaciones

```python
from django.test import TestCase
from django.core.exceptions import ValidationError
from productos.models import Producto

class ProductoValidacionesTest(TestCase):
    def test_precio_no_puede_ser_negativo(self):
        """Test: El precio no puede ser negativo"""
        producto = Producto(
            nombre="Test",
            precio=-10.00
        )
        
        with self.assertRaises(ValidationError):
            producto.full_clean()
    
    def test_nombre_requerido(self):
        """Test: El nombre es obligatorio"""
        producto = Producto(precio=10.00)
        
        with self.assertRaises(ValidationError):
            producto.full_clean()
```

---

## 2. Ejemplos de Tests de Integración

### Test de Vista Simple

```python
from django.test import TestCase, Client
from django.urls import reverse

class InicioViewTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_vista_inicio_carga(self):
        """Test: La vista de inicio carga correctamente"""
        response = self.client.get(reverse('core:inicio'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/inicio.html')
```

### Test de Vista con Datos

```python
from django.test import TestCase, Client
from django.urls import reverse
from productos.models import Producto

class CatalogoViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Crear productos de prueba
        for i in range(5):
            Producto.objects.create(
                nombre=f"Producto {i}",
                precio=10.00 + i,
                stock=10,
                esta_disponible=True
            )
    
    def test_catalogo_muestra_productos(self):
        """Test: El catálogo muestra los productos"""
        response = self.client.get(reverse('productos:catalogo'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['productos']), 5)
```

### Test de Vista con Autenticación

```python
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class PerfilViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_perfil_requiere_autenticacion(self):
        """Test: Acceso al perfil requiere autenticación"""
        response = self.client.get(reverse('clientes:perfil'))
        
        # Redirige al login
        self.assertEqual(response.status_code, 302)
    
    def test_perfil_usuario_autenticado(self):
        """Test: Usuario autenticado accede al perfil"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('clientes:perfil'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user)
```

### Test de Formulario POST

```python
from django.test import TestCase, Client
from django.urls import reverse

class RegistroFormTest(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_registro_exitoso(self):
        """Test: Registro de usuario exitoso"""
        datos = {
            'username': 'nuevouser',
            'email': 'nuevo@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        
        response = self.client.post(reverse('clientes:registro'), datos)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el usuario fue creado
        self.assertTrue(
            User.objects.filter(username='nuevouser').exists()
        )
    
    def test_registro_password_invalido(self):
        """Test: Registro falla con contraseña débil"""
        datos = {
            'username': 'nuevouser',
            'email': 'nuevo@example.com',
            'password1': '123',  # Contraseña muy débil
            'password2': '123',
        }
        
        response = self.client.post(reverse('clientes:registro'), datos)
        
        # Debe permanecer en la misma página con errores
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', 'password1', 
            'La contraseña es muy corta'
        )
```

---

## 3. Uso de Fixtures y Factories

### Fixtures Básicas

```python
from django.test import TestCase
from productos.models import Categoria, Marca, Producto

class BaseProductoTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Datos que se crean una vez para toda la clase"""
        cls.categoria = Categoria.objects.create(nombre="Juguetes")
        cls.marca = Marca.objects.create(nombre="Kong")
    
    def setUp(self):
        """Se ejecuta antes de cada test"""
        self.producto = Producto.objects.create(
            nombre="Producto Test",
            precio=19.99,
            categoria=self.categoria,
            marca=self.marca
        )
```

### Factory Boy (Avanzado)

```python
# En factories.py
import factory
from factory.django import DjangoModelFactory
from productos.models import Producto, Categoria, Marca

class CategoriaFactory(DjangoModelFactory):
    class Meta:
        model = Categoria
    
    nombre = factory.Faker('word')
    descripcion = factory.Faker('text', max_nb_chars=200)

class MarcaFactory(DjangoModelFactory):
    class Meta:
        model = Marca
    
    nombre = factory.Faker('company')

class ProductoFactory(DjangoModelFactory):
    class Meta:
        model = Producto
    
    nombre = factory.Faker('catch_phrase')
    descripcion = factory.Faker('text')
    precio = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    categoria = factory.SubFactory(CategoriaFactory)
    marca = factory.SubFactory(MarcaFactory)
    stock = factory.Faker('random_int', min=0, max=100)

# En tests.py
from .factories import ProductoFactory

class ProductoFactoryTest(TestCase):
    def test_crear_producto_con_factory(self):
        """Test: Crear producto usando factory"""
        producto = ProductoFactory()
        
        self.assertIsNotNone(producto.id)
        self.assertIsNotNone(producto.categoria)
        self.assertIsNotNone(producto.marca)
    
    def test_crear_multiples_productos(self):
        """Test: Crear múltiples productos"""
        productos = ProductoFactory.create_batch(10)
        
        self.assertEqual(len(productos), 10)
        self.assertEqual(Producto.objects.count(), 10)
```

---

## 4. Mocking y Patching

### Mock de Métodos Externos

```python
from unittest.mock import patch, Mock
from django.test import TestCase
from pedidos.models import Pedido

class PedidoEmailTest(TestCase):
    @patch('pedidos.models.send_mail')
    def test_enviar_email_confirmacion(self, mock_send_mail):
        """Test: Envío de email de confirmación"""
        pedido = Pedido.objects.create(
            nombre_cliente="Test",
            email_cliente="test@example.com",
            total=100.00,
            metodo_pago='tarjeta'
        )
        
        # Llamar método que envía email
        pedido.enviar_confirmacion()
        
        # Verificar que se llamó send_mail
        mock_send_mail.assert_called_once()
        self.assertIn('test@example.com', mock_send_mail.call_args[1]['recipient_list'])
```

### Mock de APIs Externas

```python
from unittest.mock import patch
from django.test import TestCase
from pedidos.services import PagoService

class PagoServiceTest(TestCase):
    @patch('requests.post')
    def test_procesar_pago_exitoso(self, mock_post):
        """Test: Procesar pago exitoso"""
        # Configurar respuesta mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'approved',
            'transaction_id': 'TXN123'
        }
        mock_post.return_value = mock_response
        
        # Ejecutar
        servicio = PagoService()
        resultado = servicio.procesar_pago(
            monto=100.00,
            tarjeta='4111111111111111'
        )
        
        # Verificar
        self.assertTrue(resultado['success'])
        self.assertEqual(resultado['transaction_id'], 'TXN123')
```

---

## 5. Testing de APIs (Django REST Framework)

```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from productos.models import Producto

class ProductoAPITest(APITestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre="Producto API",
            precio=29.99,
            stock=10
        )
    
    def test_listar_productos(self):
        """Test: Listar productos vía API"""
        url = reverse('api:producto-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_crear_producto_autenticado(self):
        """Test: Crear producto requiere autenticación"""
        url = reverse('api:producto-list')
        data = {
            'nombre': 'Nuevo Producto',
            'precio': 19.99,
            'stock': 5
        }
        
        # Sin autenticación
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Con autenticación
        user = User.objects.create_user('testuser', 'test@test.com', 'testpass')
        self.client.force_authenticate(user=user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
```

---

## 6. Patrones Comunes

### Test de Paginación

```python
from django.test import TestCase
from django.core.paginator import Paginator
from productos.models import Producto

class PaginacionTest(TestCase):
    def setUp(self):
        # Crear 25 productos
        for i in range(25):
            Producto.objects.create(
                nombre=f"Producto {i}",
                precio=10.00
            )
    
    def test_paginacion_12_items_por_pagina(self):
        """Test: Paginación con 12 items por página"""
        productos = Producto.objects.all()
        paginator = Paginator(productos, 12)
        
        # Verificar número de páginas
        self.assertEqual(paginator.num_pages, 3)
        
        # Verificar primera página
        pagina1 = paginator.get_page(1)
        self.assertEqual(len(pagina1), 12)
        
        # Verificar última página
        pagina3 = paginator.get_page(3)
        self.assertEqual(len(pagina3), 1)
```

### Test de Búsqueda y Filtros

```python
from django.test import TestCase
from productos.models import Producto, Categoria

class BusquedaTest(TestCase):
    def setUp(self):
        self.categoria_perros = Categoria.objects.create(nombre="Perros")
        self.categoria_gatos = Categoria.objects.create(nombre="Gatos")
        
        Producto.objects.create(
            nombre="Pelota para perros",
            categoria=self.categoria_perros,
            precio=15.00
        )
        Producto.objects.create(
            nombre="Ratón para gatos",
            categoria=self.categoria_gatos,
            precio=5.00
        )
    
    def test_busqueda_por_nombre(self):
        """Test: Buscar productos por nombre"""
        resultados = Producto.objects.filter(nombre__icontains='perro')
        
        self.assertEqual(resultados.count(), 1)
        self.assertIn('Pelota', resultados.first().nombre)
    
    def test_filtro_por_categoria(self):
        """Test: Filtrar productos por categoría"""
        resultados = Producto.objects.filter(categoria=self.categoria_gatos)
        
        self.assertEqual(resultados.count(), 1)
        self.assertEqual(resultados.first().categoria, self.categoria_gatos)
```

### Test de Transacciones

```python
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from productos.models import Producto

class TransaccionTest(TransactionTestCase):
    def test_rollback_en_error(self):
        """Test: Rollback de transacción en caso de error"""
        inicial = Producto.objects.count()
        
        try:
            with transaction.atomic():
                Producto.objects.create(
                    nombre="Producto 1",
                    precio=10.00
                )
                # Forzar error
                raise Exception("Error intencional")
        except Exception:
            pass
        
        # Verificar que no se guardó nada
        self.assertEqual(Producto.objects.count(), inicial)
```

### Test de Signals

```python
from django.test import TestCase
from django.db.models.signals import post_save
from productos.models import Producto

class SignalsTest(TestCase):
    def test_signal_post_save_producto(self):
        """Test: Signal post_save se ejecuta al crear producto"""
        # Variable para capturar la llamada al signal
        signal_called = []
        
        def signal_handler(sender, instance, created, **kwargs):
            if created:
                signal_called.append(instance)
        
        # Conectar el handler
        post_save.connect(signal_handler, sender=Producto)
        
        # Crear producto
        producto = Producto.objects.create(
            nombre="Test Signal",
            precio=10.00
        )
        
        # Verificar que se llamó
        self.assertEqual(len(signal_called), 1)
        self.assertEqual(signal_called[0], producto)
        
        # Desconectar
        post_save.disconnect(signal_handler, sender=Producto)
```

---

## 📝 Resumen de Mejores Prácticas

1. ✅ **Usa nombres descriptivos** para los tests
2. ✅ **Un test, una verificación** (cuando sea posible)
3. ✅ **Usa setUp y tearDown** apropiadamente
4. ✅ **Tests independientes** - no dependan de orden de ejecución
5. ✅ **Usa factories** para datos de prueba complejos
6. ✅ **Mock servicios externos** para tests rápidos y confiables
7. ✅ **Documenta** el propósito de cada test
8. ✅ **Mantén tests simples** y legibles
9. ✅ **Ejecuta tests frecuentemente** durante desarrollo
10. ✅ **Apunta a alta cobertura** pero prioriza calidad sobre cantidad

---

## 🎯 Ejercicios Prácticos

### Ejercicio 1: Test Básico
Crea un test para verificar que un producto sin stock no está disponible.

### Ejercicio 2: Test de Integración
Crea un test que simule el flujo completo de: agregar producto al carrito → checkout → crear pedido.

### Ejercicio 3: Test con Mock
Crea un test que verifique el envío de email de confirmación sin enviar emails reales.

---

**¡Happy Testing!** 🚀
