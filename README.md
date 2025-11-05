# CAPZONE

CAPZONE is a hybrid e-commerce project built with Django on the frontend and FastAPI on the backend. The storefront provides a premium catalog experience for urban and sports caps, while the API handles products, authentication, cart, and order logic.

## Architecture

- Backend: FastAPI + Pydantic + MongoDB-ready storage
- Frontend: Django MVT + templates + static assets
- Database: MongoDB Atlas (production) with in-memory fallback for local development

## Local development

Requirements: Python 3.12+ is recommended for compatibility with the current FastAPI/Pydantic stack.

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r backend/requirements.txt
   pip install -r frontend/requirements.txt
   ```
2. Copy environment files:
   ```bash
   copy backend/.env.example backend/.env
   copy frontend/.env.example frontend/.env
   ```
3. Start the backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Start the Django frontend:
   ```bash
   cd frontend
   python manage.py migrate
   python manage.py runserver 0.0.0.0:8000
   ```
5. Visit:
   - Frontend: http://localhost:8000
   - API docs: http://localhost:8000/docs

## Production notes

- Set `MONGODB_URL` in the backend service environment.
- Set `API_BASE_URL` in the frontend environment to the deployed FastAPI service.
- Deploy the root `render.yaml` as a Render Blueprint to create the `capzone-web-api` and `capzone-web` services.
- Enter the Atlas connection string only in the backend service's Render environment variables; never commit it.
- The project is designed to use MongoDB Atlas in production without storing credentials in code.
