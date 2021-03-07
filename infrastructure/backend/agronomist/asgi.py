
import os

from django.core.asgi import get_asgi_application
from django.urls import path, re_path

# Fetch Django ASGI application early to ensure AppRegistry is populated
# before importing consumers and AuthMiddlewareStack that may import ORM
# models.
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "agronomist.settings.production")
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from chatapp.consumers import ChatConsumer
from chatapp.pipeline import shared_pipeline

shared_pipeline.setup()

application = URLRouter([
    path('ws/chat/', AuthMiddlewareStack(ChatConsumer.as_asgi())),
    re_path(r"^.*", django_asgi_app),
])
