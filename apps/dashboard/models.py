from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import User
from apps.core.models import BaseModel


class StatusPresenca(models.TextChoices):
    ONLINE = 'online', 'Online'
    OCUPADO = 'ocupado', 'Ocupado'
    OFFLINE = 'offline', 'Offline'


class MembroCirculoQuerySet(models.QuerySet):
    def do_usuario(self, usuario):
        return self.filter(dono=usuario).select_related('contato')

    def buscar(self, termo):
        if not termo:
            return self
        return self.filter(
            Q(contato__name__icontains=termo) | Q(contato__username__icontains=termo)
        )


class MembroCirculo(BaseModel):
    dono = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='membros_circulo',
        verbose_name='Dono do círculo',
    )
    contato = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='circulos_onde_apareco',
        verbose_name='Contato',
    )
    status = models.CharField(
        'Status',
        max_length=20,
        choices=StatusPresenca.choices,
        default=StatusPresenca.OFFLINE,
    )
    eh_vip = models.BooleanField('Favorito', default=False)

    objects = MembroCirculoQuerySet.as_manager()

    class Meta:
        verbose_name = 'Membro do círculo'
        verbose_name_plural = 'Membros do círculo'
        constraints = [
            models.UniqueConstraint(
                fields=['dono', 'contato'],
                name='membro_circulo_unico',
            ),
        ]
        ordering = ['-status', 'contato__name']

    def __str__(self):
        return f'{self.contato} ({self.get_status_display()})'

    @property
    def nome_exibicao(self):
        return self.contato.name or self.contato.username

    @property
    def classe_cor_status(self):
        return {
            StatusPresenca.ONLINE: 'text-secondary',
            StatusPresenca.OCUPADO: 'text-tertiary',
            StatusPresenca.OFFLINE: 'text-outline',
        }[self.status]

    @property
    def classe_borda_status(self):
        return 'border-l-4 border-l-tertiary' if self.status == StatusPresenca.OCUPADO else ''

    @property
    def classe_card(self):
        return 'opacity-75 grayscale-[0.2]' if self.status == StatusPresenca.OFFLINE else ''

    @property
    def classe_indicador_status(self):
        return {
            StatusPresenca.ONLINE: 'bg-secondary shadow-[0_0_8px_#4cd7f6]',
            StatusPresenca.OCUPADO: 'bg-tertiary shadow-[0_0_8px_#ffb784]',
            StatusPresenca.OFFLINE: 'bg-outline',
        }[self.status]

    @property
    def pode_buzinar(self):
        return self.status != StatusPresenca.OFFLINE


class Buzina(BaseModel):
    TEMPO_MAXIMO_ESPERA = timedelta(seconds=45)

    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        ATENDIDA = 'atendida', 'Atendida'
        RECUSADA = 'recusada', 'Recusada'
        RESPONDIDA = 'respondida', 'Respondida'
        CANCELADA = 'cancelada', 'Cancelada'
        PERDIDA = 'perdida', 'Perdida'

    class RespostaRapida(models.TextChoices):
        JA_VOU = 'ja_vou', 'Já vou'
        OCUPADO = 'ocupado', 'Tô ocupado'
        LIGO_DEPOIS = 'ligo_depois', 'Ligo em 5 min'

    remetente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='buzinas_enviadas',
        verbose_name='Remetente',
    )
    destinatario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='buzinas_recebidas',
        verbose_name='Destinatário',
    )
    status = models.CharField(
        'Status',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
    resposta_rapida = models.CharField(
        'Resposta rápida',
        max_length=20,
        choices=RespostaRapida.choices,
        blank=True,
        null=True,
    )
    mensagem = models.CharField('Mensagem', max_length=80, blank=True, default='')

    class Meta:
        verbose_name = 'Buzina'
        verbose_name_plural = 'Buzinas'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.remetente} → {self.destinatario}'

    @property
    def expirada(self):
        return self.created_at <= timezone.now() - self.TEMPO_MAXIMO_ESPERA

    def payload_recebida(self):
        return {
            'tipo': 'buzina_recebida',
            'buzina_id': str(self.id),
            'remetente_id': str(self.remetente_id),
            'remetente_nome': self.remetente.name or self.remetente.username,
            'remetente_avatar': self.remetente.avatar.url if self.remetente.avatar else '',
            'mensagem': self.mensagem,
        }

    @classmethod
    def enviar(cls, remetente, destinatario_id, mensagem=''):
        membro = MembroCirculo.objects.filter(
            dono=remetente, contato_id=destinatario_id
        ).select_related('contato').first()
        if not membro or not membro.pode_buzinar:
            raise ValueError('Contato indisponível para buzina.')

        # Uma pendente por par: cancela anteriores sem notificar (nova sobrescreve)
        cls.objects.filter(
            remetente=remetente,
            destinatario_id=destinatario_id,
            status=cls.Status.PENDENTE,
        ).update(status=cls.Status.CANCELADA, updated_at=timezone.now())

        buzina = cls.objects.create(
            remetente=remetente,
            destinatario_id=destinatario_id,
            mensagem=(mensagem or '')[:80],
        )
        cls._notificar(str(destinatario_id), 'buzina_recebida', buzina.payload_recebida())
        return buzina

    @classmethod
    def enviar_favoritos(cls, remetente, mensagem=''):
        favoritos = (
            MembroCirculo.objects.do_usuario(remetente)
            .filter(eh_vip=True)
            .exclude(status=StatusPresenca.OFFLINE)
        )
        enviadas = []
        for membro in favoritos:
            try:
                enviadas.append(cls.enviar(remetente, membro.contato_id, mensagem=mensagem))
            except ValueError:
                continue
        if not enviadas:
            raise ValueError('Nenhum favorito disponível para buzinar.')
        return enviadas

    def responder(self, resposta_rapida=None, recusar=False, atender=False):
        if recusar:
            novo_status = self.Status.RECUSADA
            rotulo = 'Recusou a buzina'
            extras = {}
        elif atender:
            novo_status = self.Status.ATENDIDA
            rotulo = 'Atendeu a buzina'
            extras = {}
        else:
            novo_status = self.Status.RESPONDIDA
            extras = {'resposta_rapida': resposta_rapida}

        atualizadas = Buzina.objects.filter(
            pk=self.pk, status=self.Status.PENDENTE,
        ).update(status=novo_status, updated_at=timezone.now(), **extras)
        if not atualizadas:
            return False

        self.refresh_from_db()
        if novo_status == self.Status.RESPONDIDA:
            rotulo = self.get_resposta_rapida_display()
        self.notificar_remetente(rotulo, self.resposta_rapida or '')
        return True

    def cancelar(self):
        return self._encerrar(self.Status.CANCELADA)

    def marcar_perdida(self):
        return self._encerrar(self.Status.PERDIDA)

    def _encerrar(self, novo_status):
        atualizadas = Buzina.objects.filter(
            pk=self.pk, status=self.Status.PENDENTE,
        ).update(status=novo_status, updated_at=timezone.now())
        if not atualizadas:
            return False

        self.refresh_from_db()
        payload = {
            'tipo': 'buzina_encerrada',
            'buzina_id': str(self.id),
            'motivo': novo_status,
        }
        self._notificar(str(self.destinatario_id), 'buzina_encerrada', payload)
        self._notificar(str(self.remetente_id), 'buzina_encerrada', payload)
        return True

    def encerrar(self, motivo='usuario'):
        if motivo == 'timeout':
            return self.marcar_perdida()
        return self.cancelar()

    @classmethod
    def limpar_expiradas(cls, destinatario=None):
        filtro = cls.objects.filter(
            status=cls.Status.PENDENTE,
            created_at__lte=timezone.now() - cls.TEMPO_MAXIMO_ESPERA,
        )
        if destinatario is not None:
            filtro = filtro.filter(destinatario=destinatario)

        expiradas = list(filtro.select_related('remetente', 'destinatario'))
        for buzina in expiradas:
            buzina.marcar_perdida()
        return expiradas

    @classmethod
    def pendentes_ativas_para(cls, usuario):
        cls.limpar_expiradas(destinatario=usuario)
        # Uma por remetente: a mais recente
        vistas = set()
        ativas = []
        for buzina in (
            cls.objects.filter(destinatario=usuario, status=cls.Status.PENDENTE)
            .select_related('remetente')
            .order_by('-created_at')
        ):
            if buzina.remetente_id in vistas:
                continue
            vistas.add(buzina.remetente_id)
            ativas.append(buzina)
        return ativas

    def notificar_remetente(self, resposta_rotulo, resposta=''):
        self._notificar(
            str(self.remetente_id),
            'resposta_recebida',
            {
                'tipo': 'resposta_recebida',
                'buzina_id': str(self.id),
                'resposta': resposta,
                'resposta_rotulo': resposta_rotulo,
                'destinatario_nome': self.destinatario.name or self.destinatario.username,
            },
        )

    @classmethod
    def _notificar(cls, usuario_id, tipo_evento, payload):
        canal = get_channel_layer()
        if canal is None:
            return
        async_to_sync(canal.group_send)(
            f'buzz_{usuario_id}',
            {'type': tipo_evento, 'payload': payload},
        )
