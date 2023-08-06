"""
WSGI config for betik_app_boiled_plate project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from ws4redis.uwsgi_runserver import uWSGIWebsocketServer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

_django_app = get_wsgi_application()
_websocket_app = uWSGIWebsocketServer()

def application(environ, start_response):
    if environ.get('PATH_INFO').startswith('/ws/'):
        return _websocket_app(environ, start_response)
    return _django_app(environ, start_response)

