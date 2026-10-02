# Portal Cultural

Evolución del proyecto para la **Evaluación Sumativa #2** de Programación Back End (TI3041). La aplicación conserva los módulos `peliculasApp` y `librosApp`, pero ahora usa modelos, relaciones y consultas de Django ORM en lugar de leer los JSON en cada petición.

## Funcionalidades

- Catálogos de películas y libros almacenados en una base de datos relacional.
- Importación inicial reproducible de `peliculas.json` y `libros.json` mediante migraciones de datos.
- Categorías normalizadas y autores de libros relacionados mediante claves foráneas.
- Registro, inicio y cierre de sesión con el sistema de autenticación de Django.
- Reservas de libros y películas asociadas a cada usuario.
- Búsqueda y filtro de los dos catálogos mediante consultas ORM.
- CRUD completo de categorías, autores, catálogos, reservas y usuarios desde Django Admin.
- Configuración por variables de entorno para SQLite o MySQL/MariaDB.
- Compatibilidad con phpMyAdmin y preparación para una futura instancia EC2.

## Modelo de datos

| Tabla | Finalidad | Relaciones principales |
|---|---|---|
| `auth_user` | Usuarios y administradores | Django identifica administradores con `is_staff`/`is_superuser` |
| `peliculas_categoria` | Categorías de películas | Una categoría tiene muchas películas |
| `peliculas_pelicula` | Catálogo de películas | Pertenece a una categoría |
| `peliculas_reserva` | Reservas de funciones | Pertenece a un usuario y una película |
| `libros_categoria` | Categorías de libros | Una categoría tiene muchos libros |
| `libros_autor` | Autores | Un autor tiene muchos libros |
| `libros_libro` | Catálogo de libros | Pertenece a un autor y una categoría |
| `libros_reserva` | Reservas de libros | Pertenece a un usuario y un libro |

Django también crea sus tablas internas para permisos, grupos, sesiones y el historial del panel administrativo.

## Instalación local

```powershell
cd D:\Django\Proyecto_Django\portal_cultural
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Cambie `DJANGO_SECRET_KEY` y las credenciales de base de datos dentro de `.env`. Este archivo está excluido por `.gitignore` y no debe subirse a GitHub.

### Opción A: SQLite para desarrollo rápido

En `.env`:

```dotenv
DB_ENGINE=sqlite
```

### Opción B: MySQL/MariaDB y phpMyAdmin

1. Ejecute `database/crear_base_datos.sql` desde la pestaña **SQL** de phpMyAdmin.
2. Cree el usuario de base de datos y asígnele permisos sobre `portal_cultural`.
3. Configure `.env`:

```dotenv
DB_ENGINE=mysql
DB_NAME=portal_cultural
DB_USER=portal_cultural_user
DB_PASSWORD=una-contrasena-segura
DB_HOST=127.0.0.1
DB_PORT=3306
```

En Linux/EC2, antes de instalar `mysqlclient`, normalmente se necesitan las bibliotecas del sistema:

```bash
sudo apt update
sudo apt install -y python3-venv python3-dev default-libmysqlclient-dev build-essential pkg-config git
```

El archivo `requirements.txt` instala el controlador `mysqlclient` tanto en Windows como en Linux. SQLite no necesita un servicio de base de datos externo.

## Crear las tablas e importar los JSON

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Las migraciones `0001_initial.py` crean las tablas y relaciones. Las migraciones `0002_importar_*_json.py` cargan automáticamente los seis libros y las seis películas. Después de la importación, los nuevos registros se administran desde `/admin/`; los JSON dejan de ser la fuente consultada por las vistas.

Rutas principales:

- Sitio: <http://127.0.0.1:8000/>
- Registro: <http://127.0.0.1:8000/cuentas/registro/>
- Inicio de sesión: <http://127.0.0.1:8000/cuentas/ingresar/>
- Django Admin: <http://127.0.0.1:8000/admin/>

## Verificación para la rúbrica

```powershell
python manage.py check
python manage.py showmigrations
python manage.py test -v 2
```

En Django Admin se pueden crear, visualizar, buscar, modificar y eliminar todas las entidades. En los listados públicos, un administrador autenticado también ve los botones Agregar, Modificar y Eliminar; el botón Buscar está disponible para todos.

En phpMyAdmin deben observarse las ocho tablas de dominio descritas arriba, sus claves foráneas y los doce registros de catálogo, además de las tablas internas de Django.

## Preparación para EC2

1. Suba el proyecto a un repositorio propio de GitHub con `.env` excluido.
2. Clone el repositorio dentro de una instancia EC2 Linux.
3. Instale Python, Git, las bibliotecas de MySQL/MariaDB, MySQL/MariaDB y phpMyAdmin.
4. Cree y active el entorno virtual; instale `requirements.txt`.
5. Copie `.env.example` a `.env` y configure la IP o dominio de la instancia:

```dotenv
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=IP_PUBLICA_EC2,dominio.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=http://IP_PUBLICA_EC2,https://dominio.example.com
DB_ENGINE=mysql
```

6. Ejecute `python manage.py migrate`, `python manage.py collectstatic --noinput` y `python manage.py createsuperuser`.
7. Configure el servidor web elegido para publicar `config.wsgi:application`.

No se incluyen credenciales ni direcciones reales de AWS en el repositorio.
