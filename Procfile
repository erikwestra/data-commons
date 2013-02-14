web:    newrelic-admin run-program gunicorn dataCommons.wsgi -w 4
worker: newrelic-admin run-program python manage.py celeryd -E --loglevel=INFO --no-execv --concurrency=3
