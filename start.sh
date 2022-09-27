#!/bin/bash
echo "eval \$(envkey-source)" >> ~/.bashrc
eval $(envkey-source)

echo "Starting celery"
[ -e celeryd.pid ] && rm celeryd.pid
celery -A  app.celery worker -l info -f celery.logs --detach

echo "Starting celery-beat"
[ -e celerybeat.pid ] && rm celerybeat.pid
celery -A app.celery beat -l info -f celery-beat.logs --detach

gunicorn -b 0.0.0.0:5000 wsgi --reload --log-level DEBUG --capture-output --timeout 120