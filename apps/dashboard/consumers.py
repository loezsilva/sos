import asyncio
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.dashboard.atividades import alertas_pendentes
from apps.dashboard.presenca import Presenca


class BuzzConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        usuario = self.scope['user']
        if not usuario.is_authenticated:
            await self.close()
            return

        self.usuario_id = usuario.pk
        self.grupo = f'buzz_{usuario.pk}'
        await self.channel_layer.group_add(self.grupo, self.channel_name)
        await self.accept()
        await database_sync_to_async(Presenca.registrar)(
            self.usuario_id, self.channel_name
        )
        await self._entregar_pendentes(usuario)
        await self._entregar_snapshot_presenca()

    async def disconnect(self, close_code):
        if hasattr(self, 'grupo'):
            await self.channel_layer.group_discard(self.grupo, self.channel_name)

        if not hasattr(self, 'usuario_id'):
            return

        zerou = await database_sync_to_async(Presenca.remover)(
            self.usuario_id,
            self.channel_name,
        )
        if zerou:
            usuario_id = self.usuario_id
            await asyncio.sleep(Presenca.DEBOUNCE_SEGUNDOS)
            await database_sync_to_async(Presenca.confirmar_offline)(usuario_id)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data or not hasattr(self, 'usuario_id'):
            return
        try:
            dados = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if dados.get('tipo') == 'ping':
            await database_sync_to_async(Presenca.renovar)(self.usuario_id)

    @database_sync_to_async
    def _pendentes_ativas(self, usuario):
        return alertas_pendentes(usuario)

    async def _entregar_pendentes(self, usuario):
        for payload in await self._pendentes_ativas(usuario):
            await self.send(text_data=json.dumps(payload))

    async def _entregar_snapshot_presenca(self):
        payloads = await database_sync_to_async(Presenca.snapshot_para)(self.usuario_id)
        for payload in payloads:
            await self.send(text_data=json.dumps(payload))

    async def buzina_recebida(self, event):
        await self.send(text_data=json.dumps(event['payload']))

    async def cutucao_publico_recebido(self, event):
        await self.send(text_data=json.dumps(event['payload']))

    async def resposta_recebida(self, event):
        await self.send(text_data=json.dumps(event['payload']))

    async def buzina_encerrada(self, event):
        await self.send(text_data=json.dumps(event['payload']))

    async def presenca_atualizada(self, event):
        await self.send(text_data=json.dumps(event['payload']))
