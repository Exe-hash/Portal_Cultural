from django.contrib import admin

from .models import CategoriaPelicula, Pelicula, ReservaPelicula


@admin.register(CategoriaPelicula)
class CategoriaPeliculaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug")
    search_fields = ("nombre",)
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "categoria",
        "director",
        "anio",
        "calificacion",
        "destacada",
    )
    list_filter = ("categoria", "destacada", "anio")
    search_fields = ("titulo", "director", "sinopsis")
    autocomplete_fields = ("categoria",)
    prepopulated_fields = {"slug": ("titulo",)}
    list_select_related = ("categoria",)


@admin.register(ReservaPelicula)
class ReservaPeliculaAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "pelicula",
        "fecha_funcion",
        "cantidad_entradas",
        "estado",
        "creada_en",
    )
    list_filter = ("estado", "fecha_funcion", "creada_en")
    search_fields = ("usuario__username", "usuario__email", "pelicula__titulo")
    autocomplete_fields = ("usuario", "pelicula")
    list_select_related = ("usuario", "pelicula")
    date_hierarchy = "fecha_funcion"
