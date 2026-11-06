# CAPZONE

CAPZONE is a hybrid e-commerce project built with Django on the frontend and FastAPI on the backend. The storefront provides a premium catalog experience for urban and sports caps, while the API handles products, authentication, cart, and order logic.

## Architecture

- Backend: FastAPI + Pydantic + MongoDB-ready storage
- Frontend: Django MVT + templates + static assets
- Database: MongoDB Atlas (production) with in-memory fallback for local development

## Ejecución local

Se recomienda Python 3.12 o posterior.

1. Crea un entorno virtual e instala las dependencias desde la raíz del proyecto:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r backend/requirements.txt
   pip install -r frontend/requirements.txt
   ```
2. Configura los archivos `.env` del backend y del frontend a partir de sus archivos de ejemplo. En el backend configura `MONGODB_URL`, `SECRET_KEY` y `ADMIN_EMAIL`.
3. En una terminal, crea o actualiza la cuenta administradora. El comando solicita la contraseña de forma oculta y guarda únicamente su hash:
   ```bash
   cd backend
   python -m app.bootstrap_admin
   ```
4. En una terminal, inicia la API:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
5. En otra terminal, inicia la tienda:
   ```bash
   cd frontend
   python manage.py migrate
   python manage.py runserver 127.0.0.1:8001
   ```
6. Abre http://127.0.0.1:8001/login/ e inicia sesión con el correo configurado en `ADMIN_EMAIL` y la contraseña elegida en el paso 3. El panel está en http://127.0.0.1:8001/admin-dashboard/ y la cuenta de cliente en http://127.0.0.1:8001/mi-cuenta/. La documentación de la API está en http://127.0.0.1:8000/docs.

## Notas de producción

- Configura `MONGODB_URL` y `ADMIN_EMAIL` en el entorno del servicio backend.
- El registro público no puede asignar el rol de administrador. Crea o actualiza esa cuenta desde la terminal del backend con `python -m app.bootstrap_admin`; la contraseña se solicita de forma oculta y solo se guarda su hash.
- Configura `API_BASE_URL` en el entorno del frontend para que apunte al servicio FastAPI desplegado.
- Despliega el `render.yaml` de la raíz como un Blueprint de Render para crear `capzone-web-api` y `capzone-web`.
- No incluyas la cadena de conexión de Atlas ni otras credenciales en Git.
