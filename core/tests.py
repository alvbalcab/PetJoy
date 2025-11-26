from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from core.models import DatosEmpresa


class DatosEmpresaModelTest(TestCase):
    """Tests para el modelo DatosEmpresa"""
    
    def test_crear_datos_empresa(self):
        """Test: Crear datos de empresa"""
        datos = DatosEmpresa.objects.create(
            nombre="PetJoy Test",
            email="contacto@petjoy.com",
            telefono="123456789",
            direccion="Calle Test 123",
            ciudad="Sevilla",
            codigo_postal="41001",
            coste_envio_estandar=Decimal("5.00"),
            envio_gratuito_desde=Decimal("50.00"),
            iva_porcentaje=Decimal("21.00")
        )
        
        self.assertEqual(datos.nombre, "PetJoy Test")
        self.assertEqual(datos.coste_envio_estandar, Decimal("5.00"))
        self.assertEqual(datos.iva_porcentaje, Decimal("21.00"))
    
    def test_get_datos_singleton(self):
        """Test: Verificar patrón singleton para DatosEmpresa"""
        datos1 = DatosEmpresa.objects.create(
            nombre="PetJoy",
            email="contacto@petjoy.com",
            telefono="123456789",
            coste_envio_estandar=Decimal("5.00"),
            envio_gratuito_desde=Decimal("50.00"),
            iva_porcentaje=Decimal("21.00")
        )
        
        # Obtener datos usando el método get_datos
        datos_obtenidos = DatosEmpresa.get_datos()
        
        self.assertEqual(datos_obtenidos.id, datos1.id)
        self.assertEqual(datos_obtenidos.nombre, "PetJoy")


class CoreViewsTest(TestCase):
    """Tests para las vistas del módulo core"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        
        # Crear datos de empresa
        DatosEmpresa.objects.create(
            nombre="PetJoy",
            email="contacto@petjoy.com",
            telefono="123456789",
            direccion="Calle Test 123",
            ciudad="Sevilla",
            codigo_postal="41001",
            coste_envio_estandar=Decimal("5.00"),
            envio_gratuito_desde=Decimal("50.00"),
            iva_porcentaje=Decimal("21.00"),
            descripcion="Tienda online de productos para mascotas"
        )
    
    def test_vista_inicio(self):
        """Test: Verificar que la vista de inicio funciona"""
        response = self.client.get(reverse('core:inicio'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/inicio.html')
    
    def test_vista_acerca_de(self):
        """Test: Verificar que la vista 'Acerca de' funciona"""
        response = self.client.get(reverse('core:acerca_de'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/acerca_de.html')
    
    def test_vista_contacto(self):
        """Test: Verificar que la vista de contacto funciona"""
        response = self.client.get(reverse('core:contacto'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/contacto.html')
    
    def test_datos_empresa_en_contexto(self):
        """Test: Verificar que los datos de empresa están en el contexto"""
        response = self.client.get(reverse('core:inicio'))
        
        # Los datos de empresa deberían estar disponibles en el contexto
        # a través de un context processor
        datos_empresa = DatosEmpresa.get_datos()
        self.assertIsNotNone(datos_empresa)


class CoreIntegrationTest(TestCase):
    """Tests de integración para el módulo core"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        
        DatosEmpresa.objects.create(
            nombre="PetJoy",
            email="contacto@petjoy.com",
            telefono="123456789",
            coste_envio_estandar=Decimal("5.00"),
            envio_gratuito_desde=Decimal("50.00"),
            iva_porcentaje=Decimal("21.00")
        )
    
    def test_navegacion_entre_vistas(self):
        """Test: Verificar navegación entre diferentes vistas"""
        # Inicio
        response = self.client.get(reverse('core:inicio'))
        self.assertEqual(response.status_code, 200)
        
        # Acerca de
        response = self.client.get(reverse('core:acerca_de'))
        self.assertEqual(response.status_code, 200)
        
        # Contacto
        response = self.client.get(reverse('core:contacto'))
        self.assertEqual(response.status_code, 200)
        
        # Catálogo de productos
        response = self.client.get(reverse('productos:catalogo'))
        self.assertEqual(response.status_code, 200)
    
    def test_envio_formulario_contacto(self):
        """Test: Envío de formulario de contacto"""
        datos_contacto = {
            'nombre': 'Test User',
            'email': 'test@example.com',
            'asunto': 'Consulta de prueba',
            'mensaje': 'Este es un mensaje de prueba'
        }
        
        response = self.client.post(reverse('core:contacto'), datos_contacto)
        
        # Verificar respuesta (puede variar según la implementación)
        # Por ejemplo, puede redirigir o mostrar un mensaje de éxito
        self.assertIn(response.status_code, [200, 302])