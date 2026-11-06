import re
from datetime import timedelta
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from librosApp.models import Autor, CategoriaLibro, Libro, ReservaLibro
from peliculasApp.models import CategoriaPelicula, Pelicula, ReservaPelicula

from .perfiles import ADMINISTRADOR, ADMINISTRATIVO, SUPERVISOR


class GestionPortalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = cls.crear_cuenta("gestion", ADMINISTRADOR)
        cls.supervisor = cls.crear_cuenta("supervision", SUPERVISOR)
        cls.administrativo = cls.crear_cuenta("operaciones", ADMINISTRATIVO)
        cls.visitante = cls.crear_cuenta("lector")

    @staticmethod
    def crear_cuenta(username, perfil=None):
        cuenta = User.objects.create_user(username, password="ClavePortal-42-segura")
        if perfil:
            cuenta.groups.add(Group.objects.get(name=perfil))
        return cuenta

    def test_login_redirige_al_panel_y_logout_es_post(self):
        respuesta = self.client.post(reverse("login"), {
            "username": self.supervisor.username, "password": "ClavePortal-42-segura",
        }, follow=True)
        self.assertContains(respuesta, "Panel Supervisor")
        self.assertTrue(self.client.session.get_expire_at_browser_close())
        self.assertEqual(self.client.cookies[settings.SESSION_COOKIE_NAME]["expires"], "")
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("logout")), reverse("principal"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertRedirects(self.client.get(reverse("gestion:panel")), reverse("login") + "?next=/gestion/")

    def test_perfiles_tienen_panel_y_permisos_distintos(self):
        libro = Libro.objects.first()
        rutas = [
            reverse("gestion:libros_crear"),
            reverse("gestion:libros_editar", args=[libro.pk]),
            reverse("gestion:libros_eliminar", args=[libro.pk]),
            reverse("gestion:reservas"),
            reverse("gestion:usuarios"),
        ]
        self.assertEqual(self.client.get(rutas[0]).status_code, 302)
        for cuenta, perfil, esperados in (
            (self.admin, ADMINISTRADOR, (200, 200, 200, 200, 200)),
            (self.supervisor, SUPERVISOR, (200, 200, 403, 200, 403)),
            (self.administrativo, ADMINISTRATIVO, (403, 403, 403, 403, 403)),
        ):
            with self.subTest(perfil=perfil):
                self.client.force_login(cuenta)
                self.assertContains(self.client.get(reverse("gestion:panel")), f"Panel {perfil}")
                self.assertEqual(self.client.get(reverse("gestion:libros")).status_code, 200)
                for ruta, esperado in zip(rutas, esperados):
                    self.assertEqual(self.client.get(ruta).status_code, esperado, ruta)
                if perfil != ADMINISTRADOR:
                    self.assertEqual(self.client.post(rutas[2]).status_code, 403)
        self.assertTrue(Libro.objects.filter(pk=libro.pk).exists())
        self.client.force_login(self.visitante)
        self.assertRedirects(self.client.get(reverse("gestion:panel")), reverse("principal"))
        self.assertEqual(self.client.get(reverse("gestion:libros")).status_code, 403)
        self.assertEqual(self.client.get("/admin/").status_code, 404)

    def test_administrador_crea_usuario_y_cambia_su_perfil(self):
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse("gestion:usuarios_crear")), "Sin perfil asignado")
        crear = self.client.post(reverse("gestion:usuarios_crear"), {
            "username": "demo_supervisor", "first_name": "Cuenta", "last_name": "Demostración",
            "email": "cuenta@example.com", "password1": "secreto-demo-2984!",
            "password2": "secreto-demo-2984!", "perfil": SUPERVISOR, "is_superuser": "1",
        })
        self.assertRedirects(crear, reverse("gestion:usuarios"))
        usuario = User.objects.get(username="demo_supervisor")
        self.assertEqual(list(usuario.groups.values_list("name", flat=True)), [SUPERVISOR])
        self.assertTrue(usuario.check_password("secreto-demo-2984!"))
        self.assertFalse(usuario.is_superuser)

        editar = self.client.post(reverse("gestion:usuarios_editar", args=[usuario.pk]), {
            "first_name": "Cuenta", "last_name": "Demostración", "email": usuario.email,
            "is_active": "on", "perfil": ADMINISTRATIVO,
        })
        self.assertRedirects(editar, reverse("gestion:usuarios"))
        self.assertEqual(list(usuario.groups.values_list("name", flat=True)), [ADMINISTRATIVO])
        self.assertEqual(self.client.get(reverse("gestion:usuarios_editar", args=[self.admin.pk])).status_code, 403)

        crear_sin_perfil = self.client.post(reverse("gestion:usuarios_crear"), {
            "username": "cuenta_sin_perfil", "first_name": "Cuenta", "last_name": "Sin perfil",
            "email": "sin-perfil@example.com", "password1": "secreto-demo-2984!",
            "password2": "secreto-demo-2984!", "perfil": "",
        })
        self.assertRedirects(crear_sin_perfil, reverse("gestion:usuarios"))
        cuenta_sin_perfil = User.objects.get(username="cuenta_sin_perfil")
        self.assertFalse(cuenta_sin_perfil.groups.filter(name__in=(ADMINISTRADOR, SUPERVISOR, ADMINISTRATIVO)).exists())

    def test_administrador_elimina_usuario_sin_reservas(self):
        self.client.force_login(self.admin)
        cuenta = User.objects.create_user("cuenta_eliminable", password="ClavePortal-42-segura")
        ruta = reverse("gestion:usuarios_eliminar", args=[cuenta.pk])
        self.assertContains(self.client.get(ruta), "Confirmar eliminación")
        self.assertRedirects(self.client.post(ruta), reverse("gestion:usuarios"))
        self.assertFalse(User.objects.filter(pk=cuenta.pk).exists())
        self.assertEqual(
            self.client.get(reverse("gestion:usuarios_eliminar", args=[self.admin.pk])).status_code,
            403,
        )

    def test_administrador_no_elimina_usuario_con_reservas(self):
        cuenta = User.objects.create_user("cuenta_con_historial", password="ClavePortal-42-segura")
        retiro = timezone.localdate() + timedelta(days=1)
        ReservaLibro.objects.create(
            usuario=cuenta,
            libro=Libro.objects.filter(disponible=True).first(),
            fecha_retiro=retiro,
            fecha_devolucion_prevista=retiro + timedelta(days=5),
        )
        self.client.force_login(self.admin)
        respuesta = self.client.post(
            reverse("gestion:usuarios_eliminar", args=[cuenta.pk]),
            follow=True,
        )
        self.assertContains(respuesta, "No se puede eliminar esta cuenta porque tiene reservas asociadas")
        self.assertTrue(User.objects.filter(pk=cuenta.pk).exists())

    def test_crud_libros_y_peliculas_desde_plantillas(self):
        self.client.force_login(self.admin)
        recursos = (
            ("libros", Libro, {
                "autor": Autor.objects.first().pk,
                "categoria": CategoriaLibro.objects.first().pk, "paginas": 120,
            }),
            ("peliculas", Pelicula, {
                "categoria": CategoriaPelicula.objects.first().pk,
                "director": "Dirección de prueba", "duracion_minutos": 90,
            }),
        )
        for recurso, modelo, especificos in recursos:
            with self.subTest(recurso=recurso):
                titulo = f"Registro de prueba de {recurso}"
                datos = {
                    "titulo": titulo, "anio": 2025, "calificacion": "8",
                    "sinopsis": "Sinopsis de prueba", "imagen": "portada_general.png", **especificos,
                }
                listado = reverse(f"gestion:{recurso}")
                crear = reverse(f"gestion:{recurso}_crear")
                self.assertContains(self.client.get(crear), "Guardar")
                self.assertRedirects(self.client.post(crear, datos), listado)
                registro = modelo.objects.get(titulo=titulo)
                self.assertContains(self.client.get(listado, {"q": titulo}), titulo)
                self.assertNotContains(self.client.get(listado, {"q": "sin coincidencias"}), titulo)
                nuevo_titulo = titulo + " editado"
                editar = reverse(f"gestion:{recurso}_editar", args=[registro.pk])
                self.assertRedirects(self.client.post(editar, {**datos, "titulo": nuevo_titulo}), listado)
                registro.refresh_from_db()
                self.assertEqual(registro.titulo, nuevo_titulo)
                eliminar = reverse(f"gestion:{recurso}_eliminar", args=[registro.pk])
                self.assertContains(self.client.get(eliminar), "Confirmar eliminación")
                self.assertTrue(modelo.objects.filter(pk=registro.pk).exists())
                self.assertRedirects(self.client.post(eliminar), listado)
                self.assertFalse(modelo.objects.filter(pk=registro.pk).exists())

    def test_libro_con_reserva_conserva_historial_y_se_libera_al_cancelar(self):
        libro = Libro.objects.filter(disponible=True).first()
        retiro = timezone.localdate() + timedelta(days=1)
        self.client.force_login(self.administrativo)
        respuesta = self.client.post(reverse("reservar_libro", args=[libro.slug]), {
            "fecha_retiro": retiro.isoformat(),
            "fecha_devolucion_prevista": (retiro + timedelta(days=5)).isoformat(),
        })
        self.assertRedirects(respuesta, reverse("mis_reservas"))
        reserva = ReservaLibro.objects.get(usuario=self.administrativo, libro=libro)
        libro.refresh_from_db()
        self.assertFalse(libro.disponible)
        estado = reverse("gestion:reserva_estado", args=["libro", reserva.pk])
        self.assertEqual(self.client.post(estado, {"estado": "cancelada"}).status_code, 403)

        self.client.force_login(self.supervisor)
        self.assertContains(self.client.get(reverse("gestion:reservas")), libro.titulo)
        self.assertRedirects(self.client.post(estado, {"estado": "cancelada"}), reverse("gestion:reservas"))
        reserva.refresh_from_db()
        libro.refresh_from_db()
        self.assertEqual(reserva.estado, ReservaLibro.Estado.CANCELADA)
        self.assertTrue(libro.disponible)
        self.client.force_login(self.admin)
        respuesta = self.client.post(reverse("gestion:libros_eliminar", args=[libro.pk]), follow=True)
        self.assertContains(respuesta, "Este registro tiene reservas")
        self.assertTrue(ReservaLibro.objects.filter(pk=reserva.pk).exists())

    def test_mantenedores_de_autores_y_categorias_y_relacion_protegida(self):
        self.client.force_login(self.admin)
        recursos = (
            ("autores", Autor),
            ("categorias-libros", CategoriaLibro),
            ("categorias-peliculas", CategoriaPelicula),
        )
        for recurso, modelo in recursos:
            with self.subTest(recurso=recurso):
                nombre = f"Registro temporal {recurso}"
                listado = reverse(f"gestion:{recurso}")
                self.assertRedirects(
                    self.client.post(reverse(f"gestion:{recurso}_crear"), {"nombre": nombre}), listado,
                )
                registro = modelo.objects.get(nombre=nombre)
                self.assertContains(self.client.get(listado, {"q": nombre}), nombre)
                self.assertRedirects(self.client.post(
                    reverse(f"gestion:{recurso}_editar", args=[registro.pk]),
                    {"nombre": nombre + " editado"},
                ), listado)
                registro.refresh_from_db()
                self.assertEqual(registro.nombre, nombre + " editado")
                self.assertRedirects(
                    self.client.post(reverse(f"gestion:{recurso}_eliminar", args=[registro.pk])), listado,
                )
                self.assertFalse(modelo.objects.filter(pk=registro.pk).exists())
        autor = Libro.objects.first().autor
        respuesta = self.client.post(reverse("gestion:autores_eliminar", args=[autor.pk]), follow=True)
        self.assertContains(respuesta, "Este registro está relacionado con otros datos del catálogo.")
        self.assertTrue(Autor.objects.filter(pk=autor.pk).exists())

    def test_reserva_de_pelicula_valida_duplicados_y_protege_datos_ajenos(self):
        pelicula = Pelicula.objects.first()
        self.client.force_login(self.administrativo)
        fecha = timezone.localtime(timezone.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M")
        ruta = reverse("reservar_pelicula", args=[pelicula.slug])
        datos = {"fecha_funcion": fecha, "cantidad_entradas": 2}
        self.assertRedirects(self.client.post(ruta, datos), reverse("mis_reservas"))
        self.assertContains(self.client.post(ruta, datos), "Ya tienes una reserva activa")
        self.assertEqual(ReservaPelicula.objects.filter(usuario=self.administrativo).count(), 1)
        self.client.force_login(self.visitante)
        self.assertNotContains(self.client.get(reverse("mis_reservas")), pelicula.titulo)

    def test_formulario_de_eliminacion_exige_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        libro = Libro.objects.first()
        ruta = reverse("gestion:libros_eliminar", args=[libro.pk])
        self.assertEqual(client.post(ruta).status_code, 403)
        self.assertTrue(Libro.objects.filter(pk=libro.pk).exists())


class RecuperacionContrasenaTest(TestCase):
    def test_correo_token_de_un_uso_y_acceso_con_nueva_contrasena(self):
        cuenta = User.objects.create_user(
            "recuperacion", email="recuperacion@example.com", password="ClaveAnterior-654!",
        )
        respuesta = self.client.post(reverse("password_reset"), {"email": cuenta.email})
        self.assertRedirects(respuesta, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [cuenta.email])
        enlace = re.search(r"https?://\S+", mail.outbox[0].body).group()
        ruta = urlsplit(enlace).path
        respuesta = self.client.get(ruta, follow=True)
        self.assertContains(respuesta, "Guardar contraseña")
        ruta_formulario = respuesta.redirect_chain[-1][0]
        nueva = "ClaveNueva-8643!"
        self.assertRedirects(
            self.client.post(ruta_formulario, {"new_password1": nueva, "new_password2": nueva}),
            reverse("password_reset_complete"),
        )
        self.assertFalse(self.client.login(username=cuenta.username, password="ClaveAnterior-654!"))
        self.assertTrue(self.client.login(username=cuenta.username, password=nueva))
        self.assertContains(self.client.get(ruta), "El enlace ya fue utilizado")

    def test_correo_desconocido_muestra_la_misma_confirmacion(self):
        respuesta = self.client.post(reverse("password_reset"), {"email": "desconocido@example.com"})
        self.assertRedirects(respuesta, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)
