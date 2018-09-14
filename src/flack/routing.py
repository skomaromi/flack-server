from django.conf.urls import url

from channels.routing import ProtocolTypeRouter, URLRouter

from app_ws.consumers import GlobalConsumer

application = ProtocolTypeRouter({
    'websocket': URLRouter([
        url(r'^(?P<token>[a-z0-9]+)/(?P<room>-?[0-9]+)/(?P<message>-?[0-9]+)/$', GlobalConsumer)
    ])
})
