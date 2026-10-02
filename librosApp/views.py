from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReservaLibroForm
from .models import CategoriaLibro, Libro


def inicio(request):
    """Resume el catálogo utilizando consultas del ORM de Django."""
    libros = Libro.objects.select_related("autor", "categoria")
    promedio = libros.aggregate(valor=Avg("calificacion"))["valor"] or 0
    contexto = {
        "destacados": libros.filter(destacado=True),
        "total_libros": libros.count(),
        "promedio": round(promedio, 1),
        "disponibles": libros.filter(disponible=True).count(),
    }
    return render(request, "libros/inicio.html", contexto)


def listado(request):
    """Lista, busca y filtra libros almacenados en la base de datos."""
    libros = Libro.objects.select_related("autor", "categoria")
    categorias = CategoriaLibro.objects.filter(libros__isnull=False).distinct()
    categoria_seleccionada = request.GET.get("categoria", "todas")
    busqueda = request.GET.get("q", "").strip()

    if categoria_seleccionada != "todas":
        if categorias.filter(slug=categoria_seleccionada).exists():
            libros = libros.filter(categoria__slug=categoria_seleccionada)
        else:
            categoria_seleccionada = "todas"

    if busqueda:
        libros = libros.filter(
            Q(titulo__icontains=busqueda)
            | Q(autor__nombre__icontains=busqueda)
            | Q(sinopsis__icontains=busqueda)
        )

    contexto = {
        "libros": libros,
        "categorias": categorias,
        "categoria_seleccionada": categoria_seleccionada,
        "busqueda": busqueda,
        "total": libros.count(),
    }
    return render(request, "libros/listado.html", contexto)


def detalle(request, slug):
    libro = get_object_or_404(
        Libro.objects.select_related("autor", "categoria"), slug=slug
    )
    return render(request, "libros/detalle.html", {"libro": libro})


@login_required
def reservar(request, slug):
    libro = get_object_or_404(Libro, slug=slug)
    if not libro.disponible:
        messages.warning(request, "Este libro no se encuentra disponible para reservar.")
        return redirect("detalle_libro", slug=libro.slug)

    if request.method == "POST":
        formulario = ReservaLibroForm(request.POST)
        if formulario.is_valid():
            with transaction.atomic():
                libro = Libro.objects.select_for_update().get(pk=libro.pk)
                if not libro.disponible:
                    formulario.add_error(
                        None, "El libro acaba de ser reservado por otro usuario."
                    )
                else:
                    reserva = formulario.save(commit=False)
                    reserva.usuario = request.user
                    reserva.libro = libro
                    reserva.save()
                    libro.disponible = False
                    libro.save(update_fields=("disponible", "actualizado_en"))
                    messages.success(request, "La reserva del libro fue registrada.")
                    return redirect("mis_reservas")
    else:
        formulario = ReservaLibroForm()

    return render(
        request,
        "libros/reservar.html",
        {"libro": libro, "formulario": formulario},
    )
