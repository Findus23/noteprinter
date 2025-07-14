"""
ASGI config for noteprinter project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from notes.middleware import TokenAuthMiddleware, TokenAuthMiddlewareAsync

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "noteprinter.settings")

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.security.websocket import AllowedHostsOriginValidator

from notes.consumers import PrintConsumer, RenderConsumer
from notes.routing import websocket_urlpatterns



application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddlewareAsync(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)))
    ),
    "channel": ChannelNameRouter({
        "thumbnails-generate": PrintConsumer.as_asgi(),
        "render-note": RenderConsumer.as_asgi(),
    }),
    # Just HTTP for now. (We can add other protocols later.)
})
