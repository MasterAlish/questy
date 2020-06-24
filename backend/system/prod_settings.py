import os

STATIC_ROOT = '/home/users/m/masteralish/domains/questlabs.my.to/static/'
MEDIA_ROOT = '/home/users/m/masteralish/domains/questlabs.my.to/media/'

DEBUG = False

ALLOWED_HOSTS = ['*', ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'masteralish_questlabs',
        'USER': '046320007_quest',
        'PASSWORD': 'quest123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
