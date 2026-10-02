import json
from pathlib import Path

from django.db import migrations
from django.utils.text import slugify


def importar_peliculas(apps, schema_editor):
    CategoriaPelicula = apps.get_model("peliculasApp", "CategoriaPelicula")
    Pelicula = apps.get_model("peliculasApp", "Pelicula")
    ruta_json = Path(__file__).resolve().parents[1] / "data" / "peliculas.json"

    with ruta_json.open(encoding="utf-8") as archivo:
        registros = json.load(archivo)

    for datos in registros:
        categoria, _ = CategoriaPelicula.objects.get_or_create(
            nombre=datos["categoria"],
            defaults={"slug": slugify(datos["categoria"])},
        )
        Pelicula.objects.update_or_create(
            titulo=datos["titulo"],
            defaults={
                "slug": slugify(datos["titulo"]),
                "categoria": categoria,
                "director": datos["director"],
                "anio": datos["anio"],
                "duracion_minutos": datos["duracion_minutos"],
                "calificacion": datos["calificacion"],
                "destacada": datos["destacada"],
                "imagen": datos["imagen"],
                "sinopsis": datos["sinopsis"],
            },
        )


class Migration(migrations.Migration):
    dependencies = [("peliculasApp", "0001_initial")]

    operations = [
        migrations.RunPython(importar_peliculas, migrations.RunPython.noop),
    ]
