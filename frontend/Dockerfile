# frontend/Dockerfile
FROM nginx:alpine


# Copier le fichier de démarrage du serveur Flask
COPY server.py /usr/share/nginx/html/server.py


COPY . /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
