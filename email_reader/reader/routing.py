from django.urls import re_path

from .consumers import EmailConsumer

websocket_urlpatterns = [
    re_path(r'ws/$', EmailConsumer.as_asgi()),
]
