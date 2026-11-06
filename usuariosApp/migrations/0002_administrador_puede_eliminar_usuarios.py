from django.db import migrations


def otorgar_permiso_eliminar_usuario(apps, schema_editor):
    alias = schema_editor.connection.alias
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    tipo, _ = ContentType.objects.using(alias).get_or_create(app_label="auth", model="user")
    permiso, _ = Permission.objects.using(alias).get_or_create(
        content_type=tipo,
        codename="delete_user",
        defaults={"name": "Can delete user"},
    )
    administrador = Group.objects.using(alias).get(name="Administrador")
    administrador.permissions.add(permiso)


def retirar_permiso_eliminar_usuario(apps, schema_editor):
    alias = schema_editor.connection.alias
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    administrador = Group.objects.using(alias).get(name="Administrador")
    permiso = Permission.objects.using(alias).filter(
        content_type__app_label="auth",
        content_type__model="user",
        codename="delete_user",
    ).first()
    if permiso:
        administrador.permissions.remove(permiso)


class Migration(migrations.Migration):
    dependencies = [
        ("usuariosApp", "0001_perfiles_portal"),
    ]

    operations = [
        migrations.RunPython(otorgar_permiso_eliminar_usuario, retirar_permiso_eliminar_usuario),
    ]
