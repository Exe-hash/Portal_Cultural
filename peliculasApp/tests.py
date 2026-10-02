from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import CategoriaPelicula, Pelicula, ReservaPelicula


class PeliculasModeloYVistasTest(TestCase):
    def test_migracion_json_crea_catalogo_y_relaciones(self):
        self.assertEqual(Pelicula.objects.count(), 6)
        self.assertEqual(CategoriaPelicula.objects.count(), 5)
        pelicula = Pelicula.objects.get(titulo="Código Abierto")
        self.assertEqual(pelicula.categoria.nombre, "Ciencia Ficción")

    def test_listado_busca_con_orm(self):
        respuesta = self.client.get(reverse("listado_peliculas"), {"q": "Marina"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["total"], 2)

    def test_detalle_inexistente_devuelve_404(self):
        respuesta = self.client.get(reverse("detalle_pelicula", args=["no-existe"]))
        self.assertEqual(respuesta.status_code, 404)

    def test_modelos_estan_registrados_en_admin(self):
        self.assertIn(CategoriaPelicula, admin.site._registry)
        self.assertIn(Pelicula, admin.site._registry)
        self.assertIn(ReservaPelicula, admin.site._registry)

    def test_administrador_ve_controles_crud_en_listado(self):
        administrador = User.objects.create_user(
            "adminpeliculas", password="ClaveSegura123!", is_staff=True
        )
        self.client.force_login(administrador)
        respuesta = self.client.get(reverse("listado_peliculas"))
        self.assertContains(respuesta, "Agregar película")
        self.assertContains(respuesta, "Modificar")
        self.assertContains(respuesta, "Eliminar")

    def test_reserva_requiere_sesion(self):
        pelicula = Pelicula.objects.first()
        respuesta = self.client.get(reverse("reservar_pelicula", args=[pelicula.slug]))
        self.assertRedirects(
            respuesta,
            f"{reverse('login')}?next={reverse('reservar_pelicula', args=[pelicula.slug])}",
        )

    def test_usuario_puede_reservar_pelicula(self):
        usuario = User.objects.create_user("ana", password="ClaveSegura123!")
        pelicula = Pelicula.objects.first()
        self.client.force_login(usuario)
        fecha = timezone.localtime(timezone.now() + timedelta(days=2)).strftime(
            "%Y-%m-%dT%H:%M"
        )
        respuesta = self.client.post(
            reverse("reservar_pelicula", args=[pelicula.slug]),
            {"fecha_funcion": fecha, "cantidad_entradas": 2, "observaciones": ""},
        )
        self.assertRedirects(respuesta, reverse("mis_reservas"))
        self.assertTrue(
            ReservaPelicula.objects.filter(usuario=usuario, pelicula=pelicula).exists()
        )
