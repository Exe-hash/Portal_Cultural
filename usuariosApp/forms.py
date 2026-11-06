from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .perfiles import PERFILES


def aplicar_bootstrap(formulario):
    for campo in formulario.fields.values():
        if isinstance(campo.widget, forms.CheckboxInput):
            clase = "form-check-input"
        elif isinstance(campo.widget, forms.Select):
            clase = "form-select"
        else:
            clase = "form-control"
        campo.widget.attrs["class"] = clase


class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(max_length=150, required=True, label="Nombre")
    last_name = forms.CharField(max_length=150, required=True, label="Apellido")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario registrado con este correo.")
        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data["email"].lower()
        if commit:
            usuario.save()
        return usuario

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_bootstrap(self)


class CrearUsuarioGestionForm(RegistroUsuarioForm):
    perfil = forms.ChoiceField(
        choices=[("", "Sin perfil asignado")] + [(perfil, perfil) for perfil in PERFILES],
        required=False,
    )


class EditarUsuarioGestionForm(forms.ModelForm):
    perfil = forms.ChoiceField(
        choices=[("", "Sin perfil asignado")] + [(perfil, perfil) for perfil in PERFILES],
        required=False,
    )
    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_bootstrap(self)

    def clean_email(self):
        correo = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=correo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un usuario registrado con este correo.")
        return correo
