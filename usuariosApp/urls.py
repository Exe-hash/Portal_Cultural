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
    path(
        "recuperar/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/recuperar.html",
            email_template_name="registration/recuperar_email.txt",
            subject_template_name="registration/recuperar_asunto.txt",
        ),
        name="password_reset",
    ),
    path(
        "recuperar/enviado/",
        auth_views.PasswordResetDoneView.as_view(template_name="registration/recuperar_enviado.html"),
        name="password_reset_done",
    ),
    path(
        "restablecer/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="registration/restablecer.html"),
        name="password_reset_confirm",
    ),
    path(
        "restablecer/completado/",
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/restablecer_completado.html"),
        name="password_reset_complete",
    ),
    path("mis-reservas/", views.mis_reservas, name="mis_reservas"),
]
