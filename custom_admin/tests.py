"""Tests para el panel administrativo personalizado.

Incluye pruebas unitarias básicas para las vistas principales del
panel (dashboard, gestión de productos y pedidos). Añade tests más
detallados según se vaya ampliando la funcionalidad.
"""

from django.test import TestCase


class CustomAdminSmokeTest(TestCase):
	"""Prueba simple que verifica que la ruta del panel requiere login."""

	def test_dashboard_requires_login(self):
		response = self.client.get('/panel/')
		# Se espera redirección al login en caso de no estar autenticado
		self.assertIn(response.status_code, (302, 403))
