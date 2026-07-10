from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from django_redis import get_redis_connection

from apps.dashboard.models import MembroCirculo, StatusPresenca


class Presenca:
    """Presença efetiva baseada em conexões WebSocket (Redis)."""

    DEBOUNCE_SEGUNDOS = 2
    TTL_SEGUNDOS = 90
    PREFIXO = 'presenca:conexoes:'
    ROTULOS = dict(StatusPresenca.choices)

    @classmethod
    def _chave(cls, usuario_id):
        return f'{cls.PREFIXO}{usuario_id}'

    @classmethod
    def _redis(cls):
        return get_redis_connection('default')

    @classmethod
    def _renovar_ttl(cls, chave):
        cls._redis().expire(chave, cls.TTL_SEGUNDOS)

    @classmethod
    def esta_conectado(cls, usuario_id):
        return cls._redis().scard(cls._chave(usuario_id)) > 0

    @classmethod
    def renovar(cls, usuario_id):
        chave = cls._chave(usuario_id)
        if cls._redis().exists(chave):
            cls._renovar_ttl(chave)

    @classmethod
    def registrar(cls, usuario_id, channel_name):
        """Registra conexão e sincroniza ORM/notificação se necessário."""
        redis = cls._redis()
        chave = cls._chave(usuario_id)
        quantidade = redis.scard(chave)

        # Conexões fantasma (reload/Daphne): limpa e recomeça
        if quantidade > 5:
            redis.delete(chave)
            quantidade = 0

        redis.sadd(chave, channel_name)
        cls._renovar_ttl(chave)

        orm_desatualizado = MembroCirculo.objects.filter(
            contato_id=usuario_id,
            status=StatusPresenca.OFFLINE,
        ).exists()

        cls.espelhar_online(usuario_id)

        # Notifica se era a 1ª conexão real ou se o ORM ainda dizia offline
        if quantidade == 0 or orm_desatualizado:
            cls.notificar_circulo(usuario_id)
            return True
        return False

    @classmethod
    def remover(cls, usuario_id, channel_name):
        """Remove conexão. Retorna True se zerou (candidato a offline)."""
        redis = cls._redis()
        chave = cls._chave(usuario_id)
        redis.srem(chave, channel_name)
        if redis.scard(chave) == 0:
            redis.delete(chave)
            return True
        cls._renovar_ttl(chave)
        return False

    @classmethod
    def sem_conexoes(cls, usuario_id):
        return not cls.esta_conectado(usuario_id)

    @classmethod
    def confirmar_offline(cls, usuario_id):
        """Marca offline se ainda não houver conexões. Retorna True se aplicou."""
        if cls.esta_conectado(usuario_id):
            return False
        cls.espelhar_offline(usuario_id)
        cls.notificar_circulo(usuario_id, forcar_status=StatusPresenca.OFFLINE)
        return True

    @classmethod
    def espelhar_online(cls, usuario_id):
        MembroCirculo.objects.filter(contato_id=usuario_id).exclude(
            status=StatusPresenca.OCUPADO,
        ).update(status=StatusPresenca.ONLINE, updated_at=timezone.now())

    @classmethod
    def espelhar_offline(cls, usuario_id):
        MembroCirculo.objects.filter(contato_id=usuario_id).update(
            status=StatusPresenca.OFFLINE,
            updated_at=timezone.now(),
        )

    @classmethod
    def snapshot_para(cls, dono_id):
        """Presença atual dos contatos do círculo (para catch-up no connect)."""
        payloads = []
        membros = (
            MembroCirculo.objects.filter(dono_id=dono_id)
            .select_related('contato')
            .only('status', 'contato_id', 'contato__name', 'contato__username')
        )
        for membro in membros:
            conectado = cls.esta_conectado(membro.contato_id)
            if conectado and membro.status == StatusPresenca.OFFLINE:
                # Corrige espelho atrasado sem tocar em ocupado
                MembroCirculo.objects.filter(pk=membro.pk).exclude(
                    status=StatusPresenca.OCUPADO,
                ).update(status=StatusPresenca.ONLINE, updated_at=timezone.now())
                status = StatusPresenca.ONLINE
            elif not conectado and membro.status != StatusPresenca.OFFLINE:
                MembroCirculo.objects.filter(pk=membro.pk).update(
                    status=StatusPresenca.OFFLINE,
                    updated_at=timezone.now(),
                )
                status = StatusPresenca.OFFLINE
            else:
                status = membro.status

            contato = membro.contato
            payloads.append({
                'tipo': 'presenca_atualizada',
                'usuario_id': str(membro.contato_id),
                'status': status,
                'status_rotulo': cls.ROTULOS.get(status, status),
                'nome': contato.name or contato.username,
            })
        return payloads

    @classmethod
    def notificar_circulo(cls, usuario_id, forcar_status=None):
        from apps.accounts.models import User

        canal = get_channel_layer()
        if canal is None:
            return

        usuario = User.objects.filter(pk=usuario_id).only('id', 'name', 'username').first()
        if not usuario:
            return

        nome = usuario.name or usuario.username
        membros = MembroCirculo.objects.filter(contato_id=usuario_id).only('dono_id', 'status')

        for membro in membros:
            status = forcar_status or membro.status
            async_to_sync(canal.group_send)(
                f'buzz_{membro.dono_id}',
                {
                    'type': 'presenca_atualizada',
                    'payload': {
                        'tipo': 'presenca_atualizada',
                        'usuario_id': str(usuario_id),
                        'status': status,
                        'status_rotulo': cls.ROTULOS.get(status, status),
                        'nome': nome,
                    },
                },
            )
