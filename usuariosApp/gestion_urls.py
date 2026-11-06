from django.urls import path

from librosApp.models import Autor, CategoriaLibro, Libro
from peliculasApp.models import CategoriaPelicula, Pelicula

from . import gestion
from .catalogo_forms import AutorForm, CategoriaLibroForm, CategoriaPeliculaForm, LibroForm, PeliculaForm
from .mantenedores import MantenedorCrear, MantenedorEditar, MantenedorEliminar, MantenedorListado

app_name = "gestion"

urlpatterns = [
    path("", gestion.panel, name="panel"),
    path("usuarios/", gestion.usuarios, name="usuarios"),
    path("usuarios/crear/", gestion.crear_usuario, name="usuarios_crear"),
    path("usuarios/<int:pk>/editar/", gestion.editar_usuario, name="usuarios_editar"),
    path("usuarios/<int:pk>/eliminar/", gestion.eliminar_usuario, name="usuarios_eliminar"),
    path("reservas/", gestion.reservas, name="reservas"),
    path("reservas/<str:tipo>/<int:pk>/estado/", gestion.actualizar_reserva, name="reserva_estado"),
]

mantenedores = (
    ("libros", Libro, LibroForm, ("titulo", "autor__nombre", "sinopsis")),
    ("peliculas", Pelicula, PeliculaForm, ("titulo", "director", "sinopsis")),
    ("autores", Autor, AutorForm, ("nombre",)),
    ("categorias-libros", CategoriaLibro, CategoriaLibroForm, ("nombre",)),
    ("categorias-peliculas", CategoriaPelicula, CategoriaPeliculaForm, ("nombre",)),
)

for recurso, modelo, formulario, busqueda in mantenedores:
    opciones = {"model": modelo, "recurso": recurso}
    urlpatterns += [
        path(f"{recurso}/", MantenedorListado.as_view(**opciones, campos_busqueda=busqueda), name=recurso),
        path(f"{recurso}/crear/", MantenedorCrear.as_view(**opciones, form_class=formulario), name=f"{recurso}_crear"),
        path(f"{recurso}/<int:pk>/editar/", MantenedorEditar.as_view(**opciones, form_class=formulario), name=f"{recurso}_editar"),
        path(f"{recurso}/<int:pk>/eliminar/", MantenedorEliminar.as_view(**opciones), name=f"{recurso}_eliminar"),
    ]
