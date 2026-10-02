from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AutenticacionTest(TestCase):
    def test_usuario_puede_registrarse_e_inicia_sesion(self):
        respuesta = self.client.post(
            reverse("registro"),
            {
                "username": "maria",
                "first_name": "María",
                "last_name": "Rojas",
                "email": "maria@example.com",
                "password1": "ClaveSegura123!",
                "password2": "ClaveSegura123!",
            },
        )
        self.assertRedirects(respuesta, reverse("principal"))
        self.assertTrue(User.objects.filter(username="maria").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_mis_reservas_requiere_sesion(self):
        respuesta = self.client.get(reverse("mis_reservas"))
        self.assertRedirects(
            respuesta, f"{reverse('login')}?next={reverse('mis_reservas')}"
        )
