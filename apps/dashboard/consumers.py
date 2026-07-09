import json

from channels.generic.websocket import AsyncWebsocketConsumer


class BuzzConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        usuario = self.scope['user']
        if not usuario.is_authenticated:
            await self.close()
            return

        self.grupo = f'buzz_{usuario.pk}'
        await self.channel_layer.group_add(self.grupo, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'grupo'):
            await self.channel_layer.group_discard(self.grupo, self.channel_name)

    async def buzina_recebida(self, event):
        await self.send(text_data=json.dumps(event['payload']))

    async def resposta_recebida(self, event):
        await self.send(text_data=json.dumps(event['payload']))
