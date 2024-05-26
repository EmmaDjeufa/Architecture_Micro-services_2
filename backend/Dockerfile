# Utilisez une image de base pour Go (par exemple, golang:1.16)
FROM golang:1.16

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez le code source de votre API dans le conteneur
COPY . .

# Installez les dépendances de votre application (si nécessaire)
RUN go mod download

# Compilez votre application
RUN go build -o my-api

# Exposez le port sur lequel votre API écoutera
EXPOSE 8000

# Démarrez votre application
CMD ["./my-api"]
