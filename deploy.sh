#!/bin/bash

zip -r site.zip system/ jino/ locale/ manage.py requirements.txt tick.sh
scp site.zip masteralish@masteralish.myjino.ru:django/questlabs
rm site.zip
ssh masteralish@masteralish.myjino.ru << END
    cd django/questlabs/
    unzip -uo site.zip
    rm system/local_settings.p*
    mv system/prod_settings.py system/local_settings.py
    source env/bin/activate
    pip install -r requirements.txt
    python manage.py migrate --noinput
    python manage.py loaddata system/fixtures/initial.json
    python manage.py collectstatic --noinput
    touch system/wsgi.py
END

