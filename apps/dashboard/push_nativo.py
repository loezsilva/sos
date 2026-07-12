import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)
_firebase_app = None


class ServicoPushNativo:
    @classmethod
    def configurado(cls):
        return bool(
            settings.FIREBASE_CREDENTIALS_JSON
            or settings.GOOGLE_APPLICATION_CREDENTIALS
        )

    @classmethod
    def _firebase(cls):
        global _firebase_app
        if _firebase_app is not None:
            return _firebase_app
        if not cls.configurado():
            return None

        import firebase_admin
        from firebase_admin import credentials

        if firebase_admin._apps:
            _firebase_app = firebase_admin.get_app()
            return _firebase_app

        if settings.FIREBASE_CREDENTIALS_JSON:
            cred = credentials.Certificate(
                json.loads(settings.FIREBASE_CREDENTIALS_JSON)
            )
        else:
            cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)

        _firebase_app = firebase_admin.initialize_app(cred)
        return _firebase_app

    @classmethod
    def inscrever(cls, usuario, token, plataforma, device_id=''):
        from apps.dashboard.models import InscricaoNativa
        from apps.dashboard.presenca import Presenca

        resultado = InscricaoNativa.objects.update_or_create(
            token=token,
            defaults={
                'usuario': usuario,
                'plataforma': plataforma,
                'device_id': (device_id or '')[:255],
            },
        )
        Presenca.sincronizar_por_push(usuario.id)
        return resultado

    @classmethod
    def desinscrever(cls, usuario, token=None):
        from apps.dashboard.models import InscricaoNativa
        from apps.dashboard.presenca import Presenca

        filtro = InscricaoNativa.objects.filter(usuario=usuario)
        if token:
            filtro = filtro.filter(token=token)
        removidas = filtro.delete()[0]
        Presenca.sincronizar_por_push(usuario.id)
        return removidas

    @classmethod
    def enviar_buzina(cls, buzina):
        if not cls.configurado() or getattr(buzina, 'silenciada', False):
            return

        from apps.dashboard.models import PlataformaNativa
        from firebase_admin import messaging

        cls._firebase()
        payload = buzina.payload_push()
        cls._disparar(payload, buzina.destinatario_id, messaging, PlataformaNativa)

    @classmethod
    def enviar_cutucao_publico(cls, cutucao):
        if not cls.configurado():
            return

        from apps.dashboard.models import PlataformaNativa
        from firebase_admin import messaging

        cls._firebase()
        payload = cutucao.payload_push()
        cls._disparar(payload, cutucao.destinatario_id, messaging, PlataformaNativa)

    @classmethod
    def _disparar(cls, payload, destinatario_id, messaging, PlataformaNativa):
        from apps.dashboard.models import InscricaoNativa

        dados = {
            'tipo': payload['tipo'],
            'buzina_id': payload['buzina_id'],
            'cutucao_id': payload.get('cutucao_id', ''),
            'remetente_nome': payload['remetente_nome'],
            'remetente_avatar': payload.get('remetente_avatar', ''),
            'mensagem': payload['mensagem'] or '',
            'url': payload['url'],
            'titulo': payload['titulo'],
            'corpo': payload['corpo'],
            'origem_publica': '1' if payload.get('origem_publica') else '0',
        }

        for inscricao in InscricaoNativa.objects.filter(usuario_id=destinatario_id):
            dados_str = {chave: str(valor) for chave, valor in dados.items()}
            if inscricao.plataforma == PlataformaNativa.ANDROID:
                mensagem = messaging.Message(
                    token=inscricao.token,
                    data=dados_str,
                    android=messaging.AndroidConfig(priority='high'),
                )
            else:
                mensagem = messaging.Message(
                    token=inscricao.token,
                    notification=messaging.Notification(
                        title=payload['titulo'],
                        body=payload['corpo'],
                    ),
                    data=dados_str,
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                alert=messaging.ApsAlert(
                                    title=payload['titulo'],
                                    body=payload['corpo'],
                                ),
                                sound='buzina.wav',
                                category='BUZINA',
                            ),
                        ),
                    ),
                )
            cls._enviar(mensagem, inscricao.pk)

    @classmethod
    def _enviar(cls, mensagem, inscricao_id):
        from apps.dashboard.models import InscricaoNativa
        from firebase_admin import messaging
        from firebase_admin.exceptions import FirebaseError

        try:
            messaging.send(mensagem)
        except FirebaseError as erro:
            codigo = getattr(erro, 'code', '')
            if codigo in ('NOT_FOUND', 'UNREGISTERED', 'INVALID_ARGUMENT'):
                InscricaoNativa.objects.filter(pk=inscricao_id).delete()
            else:
                logger.error('Push nativo falhou: %s', erro)
