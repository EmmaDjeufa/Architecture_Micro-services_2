# backend/Dockerfile
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Copier les fichiers de backend
COPY . /app

WORKDIR /app

# Installer les dépendances
RUN pip install -r requirements.txt

# Exécuter le script de vérification de la disponibilité de PostgreSQL
CMD ["sh", "-c", "python wait_for_postgres.py && uvicorn FastAPI:app --host 0.0.0.0 --port 8000"]
