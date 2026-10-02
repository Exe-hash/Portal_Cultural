from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReservaPeliculaForm
from .models import CategoriaPelicula, Pelicula, ReservaPelicula


def inicio(request):
    """Resume el catálogo utilizando consultas del ORM de Django."""
    peliculas = Pelicula.objects.select_related("categoria")
    promedio = peliculas.aggregate(valor=Avg("calificacion"))["valor"] or 0
    contexto = {
        "destacadas": peliculas.filter(destacada=True),
        "total_peliculas": peliculas.count(),
        "promedio": round(promedio, 1),
    }
    return render(request, "peliculas/inicio.html", contexto)


def listado(request):
    """Lista, busca y filtra películas almacenadas en la base de datos."""
    peliculas = Pelicula.objects.select_related("categoria")
    categorias = CategoriaPelicula.objects.filter(peliculas__isnull=False).distinct()
    categoria_seleccionada = request.GET.get("categoria", "todas")
    busqueda = request.GET.get("q", "").strip()

    if categoria_seleccionada != "todas":
        if categorias.filter(slug=categoria_seleccionada).exists():
            peliculas = peliculas.filter(categoria__slug=categoria_seleccionada)
        else:
            categoria_seleccionada = "todas"

    if busqueda:
        peliculas = peliculas.filter(
            Q(titulo__icontains=busqueda)
            | Q(director__icontains=busqueda)
            | Q(sinopsis__icontains=busqueda)
        )

    contexto = {
        "peliculas": peliculas,
        "categorias": categorias,
        "categoria_seleccionada": categoria_seleccionada,
        "busqueda": busqueda,
        "total": peliculas.count(),
    }
    return render(request, "peliculas/listado.html", contexto)


def detalle(request, slug):
    pelicula = get_object_or_404(
        Pelicula.objects.select_related("categoria"), slug=slug
    )
    return render(request, "peliculas/detalle.html", {"pelicula": pelicula})


@login_required
def reservar(request, slug):
    pelicula = get_object_or_404(Pelicula, slug=slug)
    if request.method == "POST":
        formulario = ReservaPeliculaForm(request.POST)
        if formulario.is_valid():
            fecha = formulario.cleaned_data["fecha_funcion"]
            duplicada = ReservaPelicula.objects.filter(
                usuario=request.user,
                pelicula=pelicula,
                fecha_funcion=fecha,
            ).exclude(estado=ReservaPelicula.Estado.CANCELADA)
            if duplicada.exists():
                formulario.add_error(
                    None, "Ya tienes una reserva activa para esta película y función."
                )
            else:
                reserva = formulario.save(commit=False)
                reserva.usuario = request.user
                reserva.pelicula = pelicula
                reserva.save()
                messages.success(request, "La reserva de la película fue registrada.")
                return redirect("mis_reservas")
    else:
        formulario = ReservaPeliculaForm()

    return render(
        request,
        "peliculas/reservar.html",
        {"pelicula": pelicula, "formulario": formulario},
    )
