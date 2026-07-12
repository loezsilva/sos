import json
import logging

from django.conf import settings
from py_vapid import Vapid
from pywebpush import WebPushException, webpush

logger = logging.getLogger(__name__)
_vapid = None


class ServicoPush:
    @classmethod
    def configurado(cls):
        return bool(settings.VAPID_PUBLIC_KEY and settings.VAPID_PRIVATE_KEY)

    @classmethod
    def _vapid(cls):
        global _vapid
        if _vapid is None and cls.configurado():
            _vapid = Vapid.from_pem(settings.VAPID_PRIVATE_KEY.encode())
        return _vapid

    @classmethod
    def inscrever(cls, usuario, endpoint, p256dh, auth, user_agent=''):
        from apps.dashboard.models import InscricaoPush
        from apps.dashboard.presenca import Presenca

        resultado = InscricaoPush.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'usuario': usuario,
                'p256dh': p256dh,
                'auth': auth,
                'user_agent': (user_agent or '')[:255],
            },
        )
        Presenca.sincronizar_por_push(usuario.id)
        return resultado

    @classmethod
    def desinscrever(cls, usuario, endpoint=None):
        from apps.dashboard.models import InscricaoPush
        from apps.dashboard.presenca import Presenca

        filtro = InscricaoPush.objects.filter(usuario=usuario)
        if endpoint:
            filtro = filtro.filter(endpoint=endpoint)
        removidas = filtro.delete()[0]
        Presenca.sincronizar_por_push(usuario.id)
        return removidas

    @classmethod
    def enviar_buzina(cls, buzina):
        if not cls.configurado() or getattr(buzina, 'silenciada', False):
            return

        from apps.dashboard.models import InscricaoPush

        payload = buzina.payload_push()
        for inscricao_id in InscricaoPush.objects.filter(
            usuario_id=buzina.destinatario_id,
        ).values_list('id', flat=True):
            cls._enviar(inscricao_id, payload)

    @classmethod
    def enviar_cutucao_publico(cls, cutucao):
        if not cls.configurado():
            return

        from apps.dashboard.models import InscricaoPush

        payload = cutucao.payload_push()
        for inscricao_id in InscricaoPush.objects.filter(
            usuario_id=cutucao.destinatario_id,
        ).values_list('id', flat=True):
            cls._enviar(inscricao_id, payload)

    @classmethod
    def _enviar(cls, inscricao_id, payload):
        from apps.dashboard.models import InscricaoPush

        inscricao = InscricaoPush.objects.filter(pk=inscricao_id).first()
        if not inscricao:
            return

        try:
            webpush(
                subscription_info={
                    'endpoint': inscricao.endpoint,
                    'keys': {
                        'p256dh': inscricao.p256dh,
                        'auth': inscricao.auth,
                    },
                },
                data=json.dumps(payload),
                vapid_private_key=cls._vapid(),
                vapid_claims={'sub': f'mailto:{settings.VAPID_ADMIN_EMAIL}'},
            )
        except WebPushException as erro:
            status = erro.response.status_code if erro.response else None
            if status in (404, 410):
                inscricao.delete()
            else:
                logger.error('Push falhou (%s): %s', status, erro)
