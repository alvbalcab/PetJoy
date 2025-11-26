from decimal import Decimal
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from pedidos.models import Carrito, ItemCarrito, Pedido, ItemPedido
from pedidos.carrito import Carrito as CarritoSesion
from productos.models import Producto
from core.models import DatosEmpresa

User = get_user_model()


class CarritoIntegrationTest(TestCase):
    """Tests de integración para el carrito de compras"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        self.factory = RequestFactory()
        
        # Crear datos de empresa para cálculos
        DatosEmpresa.objects.create(
            nombre="PetJoy",
            email="contacto@petjoy.com",
            telefono="123456789",
            coste_envio_estandar=Decimal("5.00"),
            envio_gratuito_desde=Decimal("50.00"),
            iva_porcentaje=Decimal("21.00")
        )
        
        # Crear productos de prueba
        self.producto1 = Producto.objects.create(
            nombre="Producto 1",
            descripcion="Descripción 1",
            precio=Decimal("20.00"),
            stock=50,
            esta_disponible=True
        )
        
        self.producto2 = Producto.objects.create(
            nombre="Producto 2",
            descripcion="Descripción 2",
            precio=Decimal("30.00"),
            precio_oferta=Decimal("25.00"),
            stock=30,
            esta_disponible=True
        )
    
    def _crear_request_con_sesion(self):
        """Helper para crear un request con sesión"""
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(request)
        request.session.save()
        return request
    
    def test_carrito_agregar_producto(self):
        """Test: Agregar un producto al carrito"""
        request = self._crear_request_con_sesion()
        carrito = CarritoSesion(request)
        
        carrito.agregar(self.producto1, cantidad=2)
        
        self.assertEqual(len(carrito), 2)
        self.assertIn(str(self.producto1.id), carrito.carrito)
    
    def test_carrito_agregar_producto_con_talla(self):
        """Test: Agregar producto con talla específica"""
        request = self._crear_request_con_sesion()
        carrito = CarritoSesion(request)
        
        carrito.agregar(self.producto1, cantidad=1, talla="M")
        carrito.agregar(self.producto1, cantidad=2, talla="L")
        
        self.assertEqual(len(carrito), 3)
    
    def test_carrito_eliminar_producto(self):
        """Test: Eliminar un producto del carrito"""
        request = self._crear_request_con_sesion()
        carrito = CarritoSesion(request)
        
        carrito.agregar(self.producto1, cantidad=2)
        carrito.eliminar(self.producto1)
        
        self.assertEqual(len(carrito), 0)
        self.assertNotIn(str(self.producto1.id), carrito.carrito)
    
    def test_carrito_actualizar_cantidad(self):
        """Test: Actualizar cantidad de un producto"""
        request = self._crear_request_con_sesion()
        carrito = CarritoSesion(request)
        
        carrito.agregar(self.producto1, cantidad=2)
        carrito.agregar(self.producto1, cantidad=5, actualizar_cantidad=True)
        
        self.assertEqual(len(carrito), 5)
    
    def test_carrito_precio_total(self):
        """Test: Calcular el precio total del carrito"""
        request = self._crear_request_con_sesion()
        carrito = CarritoSesion(request)
        
        carrito.agregar(self.producto1, cantidad=2)  # 20 * 2 = 40
        carrito.agregar(self.producto2, cantidad=1)  # 25 (oferta)
        
        total = carrito.obtener_precio_total()
        self.assertEqual(total, Decimal("65.00"))
    
    def test_carrito_coste_envio_con_minimo(self):
        """Test: Coste de envío cuando se alcanza el mínimo"""
        request = self._crear_request_con_sesion()
        carrito = CarritoSesion(request)
        
        # Agregar productos por más de 50€
        carrito.agregar(self.producto1, cantidad=3)  # 60€
        
        coste_envio = carrito.obtener_coste_envio()
        self.assertEqual(coste_envio, Decimal("0.00"))
    
    def test_carrito_coste_envio_sin_minimo(self):
        """Test: Coste de envío cuando no se alcanza el mínimo"""
        request = self._crear_request_con_sesion()
        carrito = CarritoSesion(request)
        
        carrito.agregar(self.producto1, cantidad=1)  # 20€
        
        coste_envio = carrito.obtener_coste_envio()
        self.assertEqual(coste_envio, Decimal("5.00"))
    
    def test_carrito_impuestos(self):
        """Test: Cálculo de impuestos (IVA)"""
        request = self._crear_request_con_sesion()
        carrito = CarritoSesion(request)
        
        carrito.agregar(self.producto1, cantidad=1)  # 20€
        
        impuestos = carrito.obtener_impuestos()
        # 20 * 21% = 4.20
        self.assertEqual(impuestos, Decimal("4.20"))
    
    def test_carrito_total_final(self):
        """Test: Cálculo del total final (subtotal + envío + IVA)"""
        request = self._crear_request_con_sesion()
        carrito = CarritoSesion(request)
        
        carrito.agregar(self.producto1, cantidad=1)  # 20€
        
        total_final = carrito.obtener_total_final()
        # Subtotal: 20€
        # Envío: 5€
        # IVA: 20 * 0.21 = 4.20€
        # Total: 29.20€
        self.assertEqual(total_final, Decimal("29.20"))
    
    def test_carrito_limpiar(self):
        """Test: Limpiar el carrito"""
        request = self._crear_request_con_sesion()
        carrito = CarritoSesion(request)
        
        carrito.agregar(self.producto1, cantidad=2)
        carrito.agregar(self.producto2, cantidad=1)
        
        carrito.limpiar()
        
        self.assertEqual(len(carrito), 0)
        self.assertEqual(len(request.session.get('carrito', {})), 0)
    
    def test_carrito_iteracion(self):
        """Test: Iterar sobre los items del carrito"""
        request = self._crear_request_con_sesion()
        carrito = CarritoSesion(request)
        
        carrito.agregar(self.producto1, cantidad=2)
        carrito.agregar(self.producto2, cantidad=1)
        
        items = list(carrito)
        self.assertEqual(len(items), 2)
        
        # Verificar que los items tienen los atributos necesarios
        for item in items:
            self.assertIn('producto', item)
            self.assertIn('cantidad', item)
            self.assertIn('precio', item)
            self.assertIn('total', item)


class PedidoIntegrationTest(TestCase):
    """Tests de integración para el proceso de pedidos"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        
        # Crear usuario
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Crear datos de empresa
        DatosEmpresa.objects.create(
            nombre="PetJoy",
            email="contacto@petjoy.com",
            telefono="123456789",
            coste_envio_estandar=Decimal("5.00"),
            envio_gratuito_desde=Decimal("50.00"),
            iva_porcentaje=Decimal("21.00")
        )
        
        # Crear producto
        self.producto = Producto.objects.create(
            nombre="Producto Test",
            descripcion="Descripción test",
            precio=Decimal("25.00"),
            stock=50,
            esta_disponible=True
        )
    
    def test_crear_pedido_completo(self):
        """Test: Crear un pedido completo con todos los datos"""
        pedido = Pedido.objects.create(
            cliente=self.user,
            nombre_cliente='Test',
            apellidos_cliente='User',
            email_cliente='test@example.com',
            telefono_cliente='123456789',
            direccion_envio='Calle Test 123',
            ciudad_envio='Sevilla',
            codigo_postal_envio='41001',
            subtotal=Decimal("25.00"),
            impuestos=Decimal("5.25"),
            coste_entrega=Decimal("5.00"),
            total=Decimal("35.25"),
            metodo_pago='tarjeta'
        )
        
        # Crear item del pedido
        ItemPedido.objects.create(
            pedido=pedido,
            producto=self.producto,
            nombre_producto=self.producto.nombre,
            cantidad=1,
            precio_unitario=Decimal("25.00"),
            total=Decimal("25.00")
        )
        
        self.assertIsNotNone(pedido.numero_pedido)
        self.assertEqual(pedido.estado, 'pendiente')
        self.assertEqual(pedido.items.count(), 1)
        self.assertEqual(pedido.total, Decimal("35.25"))
    
    def test_pedido_sin_usuario_registrado(self):
        """Test: Crear pedido como invitado (sin usuario registrado)"""
        pedido = Pedido.objects.create(
            nombre_cliente='Usuario Invitado',
            apellidos_cliente='Apellidos',
            email_cliente='invitado@example.com',
            telefono_cliente='987654321',
            direccion_envio='Calle Invitado 456',
            ciudad_envio='Madrid',
            codigo_postal_envio='28001',
            subtotal=Decimal("50.00"),
            impuestos=Decimal("10.50"),
            coste_entrega=Decimal("0.00"),
            total=Decimal("60.50"),
            metodo_pago='contrareembolso'
        )
        
        self.assertIsNone(pedido.cliente)
        self.assertEqual(pedido.email_cliente, 'invitado@example.com')
        self.assertIsNotNone(pedido.numero_pedido)
    
    def test_cambiar_estado_pedido(self):
        """Test: Cambiar el estado de un pedido"""
        pedido = Pedido.objects.create(
            cliente=self.user,
            nombre_cliente='Test',
            apellidos_cliente='User',
            email_cliente='test@example.com',
            telefono_cliente='123456789',
            direccion_envio='Calle 123',
            ciudad_envio='Sevilla',
            codigo_postal_envio='41001',
            subtotal=Decimal("100.00"),
            total=Decimal("126.00"),
            metodo_pago='tarjeta'
        )
        
        self.assertEqual(pedido.estado, 'pendiente')
        
        pedido.estado = 'procesando'
        pedido.save()
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'procesando')
        
        pedido.estado = 'enviado'
        pedido.save()
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'enviado')
    
    def test_item_pedido_mantiene_datos_producto_eliminado(self):
        """Test: Los items del pedido mantienen datos aunque se elimine el producto"""
        pedido = Pedido.objects.create(
            cliente=self.user,
            nombre_cliente='Test',
            apellidos_cliente='User',
            email_cliente='test@example.com',
            telefono_cliente='123456789',
            direccion_envio='Calle 123',
            ciudad_envio='Sevilla',
            codigo_postal_envio='41001',
            subtotal=Decimal("25.00"),
            total=Decimal("35.25"),
            metodo_pago='tarjeta'
        )
        
        item = ItemPedido.objects.create(
            pedido=pedido,
            producto=self.producto,
            nombre_producto=self.producto.nombre,
            cantidad=1,
            precio_unitario=Decimal("25.00"),
            total=Decimal("25.00")
        )
        
        nombre_producto = item.nombre_producto
        precio_unitario = item.precio_unitario
        
        # Eliminar el producto
        self.producto.delete()
        
        # Verificar que el item aún tiene los datos
        item.refresh_from_db()
        self.assertIsNone(item.producto)
        self.assertEqual(item.nombre_producto, nombre_producto)
        self.assertEqual(item.precio_unitario, precio_unitario)
    
    def test_pedido_calculos_totales_correctos(self):
        """Test: Los cálculos de totales son correctos"""
        pedido = Pedido.objects.create(
            cliente=self.user,
            nombre_cliente='Test',
            apellidos_cliente='User',
            email_cliente='test@example.com',
            telefono_cliente='123456789',
            direccion_envio='Calle 123',
            ciudad_envio='Sevilla',
            codigo_postal_envio='41001',
            subtotal=Decimal("100.00"),
            impuestos=Decimal("21.00"),
            coste_entrega=Decimal("5.00"),
            descuento=Decimal("10.00"),
            total=Decimal("116.00"),
            metodo_pago='tarjeta'
        )
        
        # Total = Subtotal + Impuestos + Envío - Descuento
        # 100 + 21 + 5 - 10 = 116
        total_esperado = (
            pedido.subtotal + 
            pedido.impuestos + 
            pedido.coste_entrega - 
            pedido.descuento
        )
        
        self.assertEqual(pedido.total, total_esperado)


class CheckoutIntegrationTest(TestCase):
    """Tests de integración para el proceso de checkout"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        
        # Crear usuario
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear datos de empresa
        DatosEmpresa.objects.create(
            nombre="PetJoy",
            email="contacto@petjoy.com",
            telefono="123456789",
            coste_envio_estandar=Decimal("5.00"),
            envio_gratuito_desde=Decimal("50.00"),
            iva_porcentaje=Decimal("21.00")
        )
        
        # Crear productos
        self.producto1 = Producto.objects.create(
            nombre="Producto 1",
            descripcion="Descripción 1",
            precio=Decimal("30.00"),
            stock=50,
            esta_disponible=True
        )
        
        self.producto2 = Producto.objects.create(
            nombre="Producto 2",
            descripcion="Descripción 2",
            precio=Decimal("25.00"),
            stock=30,
            esta_disponible=True
        )
    
    def test_carrito_a_pedido_conversion(self):
        """Test: Conversión de carrito a pedido"""
        # Simular agregar productos al carrito
        session = self.client.session
        session['carrito'] = {
            str(self.producto1.id): {
                'producto_id': str(self.producto1.id),
                'cantidad': 2,
                'precio': str(self.producto1.precio),
                'talla': ''
            },
            str(self.producto2.id): {
                'producto_id': str(self.producto2.id),
                'cantidad': 1,
                'precio': str(self.producto2.precio),
                'talla': ''
            }
        }
        session.save()
        
        # Crear pedido basado en el carrito
        subtotal = Decimal("85.00")  # (30*2) + 25
        impuestos = subtotal * Decimal("0.21")  # 17.85
        coste_entrega = Decimal("0.00")  # Supera los 50€
        total = subtotal + impuestos + coste_entrega
        
        pedido = Pedido.objects.create(
            cliente=self.user,
            nombre_cliente='Test',
            apellidos_cliente='User',
            email_cliente='test@example.com',
            telefono_cliente='123456789',
            direccion_envio='Calle 123',
            ciudad_envio='Sevilla',
            codigo_postal_envio='41001',
            subtotal=subtotal,
            impuestos=impuestos,
            coste_entrega=coste_entrega,
            total=total,
            metodo_pago='tarjeta'
        )
        
        # Crear items del pedido basados en el carrito
        for item_data in session['carrito'].values():
            producto = Producto.objects.get(id=item_data['producto_id'])
            ItemPedido.objects.create(
                pedido=pedido,
                producto=producto,
                nombre_producto=producto.nombre,
                cantidad=item_data['cantidad'],
                precio_unitario=Decimal(item_data['precio']),
                total=Decimal(item_data['precio']) * item_data['cantidad']
            )
        
        self.assertEqual(pedido.items.count(), 2)
        self.assertEqual(pedido.total, Decimal("102.85"))