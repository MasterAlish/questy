#!/bin/bash
set -o nounset -o pipefail -o errexit

if [ "$1" = '/usr/local/bin/honcho' ]; then
    echo 'running migrations'
    /usr/local/bin/python manage.py migrate
    /usr/local/bin/python manage.py collectstatic --noinput
fi
exec "$@"
