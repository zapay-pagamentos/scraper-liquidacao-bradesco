# flake8: noqa
import os
from flask import Flask
from flask_jwt_extended import JWTManager
from django.apps import apps
from django.conf import settings
from celery import Celery
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    environment=os.environ.get('ENVIRONMENT'),
    integrations=[FlaskIntegration()]
)

apps.populate(settings.INSTALLED_APPS)

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = settings.SECRET_KEY
jwt = JWTManager(app)

if os.environ.get('ENVIRONMENT') == 'PRODUCTION':
    celery = Celery(app.name)
else:
    celery = Celery(app.name, namespace='CELERY')

celery.config_from_object('settings')

tasks_files = ['get_receipt.tasks.py']
celery.autodiscover_tasks(tasks_files, force=True)

from get_receipt.views import get_receipt_blueprint

app.register_blueprint(get_receipt_blueprint)
