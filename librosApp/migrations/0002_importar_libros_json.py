import json
from pathlib import Path

from django.db import migrations
from django.utils.text import slugify


def importar_libros(apps, schema_editor):
    Autor = apps.get_model("librosApp", "Autor")
    CategoriaLibro = apps.get_model("librosApp", "CategoriaLibro")
    Libro = apps.get_model("librosApp", "Libro")
    ruta_json = Path(__file__).resolve().parents[1] / "data" / "libros.json"

    with ruta_json.open(encoding="utf-8") as archivo:
        registros = json.load(archivo)

    for datos in registros:
        autor, _ = Autor.objects.get_or_create(nombre=datos["autor"])
        categoria, _ = CategoriaLibro.objects.get_or_create(
            nombre=datos["categoria"],
            defaults={"slug": slugify(datos["categoria"])},
        )
        Libro.objects.update_or_create(
            titulo=datos["titulo"],
            defaults={
                "slug": slugify(datos["titulo"]),
                "categoria": categoria,
                "autor": autor,
                "anio": datos["anio"],
                "paginas": datos["paginas"],
                "calificacion": datos["calificacion"],
                "disponible": datos["disponible"],
                "destacado": datos["destacado"],
                "imagen": datos["imagen"],
                "sinopsis": datos["sinopsis"],
            },
        )


class Migration(migrations.Migration):
    dependencies = [("librosApp", "0001_initial")]

    operations = [
        migrations.RunPython(importar_libros, migrations.RunPython.noop),
    ]
