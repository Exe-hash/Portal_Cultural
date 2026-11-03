from django import forms
from django.utils.text import slugify

from librosApp.models import Autor, CategoriaLibro, Libro
from peliculasApp.models import CategoriaPelicula, Pelicula


class FormularioConSlug(forms.ModelForm):
    campo_slug = "titulo"

    def clean(self):
        datos = super().clean()
        if not self.instance.slug and datos.get(self.campo_slug):
            slug = slugify(datos[self.campo_slug])
            if not slug:
                self.add_error(self.campo_slug, "Incluye al menos una letra o un número.")
            elif self._meta.model.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
                self.add_error(self.campo_slug, "Este valor genera una dirección ya utilizada.")
        return datos


class LibroForm(FormularioConSlug):
    class Meta:
        model = Libro
        fields = ("titulo", "autor", "categoria", "anio", "paginas", "calificacion", "destacado", "imagen", "sinopsis")
        widgets = {"sinopsis": forms.Textarea(attrs={"rows": 4})}


class PeliculaForm(FormularioConSlug):
    class Meta:
        model = Pelicula
        fields = ("titulo", "categoria", "director", "anio", "duracion_minutos", "calificacion", "destacada", "imagen", "sinopsis")
        widgets = {"sinopsis": forms.Textarea(attrs={"rows": 4})}


class CategoriaLibroForm(FormularioConSlug):
    campo_slug = "nombre"

    class Meta:
        model = CategoriaLibro
        fields = ("nombre",)


class CategoriaPeliculaForm(FormularioConSlug):
    campo_slug = "nombre"

    class Meta:
        model = CategoriaPelicula
        fields = ("nombre",)


class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ("nombre",)
