import os
import sentry_sdk


def capture_exception(ex: Exception):
    if os.environ.get('ENVIRONMENT') == 'PRODUCTION':
        sentry_sdk.capture_exception(ex)
