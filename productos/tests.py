"""
Tests adicionales para productos/views.py - VERSIÓN CORREGIDA
Complementa test_views_integration.py para alcanzar 95%+ de cobertura
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from productos.models import Producto, Categoria, Marca


class CatalogoBusquedaAvanzadaTest(TestCase):
    """Tests adicionales de búsqueda en catálogo"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('productos:catalogo')
        
        self.categoria = Categoria.objects.create(nombre="Test Categoria")
        self.marca = Marca.objects.create(nombre="Test Marca")
        
        self.producto = Producto.objects.create(
            nombre="Producto Especial",
            descripcion="Descripción única con palabras clave especiales",
            precio=Decimal("25.00"),
            categoria=self.categoria,
            marca=self.marca,
            genero='hombre',
            stock=10,
            esta_disponible=True
        )
    
    def test_busqueda_por_categoria_nombre_en_query(self):
        """Test: Búsqueda encuentra productos por nombre de categoría"""
        response = self.client.get(self.url, {'q': 'Test Categoria'})
        
        productos = list(response.context['productos'])
        self.assertIn(self.producto, productos)
    
    def test_busqueda_por_marca_nombre_en_query(self):
        """Test: Búsqueda encuentra productos por nombre de marca"""
        response = self.client.get(self.url, {'q': 'Test Marca'})
        
        productos = list(response.context['productos'])
        self.assertIn(self.producto, productos)
    
    def test_filtro_por_genero(self):
        """Test: Filtrar productos por género"""
        producto_mujer = Producto.objects.create(
            nombre="Producto Mujer",
            descripcion="Para mujer",
            precio=Decimal("20.00"),
            genero='mujer',
            stock=10,
            esta_disponible=True
        )
        
        response = self.client.get(self.url, {'genero': 'hombre'})
        
        productos = list(response.context['productos'])
        self.assertIn(self.producto, productos)
        self.assertNotIn(producto_mujer, productos)
    
    def test_filtros_categoria_y_marca_combinados(self):
        """Test: Combinar filtros de categoría y marca"""
        # Producto de otra categoría
        otra_categoria = Categoria.objects.create(nombre="Otra Categoria")
        producto_otra_cat = Producto.objects.create(
            nombre="Producto Otra Cat",
            descripcion="Descripción",
            precio=Decimal("15.00"),
            categoria=otra_categoria,
            marca=self.marca,
            stock=10,
            esta_disponible=True
        )
        
        response = self.client.get(self.url, {
            'categoria': self.categoria.id,
            'marca': self.marca.id
        })
        
        productos = list(response.context['productos'])
        self.assertIn(self.producto, productos)
        self.assertNotIn(producto_otra_cat, productos)
    
    def test_context_incluye_variables_seleccion(self):
        """Test: El contexto incluye las variables de selección"""
        response = self.client.get(self.url, {
            'categoria': self.categoria.id,
            'marca': self.marca.id
        })
        
        self.assertIn('categoria_seleccionada_id', response.context)
        self.assertIn('marca_seleccionada_id', response.context)
        self.assertEqual(response.context['categoria_seleccionada_id'], self.categoria.id)
        self.assertEqual(response.context['marca_seleccionada_id'], self.marca.id)
    
    def test_catalogo_con_parametros_invalidos_no_causa_error(self):
        """Test: Catálogo con parámetros inválidos no causa ValueError"""
        # Esta vista ya maneja esto con try/except
        response = self.client.get(self.url, {
            'categoria': '999999',  # ID que no existe
            'marca': '999999'
        })
        
        self.assertEqual(response.status_code, 200)
        # No debería filtrar nada con IDs inválidos
        self.assertIsNotNone(response.context['categoria_seleccionada_id'])


class CatalogoEdgeCasesTest(TestCase):
    """Tests de casos edge para el catálogo"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('productos:catalogo')
    
    def test_catalogo_sin_productos(self):
        """Test: Catálogo sin productos disponibles"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['productos']), 0)
    
    def test_busqueda_query_vacia(self):
        """Test: Búsqueda con query vacía"""
        producto = Producto.objects.create(
            nombre="Producto Test",
            descripcion="Descripción",
            precio=Decimal("10.00"),
            stock=10,
            esta_disponible=True
        )
        
        response = self.client.get(self.url, {'q': ''})
        
        # Query vacía no debe filtrar
        productos = list(response.context['productos'])
        self.assertIn(producto, productos)
    
    def test_categoria_sin_productos(self):
        """Test: Filtrar por categoría sin productos"""
        categoria_vacia = Categoria.objects.create(nombre="Categoría Vacía")
        
        response = self.client.get(self.url, {'categoria': categoria_vacia.id})
        
        self.assertEqual(len(response.context['productos']), 0)


class DetalleProductoEdgeCasesTest(TestCase):
    """Tests de casos edge para detalle de producto"""
    
    def setUp(self):
        self.client = Client()
        
        self.categoria = Categoria.objects.create(nombre="Test Categoria")
        
        self.producto = Producto.objects.create(
            nombre="Producto Principal",
            descripcion="Descripción principal",
            precio=Decimal("50.00"),
            categoria=self.categoria,
            stock=10,
            esta_disponible=True
        )
        
        self.url = reverse('productos:detalle', args=[self.producto.slug])
    
    def test_detalle_sin_productos_relacionados(self):
        """Test: Detalle sin productos relacionados"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['productos_relacionados']), 0)
    
    def test_detalle_productos_relacionados_maximo_4(self):
        """Test: Productos relacionados limitados a 4"""
        # Crear 10 productos relacionados
        for i in range(10):
            Producto.objects.create(
                nombre=f"Relacionado {i}",
                descripcion=f"Descripción {i}",
                precio=Decimal("20.00"),
                categoria=self.categoria,
                stock=10,
                esta_disponible=True
            )
        
        response = self.client.get(self.url)
        
        # Solo debe mostrar 4
        self.assertEqual(len(response.context['productos_relacionados']), 4)
    
    def test_detalle_productos_relacionados_excluye_actual(self):
        """Test: Productos relacionados no incluyen el producto actual"""
        # Crear productos relacionados
        for i in range(3):
            Producto.objects.create(
                nombre=f"Relacionado {i}",
                descripcion=f"Descripción {i}",
                precio=Decimal("20.00"),
                categoria=self.categoria,
                stock=10,
                esta_disponible=True
            )
        
        response = self.client.get(self.url)
        
        productos_relacionados = list(response.context['productos_relacionados'])
        self.assertNotIn(self.producto, productos_relacionados)
    
    def test_detalle_productos_relacionados_solo_disponibles(self):
        """Test: Productos relacionados solo muestra disponibles"""
        disponible = Producto.objects.create(
            nombre="Disponible",
            descripcion="Descripción",
            precio=Decimal("20.00"),
            categoria=self.categoria,
            stock=10,
            esta_disponible=True
        )
        
        no_disponible = Producto.objects.create(
            nombre="No Disponible",
            descripcion="Descripción",
            precio=Decimal("20.00"),
            categoria=self.categoria,
            stock=0,
            esta_disponible=False
        )
        
        response = self.client.get(self.url)
        
        productos_relacionados = list(response.context['productos_relacionados'])
        self.assertIn(disponible, productos_relacionados)
        self.assertNotIn(no_disponible, productos_relacionados)
    
    def test_detalle_slug_con_caracteres_especiales(self):
        """Test: Slug con caracteres especiales"""
        producto_especial = Producto.objects.create(
            nombre="Producto con Ñ y Acentós",
            descripcion="Descripción",
            precio=Decimal("25.00"),
            stock=10,
            esta_disponible=True
        )
        
        url = reverse('productos:detalle', args=[producto_especial.slug])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['producto'], producto_especial)