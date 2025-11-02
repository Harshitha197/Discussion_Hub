"""
ASGI config for comment_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

# ✅ Step 1: Set environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "comment_system.settings")

# ✅ Step 2: Setup Django before importing routing
django.setup()

# ✅ Step 3: Import your websocket routes
from comments.routing import websocket_urlpatterns

# ✅ Step 4: Create ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
