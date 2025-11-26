"""
Tests completos para pedidos/views.py - VERSIÓN CORREGIDA
Cubre: views.py (16% -> 95%+)
"""
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from productos.models import Producto
from pedidos.models import Pedido, ItemPedido
from pedidos.carrito import Carrito
from pedidos.forms import DatosEnvioForm
from core.models import DatosEmpresa

User = get_user_model()


class CarritoSetupMixin:
    """Mixin para configurar el carrito en los tests"""
    
    def setup_carrito_con_productos(self, client_obj=None):
        """Crea productos y los agrega al carrito"""
        if client_obj is None:
            client_obj = self.client
            
        self.producto1 = Producto.objects.create(
            nombre="Producto Test 1",
            descripcion="Descripción 1",
            precio=Decimal("20.00"),
            stock=50,
            esta_disponible=True
        )
        self.producto2 = Producto.objects.create(
            nombre="Producto Test 2",
            descripcion="Descripción 2",
            precio=Decimal("30.00"),
            stock=30,
            esta_disponible=True
        )
        
        # Agregar productos al carrito
        session = client_obj.session
        session['carrito'] = {
            str(self.producto1.id): {
                'producto_id': str(self.producto1.id),
                'cantidad': 2,
                'precio': str(self.producto1.precio),
                'talla': '',
            },
            f"{self.producto2.id}_M": {
                'producto_id': str(self.producto2.id),
                'cantidad': 1,
                'precio': str(self.producto2.precio),
                'talla': 'M',
            }
        }
        session.save()


class VerCarritoViewTest(CarritoSetupMixin, TestCase):
    """Tests para la vista ver_carrito"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('pedidos:carrito')
        DatosEmpresa.objects.create(
            nombre="Test Shop",
            email="test@shop.com",
            telefono="123456789",
            direccion="Test St",
            ciudad="Test City",
            codigo_postal="12345"
        )
    
    def test_ver_carrito_vacio(self):
        """Test: Ver carrito vacío"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/carrito.html')
        self.assertIn('carrito', response.context)
        self.assertIn('datos_empresa', response.context)
    
    def test_ver_carrito_con_productos(self):
        """Test: Ver carrito con productos"""
        self.setup_carrito_con_productos()
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        carrito = response.context['carrito']
        self.assertEqual(len(carrito), 3)  # 2 + 1 = 3 items


class AgregarAlCarritoViewTest(TestCase):
    """Tests para la vista agregar_al_carrito"""
    
    def setUp(self):
        self.client = Client()
        self.producto = Producto.objects.create(
            nombre="Producto Test",
            descripcion="Descripción",
            precio=Decimal("25.00"),
            stock=100,
            esta_disponible=True
        )
        self.url = reverse('pedidos:agregar_carrito', args=[self.producto.id])
    
    def test_agregar_producto_al_carrito(self):
        """Test: Agregar producto al carrito"""
        response = self.client.post(self.url, {
            'cantidad': 2,
            'talla': 'L'
        })
        
        # Debe redirigir
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el producto está en el carrito
        carrito = self.client.session.get('carrito', {})
        key = f"{self.producto.id}_L"
        self.assertIn(key, carrito)
        self.assertEqual(carrito[key]['cantidad'], 2)
    
    def test_agregar_producto_sin_talla(self):
        """Test: Agregar producto sin talla"""
        response = self.client.post(self.url, {
            'cantidad': 1,
        })
        
        self.assertEqual(response.status_code, 302)
        
        carrito = self.client.session.get('carrito', {})
        self.assertIn(str(self.producto.id), carrito)
    
    def test_agregar_producto_cantidad_default(self):
        """Test: Cantidad por defecto es 1"""
        response = self.client.post(self.url, {})
        
        carrito = self.client.session.get('carrito', {})
        self.assertEqual(carrito[str(self.producto.id)]['cantidad'], 1)
    
    def test_agregar_producto_no_existe(self):
        """Test: Intentar agregar producto que no existe"""
        url = reverse('pedidos:agregar_carrito', args=[9999])
        response = self.client.post(url, {'cantidad': 1})
        
        self.assertEqual(response.status_code, 404)


class ActualizarCarritoViewTest(CarritoSetupMixin, TestCase):
    """Tests para la vista actualizar_carrito"""
    
    def setUp(self):
        self.client = Client()
        self.setup_carrito_con_productos()
        self.url = reverse('pedidos:actualizar_carrito', args=[self.producto1.id])
    
    def test_actualizar_cantidad_producto(self):
        """Test: Actualizar cantidad de producto"""
        response = self.client.post(self.url, {
            'cantidad': 5,
            'talla': ''
        })
        
        self.assertRedirects(response, reverse('pedidos:carrito'))
        
        carrito = self.client.session.get('carrito', {})
        self.assertEqual(carrito[str(self.producto1.id)]['cantidad'], 5)
    
    def test_actualizar_cantidad_a_cero_elimina_producto(self):
        """Test: Actualizar cantidad a 0 elimina el producto"""
        response = self.client.post(self.url, {
            'cantidad': 0,
            'talla': ''
        })
        
        self.assertRedirects(response, reverse('pedidos:carrito'))
        
        carrito = self.client.session.get('carrito', {})
        self.assertNotIn(str(self.producto1.id), carrito)
    
    def test_actualizar_producto_con_talla(self):
        """Test: Actualizar producto con talla específica"""
        url = reverse('pedidos:actualizar_carrito', args=[self.producto2.id])
        response = self.client.post(url, {
            'cantidad': 3,
            'talla': 'M'
        })
        
        carrito = self.client.session.get('carrito', {})
        key = f"{self.producto2.id}_M"
        self.assertEqual(carrito[key]['cantidad'], 3)


class EliminarDelCarritoViewTest(CarritoSetupMixin, TestCase):
    """Tests para la vista eliminar_del_carrito"""
    
    def setUp(self):
        self.client = Client()
        self.setup_carrito_con_productos()
        self.url = reverse('pedidos:eliminar_carrito', args=[self.producto1.id])
    
    def test_eliminar_producto_del_carrito(self):
        """Test: Eliminar producto del carrito"""
        response = self.client.get(self.url)
        
        self.assertRedirects(response, reverse('pedidos:carrito'))
        
        carrito = self.client.session.get('carrito', {})
        self.assertNotIn(str(self.producto1.id), carrito)
    
    def test_eliminar_producto_con_talla(self):
        """Test: Eliminar producto con talla específica"""
        url = reverse('pedidos:eliminar_carrito', args=[self.producto2.id]) + '?talla=M'
        response = self.client.get(url)
        
        carrito = self.client.session.get('carrito', {})
        key = f"{self.producto2.id}_M"
        self.assertNotIn(key, carrito)


class CheckoutViewTest(CarritoSetupMixin, TestCase):
    """Tests para la vista checkout"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('pedidos:checkout')
        DatosEmpresa.objects.create(
            nombre="Test Shop",
            email="test@shop.com",
            telefono="123456789",
            direccion="Test St",
            ciudad="Test City",
            codigo_postal="12345"
        )
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            telefono='123456789',
            direccion='Calle Test 123',
            ciudad='Sevilla',
            codigo_postal='41001'
        )
    
    def test_checkout_carrito_vacio_redirige(self):
        """Test: Checkout con carrito vacío redirige"""
        response = self.client.get(self.url)
        
        # Redirige a carrito (no a detalle_carrito)
        self.assertRedirects(response, reverse('pedidos:carrito'))
    
    def test_checkout_get_usuario_anonimo(self):
        """Test: Checkout GET con usuario anónimo"""
        self.setup_carrito_con_productos()
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/checkout.html')
        self.assertIsInstance(response.context['form'], DatosEnvioForm)
    
    def test_checkout_get_usuario_autenticado_precarga_datos(self):
        """Test: Checkout GET con usuario autenticado precarga sus datos"""
        self.client.login(username='test@example.com', password='testpass123')
        self.setup_carrito_con_productos()
        
        response = self.client.get(self.url)
        
        form = response.context['form']
        self.assertEqual(form.initial['nombre'], 'Test')
        self.assertEqual(form.initial['apellidos'], 'User')
        self.assertEqual(form.initial['email'], 'test@example.com')
        self.assertEqual(form.initial['direccion'], 'Calle Test 123')
    
    def test_checkout_post_valido_redirige_stripe(self):
        """Test: Checkout POST válido redirige a crear sesión Stripe por defecto"""
        self.setup_carrito_con_productos()
        
        form_data = {
            'nombre': 'Test',
            'apellidos': 'User',
            'email': 'test@example.com',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
            'metodo_pago': 'tarjeta',
            'metodo_pago_final': 'tarjeta',
            'notas': 'Test notas'
        }
        response = self.client.post(self.url, data=form_data)
        
        # Debe guardar datos en sesión
        self.assertIn('datos_envio_checkout', self.client.session)
        
        # Debe redirigir a Stripe (sin verificar que la página responda)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pedidos:crear_sesion_stripe'))
    
    def test_checkout_post_contrareembolso(self):
        """Test: Checkout POST con contrareembolso"""
        self.setup_carrito_con_productos()
        
        form_data = {
            'nombre': 'Test',
            'apellidos': 'User',
            'email': 'test@example.com',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
            'metodo_pago': 'contrareembolso',
            'metodo_pago_final': 'contrareembolso'
        }
        response = self.client.post(self.url, data=form_data)
        
        # Debe redirigir a pago contrareembolso (sin verificar que la página responda)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pedidos:pago_contrareembolso'))
    
    def test_checkout_post_invalido(self):
        """Test: Checkout POST con datos inválidos"""
        self.setup_carrito_con_productos()
        
        form_data = {
            'nombre': 'Test',
            'email': 'not-a-valid-email',  # Email inválido
        }
        response = self.client.post(self.url, data=form_data)
        
        # No debe redirigir, debe mostrar errores
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/checkout.html')


class PagoContrareembolsoViewTest(CarritoSetupMixin, TestCase):
    """Tests para la vista pago_contrareembolso"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('pedidos:pago_contrareembolso')
        DatosEmpresa.objects.create(
            nombre="Test Shop",
            email="test@shop.com",
            telefono="123456789",
            direccion="Test St",
            ciudad="Test City",
            codigo_postal="12345",
            envio_gratuito_desde=Decimal("100.00"),
            coste_envio_estandar=Decimal("5.00"),
            iva_porcentaje=Decimal("21.00")
        )
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
    
    @patch('pedidos.views.send_mail')
    def test_pago_contrareembolso_exitoso(self, mock_send_mail):
        """Test: Pago contrareembolso exitoso crea pedido"""
        self.setup_carrito_con_productos()
        
        # Configurar sesión con datos de envío
        session = self.client.session
        session['datos_envio_checkout'] = {
            'nombre': 'Test',
            'apellidos': 'User',
            'email': 'test@example.com',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
            'notas': 'Notas de prueba'
        }
        session.save()
        
        response = self.client.get(self.url)
        
        # Verificar que se creó el pedido
        pedido = Pedido.objects.first()
        self.assertIsNotNone(pedido)
        self.assertEqual(pedido.nombre_cliente, 'Test')
        self.assertEqual(pedido.metodo_pago, 'contrareembolso')
        self.assertEqual(pedido.estado, 'pendiente')
        
        # Verificar que se envió el email
        mock_send_mail.assert_called_once()
        
        # Verificar redirección
        self.assertRedirects(response, reverse('pedidos:confirmacion', args=[pedido.numero_pedido]))
        
        # Verificar que se limpió datos_envio_checkout
        self.assertNotIn('datos_envio_checkout', self.client.session)
    
    @patch('pedidos.views.send_mail')
    def test_pago_contrareembolso_actualiza_stock(self, mock_send_mail):
        """Test: Pago contrareembolso actualiza el stock de productos"""
        self.setup_carrito_con_productos()
        stock_inicial_1 = self.producto1.stock
        stock_inicial_2 = self.producto2.stock
        
        session = self.client.session
        session['datos_envio_checkout'] = {
            'nombre': 'Test',
            'apellidos': 'User',
            'email': 'test@example.com',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
        }
        session.save()
        
        self.client.get(self.url)
        
        # Verificar stock actualizado
        self.producto1.refresh_from_db()
        self.producto2.refresh_from_db()
        self.assertEqual(self.producto1.stock, stock_inicial_1 - 2)
        self.assertEqual(self.producto2.stock, stock_inicial_2 - 1)
    
    def test_pago_contrareembolso_sin_datos_sesion(self):
        """Test: Pago contrareembolso sin datos en sesión redirige"""
        response = self.client.get(self.url)
        
        # Debe redirigir a checkout
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pedidos:checkout'))
        
        # No se debe crear ningún pedido
        self.assertEqual(Pedido.objects.count(), 0)
    
    def test_pago_contrareembolso_carrito_vacio(self):
        """Test: Pago contrareembolso con carrito vacío redirige"""
        session = self.client.session
        session['datos_envio_checkout'] = {
            'nombre': 'Test',
            'apellidos': 'User',
            'email': 'test@example.com',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
        }
        session.save()
        
        response = self.client.get(self.url)
        
        # Debe redirigir a checkout
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pedidos:checkout'))
        self.assertEqual(Pedido.objects.count(), 0)
    
    @patch('pedidos.views.send_mail')
    def test_pago_contrareembolso_usuario_autenticado(self, mock_send_mail):
        """Test: Pago contrareembolso con usuario autenticado vincula el pedido"""
        self.client.login(username='test@example.com', password='testpass123')
        self.setup_carrito_con_productos()
        
        session = self.client.session
        session['datos_envio_checkout'] = {
            'nombre': 'Test',
            'apellidos': 'User',
            'email': 'test@example.com',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
        }
        session.save()
        
        self.client.get(self.url)
        
        pedido = Pedido.objects.first()
        self.assertEqual(pedido.cliente, self.user)
    
    @patch('pedidos.views.send_mail', side_effect=Exception('Email error'))
    def test_pago_contrareembolso_error_manejo(self, mock_send_mail):
        """Test: Manejo de errores en pago contrareembolso"""
        self.setup_carrito_con_productos()
        
        session = self.client.session
        session['datos_envio_checkout'] = {
            'nombre': 'Test',
            'apellidos': 'User',
            'email': 'test@example.com',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
        }
        session.save()
        
        response = self.client.get(self.url)
        
        # Debe redirigir a checkout con mensaje de error
        self.assertRedirects(response, reverse('pedidos:checkout'))


class CrearSesionStripeViewTest(CarritoSetupMixin, TestCase):
    """Tests para la vista crear_sesion_stripe"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('pedidos:crear_sesion_stripe')
        DatosEmpresa.objects.create(
            nombre="Test Shop",
            email="test@shop.com",
            telefono="123456789",
            direccion="Test St",
            ciudad="Test City",
            codigo_postal="12345",
            envio_gratuito_desde=Decimal("100.00"),
            coste_envio_estandar=Decimal("5.00"),
            iva_porcentaje=Decimal("21.00")
        )
    
    def test_crear_sesion_sin_datos_envio(self):
        """Test: Crear sesión sin datos de envío retorna error"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Faltan datos de envío o el carrito está vacío.')
    
    def test_crear_sesion_carrito_vacio(self):
        """Test: Crear sesión con carrito vacío retorna error"""
        session = self.client.session
        session['datos_envio_checkout'] = {
            'nombre': 'Test',
            'email': 'test@example.com'
        }
        session.save()
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 400)
    
    @patch('pedidos.views.stripe.checkout.Session.create')
    def test_crear_sesion_stripe_exitoso(self, mock_stripe_session):
        """Test: Crear sesión Stripe exitosa"""
        self.setup_carrito_con_productos()
        
        # Mock de Stripe
        mock_stripe_session.return_value = MagicMock(
            url='https://checkout.stripe.com/test-session'
        )
        
        session = self.client.session
        session['datos_envio_checkout'] = {
            'nombre': 'Test',
            'apellidos': 'User',
            'email': 'test@example.com',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
        }
        session.save()
        
        response = self.client.get(self.url)
        
        # Debe redirigir a Stripe
        self.assertEqual(response.status_code, 302)
        mock_stripe_session.assert_called_once()
    
    @patch('pedidos.views.stripe.checkout.Session.create', side_effect=Exception('Stripe error'))
    def test_crear_sesion_stripe_error(self, mock_stripe_session):
        """Test: Manejo de error al crear sesión Stripe"""
        self.setup_carrito_con_productos()
        
        session = self.client.session
        session['datos_envio_checkout'] = {
            'nombre': 'Test',
            'email': 'test@example.com',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
        }
        session.save()
        
        response = self.client.get(self.url)
        
        self.assertRedirects(response, reverse('pedidos:checkout'))


class PagoExitosoViewTest(CarritoSetupMixin, TestCase):
    """Tests para la vista pago_exitoso"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('pedidos:pago_exitoso')
        DatosEmpresa.objects.create(
            nombre="Test Shop",
            email="test@shop.com",
            telefono="123456789",
            direccion="Test St",
            ciudad="Test City",
            codigo_postal="12345",
            envio_gratuito_desde=Decimal("100.00"),
            coste_envio_estandar=Decimal("5.00"),
            iva_porcentaje=Decimal("21.00")
        )
    
    def test_pago_exitoso_sin_session_id(self):
        """Test: Pago exitoso sin session_id redirige"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pedidos:checkout'))
    
    def test_pago_exitoso_sin_datos_envio(self):
        """Test: Pago exitoso sin datos de envío redirige"""
        response = self.client.get(self.url + '?session_id=test_session')
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pedidos:checkout'))
    
    @patch('pedidos.views.stripe.checkout.Session.retrieve')
    @patch('pedidos.views.send_mail')
    def test_pago_exitoso_completo(self, mock_send_mail, mock_stripe_retrieve):
        """Test: Pago exitoso completo crea pedido"""
        self.setup_carrito_con_productos()
        
        # Mock de Stripe
        mock_stripe_retrieve.return_value = MagicMock(
            payment_status='paid'
        )
        
        session = self.client.session
        session['datos_envio_checkout'] = {
            'nombre': 'Test',
            'apellidos': 'User',
            'email': 'test@example.com',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
        }
        session.save()
        
        response = self.client.get(self.url + '?session_id=test_session')
        
        # Verificar que se creó el pedido
        pedido = Pedido.objects.first()
        self.assertIsNotNone(pedido)
        self.assertEqual(pedido.metodo_pago, 'tarjeta')
        self.assertEqual(pedido.estado, 'procesando')
        
        # Verificar email enviado
        mock_send_mail.assert_called_once()
    
    @patch('pedidos.views.stripe.checkout.Session.retrieve')
    def test_pago_no_completado(self, mock_stripe_retrieve):
        """Test: Pago no completado redirige a cancelado"""
        # Mock de Stripe con pago no completado
        mock_stripe_retrieve.return_value = MagicMock(
            payment_status='unpaid'
        )
        
        session = self.client.session
        session['datos_envio_checkout'] = {
            'nombre': 'Test',
            'email': 'test@example.com',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
        }
        session.save()
        
        response = self.client.get(self.url + '?session_id=test_session')
        
        self.assertRedirects(response, reverse('pedidos:pago_cancelado'))
    
    @patch('pedidos.views.stripe.checkout.Session.retrieve')
    def test_pago_exitoso_carrito_vacio_ya_procesado(self, mock_stripe_retrieve):
        """Test: Pago exitoso con carrito vacío (pedido ya procesado)"""
        mock_stripe_retrieve.return_value = MagicMock(
            payment_status='paid'
        )
        
        session = self.client.session
        session['datos_envio_checkout'] = {
            'nombre': 'Test',
            'email': 'test@example.com',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
        }
        session.save()
        
        response = self.client.get(self.url + '?session_id=test_session')
        
        self.assertRedirects(response, reverse('pedidos:seguimiento'))


class PagoCanceladoViewTest(TestCase):
    """Tests para la vista pago_cancelado"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('pedidos:pago_cancelado')
    
    def test_pago_cancelado_vista(self):
        """Test: Vista de pago cancelado"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/pago_cancelado.html')


class ConfirmacionPedidoViewTest(TestCase):
    """Tests para la vista confirmacion_pedido"""
    
    def setUp(self):
        self.client = Client()
        DatosEmpresa.objects.create(
            nombre="Test Shop",
            email="test@shop.com",
            telefono="123456789",
            direccion="Test St",
            ciudad="Test City",
            codigo_postal="12345"
        )
        self.pedido = Pedido.objects.create(
            nombre_cliente='Test',
            apellidos_cliente='User',
            email_cliente='test@example.com',
            telefono_cliente='123456789',
            direccion_envio='Calle Test 123',
            ciudad_envio='Sevilla',
            codigo_postal_envio='41001',
            subtotal=Decimal("50.00"),
            total=Decimal("60.50"),
            metodo_pago='tarjeta'
        )
        self.url = reverse('pedidos:confirmacion', args=[self.pedido.numero_pedido])
    
    def test_confirmacion_pedido_vista(self):
        """Test: Vista de confirmación de pedido"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/confirmacion.html')
        self.assertEqual(response.context['pedido'], self.pedido)
        self.assertIn('datos_empresa', response.context)
    
    def test_confirmacion_pedido_no_existe(self):
        """Test: Confirmación de pedido que no existe"""
        url = reverse('pedidos:confirmacion', args=['NOEXISTE123'])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class SeguimientoPedidoViewTest(TestCase):
    """Tests para la vista seguimiento_pedido"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('pedidos:seguimiento')
        self.pedido = Pedido.objects.create(
            nombre_cliente='Test',
            apellidos_cliente='User',
            email_cliente='test@example.com',
            telefono_cliente='123456789',
            direccion_envio='Calle Test 123',
            ciudad_envio='Sevilla',
            codigo_postal_envio='41001',
            subtotal=Decimal("50.00"),
            total=Decimal("60.50"),
            metodo_pago='tarjeta'
        )
    
    def test_seguimiento_get(self):
        """Test: Página de seguimiento GET"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/seguimiento.html')
        self.assertIsNone(response.context['pedido'])
    
    def test_seguimiento_post_pedido_encontrado(self):
        """Test: Seguimiento POST con pedido encontrado"""
        response = self.client.post(self.url, {
            'numero_pedido': self.pedido.numero_pedido,
            'email': 'test@example.com'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pedido'], self.pedido)
    
    def test_seguimiento_post_pedido_no_encontrado(self):
        """Test: Seguimiento POST con pedido no encontrado"""
        response = self.client.post(self.url, {
            'numero_pedido': 'NOEXISTE123',
            'email': 'test@example.com'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['pedido'])
    
    def test_seguimiento_post_email_incorrecto(self):
        """Test: Seguimiento POST con email incorrecto"""
        response = self.client.post(self.url, {
            'numero_pedido': self.pedido.numero_pedido,
            'email': 'wrong@example.com'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['pedido'])


class MisPedidosViewTest(TestCase):
    """Tests para la vista mis_pedidos"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('pedidos:mis_pedidos')
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_mis_pedidos_requiere_login(self):
        """Test: Vista mis_pedidos requiere autenticación"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_mis_pedidos_usuario_autenticado(self):
        """Test: Usuario autenticado ve sus pedidos"""
        self.client.login(username='test@example.com', password='testpass123')
        
        # Crear pedidos del usuario
        pedido1 = Pedido.objects.create(
            cliente=self.user,
            nombre_cliente='Test',
            apellidos_cliente='User',
            email_cliente='test@example.com',
            telefono_cliente='123456789',
            direccion_envio='Calle Test 123',
            ciudad_envio='Sevilla',
            codigo_postal_envio='41001',
            subtotal=Decimal("50.00"),
            total=Decimal("60.50"),
            metodo_pago='tarjeta'
        )
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pedidos/mis_pedidos.html')
        self.assertIn(pedido1, response.context['pedidos'])
    
    def test_mis_pedidos_sin_pedidos(self):
        """Test: Usuario sin pedidos"""
        self.client.login(username='test@example.com', password='testpass123')
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['pedidos']), 0)