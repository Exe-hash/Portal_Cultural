# Portal Cultural

Aplicación de Programación Back End (TI3041) para consultar y gestionar un catálogo de libros y películas. En la **Evaluación Sumativa 3** los mantenedores, usuarios y reservas se operan desde pantallas propias con Django Templates y Bootstrap.

## Funcionalidades

- Catálogos de películas y libros almacenados en una base de datos relacional.
- Importación inicial reproducible de `peliculas.json` y `libros.json` mediante migraciones de datos.
- Categorías normalizadas y autores de libros relacionados mediante claves foráneas.
- Registro público, inicio y cierre de sesión, y recuperación de contraseña por correo con un enlace de un solo uso.
- Tres perfiles mediante grupos y permisos de Django, con paneles diferenciados.
- Mantenedores de libros, películas, autores y categorías con altas, búsqueda, listados, edición y eliminación.
- Reservas de libros y películas asociadas a cada usuario. Supervisión puede consultar todas y cambiar su estado.
- Configuración por variables de entorno para SQLite o MySQL/MariaDB.
- Despliegue en EC2 con Gunicorn, Apache y MariaDB. phpMyAdmin permite revisar la base mediante el túnel SSH.

## Perfiles y permisos

| Perfil | Catálogos | Reservas | Usuarios |
|---|---|---|---|
| Administrador | Crear, buscar, listar, modificar y eliminar. También administra autores y categorías. | Ve todas, puede reservar y cambiar el estado. | Crea cuentas, asigna perfiles y puede desactivar cuentas gestionables. |
| Supervisor | Busca, lista, crea y modifica libros y películas. Consulta autores y categorías. | Ve todas, puede reservar y cambiar el estado. | — |
| Administrativo | Consulta y busca libros y películas. | Crea y consulta sus propias reservas. | — |

El registro público crea una cuenta de lector sin grupo interno. Un administrador puede asignarle un perfil después. El superusuario existente puede entrar al panel y crear cuentas para la demostración. El servidor comprueba el permiso en cada operación. La migración `usuariosApp.0001_perfiles_portal` crea los grupos y asigna los permisos en las tablas de autenticación existentes.

## Modelo de datos

| Tabla | Finalidad | Relaciones principales |
|---|---|---|
| `auth_user` | Cuentas del portal | Se relacionan con grupos de permisos y con sus reservas |
| `peliculas_categoria` | Categorías de películas | Una categoría tiene muchas películas |
| `peliculas_pelicula` | Catálogo de películas | Pertenece a una categoría |
| `peliculas_reserva` | Reservas de funciones | Pertenece a un usuario y una película |
| `libros_categoria` | Categorías de libros | Una categoría tiene muchos libros |
| `libros_autor` | Autores | Un autor tiene muchos libros |
| `libros_libro` | Catálogo de libros | Pertenece a un autor y una categoría |
| `libros_reserva` | Reservas de libros | Pertenece a un usuario y un libro |

Django utiliza `auth_group`, `auth_permission`, `auth_user_groups` y `auth_group_permissions` para los perfiles y sus permisos.

## Instalación local

```powershell
cd D:\Django\Proyecto_Django\portal_cultural
if (-not (Test-Path .venv\Scripts\python.exe)) { py -m venv .venv }
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Configura `DJANGO_SECRET_KEY` y el motor en tu `.env`. Git excluye este archivo porque contiene credenciales. Si ya tenías un `.env` funcional, edita solo las variables que necesites.

### Opción A · Prueba local aislada con SQLite

Ejecuta en la misma ventana de PowerShell que usarás para los comandos siguientes. La base de demostración queda dentro de `.venv`.

```powershell
$env:DB_ENGINE = 'sqlite'
$env:SQLITE_NAME = '.venv/eva3-demo.sqlite3'
$env:DJANGO_DEBUG = 'True'
$env:PORTAL_EMAIL_MODE = 'console'
```

### Opción B · MySQL o MariaDB

Si ya existe la base de la Eva 2, usa su configuración actual. Para una instalación limpia, ejecuta `database/crear_base_datos.sql`, crea un usuario con acceso a `portal_cultural` y configura `.env` con tus valores.

```dotenv
DB_ENGINE=mysql
DB_NAME=portal_cultural
DB_USER=portal_cultural_user
DB_PASSWORD=una-contrasena-segura
DB_HOST=127.0.0.1
DB_PORT=3306
```

### Aplica las migraciones y abre el sitio

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
```

Si esa base todavía no tiene superusuario, ejecuta el primer comando. Dale un correo al que tengas acceso si vas a probar la recuperación con esa cuenta. Usa el segundo comando para abrir el sitio.

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

En una base nueva, las migraciones de la Eva 2 importan los catálogos iniciales desde JSON. Sobre una base existente, Django aplica únicamente las migraciones pendientes. La de la Eva 3 agrega grupos y permisos, sin reimportar el catálogo.

- [Inicio local](http://127.0.0.1:8000/)
- [Ingreso](http://127.0.0.1:8000/cuentas/ingresar/)
- [Panel](http://127.0.0.1:8000/gestion/)
- [Recuperación de contraseña](http://127.0.0.1:8000/cuentas/recuperar/)

## Demostración de la Sumativa 3

1. Entra con el superusuario y abre **Mi panel → Gestionar usuarios → Crear usuario**. Crea una cuenta para cada perfil y usa correos distintos. Si vas a cambiar el perfil de una cuenta, abre **Modificar perfil**, guarda y vuelve a ingresar con esa cuenta.
2. Entra como **Administrador**. En los mantenedores de Libros y Películas agrega un registro de prueba, búscalo, edítalo y elimínalo. Para la eliminación usa un registro sin reservas. El portal conserva los registros que tienen historial.
3. Entra como **Supervisor**. Abre los mantenedores y **Gestionar reservas**. Intenta abrir directamente `/gestion/usuarios/` y la URL de eliminación de un registro. El servidor devuelve HTTP 403.
4. Entra como **Administrativo**. Consulta los catálogos, abre la ficha de un libro disponible y reserva indicando retiro y devolución. Comprueba el registro en **Mis reservas** y que el libro queda ocupado. Repite con una película indicando fecha, hora y cantidad de entradas.
5. Vuelve a **Gestionar reservas** como Supervisor o Administrador. Confirma una reserva y luego complétala, o cancélala. Al cerrar una reserva de libro, el libro vuelve a estar disponible cuando no quedan reservas activas para ese título.
6. Cierra la sesión y pulsa **Olvidé mi contraseña**. Solicita un enlace, ábrelo, guarda una contraseña nueva y vuelve a entrar. El enlace dura una hora y pierde validez tras cambiar la contraseña.

## Correo de recuperación

En modo `console`, el servidor de desarrollo imprime el correo en la terminal. Abre el enlace que aparece ahí para probar el flujo local.

Para recibir un correo real, configura en el `.env` de ese entorno un proveedor SMTP y un remitente autorizado por el proveedor. Para SMTP con STARTTLS, un ejemplo de configuración es:

```dotenv
PORTAL_EMAIL_MODE=smtp
PORTAL_SMTP_HOST=smtp.tu-proveedor.example
PORTAL_SMTP_PORT=587
PORTAL_SMTP_USER=usuario-proporcionado-por-el-proveedor
PORTAL_SMTP_PASSWORD=credencial-proporcionada-por-el-proveedor
PORTAL_SMTP_TLS=True
PORTAL_SMTP_SSL=False
PORTAL_FROM_EMAIL=Portal Cultural <remitente-verificado@example.com>
```

Usa el puerto y el modo de cifrado que indica tu proveedor. Si exige TLS implícito (habitualmente 465), usa `PORTAL_SMTP_TLS=False` y `PORTAL_SMTP_SSL=True`. Reinicia el servidor después de editar `.env`. Desde un navegador solicita la recuperación para una cuenta con un correo real y verifica que el mensaje llegue a su buzón. Para la demostración por túnel SSH, solicita y abre el enlace en el mismo equipo y con el túnel activo.

## Comprobaciones

```powershell
$env:DB_ENGINE = 'sqlite'
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test -v 2
```

## Publicación en GitHub y actualización de EC2

Desde el repositorio de Windows revisa los cambios y verifica que `.env` está excluido. Si tu rama de entrega es `main`, publica así:

```powershell
git status --short
git check-ignore .env
git add -- .env.example README.md config/settings.py config/urls.py librosApp/views.py librosApp/tests.py peliculasApp/views.py peliculasApp/tests.py templates usuariosApp
git diff --cached --stat
git commit -m "feat: incorpora perfiles, gestión y recuperación de la Eva 3"
git push origin main
```

En AWS Academy inicia el laboratorio y la EC2 existente del Portal Cultural. Espera a que las comprobaciones estén aprobadas. Conéctate por SSH y verifica que el clon esté limpio antes de actualizarlo. Configura las variables SMTP en el `.env` de EC2, mantén `DJANGO_DEBUG=False` y conserva la IP elástica y `127.0.0.1` en `DJANGO_ALLOWED_HOSTS` si usarás el túnel. Haz un respaldo privado de la base antes de aplicar cambios.

```bash
umask 077
respaldo="$HOME/portal_cultural_antes_eva3_$(date +%Y%m%d_%H%M%S).sql"
sudo mariadb-dump --single-transaction --databases portal_cultural > "$respaldo"
ls -lh "$respaldo"
```

Si el respaldo termina correctamente, actualiza el código y comprueba la migración:

```bash
cd /home/ec2-user/portal_cultural
git status -sb
git pull --ff-only origin main
.venv/bin/python manage.py migrate --plan
.venv/bin/python manage.py migrate
.venv/bin/python manage.py showmigrations usuariosApp
.venv/bin/python manage.py check
sudo systemctl restart portal_cultural.service
systemctl is-active mariadb portal_cultural httpd
git log -4 --oneline
```

Abre el portal por su dirección pública y usa el túnel SSH para ingresar con contraseñas mientras el sitio público use HTTP. Desde PowerShell, sustituye la ruta de la clave y la IP por las de tu instancia:

```powershell
ssh -N -o ExitOnForwardFailure=yes -L 127.0.0.1:8082:127.0.0.1:80 -i "RUTA_DE_TU_CLAVE.pem" ec2-user@IP_ELASTICA
```

Deja la terminal abierta y usa [el portal por el túnel](http://127.0.0.1:8082/) o [phpMyAdmin](http://127.0.0.1:8082/phpMyAdmin/).

## Evidencia para la revisión

- Login, cierre de sesión, los tres paneles y una ruta con acceso restringido.
- Creación de usuario y asignación de un grupo. Capturas del CRUD de Libros y Películas.
- Reserva en pantalla, confirmación en **Mis reservas** y el registro relacionado en la base de datos.
- Solicitud de recuperación, correo recibido, confirmación de cambio y acceso con la nueva contraseña. Oculta el token y las credenciales en las capturas.
- Instancia EC2 en ejecución, sitio abierto, tablas, repositorio e historial de commits.
- Uso de IA. Guarda la solicitud «agrega todo lo que tengas que agregar de esta rúbrica y explícame cómo aplicar todo, dejando de lado el informe Word», la respuesta que describe los cambios y un ejemplo comprobable de su aplicación, como la prueba de permiso denegado o el restablecimiento.
