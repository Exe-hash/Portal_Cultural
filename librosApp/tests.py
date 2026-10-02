from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Autor, CategoriaLibro, Libro, ReservaLibro


class LibrosModeloYVistasTest(TestCase):
    def test_migracion_json_crea_catalogo_y_relaciones(self):
        self.assertEqual(Libro.objects.count(), 6)
        self.assertEqual(Autor.objects.count(), 5)
        self.assertEqual(CategoriaLibro.objects.count(), 5)
        libro = Libro.objects.get(titulo="Manual del Programador Curioso")
        self.assertEqual(libro.autor.nombre, "Rodrigo Ortiz")
        self.assertEqual(libro.categoria.nombre, "Tecnología")

    def test_listado_busca_con_orm(self):
        respuesta = self.client.get(reverse("listado_libros"), {"q": "Rodrigo"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["total"], 2)

    def test_detalle_inexistente_devuelve_404(self):
        respuesta = self.client.get(reverse("detalle_libro", args=["no-existe"]))
        self.assertEqual(respuesta.status_code, 404)

    def test_modelos_estan_registrados_en_admin(self):
        self.assertIn(Autor, admin.site._registry)
        self.assertIn(CategoriaLibro, admin.site._registry)
        self.assertIn(Libro, admin.site._registry)
        self.assertIn(ReservaLibro, admin.site._registry)

    def test_administrador_ve_controles_crud_en_listado(self):
        administrador = User.objects.create_user(
            "adminlibros", password="ClaveSegura123!", is_staff=True
        )
        self.client.force_login(administrador)
        respuesta = self.client.get(reverse("listado_libros"))
        self.assertContains(respuesta, "Agregar libro")
        self.assertContains(respuesta, "Modificar")
        self.assertContains(respuesta, "Eliminar")

    def test_usuario_puede_reservar_libro_disponible(self):
        usuario = User.objects.create_user("luis", password="ClaveSegura123!")
        libro = Libro.objects.filter(disponible=True).first()
        self.client.force_login(usuario)
        retiro = timezone.localdate() + timedelta(days=1)
        respuesta = self.client.post(
            reverse("reservar_libro", args=[libro.slug]),
            {
                "fecha_retiro": retiro.isoformat(),
                "fecha_devolucion_prevista": (retiro + timedelta(days=7)).isoformat(),
                "observaciones": "",
            },
        )
        self.assertRedirects(respuesta, reverse("mis_reservas"))
        self.assertTrue(
            ReservaLibro.objects.filter(usuario=usuario, libro=libro).exists()
        )
        libro.refresh_from_db()
        self.assertFalse(libro.disponible)
