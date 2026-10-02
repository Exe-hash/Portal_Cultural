from django import forms
from django.utils import timezone

from .models import ReservaLibro


class ReservaLibroForm(forms.ModelForm):
    class Meta:
        model = ReservaLibro
        fields = ("fecha_retiro", "fecha_devolucion_prevista", "observaciones")
        widgets = {
            "fecha_retiro": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "fecha_devolucion_prevista": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "observaciones": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }
        labels = {
            "fecha_retiro": "Fecha de retiro",
            "fecha_devolucion_prevista": "Fecha de devolución prevista",
            "observaciones": "Observaciones (opcional)",
        }

    def clean_fecha_retiro(self):
        fecha = self.cleaned_data["fecha_retiro"]
        if fecha < timezone.localdate():
            raise forms.ValidationError("La fecha de retiro no puede estar en el pasado.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        retiro = cleaned_data.get("fecha_retiro")
        devolucion = cleaned_data.get("fecha_devolucion_prevista")
        if retiro and devolucion and devolucion < retiro:
            self.add_error(
                "fecha_devolucion_prevista",
                "La devolución no puede ser anterior al retiro.",
            )
        return cleaned_data
