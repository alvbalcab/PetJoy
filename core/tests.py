"""Casos de prueba unitarios para la app `core`.

Incluye pruebas básicas para comprobar que las páginas estáticas y las
utilidades del paquete funcionan correctamente. Añade aquí pruebas más
detalladas según la lógica de negocio ande sea necesario.
"""

from django.test import TestCase


class CoreSmokeTests(TestCase):
	"""Pruebas sencillas que verifican la disponibilidad de páginas clave."""

	def test_homepage_loads(self):
		response = self.client.get('/')
		self.assertIn(response.status_code, (200, 302))

