# TechGear | Tienda de gorras

Aplicación de comercio electrónico compuesta por una tienda web y una API independiente. La tienda Django presenta el catálogo y las funciones de compra; la API FastAPI administra productos, usuarios, autenticación y pedidos.

## Aplicación en producción

| Componente | Enlace | Descripción |
| --- | --- | --- |
| Tienda web | [Abrir TechGear Web](https://capzone-web.onrender.com) | Sitio para explorar el catálogo y usar la tienda. |
| API REST | [Abrir TechGear API](https://capzone-web-api.onrender.com) | Servicio de datos y lógica de negocio. |
| Documentación de la API | [Abrir Swagger UI](https://capzone-web-api.onrender.com/docs) | Explorar y probar los endpoints disponibles. |
| Salud de la API | [Comprobar estado](https://capzone-web-api.onrender.com/api/health) | Verificar que la API está respondiendo. |

Los dominios publicados actualmente en Render son `capzone-web` y `capzone-web-api`.

## Estructura del repositorio

```text
.
├── backend/                     # API REST (servicio techgear_api)
│   ├── app/
│   │   ├── main.py              # Inicio de FastAPI y endpoints
│   │   ├── models.py            # Esquemas de productos, usuarios y pedidos
│   │   ├── database.py          # Conexión y operaciones con MongoDB
│   │   ├── security.py          # Autenticación, tokens y contraseñas
│   │   ├── config.py            # Configuración del servicio
│   │   ├── seed_data.py         # Datos iniciales para desarrollo
│   │   └── bootstrap_admin.py   # Creación o actualización del administrador
│   ├── .env.example             # Plantilla de configuración local
│   └── requirements.txt         # Dependencias de la API
├── frontend/                    # Sitio web (servicio techgear_web)
│   ├── capzone_django/          # Configuración, URLs y servidor WSGI
│   ├── store/                   # Rutas, vistas y lógica de la tienda
│   ├── templates/               # Páginas HTML renderizadas por Django
│   ├── static/                  # CSS, JavaScript e imágenes
│   ├── manage.py                # Comandos de administración de Django
│   ├── .env.example             # Plantilla de configuración local
│   └── requirements.txt         # Dependencias del sitio web
└── render.yaml                  # Configuración de los dos servicios en Render
```

### ¿Qué hace cada parte?

**API (`backend/`, servicio `techgear_api`).** Expone endpoints HTTP y gestiona los datos, MongoDB, autenticación y pedidos. Su documentación interactiva está en `/docs`.

**Web (`frontend/`, servicio `techgear_web`).** Entrega la experiencia de usuario mediante Django y consume la API configurada con `API_BASE_URL`.

**Render (`render.yaml`).** Define ambos servicios como aplicaciones web independientes, con su directorio raíz, dependencias, comando de inicio y variables de entorno.

## Tecnologías

Python, FastAPI y Pydantic para la API; Django, plantillas MVT, HTML, CSS y JavaScript para la tienda; MongoDB Atlas para persistencia en producción; Render para el alojamiento.

## Requisitos

Se recomienda Python 3.12 o posterior. Para producción, configura una instancia de MongoDB Atlas y las variables de entorno indicadas en la sección de despliegue.

## Preparación local en Windows

Ejecuta estos comandos desde la carpeta raíz del proyecto para crear un entorno e instalar las dependencias:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

Crea la configuración local copiando las plantillas. No subas los archivos `.env` ni sus credenciales a Git:

```powershell
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env
```

En `backend/.env`, configura `MONGODB_URL`, `SECRET_KEY` y `ADMIN_EMAIL`. La aplicación usa la base de datos `PROYECTOS`, la colección de productos `JOSE_DM_CAPS` y las colecciones `users` y `orders`. Puedes cambiar la base con `MONGODB_DATABASE` y la colección con `MONGODB_PRODUCTS_COLLECTION`.

## Ejecutar en desarrollo

Abre una terminal para cada servicio, comenzando desde la raíz del repositorio.

### 1. Iniciar la API

```powershell
cd backend
python -m app.bootstrap_admin
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

El comando de bootstrap crea o actualiza la cuenta administradora y solicita una contraseña segura si `ADMIN_PASSWORD` no está definida. La API queda en [http://127.0.0.1:8000](http://127.0.0.1:8000) y la documentación local en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 2. Iniciar la tienda web

```powershell
cd frontend
python manage.py migrate
python manage.py runserver 127.0.0.1:8001
```

Abre la tienda en [http://127.0.0.1:8001](http://127.0.0.1:8001). El panel está en `/admin-dashboard/` y la cuenta de cliente en `/mi-cuenta/`.

## Despliegue en Render

El archivo `render.yaml` permite crear ambos servicios mediante un Blueprint conectado al repositorio.

### Variables del servicio API

Configura `MONGODB_URL`, `ADMIN_EMAIL` y `ADMIN_PASSWORD`. Usa una `SECRET_KEY` segura y asegúrate de que `ALLOWED_ORIGINS` incluya el dominio de la tienda. Las credenciales deben guardarse como secretos en Render.

### Variables del servicio web

Configura `API_BASE_URL` con la URL pública de la API, además de `SECRET_KEY`, `DEBUG=false` y `ALLOWED_HOSTS` para el dominio de la tienda.

El registro público no puede asignar permisos de administrador. El comando `python -m app.bootstrap_admin` prepara esa cuenta y almacena únicamente el hash de la contraseña.
