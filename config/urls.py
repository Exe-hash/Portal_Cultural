from django.urls import path, include

from config import views as vistas_principales

urlpatterns = [

    # Página de inicio general del sitio (punto de entrada del proyecto)
    path('', vistas_principales.principal, name='principal'),

    # Cada aplicación mantiene su propio archivo de rutas (urls.py).
    # config/urls.py actúa como punto de entrada y solo las incluye.
    path('peliculas/', include('peliculasApp.urls')),
    path('libros/', include('librosApp.urls')),
    path('cuentas/', include('usuariosApp.urls')),
    path('gestion/', include('usuariosApp.gestion_urls')),
]
