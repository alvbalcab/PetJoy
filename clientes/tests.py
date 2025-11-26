
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from clientes.forms import RegistroForm, LoginForm, PerfilForm
from clientes.models import Cliente

User = get_user_model()


class RegistroFormTest(TestCase):
    """Tests para RegistroForm - Cubre clientes/forms.py"""
    
    def test_registro_form_campos_requeridos(self):
        """Test: Verificar que los campos requeridos están presentes"""
        form = RegistroForm()
        self.assertIn('email', form.fields)
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('direccion', form.fields)
        self.assertIn('ciudad', form.fields)
        self.assertIn('codigo_postal', form.fields)
        self.assertIn('password1', form.fields)
        self.assertIn('password2', form.fields)
    
    def test_registro_form_telefono_opcional(self):
        """Test: El teléfono no es requerido"""
        form = RegistroForm()
        self.assertFalse(form.fields['telefono'].required)
    
    def test_registro_form_valido(self):
        """Test: Formulario válido con todos los datos"""
        form_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        form = RegistroForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_registro_form_sin_telefono(self):
        """Test: Formulario válido sin teléfono"""
        form_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        form = RegistroForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_registro_form_passwords_no_coinciden(self):
        """Test: Formulario inválido si las contraseñas no coinciden"""
        form_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
            'password1': 'testpass123',
            'password2': 'differentpass',
        }
        form = RegistroForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_registro_form_save_usa_email_como_username(self):
        """Test: El método save usa el email como username"""
        form_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'telefono': '123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        form = RegistroForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        
        self.assertEqual(user.username, 'test@example.com')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.telefono, '123456789')
        self.assertEqual(user.direccion, 'Calle Test 123')
    
    def test_registro_form_save_sin_commit(self):
        """Test: El método save funciona con commit=False"""
        form_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'direccion': 'Calle Test 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        form = RegistroForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        
        # El usuario no debe estar en la BD aún
        self.assertIsNone(user.pk)
        self.assertEqual(user.username, 'test@example.com')


class LoginFormTest(TestCase):
    """Tests para LoginForm"""
    
    def test_login_form_campos(self):
        """Test: Verificar que los campos están presentes"""
        form = LoginForm()
        self.assertIn('email', form.fields)
        self.assertIn('password', form.fields)
    
    def test_login_form_valido(self):
        """Test: Formulario válido con email y password"""
        form_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_login_form_email_invalido(self):
        """Test: Formulario inválido con email mal formado"""
        form_data = {
            'email': 'not-an-email',
            'password': 'testpass123',
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())


class PerfilFormTest(TestCase):
    """Tests para PerfilForm"""
    
    def test_perfil_form_campos(self):
        """Test: Verificar que los campos están presentes"""
        form = PerfilForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('email', form.fields)
        self.assertIn('telefono', form.fields)
        self.assertIn('direccion', form.fields)
        self.assertIn('ciudad', form.fields)
        self.assertIn('codigo_postal', form.fields)
    
    def test_perfil_form_valido(self):
        """Test: Formulario válido con todos los datos"""
        user = Cliente.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'telefono': '987654321',
            'direccion': 'Nueva Calle 456',
            'ciudad': 'Madrid',
            'codigo_postal': '28001',
        }
        form = PerfilForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())


class RegistroViewTest(TestCase):
    """Tests para la vista de registro - Cubre clientes/views.py"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('clientes:registro')
    
    def test_registro_view_get(self):
        """Test: Acceder a la página de registro (GET)"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/registro.html')
        self.assertIsInstance(response.context['form'], RegistroForm)
    
    def test_registro_view_post_valido(self):
        """Test: Registro exitoso con datos válidos"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'telefono': '123456789',
            'direccion': 'Calle Nueva 123',
            'ciudad': 'Sevilla',
            'codigo_postal': '41001',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        response = self.client.post(self.url, data=form_data)
        
        # Debe redirigir a inicio
        self.assertRedirects(response, reverse('core:inicio'))
        
        # Usuario debe estar creado
        user = Cliente.objects.get(email='newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.username, 'newuser@example.com')
        
        # Usuario debe estar logueado
        self.assertTrue(user.is_authenticated)
    
    def test_registro_view_post_invalido(self):
        """Test: Registro con datos inválidos"""
        form_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'testpass123',
            'password2': 'differentpass',  # Contraseñas no coinciden
        }
        response = self.client.post(self.url, data=form_data)
        
        # No debe redirigir, debe mostrar el formulario con errores
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/registro.html')
        self.assertFalse(Cliente.objects.filter(email='newuser@example.com').exists())
    
    def test_registro_view_usuario_autenticado_redirige(self):
        """Test: Usuario autenticado no puede acceder al registro"""
        user = Cliente.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='testpass123'
        )
        self.client.login(username='existing@example.com', password='testpass123')
        
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('core:inicio'))


class LoginViewTest(TestCase):
    """Tests para la vista de login"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('clientes:login')
        self.user = Cliente.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            first_name='Test'
        )
    
    def test_login_view_get(self):
        """Test: Acceder a la página de login (GET)"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/login.html')
        self.assertIsInstance(response.context['form'], LoginForm)
    
    def test_login_view_post_credenciales_validas(self):
        """Test: Login exitoso con credenciales válidas"""
        form_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        response = self.client.post(self.url, data=form_data)
        
        # Debe redirigir a inicio
        self.assertRedirects(response, reverse('core:inicio'))
        
        # Usuario debe estar logueado
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_view_post_credenciales_invalidas(self):
        """Test: Login fallido con contraseña incorrecta"""
        form_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword',
        }
        response = self.client.post(self.url, data=form_data)
        
        # No debe redirigir
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/login.html')
        
        # Usuario no debe estar logueado
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_login_view_post_email_no_existe(self):
        """Test: Login fallido con email que no existe"""
        form_data = {
            'email': 'noexiste@example.com',
            'password': 'testpass123',
        }
        response = self.client.post(self.url, data=form_data)
        
        # No debe redirigir
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_login_view_con_parametro_next(self):
        """Test: Redirigir a URL 'next' después del login"""
        form_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        response = self.client.post(self.url + '?next=/pedidos/mis-pedidos/', data=form_data)
        
        # Debe redirigir a la URL next
        self.assertRedirects(response, '/pedidos/mis-pedidos/')
    
    def test_login_view_usuario_autenticado_redirige(self):
        """Test: Usuario autenticado no puede acceder al login"""
        self.client.login(username='test@example.com', password='testpass123')
        
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('core:inicio'))
    
    def test_login_view_formulario_invalido(self):
        """Test: Login con formulario inválido"""
        form_data = {
            'email': 'not-an-email',
            'password': 'testpass123',
        }
        response = self.client.post(self.url, data=form_data)
        
        # No debe redirigir
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class LogoutViewTest(TestCase):
    """Tests para la vista de logout"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('clientes:logout')
        self.user = Cliente.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_logout_view(self):
        """Test: Logout cierra la sesión correctamente"""
        # Primero hacer login
        self.client.login(username='test@example.com', password='testpass123')
        
        # Hacer logout
        response = self.client.get(self.url)
        
        # Debe redirigir a inicio
        self.assertRedirects(response, reverse('core:inicio'))
        
        # Usuario no debe estar autenticado
        response = self.client.get(reverse('core:inicio'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class PerfilViewTest(TestCase):
    """Tests para la vista de perfil"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('clientes:perfil')
        self.user = Cliente.objects.create_user(
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
    
    def test_perfil_view_requiere_login(self):
        """Test: Vista de perfil requiere autenticación"""
        response = self.client.get(self.url)
        
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_perfil_view_get(self):
        """Test: Acceder a la página de perfil (GET)"""
        self.client.login(username='test@example.com', password='testpass123')
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/perfil.html')
        self.assertIsInstance(response.context['form'], PerfilForm)
        
        # Verificar que el formulario tiene los datos del usuario
        form = response.context['form']
        self.assertEqual(form.initial['first_name'], 'Test')
        self.assertEqual(form.initial['email'], 'test@example.com')
    
    def test_perfil_view_post_actualiza_datos(self):
        """Test: Actualizar perfil con datos válidos"""
        self.client.login(username='test@example.com', password='testpass123')
        
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'test@example.com',
            'telefono': '987654321',
            'direccion': 'Nueva Calle 456',
            'ciudad': 'Madrid',
            'codigo_postal': '28001',
        }
        response = self.client.post(self.url, data=form_data)
        
        # Debe redirigir al perfil
        self.assertRedirects(response, self.url)
        
        # Verificar que los datos se actualizaron
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.telefono, '987654321')
        self.assertEqual(self.user.direccion, 'Nueva Calle 456')
        self.assertEqual(self.user.ciudad, 'Madrid')
    
    def test_perfil_view_post_datos_invalidos(self):
        """Test: Intentar actualizar perfil con datos inválidos"""
        self.client.login(username='test@example.com', password='testpass123')
        
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'not-a-valid-email',  # Email inválido
            'telefono': '987654321',
            'direccion': 'Nueva Calle 456',
            'ciudad': 'Madrid',
            'codigo_postal': '28001',
        }
        response = self.client.post(self.url, data=form_data)
        
        # No debe redirigir, debe mostrar el formulario con errores
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clientes/perfil.html')
        
        # Los datos no deben haberse actualizado
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')  # Datos originales


class ClienteModelTest(TestCase):
    """Tests adicionales para el modelo Cliente"""
    
    def test_nombre_completo_con_nombre_y_apellido(self):
        """Test: nombre_completo retorna nombre y apellido"""
        user = Cliente.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.nombre_completo(), 'Test User')
    
    def test_nombre_completo_sin_nombre(self):
        """Test: nombre_completo retorna username si no hay nombre"""
        user = Cliente.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.nombre_completo(), 'test@example.com')
    
    def test_nombre_completo_solo_nombre(self):
        """Test: nombre_completo retorna solo nombre si no hay apellido"""
        user = Cliente.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123',
            first_name='Test'
        )
        self.assertEqual(user.nombre_completo(), 'Test')