import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.dashboard.models import Buzina


class BuzzConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        usuario = self.scope['user']
        if not usuario.is_authenticated:
            await self.close()
            return

        self.grupo = f'buzz_{usuario.pk}'
        await self.channel_layer.group_add(self.grupo, self.channel_name)
        await self.accept()
        await self._entregar_pendentes(usuario)

    async def disconnect(self, close_code):
        if hasattr(self, 'grupo'):
            await self.channel_layer.group_discard(self.grupo, self.channel_name)

    @database_sync_to_async
    def _pendentes_ativas(self, usuario):
        return [b.payload_recebida() for b in Buzina.pendentes_ativas_para(usuario)]

    async def _entregar_pendentes(self, usuario):
        for payload in await self._pendentes_ativas(usuario):
            await self.send(text_data=json.dumps(payload))

    async def buzina_recebida(self, event):
        await self.send(text_data=json.dumps(event['payload']))

    async def resposta_recebida(self, event):
        await self.send(text_data=json.dumps(event['payload']))

    async def buzina_encerrada(self, event):
        await self.send(text_data=json.dumps(event['payload']))
