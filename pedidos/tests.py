"""Pruebas unitarias para la app `pedidos`.

Agrega casos que verifiquen la lógica del carrito, creación de pedidos,
actualización de stock y generación de emails de confirmación.
"""

from django.test import TestCase


class PedidosSmokeTest(TestCase):
	"""Prueba sencilla para comprobar que la vista del carrito carga."""

	def test_carrito_view_loads(self):
		response = self.client.get('/pedidos/carrito/')
		self.assertIn(response.status_code, (200, 302))
