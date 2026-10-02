from django.shortcuts import render


def principal(request):
    """
    Página de inicio general del sitio (punto de entrada del proyecto).

    Solo enlaza hacia las dos aplicaciones (peliculasApp y librosApp) sin
    depender de sus datos internos, para mantener ambas aplicaciones
    completamente independientes entre sí.
    """
    return render(request, 'home.html')
