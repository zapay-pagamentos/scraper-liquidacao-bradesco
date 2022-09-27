import os

INSTALLED_APPS = (
    'get_receipt',
)

SECRET_KEY = os.environ.get('SECRET_KEY')

ENVIRONMENT = os.environ.get('ENVIRONMENT')

if ENVIRONMENT == 'PRODUCTION':
    SQS_ACCESS_KEY_ID = os.environ.get('SQS_ACCESS_KEY_ID')

    SQS_SECRET_ACCESS_KEY = os.environ.get('SQS_SECRET_ACCESS_KEY')

    SQS_REGION = os.environ.get('SQS_REGION')

    SQS_QUEUE_NAME = os.environ.get('SQS_QUEUE_NAME')

    # Celery
    BROKER_URL = f"sqs://{SQS_ACCESS_KEY_ID}:{SQS_SECRET_ACCESS_KEY}@"

    CELERY_ACCEPT_CONTENT = ['application/json']

    CELERY_RESULT_SERIALIZER = 'json'

    CELERY_TASK_SERIALIZER = 'json'

    CELERY_DEFAULT_QUEUE = SQS_QUEUE_NAME

    CELERY_RESULT_BACKEND = None

    BROKER_TRANSPORT_OPTIONS = {
        'region': SQS_REGION,
        'polling_interval': 20,
        'visibility_timeout': 331
    }
else:
    rabbitmq_user = 'zapay'
    rabbitmq_password = 'rabbitzapay'
    rabbitmq_host = 'get_receipt_rabbitmq:5672'
    rabbitmq_vhost = 'zapayvhost'

    CELERY_BROKER_URL = (
        f'amqp://{rabbitmq_user}:{rabbitmq_password}@' +
        f'{rabbitmq_host}/{rabbitmq_vhost}'
    )
