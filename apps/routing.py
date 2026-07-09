from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

from apps.dashboard.consumers import BuzzConsumer

# HTTP continua no urls.py — aqui só WebSocket
websocket_urlpatterns = [
    path('ws/buzz/', BuzzConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
        ),
    }
)

# Mantido vazio para o include HTTP legado em apps/urls.py
urlpatterns = []
