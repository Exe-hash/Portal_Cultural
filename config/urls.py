from django.contrib import admin
from django.urls import path, include

from config import views as vistas_principales

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página de inicio general del sitio (punto de entrada del proyecto)
    path('', vistas_principales.principal, name='principal'),

    # Cada aplicación mantiene su propio archivo de rutas (urls.py).
    # config/urls.py actúa como punto de entrada y solo las incluye.
    path('peliculas/', include('peliculasApp.urls')),
    path('libros/', include('librosApp.urls')),
    path('cuentas/', include('usuariosApp.urls')),
]

admin.site.site_header = 'Administración del Portal Cultural'
admin.site.site_title = 'Portal Cultural'
admin.site.index_title = 'Gestión de catálogos, usuarios y reservas'
