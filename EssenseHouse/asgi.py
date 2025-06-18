import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import support_chat.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EssenseHouse.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            support_chat.routing.websocket_urlpatterns
        )
    ),
})
