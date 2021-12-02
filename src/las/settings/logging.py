import os
import sys
from pathlib import Path

from .common import env, BASE_DIR

HANDLERS = {
    'stream': {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'standard'
    },
    'django_request': {
        'level': 'ERROR',
        'class': 'logging.handlers.WatchedFileHandler',
        'filename': os.path.join(BASE_DIR, 'logs', 'django_request.log'),
        'formatter': 'standard'
    },
}
FORMATTERS = {
    'standard': {
        'format': '%(asctime)s [%(levelname)s %(process)d]: %(message)s'
    },
}
LOGGING_FLUENTD_ENABLED = env.bool('LOGGING_FLUENTD_ENABLED', default=False)
if LOGGING_FLUENTD_ENABLED:
    FORMATTERS['fluentd'] = {
        '()': 'fluent.handler.FluentRecordFormatter',
        'format': {
            'level': '%(levelname)s',
            'hostname': '%(hostname)s',
            'where': '%(module)s.%(funcName)s',
        }
    }
    HANDLERS['fluentinfo'] = {
        'level': 'DEBUG',
        'class': 'fluent.handler.FluentHandler',
        'formatter': 'fluentd',
        'nanosecond_precision': True,
        'tag': env.str('FLUENT_TAG'),
        'host': env.str('FLUENT_HOST'),
        'port': env.int('FLUENT_PORT'),
    }
LOGGING_CONSOLE_ENABLED = env.bool('LOGGING_CONSOLE_ENABLED', default=False)
if LOGGING_CONSOLE_ENABLED:
    HANDLERS['console'] = {
        'level': 'DEBUG',
        'class': 'logging.StreamHandler',
        'formatter': 'standard',
        'stream': sys.stdout,
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': FORMATTERS,
    'handlers': HANDLERS,
    'loggers': {
        'django.request': {
            'handlers': ['django_request'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}


def add_logger(name, level='DEBUG', directory=''):
    Path(os.path.join(BASE_DIR, 'logs', directory)).mkdir(parents=True, exist_ok=True)

    LOGGING['handlers'][name] = {
        'level': level,
        'class': 'logging.handlers.WatchedFileHandler',
        'filename': os.path.join(BASE_DIR, 'logs', directory, name + '.log'),
        'formatter': 'standard',
    }
    handlers = [name]
    if LOGGING_FLUENTD_ENABLED:
        handlers.append('fluentinfo')
    if LOGGING_CONSOLE_ENABLED:
        handlers.append('console')
    LOGGING['loggers'][name] = {
        'handlers': handlers,
        'level': level,
        'propagate': True,
    }

# тут добавляем новые логгеры
add_logger('register_add')
add_logger('register_cancel')
add_logger('register_edit')
