from django.db import migrations


def crear_perfiles(apps, schema_editor):
    alias = schema_editor.connection.alias
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    reglas = (
        ("librosApp", "libro", ("view", "add", "change", "delete"), ("view", "add", "change"), ("view",)),
        ("peliculasApp", "pelicula", ("view", "add", "change", "delete"), ("view", "add", "change"), ("view",)),
        ("librosApp", "autor", ("view", "add", "change", "delete"), ("view",), ()),
        ("librosApp", "categorialibro", ("view", "add", "change", "delete"), ("view",), ()),
        ("peliculasApp", "categoriapelicula", ("view", "add", "change", "delete"), ("view",), ()),
        ("librosApp", "reservalibro", ("view", "change"), ("view", "change"), ()),
        ("peliculasApp", "reservapelicula", ("view", "change"), ("view", "change"), ()),
        ("auth", "user", ("view", "add", "change"), (), ()),
    )
    nombres = ("Administrador", "Supervisor", "Administrativo")
    permisos = {nombre: [] for nombre in nombres}
    for app_label, model, *niveles in reglas:
        tipo, _ = ContentType.objects.using(alias).get_or_create(app_label=app_label, model=model)
        for nombre, acciones in zip(nombres, niveles):
            for accion in acciones:
                permiso, _ = Permission.objects.using(alias).get_or_create(
                    content_type=tipo,
                    codename=f"{accion}_{model}",
                    defaults={"name": f"Can {accion} {apps.get_model(app_label, model)._meta.verbose_name_raw}"},
                )
                permisos[nombre].append(permiso.pk)
    for nombre, ids in permisos.items():
        grupo, _ = Group.objects.using(alias).get_or_create(name=nombre)
        grupo.permissions.set(ids)


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("librosApp", "0002_importar_libros_json"),
        ("peliculasApp", "0002_importar_peliculas_json"),
    ]
    operations = [migrations.RunPython(crear_perfiles, migrations.RunPython.noop)]
