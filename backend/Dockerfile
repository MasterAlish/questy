FROM python:2.7.18-alpine3.11 as backend
ENV PYTHONUNBUFFERED 1
ENV DEBUG 'True'
WORKDIR /code

# Install nginx to serve static files
RUN apk --no-cache add nginx bash

# Install honcho Procfile-based application manager
# https://honcho.readthedocs.io
RUN python -m pip install honcho --no-cache-dir

# Install uwsgi application server
RUN apk add --no-cache --virtual .uwsgi-build-deps \
        gcc \
        musl-dev \
        linux-headers && \
    python -m pip install uwsgi --no-cache-dir && \
    apk --purge del .uwsgi-build-deps;

# Dockerize delay the starting of the honcho
# until the database container is running and listening on the TCP port.
RUN apk add --no-cache openssl
ENV DOCKERIZE_VERSION v0.6.1
RUN wget "https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz" \
    && tar -C /usr/local/bin -xzvf "dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz" \
    && rm "dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz"

# Install application dependencies
COPY requirements.txt .
RUN apk --no-cache add \
        jpeg \
        libffi \
        postgresql-libs \
        && \
    apk --no-cache add \
        --virtual .requirements-build-deps \
        gcc \
        jpeg-dev \
        libffi-dev \
        musl-dev \
        postgresql-dev \
        zlib-dev \
        && \
    python -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .requirements-build-deps

COPY backend .

RUN  mkdir -p /run/nginx/
COPY docker/nginx-app.conf /etc/nginx/conf.d/default.conf
COPY docker/uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY docker/uwsgi_params /etc/nginx/uwsgi_params
COPY docker/Procfile /code/Procfile

VOLUME [ "/code/media" ]
EXPOSE 8000

ENTRYPOINT [ "/code/entrypoint.sh" ]
CMD [ "/usr/local/bin/honcho", "-f", "/code/Procfile", "start" ]