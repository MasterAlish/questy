#!/bin/bash

zip -r site.zip system/ conf/ locale/ manage.py requirements.txt
scp site.zip user1@10.121.2.18:projects/hotstart
rm site.zip
ssh user1@10.121.2.18 << END
    cd projects/hotstart/
    unzip -uo site.zip
    rm system/local_settings.p*
    mv system/prod_settings.py system/local_settings.py
    source env/bin/activate
    pip install -r req.txt
    python manage.py migrate --noinput
    python manage.py loaddata system/fixtures/initial.json
    python manage.py collectstatic --noinput
    touch conf/site_wsgi.ini
    touch system/wsgi.py
END

