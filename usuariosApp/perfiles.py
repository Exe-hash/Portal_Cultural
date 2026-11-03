ADMINISTRADOR = "Administrador"
SUPERVISOR = "Supervisor"
ADMINISTRATIVO = "Administrativo"
PERFILES = (ADMINISTRADOR, SUPERVISOR, ADMINISTRATIVO)


def perfil_de(usuario):
    if usuario.is_superuser:
        return ADMINISTRADOR
    perfiles = set(usuario.groups.filter(name__in=PERFILES).values_list("name", flat=True))
    return next((perfil for perfil in PERFILES if perfil in perfiles), None)
