from django.urls import path

from librosApp import views

urlpatterns = [
    # (lo_que_escribe_el_usuario, vista_que_se_carga, nombre_para_el_template)
    path('', views.inicio, name='inicio_libros'),
    path('catalogo/', views.listado, name='listado_libros'),
    path('detalle/<str:slug>/', views.detalle, name='detalle_libro'),
    path('reservar/<slug:slug>/', views.reservar, name='reservar_libro'),
]
