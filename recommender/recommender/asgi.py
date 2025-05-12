"""
ASGI config for recommender project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import chat_bot.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recommender.settings')

application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": application,
    # "websocket": AuthMiddlewareStack(
    #     URLRouter(
    #         chat_bot.routing.websocket_urlpatterns
    #     )
    # ),
    'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    # your routing configuration goes here
                    chat_bot.routing.websocket_urlpatterns
            )
        )
    ),
})