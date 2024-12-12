from django.urls import path
from .consumers import LiveStreamConsumer

websocket_urlpatterns = [
    path('ws/stream/<str:tab_id>/', LiveStreamConsumer.as_asgi()),
]
