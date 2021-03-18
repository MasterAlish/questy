FROM python:2.7.18-alpine3.11 as backend
ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY backend .
COPY requirements.txt /app

RUN apk add --no-cache nginx nano bash

RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev linux-headers jpeg-dev zlib-dev && \
 pip install --no-cache-dir -r requirements.txt && \
 apk --purge del .build-deps

RUN  mkdir -p /run/nginx/
COPY docker/nginx-app.conf /etc/nginx/conf.d/default.conf
COPY docker/uwsgi.ini /etc/uwsgi/uwsgi.ini
COPY docker/uwsgi_params /etc/nginx/uwsgi_params

CMD ["uwsgi", "--ini", "/etc/uwsgi/uwsgi.ini", "--daemonize", "uwsgi-ss.log"]