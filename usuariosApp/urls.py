from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path(
        "ingresar/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("mis-reservas/", views.mis_reservas, name="mis_reservas"),
]
