from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from productos.models import Producto, Categoria, Marca


class ProductoViewsIntegrationTest(TestCase):
    """Tests de integración para las vistas de productos"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        
        # Crear categorías
        self.categoria_perros = Categoria.objects.create(
            nombre="Juguetes para Perros",
            descripcion="Juguetes para perros"
        )
        self.categoria_gatos = Categoria.objects.create(
            nombre="Juguetes para Gatos",
            descripcion="Juguetes para gatos"
        )
        
        # Crear marcas
        self.marca_kong = Marca.objects.create(nombre="Kong")
        self.marca_petjoy = Marca.objects.create(nombre="PetJoy")
        
        # Crear productos
        self.producto1 = Producto.objects.create(
            nombre="Pelota Kong Classic",
            descripcion="Pelota resistente para perros de caucho natural",
            precio=Decimal("19.99"),
            marca=self.marca_kong,
            categoria=self.categoria_perros,
            stock=50,
            esta_disponible=True,
            es_destacado=True
        )
        
        self.producto2 = Producto.objects.create(
            nombre="Ratón de Juguete",
            descripcion="Ratón de juguete para gatos",
            precio=Decimal("5.99"),
            precio_oferta=Decimal("3.99"),
            marca=self.marca_petjoy,
            categoria=self.categoria_gatos,
            stock=100,
            esta_disponible=True
        )
        
        self.producto3 = Producto.objects.create(
            nombre="Cuerda Trenzada",
            descripcion="Cuerda trenzada XXL para perros grandes",
            precio=Decimal("12.99"),
            marca=self.marca_kong,
            categoria=self.categoria_perros,
            stock=30,
            esta_disponible=True
        )
        
        # Producto no disponible
        self.producto_no_disponible = Producto.objects.create(
            nombre="Producto Agotado",
            descripcion="Este producto no está disponible",
            precio=Decimal("9.99"),
            stock=0,
            esta_disponible=False
        )
    
    def test_catalogo_productos_vista(self):
        """Test: Verificar que la vista de catálogo funciona"""
        response = self.client.get(reverse('productos:catalogo'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'productos/catalogo.html')
        self.assertIn('productos', response.context)
        self.assertIn('categorias', response.context)
        self.assertIn('marcas', response.context)
    
    def test_catalogo_muestra_solo_productos_disponibles(self):
        """Test: El catálogo solo debe mostrar productos disponibles"""
        response = self.client.get(reverse('productos:catalogo'))
        productos = response.context['productos']
        
        self.assertEqual(len(productos), 3)
        self.assertNotIn(self.producto_no_disponible, productos)
    
    def test_catalogo_filtro_por_categoria(self):
        """Test: Filtrar productos por categoría"""
        response = self.client.get(
            reverse('productos:catalogo'),
            {'categoria': self.categoria_perros.id}
        )
        
        productos = response.context['productos']
        self.assertEqual(len(productos), 2)
        for producto in productos:
            self.assertEqual(producto.categoria, self.categoria_perros)
    
    def test_catalogo_filtro_por_marca(self):
        """Test: Filtrar productos por marca"""
        response = self.client.get(
            reverse('productos:catalogo'),
            {'marca': self.marca_kong.id}
        )
        
        productos = response.context['productos']
        self.assertEqual(len(productos), 2)
        for producto in productos:
            self.assertEqual(producto.marca, self.marca_kong)
    
    def test_catalogo_busqueda_por_nombre(self):
        """Test: Buscar productos por nombre"""
        response = self.client.get(
            reverse('productos:catalogo'),
            {'q': 'Kong'}
        )
        
        productos = list(response.context['productos'])
        self.assertGreaterEqual(len(productos), 1)
        self.assertIn(self.producto1, productos)
    
    def test_catalogo_busqueda_por_descripcion(self):
        """Test: Buscar productos por descripción"""
        response = self.client.get(
            reverse('productos:catalogo'),
            {'q': 'resistente'}
        )
        
        productos = list(response.context['productos'])
        self.assertIn(self.producto1, productos)
    
    def test_catalogo_paginacion(self):
        """Test: Verificar la paginación del catálogo"""
        # Crear 15 productos adicionales para probar paginación
        for i in range(15):
            Producto.objects.create(
                nombre=f"Producto {i}",
                descripcion=f"Descripción {i}",
                precio=Decimal("10.00"),
                stock=10,
                esta_disponible=True
            )
        
        response = self.client.get(reverse('productos:catalogo'))
        self.assertTrue(response.context['productos'].has_other_pages())
        self.assertEqual(len(response.context['productos']), 12)
    
    def test_detalle_producto_vista(self):
        """Test: Verificar que la vista de detalle de producto funciona"""
        response = self.client.get(
            reverse('productos:detalle', args=[self.producto1.slug])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'productos/detalle.html')
        self.assertEqual(response.context['producto'], self.producto1)
    
    def test_detalle_producto_muestra_productos_relacionados(self):
        """Test: La vista de detalle muestra productos relacionados"""
        response = self.client.get(
            reverse('productos:detalle', args=[self.producto1.slug])
        )
        
        productos_relacionados = response.context['productos_relacionados']
        self.assertIn(self.producto3, productos_relacionados)
        self.assertNotIn(self.producto1, productos_relacionados)
        self.assertNotIn(self.producto2, productos_relacionados)
    
    def test_detalle_producto_no_disponible_404(self):
        """Test: Producto no disponible debe devolver 404"""
        response = self.client.get(
            reverse('productos:detalle', args=[self.producto_no_disponible.slug])
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_detalle_producto_inexistente_404(self):
        """Test: Producto inexistente debe devolver 404"""
        response = self.client.get(
            reverse('productos:detalle', args=['producto-que-no-existe'])
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_catalogo_filtros_multiples(self):
        """Test: Aplicar múltiples filtros simultáneamente"""
        response = self.client.get(
            reverse('productos:catalogo'),
            {
                'categoria': self.categoria_perros.id,
                'marca': self.marca_kong.id,
                'q': 'Pelota'
            }
        )
        
        productos = list(response.context['productos'])
        self.assertEqual(len(productos), 1)
        self.assertEqual(productos[0], self.producto1)
    
    def test_catalogo_sin_resultados(self):
        """Test: Búsqueda sin resultados"""
        response = self.client.get(
            reverse('productos:catalogo'),
            {'q': 'ProductoQueNoExiste123'}
        )
        
        productos = response.context['productos']
        self.assertEqual(len(productos), 0)
    
    def test_productos_destacados_en_catalogo(self):
        """Test: Los productos destacados están marcados correctamente"""
        response = self.client.get(reverse('productos:catalogo'))
        productos = list(response.context['productos'])
        
        producto_destacado = next(p for p in productos if p.id == self.producto1.id)
        self.assertTrue(producto_destacado.es_destacado)


class ProductoPreciosIntegrationTest(TestCase):
    """Tests de integración para precios y ofertas de productos"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        
        self.producto_con_oferta = Producto.objects.create(
            nombre="Producto con Oferta",
            descripcion="Producto en oferta",
            precio=Decimal("100.00"),
            precio_oferta=Decimal("75.00"),
            stock=10,
            esta_disponible=True
        )
        
        self.producto_sin_oferta = Producto.objects.create(
            nombre="Producto sin Oferta",
            descripcion="Producto a precio normal",
            precio=Decimal("50.00"),
            stock=10,
            esta_disponible=True
        )
    
    def test_precio_actual_mostrado_correctamente(self):
        """Test: El precio actual se muestra correctamente en el catálogo"""
        response = self.client.get(reverse('productos:catalogo'))
        
        productos = {p.id: p for p in response.context['productos']}
        producto_oferta = productos[self.producto_con_oferta.id]
        
        self.assertEqual(producto_oferta.precio_actual(), Decimal("75.00"))
    
    def test_descuento_calculado_correctamente(self):
        """Test: El descuento se calcula correctamente"""
        response = self.client.get(
            reverse('productos:detalle', args=[self.producto_con_oferta.slug])
        )
        
        producto = response.context['producto']
        self.assertEqual(producto.descuento_porcentaje(), 25)
    
    def test_oferta_mostrada_en_detalle(self):
        """Test: La oferta se muestra en la vista de detalle"""
        response = self.client.get(
            reverse('productos:detalle', args=[self.producto_con_oferta.slug])
        )
        
        producto = response.context['producto']
        self.assertTrue(producto.tiene_oferta())
        self.assertEqual(producto.precio_oferta, Decimal("75.00"))
