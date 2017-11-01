import os

STATIC_ROOT = '/var/www/hotstart/static/'
MEDIA_ROOT = '/var/www/hotstart/media/'

DEBUG = False

ALLOWED_HOSTS = ['*',]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hostart',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
