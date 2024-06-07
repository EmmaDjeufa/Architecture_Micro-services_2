# frontend/Dockerfile

FROM python:3.9



RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y nginx git \
    && rm -rf /var/www/html/*

# Copier les fichiers frontend dans /var/www/html/
ADD ./* /var/www/html/

EXPOSE 8081

ENTRYPOINT ["nginx", "-g", "daemon off;"]
 