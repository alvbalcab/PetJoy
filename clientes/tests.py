"""Casos de prueba para la app `clientes`.

Incluye pruebas básicas que pueden ampliarse para cubrir registro,
autenticación y edición de perfil.
"""

from django.test import TestCase


class ClientesSmokeTest(TestCase):
    """Prueba simple que verifica que la página de registro carga."""

    def test_registro_page_loads(self):
        response = self.client.get('/cuenta/registro/')
        self.assertIn(response.status_code, (200, 302))
