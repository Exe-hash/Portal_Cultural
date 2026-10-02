from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from librosApp.models import ReservaLibro
from peliculasApp.models import ReservaPelicula

from .forms import RegistroUsuarioForm


def registro(request):
    if request.user.is_authenticated:
        return redirect("principal")

    if request.method == "POST":
        formulario = RegistroUsuarioForm(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            login(request, usuario)
            messages.success(request, "Tu cuenta fue creada correctamente.")
            return redirect("principal")
    else:
        formulario = RegistroUsuarioForm()

    return render(request, "usuarios/registro.html", {"formulario": formulario})


@login_required
def mis_reservas(request):
    reservas_libros = ReservaLibro.objects.filter(usuario=request.user).select_related(
        "libro"
    )
    reservas_peliculas = ReservaPelicula.objects.filter(
        usuario=request.user
    ).select_related("pelicula")
    return render(
        request,
        "usuarios/mis_reservas.html",
        {
            "reservas_libros": reservas_libros,
            "reservas_peliculas": reservas_peliculas,
        },
    )
