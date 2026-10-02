from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class CategoriaPelicula(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)

    class Meta:
        db_table = "peliculas_categoria"
        ordering = ("nombre",)
        verbose_name = "categoría de película"
        verbose_name_plural = "categorías de películas"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Pelicula(models.Model):
    titulo = models.CharField(max_length=180, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    categoria = models.ForeignKey(
        CategoriaPelicula,
        on_delete=models.PROTECT,
        related_name="peliculas",
    )
    director = models.CharField(max_length=150)
    anio = models.PositiveSmallIntegerField(
        "año",
        validators=[MinValueValidator(1888), MaxValueValidator(2100)],
    )
    duracion_minutos = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    calificacion = models.DecimalField(
        "calificación",
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    destacada = models.BooleanField(default=False)
    imagen = models.CharField(max_length=255, default="portada_general.png")
    sinopsis = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "peliculas_pelicula"
        ordering = ("titulo",)
        verbose_name = "película"
        verbose_name_plural = "películas"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class ReservaPelicula(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADA = "confirmada", "Confirmada"
        CANCELADA = "cancelada", "Cancelada"
        COMPLETADA = "completada", "Completada"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservas_peliculas",
    )
    pelicula = models.ForeignKey(
        Pelicula,
        on_delete=models.CASCADE,
        related_name="reservas",
    )
    fecha_funcion = models.DateTimeField("fecha y hora de la función")
    cantidad_entradas = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
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
        db_table = "peliculas_reserva"
        ordering = ("-creada_en",)
        verbose_name = "reserva de película"
        verbose_name_plural = "reservas de películas"

    def __str__(self):
        return f"{self.usuario} - {self.pelicula} ({self.fecha_funcion:%d-%m-%Y %H:%M})"
