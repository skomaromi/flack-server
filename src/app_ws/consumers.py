from channels.consumer import AsyncConsumer
from channels.exceptions import StopConsumer
from channels.db import database_sync_to_async

from rest_framework.authtoken.models import Token


class GlobalConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.token = None

        token = self.scope['url_route']['kwargs']['token']

        if await self.check_token_exists(token):
            self.token = token
            await self.send({
                'type': 'websocket.accept'
            })
        else:
            await self.send({
                'type': 'websocket.close'
            })

    async def websocket_receive(self, event):
        if self.token:
            print("message received", event)

        else:
            await self.send({
                "type": "websocket.send",
                "text": "not authenticated!"
            })

    async def websocket_disconnect(self, event):
        print("disconnected", event)
        raise StopConsumer()

    @database_sync_to_async
    def check_token_exists(self, token):
        return Token.objects.filter(key=token).exists()
