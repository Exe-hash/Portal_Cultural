from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class CategoriaLibro(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)

    class Meta:
        db_table = "libros_categoria"
        ordering = ("nombre",)
        verbose_name = "categoría de libro"
        verbose_name_plural = "categorías de libros"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Autor(models.Model):
    nombre = models.CharField(max_length=150, unique=True)

    class Meta:
        db_table = "libros_autor"
        ordering = ("nombre",)
        verbose_name = "autor"
        verbose_name_plural = "autores"

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    titulo = models.CharField(max_length=180, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    categoria = models.ForeignKey(
        CategoriaLibro,
        on_delete=models.PROTECT,
        related_name="libros",
    )
    autor = models.ForeignKey(
        Autor,
        on_delete=models.PROTECT,
        related_name="libros",
    )
    anio = models.PositiveSmallIntegerField(
        "año",
        validators=[MinValueValidator(1), MaxValueValidator(2100)],
    )
    paginas = models.PositiveIntegerField(
        "páginas",
        validators=[MinValueValidator(1)],
    )
    calificacion = models.DecimalField(
        "calificación",
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    disponible = models.BooleanField(default=True, db_index=True)
    destacado = models.BooleanField(default=False)
    imagen = models.CharField(max_length=255, default="portada_general.png")
    sinopsis = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "libros_libro"
        ordering = ("titulo",)
        verbose_name = "libro"
        verbose_name_plural = "libros"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class ReservaLibro(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADA = "confirmada", "Confirmada"
        CANCELADA = "cancelada", "Cancelada"
        COMPLETADA = "completada", "Completada"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservas_libros",
    )
    libro = models.ForeignKey(
        Libro,
        on_delete=models.CASCADE,
        related_name="reservas",
    )
    fecha_retiro = models.DateField()
    fecha_devolucion_prevista = models.DateField()
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        db_index=True,
    )
    observaciones = models.CharField(max_length=300, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "libros_reserva"
        ordering = ("-creada_en",)
        verbose_name = "reserva de libro"
        verbose_name_plural = "reservas de libros"

    def clean(self):
        super().clean()
        if (
            self.fecha_retiro
            and self.fecha_devolucion_prevista
            and self.fecha_devolucion_prevista < self.fecha_retiro
        ):
            raise ValidationError(
                {"fecha_devolucion_prevista": "La devolución no puede ser anterior al retiro."}
            )

    def __str__(self):
        return f"{self.usuario} - {self.libro} ({self.fecha_retiro:%d-%m-%Y})"
