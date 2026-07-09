from django.db import models
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
    eh_vip = models.BooleanField('VIP', default=False)

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
    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        ATENDIDA = 'atendida', 'Atendida'
        RECUSADA = 'recusada', 'Recusada'
        RESPONDIDA = 'respondida', 'Respondida'

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

    class Meta:
        verbose_name = 'Buzina'
        verbose_name_plural = 'Buzinas'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.remetente} → {self.destinatario}'

    @classmethod
    def enviar(cls, remetente, destinatario_id):
        membro = MembroCirculo.objects.filter(
            dono=remetente, contato_id=destinatario_id
        ).select_related('contato').first()
        if not membro or not membro.pode_buzinar:
            raise ValueError('Contato indisponível para buzina.')

        buzina = cls.objects.create(
            remetente=remetente,
            destinatario_id=destinatario_id,
        )
        cls._notificar(
            str(destinatario_id),
            'buzina_recebida',
            {
                'tipo': 'buzina_recebida',
                'buzina_id': str(buzina.id),
                'remetente_id': str(remetente.id),
                'remetente_nome': remetente.name or remetente.username,
                'remetente_avatar': buzina.remetente.avatar.url if buzina.remetente.avatar else '',
            },
        )
        return buzina

    def responder(self, resposta_rapida=None, recusar=False, atender=False):
        if recusar:
            self.status = self.Status.RECUSADA
            rotulo = 'Recusou a buzina'
            campos = ['status', 'updated_at']
        elif atender:
            self.status = self.Status.ATENDIDA
            rotulo = 'Atendeu a buzina'
            campos = ['status', 'updated_at']
        else:
            self.resposta_rapida = resposta_rapida
            self.status = self.Status.RESPONDIDA
            rotulo = self.get_resposta_rapida_display()
            campos = ['resposta_rapida', 'status', 'updated_at']

        self.save(update_fields=campos)
        self.notificar_remetente(rotulo, self.resposta_rapida or '')

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
