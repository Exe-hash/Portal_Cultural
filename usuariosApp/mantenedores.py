from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import aplicar_bootstrap


class Mantenedor(PermissionRequiredMixin):
    recurso = ""
    accion = ""

    def permiso(self, accion):
        opciones = self.model._meta
        return f"{opciones.app_label}.{accion}_{opciones.model_name}"

    def get_permission_required(self):
        return (self.permiso(self.accion),)

    def get_success_url(self):
        return reverse(f"gestion:{self.recurso}")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(
            recurso=self.recurso,
            volver=self.get_success_url(),
            entidad=self.model._meta.verbose_name,
            entidades=self.model._meta.verbose_name_plural,
            puede_crear=self.request.user.has_perm(self.permiso("add")),
            puede_editar=self.request.user.has_perm(self.permiso("change")),
            puede_eliminar=self.request.user.has_perm(self.permiso("delete")),
        )
        return contexto


class MantenedorListado(Mantenedor, ListView):
    accion = "view"
    template_name = "gestion/catalogo.html"
    campos_busqueda = ()
    context_object_name = "registros"

    def get_queryset(self):
        registros = super().get_queryset()
        busqueda = self.request.GET.get("q", "").strip()
        if busqueda:
            filtro = Q()
            for campo in self.campos_busqueda:
                filtro |= Q(**{f"{campo}__icontains": busqueda})
            registros = registros.filter(filtro)
        return registros

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["busqueda"] = self.request.GET.get("q", "").strip()
        contexto["ruta_crear"] = f"gestion:{self.recurso}_crear"
        contexto["ruta_editar"] = f"gestion:{self.recurso}_editar"
        contexto["ruta_eliminar"] = f"gestion:{self.recurso}_eliminar"
        return contexto


class MantenedorFormulario(Mantenedor):
    template_name = "gestion/formulario.html"

    def get_form(self, form_class=None):
        formulario = super().get_form(form_class)
        aplicar_bootstrap(formulario)
        return formulario

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        verbo = "Agregar" if self.accion == "add" else "Modificar"
        contexto["titulo"] = f"{verbo} {self.model._meta.verbose_name}"
        return contexto

    def form_valid(self, form):
        try:
            with transaction.atomic():
                respuesta = super().form_valid(form)
        except IntegrityError:
            form.add_error(None, "Los datos cambiaron durante el guardado. Revisa el formulario e inténtalo de nuevo.")
            return self.form_invalid(form)
        messages.success(self.request, "El registro se guardó correctamente.")
        return respuesta


class MantenedorCrear(MantenedorFormulario, CreateView):
    accion = "add"


class BloquearEnEscritura:
    def get_queryset(self):
        registros = super().get_queryset()
        if self.request.method == "POST":
            return registros.select_for_update()
        return registros

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MantenedorEditar(BloquearEnEscritura, MantenedorFormulario, UpdateView):
    accion = "change"


class MantenedorEliminar(BloquearEnEscritura, Mantenedor, DeleteView):
    accion = "delete"
    template_name = "gestion/eliminar.html"

    # Esta operación se confirma mediante un formulario POST con CSRF.
    http_method_names = ["get", "post", "head", "options"]

    def form_valid(self, form):
        try:
            with transaction.atomic():
                if hasattr(self.object, "reservas") and self.object.reservas.exists():
                    messages.error(self.request, "Este registro tiene reservas. Debe conservarse para mantener su historial.")
                    return redirect(self.get_success_url())
                respuesta = super().form_valid(form)
        except (ProtectedError, IntegrityError):
            messages.error(self.request, "Este registro está relacionado con otros datos del catálogo.")
            return redirect(self.get_success_url())
        messages.success(self.request, "El registro se eliminó correctamente.")
        return respuesta
