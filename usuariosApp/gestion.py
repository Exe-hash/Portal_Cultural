from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from librosApp.models import Libro, ReservaLibro
from peliculasApp.models import Pelicula, ReservaPelicula

from .forms import CrearUsuarioGestionForm, EditarUsuarioGestionForm
from .perfiles import ADMINISTRADOR, ADMINISTRATIVO, PERFILES, SUPERVISOR, perfil_de


@login_required
def panel(request):
    perfil = perfil_de(request.user)
    if perfil is None:
        return redirect("principal")

    descripcion = {
        ADMINISTRADOR: "Gestiona los catálogos, usuarios y reservas del portal.",
        SUPERVISOR: "Actualiza los catálogos y revisa las reservas de ambos módulos.",
        ADMINISTRATIVO: "Consulta los catálogos y opera con tus propias reservas.",
    }
    indicadores = {}
    if perfil in (ADMINISTRADOR, SUPERVISOR):
        indicadores = {
            "Libros": Libro.objects.count(),
            "Películas": Pelicula.objects.count(),
            "Reservas pendientes": (
                ReservaLibro.objects.filter(estado=ReservaLibro.Estado.PENDIENTE).count()
                + ReservaPelicula.objects.filter(estado=ReservaPelicula.Estado.PENDIENTE).count()
            ),
        }
        if perfil == ADMINISTRADOR:
            indicadores["Usuarios activos"] = User.objects.filter(is_active=True).count()
    return render(request, "gestion/panel.html", {
        "perfil": perfil,
        "descripcion": descripcion[perfil],
        "indicadores": indicadores,
    })


def asignar_perfil(usuario, perfil):
    grupos_actuales = Group.objects.filter(name__in=PERFILES, user=usuario)
    usuario.groups.remove(*grupos_actuales)
    if perfil:
        usuario.groups.add(Group.objects.get(name=perfil))


@login_required
@permission_required("auth.view_user", raise_exception=True)
def usuarios(request):
    registros = User.objects.order_by("username").prefetch_related("groups")
    busqueda = request.GET.get("q", "").strip()
    if busqueda:
        registros = registros.filter(Q(username__icontains=busqueda) | Q(email__icontains=busqueda))
    return render(request, "gestion/usuarios.html", {"registros": registros, "busqueda": busqueda})


@login_required
@permission_required("auth.add_user", raise_exception=True)
def crear_usuario(request):
    formulario = CrearUsuarioGestionForm(request.POST if request.method == "POST" else None)
    if formulario.is_valid():
        with transaction.atomic():
            usuario = formulario.save()
            asignar_perfil(usuario, formulario.cleaned_data["perfil"])
        messages.success(request, "La cuenta y su perfil se guardaron correctamente.")
        return redirect("gestion:usuarios")
    return render(request, "gestion/formulario.html", {
        "form": formulario, "titulo": "Crear usuario", "volver": reverse("gestion:usuarios"),
    })


@login_required
@permission_required("auth.change_user", raise_exception=True)
@transaction.atomic
def editar_usuario(request, pk):
    registros = User.objects.select_for_update() if request.method == "POST" else User.objects.all()
    usuario = get_object_or_404(registros, pk=pk)
    if usuario.is_superuser or usuario.pk == request.user.pk:
        raise PermissionDenied
    formulario = EditarUsuarioGestionForm(
        request.POST if request.method == "POST" else None,
        instance=usuario,
        initial={"perfil": perfil_de(usuario)},
    )
    if formulario.is_valid():
        formulario.save()
        asignar_perfil(usuario, formulario.cleaned_data["perfil"])
        messages.success(request, "Se actualizaron los datos y el perfil de la cuenta.")
        return redirect("gestion:usuarios")
    return render(request, "gestion/formulario.html", {
        "form": formulario, "titulo": f"Modificar usuario {usuario.username}", "volver": reverse("gestion:usuarios"),
    })


@login_required
@permission_required("auth.delete_user", raise_exception=True)
@transaction.atomic
def eliminar_usuario(request, pk):
    registros = User.objects.select_for_update() if request.method == "POST" else User.objects.all()
    usuario = get_object_or_404(registros, pk=pk)
    if usuario.is_superuser or usuario.pk == request.user.pk:
        raise PermissionDenied

    tiene_reservas = usuario.reservas_libros.exists() or usuario.reservas_peliculas.exists()
    if tiene_reservas:
        messages.error(
            request,
            "No se puede eliminar esta cuenta porque tiene reservas asociadas. "
            "Así se conserva el historial del portal.",
        )
        return redirect("gestion:usuarios")

    if request.method == "POST":
        username = usuario.username
        usuario.delete()
        messages.success(request, f"La cuenta {username} se eliminó correctamente.")
        return redirect("gestion:usuarios")

    return render(request, "gestion/eliminar.html", {
        "object": usuario,
        "entidad": "usuario",
        "volver": reverse("gestion:usuarios"),
    })


@login_required
@permission_required(("librosApp.view_reservalibro", "peliculasApp.view_reservapelicula"), raise_exception=True)
def reservas(request):
    return render(request, "gestion/reservas.html", {
        "reservas_libros": ReservaLibro.objects.select_related("libro", "usuario"),
        "reservas_peliculas": ReservaPelicula.objects.select_related("pelicula", "usuario"),
    })


TRANSICIONES = {
    "pendiente": {"confirmada", "cancelada"},
    "confirmada": {"completada", "cancelada"},
}


@login_required
@require_POST
@transaction.atomic
def actualizar_reserva(request, tipo, pk):
    if tipo == "libro":
        modelo, catalogo, campo = ReservaLibro, Libro, "libro"
    elif tipo == "pelicula":
        modelo, catalogo, campo = ReservaPelicula, Pelicula, "pelicula"
    else:
        raise Http404

    meta = modelo._meta
    if not request.user.has_perm(f"{meta.app_label}.change_{meta.model_name}"):
        raise PermissionDenied
    referencia = get_object_or_404(modelo.objects.only(f"{campo}_id"), pk=pk)
    item = get_object_or_404(catalogo.objects.select_for_update(), pk=getattr(referencia, f"{campo}_id"))
    reserva = get_object_or_404(modelo.objects.select_for_update(), pk=pk)
    estado = request.POST.get("estado")
    if estado not in TRANSICIONES.get(reserva.estado, ()):
        messages.error(request, "El cambio solicitado no es válido para el estado actual.")
        return redirect("gestion:reservas")

    reserva.estado = estado
    reserva.save(update_fields=("estado", "actualizada_en"))
    if tipo == "libro" and estado in ("cancelada", "completada"):
        estados_activos = (ReservaLibro.Estado.PENDIENTE, ReservaLibro.Estado.CONFIRMADA)
        if not item.reservas.filter(estado__in=estados_activos).exists():
            item.disponible = True
            item.save(update_fields=("disponible", "actualizado_en"))
    messages.success(request, "Se actualizó el estado de la reserva.")
    return redirect("gestion:reservas")
