from django.contrib import admin

from .models import Autor, CategoriaLibro, Libro, ReservaLibro


@admin.register(CategoriaLibro)
class CategoriaLibroAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug")
    search_fields = ("nombre",)
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "autor",
        "categoria",
        "anio",
        "disponible",
        "destacado",
    )
    list_filter = ("categoria", "disponible", "destacado", "anio")
    search_fields = ("titulo", "autor__nombre", "sinopsis")
    autocomplete_fields = ("autor", "categoria")
    prepopulated_fields = {"slug": ("titulo",)}
    list_select_related = ("autor", "categoria")


@admin.register(ReservaLibro)
class ReservaLibroAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "libro",
        "fecha_retiro",
        "fecha_devolucion_prevista",
        "estado",
        "creada_en",
    )
    list_filter = ("estado", "fecha_retiro", "creada_en")
    search_fields = ("usuario__username", "usuario__email", "libro__titulo")
    autocomplete_fields = ("usuario", "libro")
    list_select_related = ("usuario", "libro")
    date_hierarchy = "fecha_retiro"
