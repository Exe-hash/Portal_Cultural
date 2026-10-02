from django import forms
from django.utils import timezone

from .models import ReservaPelicula


class ReservaPeliculaForm(forms.ModelForm):
    class Meta:
        model = ReservaPelicula
        fields = ("fecha_funcion", "cantidad_entradas", "observaciones")
        widgets = {
            "fecha_funcion": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "cantidad_entradas": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 10}
            ),
            "observaciones": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }
        labels = {
            "fecha_funcion": "Fecha y hora de la función",
            "cantidad_entradas": "Cantidad de entradas",
            "observaciones": "Observaciones (opcional)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_funcion"].input_formats = ("%Y-%m-%dT%H:%M",)

    def clean_fecha_funcion(self):
        fecha = self.cleaned_data["fecha_funcion"]
        if fecha <= timezone.now():
            raise forms.ValidationError("La función debe programarse para una fecha futura.")
        return fecha
