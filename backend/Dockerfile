# Dockerfile de backend
FROM python:3.8

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez le code source de votre API dans le conteneur
COPY . .

# Installez les dépendances de votre application
RUN pip install -r requirements.txt

# Exposez le port sur lequel votre API écoutera
EXPOSE 8000

# Démarrez votre application
CMD ["python", "FastAPI.py"]