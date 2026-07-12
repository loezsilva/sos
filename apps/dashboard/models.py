import hashlib
import logging
import secrets
import unicodedata
import uuid
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import User
from apps.core.models import BaseModel

logger = logging.getLogger(__name__)


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
        verbose_name='Dono dos próximos',
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
        verbose_name = 'Membro dos próximos'
        verbose_name_plural = 'Membros dos próximos'
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
        }[self.status_para_dono()]

    @property
    def classe_borda_status(self):
        return (
            'border-l-4 border-l-tertiary'
            if self.status_para_dono() == StatusPresenca.OCUPADO
            else ''
        )

    @property
    def classe_card(self):
        return (
            'opacity-75 grayscale-[0.2]'
            if self.status_para_dono() == StatusPresenca.OFFLINE
            else ''
        )

    @property
    def classe_indicador_status(self):
        return {
            StatusPresenca.ONLINE: 'bg-secondary shadow-[0_0_8px_#8E24AA]',
            StatusPresenca.OCUPADO: 'bg-tertiary shadow-[0_0_8px_#E65100]',
            StatusPresenca.OFFLINE: 'bg-outline',
        }[self.status_para_dono()]

    @property
    def rotulo_status_exibicao(self):
        return dict(StatusPresenca.choices).get(
            self.status_para_dono(), self.status_para_dono()
        )

    @classmethod
    def remetente_eh_favorito_de(cls, destinatario_id, remetente_id):
        """VIP do ponto de vista do destinatário (dono=destinatário, contato=remetente)."""
        return cls.objects.filter(
            dono_id=destinatario_id,
            contato_id=remetente_id,
            eh_vip=True,
        ).exists()

    @classmethod
    def sao_favoritos_mutuos(cls, usuario_a_id, usuario_b_id):
        return (
            cls.objects.filter(
                dono_id=usuario_a_id, contato_id=usuario_b_id, eh_vip=True
            ).exists()
            and cls.objects.filter(
                dono_id=usuario_b_id, contato_id=usuario_a_id, eh_vip=True
            ).exists()
        )

    @property
    def sou_favorito_do_contato(self):
        return self.remetente_eh_favorito_de(self.contato_id, self.dono_id)

    @property
    def favoritos_mutuos(self):
        return self.sao_favoritos_mutuos(self.contato_id, self.dono_id)

    def status_para_dono(self):
        """Status exibido ao dono dos próximos (oculta não perturbe entre favoritos mútuos)."""
        from apps.dashboard.presenca import Presenca

        if not Presenca.esta_alcancavel(self.contato_id):
            return StatusPresenca.OFFLINE
        if self.status == StatusPresenca.OFFLINE:
            return StatusPresenca.ONLINE
        if self.status == StatusPresenca.OCUPADO and self.sao_favoritos_mutuos(
            self.contato_id, self.dono_id
        ):
            return StatusPresenca.ONLINE
        return self.status

    @property
    def pode_buzinar(self):
        status = self.status_para_dono()
        if status == StatusPresenca.OFFLINE:
            return False
        if self.status == StatusPresenca.OCUPADO:
            return self.sou_favorito_do_contato or self.sao_favoritos_mutuos(
                self.contato_id, self.dono_id
            )
        return True


class StatusConvite(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    ACEITO = 'aceito', 'Aceito'
    RECUSADO = 'recusado', 'Recusado'


class ConviteCirculoQuerySet(models.QuerySet):
    def pendentes_para(self, usuario):
        return self.filter(
            destinatario=usuario,
            status=StatusConvite.PENDENTE,
        ).select_related('remetente')


class ConviteCirculo(BaseModel):
    remetente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='convites_enviados',
        verbose_name='Remetente',
    )
    destinatario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='convites_recebidos',
        verbose_name='Destinatário',
    )
    status = models.CharField(
        'Status',
        max_length=20,
        choices=StatusConvite.choices,
        default=StatusConvite.PENDENTE,
    )

    objects = ConviteCirculoQuerySet.as_manager()

    class Meta:
        verbose_name = 'Convite de próximos'
        verbose_name_plural = 'Convites de próximos'
        constraints = [
            models.UniqueConstraint(
                fields=['remetente', 'destinatario'],
                condition=models.Q(status=StatusConvite.PENDENTE),
                name='convite_pendente_unico',
            ),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.remetente} → {self.destinatario} ({self.status})'

    @classmethod
    def enviar(cls, remetente, destinatario):
        from django.core.exceptions import ValidationError

        if remetente.pk == destinatario.pk:
            raise ValidationError('Você não pode convidar a si mesmo.')
        if MembroCirculo.objects.filter(dono=remetente, contato=destinatario).exists():
            raise ValidationError('Essa pessoa já está entre os seus próximos.')
        if cls.objects.filter(
            remetente=remetente,
            destinatario=destinatario,
            status=StatusConvite.PENDENTE,
        ).exists():
            raise ValidationError('Já existe um convite pendente para essa pessoa.')
        # Convite inverso pendente: aceitar automaticamente
        inverso = cls.objects.filter(
            remetente=destinatario,
            destinatario=remetente,
            status=StatusConvite.PENDENTE,
        ).first()
        if inverso:
            inverso.aceitar()
            return inverso
        return cls.objects.create(remetente=remetente, destinatario=destinatario)

    def aceitar(self):
        if self.status != StatusConvite.PENDENTE:
            return False
        MembroCirculo.objects.get_or_create(
            dono=self.remetente, contato=self.destinatario
        )
        MembroCirculo.objects.get_or_create(
            dono=self.destinatario, contato=self.remetente
        )
        self.status = StatusConvite.ACEITO
        self.save(update_fields=['status', 'updated_at'])
        ConviteCirculo.objects.filter(
            remetente=self.destinatario,
            destinatario=self.remetente,
            status=StatusConvite.PENDENTE,
        ).update(status=StatusConvite.ACEITO)
        return True

    def recusar(self):
        if self.status != StatusConvite.PENDENTE:
            return False
        self.status = StatusConvite.RECUSADO
        self.save(update_fields=['status', 'updated_at'])
        return True


class BuzinaQuerySet(models.QuerySet):
    STATUS_NOTIFICACAO_REMETENTE = (
        'respondida',
        'atendida',
        'recusada',
        'perdida',
    )

    def historico_de(self, usuario):
        return (
            self.filter(Q(remetente=usuario) | Q(destinatario=usuario))
            .select_related('remetente', 'destinatario')
            .order_by('-created_at')
        )

    def entre(self, usuario, contato):
        return (
            self.filter(
                Q(remetente=usuario, destinatario=contato)
                | Q(remetente=contato, destinatario=usuario),
            )
            .select_related('remetente', 'destinatario')
            .order_by('-created_at')
        )

    def nao_lidas_de(self, usuario):
        return self.filter(lida_em__isnull=True).filter(
            Q(destinatario=usuario)
            | Q(remetente=usuario, status__in=self.STATUS_NOTIFICACAO_REMETENTE),
        )

    def atividades_recentes(self, usuario, limite=15):
        return self.historico_de(usuario).exclude(
            status='cancelada',
        )[:limite]


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
    lida_em = models.DateTimeField('Lida em', null=True, blank=True)

    objects = BuzinaQuerySet.as_manager()

    class Meta:
        verbose_name = 'Buzina'
        verbose_name_plural = 'Buzinas'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.remetente} → {self.destinatario}'

    @property
    def expirada(self):
        return self.created_at <= timezone.now() - self.TEMPO_MAXIMO_ESPERA

    def contato_para(self, usuario):
        if self.destinatario_id == usuario.id:
            return self.remetente
        return self.destinatario

    def direcao_para(self, usuario):
        return 'enviada' if self.remetente_id == usuario.id else 'recebida'

    def tipo_atividade(self, usuario):
        if self.destinatario_id == usuario.id:
            if self.status == self.Status.PENDENTE:
                return 'buzina_recebida'
            return 'buzina_recebida'
        if self.status == self.Status.PERDIDA:
            return 'chamada_perdida'
        if self.status in (
            self.Status.RESPONDIDA,
            self.Status.ATENDIDA,
            self.Status.RECUSADA,
        ):
            return 'resposta_recebida'
        return 'chamada_enviada'

    def rotulo_atividade(self, usuario):
        mapa = {
            'buzina_recebida': 'Cutucão recebido',
            'resposta_recebida': self.get_resposta_rapida_display()
            if self.status == self.Status.RESPONDIDA and self.resposta_rapida
            else self.get_status_display(),
            'chamada_perdida': 'Chamada perdida',
            'chamada_enviada': self.get_status_display(),
        }
        return mapa.get(self.tipo_atividade(usuario), self.get_status_display())

    def membro_id_para(self, usuario):
        contato = self.contato_para(usuario)
        membro = (
            MembroCirculo.objects.filter(
                dono=usuario,
                contato=contato,
            )
            .values_list('id', flat=True)
            .first()
        )
        return str(membro) if membro else None

    def serializar_notificacao(self, usuario):
        contato = self.contato_para(usuario)
        return {
            'buzina_id': str(self.id),
            'tipo': self.tipo_atividade(usuario),
            'rotulo': self.rotulo_atividade(usuario),
            'contato_nome': contato.name or contato.username,
            'contato_avatar': contato.avatar.url if contato.avatar else '',
            'membro_id': self.membro_id_para(usuario),
            'horario': self.created_at.isoformat(),
            'lida': self.lida_em is not None,
            'status': self.status,
            'direcao': self.direcao_para(usuario),
        }

    @classmethod
    def marcar_lidas(cls, usuario):
        return cls.objects.nao_lidas_de(usuario).update(lida_em=timezone.now())

    def payload_recebida(self):
        return {
            'tipo': 'buzina_recebida',
            'buzina_id': str(self.id),
            'remetente_id': str(self.remetente_id),
            'remetente_nome': self.remetente.name or self.remetente.username,
            'remetente_avatar': self.remetente.avatar.url
            if self.remetente.avatar
            else '',
            'mensagem': self.mensagem,
        }

    def payload_push(self):
        nome = self.remetente.name or self.remetente.username
        msg = (self.mensagem or '').strip()
        if msg:
            titulo = f'{nome} te cutucou'
            corpo = f'"{msg}" — toque para responder agora'
        else:
            titulo = f'Chamada urgente — {nome}'
            corpo = f'{nome} precisa da sua atenção. Toque para abrir.'
        return {
            'tipo': 'buzina_recebida',
            'buzina_id': str(self.id),
            'remetente_nome': nome,
            'remetente_avatar': self.remetente.avatar.url
            if self.remetente.avatar
            else '',
            'mensagem': self.mensagem,
            'titulo': titulo,
            'corpo': corpo,
            'url': f'/?buzina={self.id}',
        }

    @classmethod
    def enviar(cls, remetente, destinatario_id, mensagem=''):
        from apps.dashboard.presenca import Presenca

        membro = (
            MembroCirculo.objects.filter(dono=remetente, contato_id=destinatario_id)
            .select_related('contato')
            .first()
        )
        if not membro or not Presenca.esta_alcancavel(destinatario_id):
            raise ValueError('Contato indisponível para buzina.')

        eh_favorito = MembroCirculo.remetente_eh_favorito_de(
            destinatario_id, remetente.pk
        )
        mutuos = MembroCirculo.sao_favoritos_mutuos(destinatario_id, remetente.pk)
        silenciada = (
            membro.status == StatusPresenca.OCUPADO and not eh_favorito and not mutuos
        )

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
        buzina.silenciada = silenciada
        if not silenciada:
            cls._notificar(
                str(destinatario_id), 'buzina_recebida', buzina.payload_recebida()
            )
            from apps.dashboard.push import ServicoPush
            from apps.dashboard.push_nativo import ServicoPushNativo

            ServicoPush.enviar_buzina(buzina)
            ServicoPushNativo.enviar_buzina(buzina)
        return buzina

    @classmethod
    def enviar_favoritos(cls, remetente, mensagem=''):
        from apps.dashboard.presenca import Presenca

        favoritos = MembroCirculo.objects.do_usuario(remetente).filter(eh_vip=True)
        enviadas = []
        for membro in favoritos:
            if not Presenca.esta_alcancavel(membro.contato_id):
                continue
            try:
                enviadas.append(
                    cls.enviar(remetente, membro.contato_id, mensagem=mensagem)
                )
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
            pk=self.pk,
            status=self.Status.PENDENTE,
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
            pk=self.pk,
            status=self.Status.PENDENTE,
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
                'destinatario_nome': self.destinatario.name
                or self.destinatario.username,
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


class PlataformaNativa(models.TextChoices):
    ANDROID = 'android', 'Android'
    IOS = 'ios', 'iOS'


class InscricaoNativa(BaseModel):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inscricoes_push_nativo',
        verbose_name='Usuário',
    )
    token = models.CharField('Token FCM/APNs', max_length=512, unique=True)
    plataforma = models.CharField(
        'Plataforma',
        max_length=10,
        choices=PlataformaNativa.choices,
    )
    device_id = models.CharField(
        'ID do dispositivo', max_length=255, blank=True, default=''
    )

    class Meta:
        verbose_name = 'Inscrição push nativo'
        verbose_name_plural = 'Inscrições push nativo'

    def __str__(self):
        return f'Push nativo ({self.plataforma}) de {self.usuario}'


class InscricaoPush(BaseModel):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inscricoes_push',
        verbose_name='Usuário',
    )
    endpoint = models.URLField('Endpoint', max_length=500, unique=True)
    p256dh = models.CharField('Chave p256dh', max_length=255)
    auth = models.CharField('Chave auth', max_length=255)
    user_agent = models.CharField('User agent', max_length=255, blank=True, default='')

    class Meta:
        verbose_name = 'Inscrição push'
        verbose_name_plural = 'Inscrições push'

    def __str__(self):
        return f'Push de {self.usuario}'


class CanalPublico(BaseModel):
    proprietario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='canal_publico',
        verbose_name='Proprietário',
    )
    chave = models.UUIDField(
        'Chave pública', default=uuid.uuid4, unique=True, editable=False
    )
    ativo = models.BooleanField('Ativo', default=True)
    regenerado_em = models.DateTimeField('Regenerado em', null=True, blank=True)

    class Meta:
        verbose_name = 'Canal público'
        verbose_name_plural = 'Canais públicos'

    def __str__(self):
        return f'Canal de {self.proprietario}'

    @property
    def nome_publico(self):
        return self.proprietario.name.strip() or 'alguém'

    @classmethod
    def obter_ou_criar_para(cls, usuario):
        canal, _ = cls.objects.get_or_create(proprietario=usuario)
        return canal

    @classmethod
    def ativo_por_chave(cls, chave):
        return (
            cls.objects.filter(chave=chave, ativo=True)
            .select_related('proprietario')
            .first()
        )

    def desativar(self):
        if not self.ativo:
            return self
        self.ativo = False
        self.save(update_fields=['ativo', 'updated_at'])
        return self

    def ativar(self):
        if self.ativo:
            return self
        self.ativo = True
        self.save(update_fields=['ativo', 'updated_at'])
        return self

    def regenerar(self):
        self.chave = uuid.uuid4()
        self.ativo = True
        self.regenerado_em = timezone.now()
        self.save(update_fields=['chave', 'ativo', 'regenerado_em', 'updated_at'])
        return self


class CutucaoPublicoQuerySet(models.QuerySet):
    def do_destinatario(self, usuario):
        return self.filter(destinatario=usuario).select_related(
            'destinatario', 'remetente', 'canal'
        )

    def nao_lidas_de(self, usuario):
        return self.filter(destinatario=usuario, lida_em__isnull=True)

    def atividades_recentes(self, usuario, limite=15):
        return (
            self.do_destinatario(usuario)
            .exclude(status=CutucaoPublico.Status.CANCELADA)
            .order_by('-created_at')[:limite]
        )


class CutucaoPublico(BaseModel):
    TEMPO_MAXIMO_ESPERA = timedelta(seconds=45)
    TEMPO_MAXIMO_ALERTA = TEMPO_MAXIMO_ESPERA

    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        RESPONDIDA = 'respondida', 'Respondida'
        ATENDIDA = 'atendida', 'Atendida'
        RECUSADA = 'recusada', 'Recusada'
        CANCELADA = 'cancelada', 'Cancelada'
        PERDIDA = 'perdida', 'Perdida'

    class RespostaRapida(models.TextChoices):
        JA_VOU = 'ja_vou', 'Já vou'
        OCUPADO = 'ocupado', 'Tô ocupado'
        LIGO_DEPOIS = 'ligo_depois', 'Ligo em 5 min'

    canal = models.ForeignKey(
        CanalPublico,
        on_delete=models.CASCADE,
        related_name='cutucoes',
        verbose_name='Canal',
    )
    destinatario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cutucoes_publicos_recebidos',
        verbose_name='Destinatário',
    )
    remetente = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cutucoes_publicos_enviados',
        verbose_name='Remetente autenticado',
    )
    nickname = models.CharField('Nickname', max_length=40, blank=True, default='')
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
    token_visita = models.CharField(
        'Token de visita',
        max_length=64,
        blank=True,
        default='',
        db_index=True,
    )
    lida_em = models.DateTimeField('Lida em', null=True, blank=True)

    objects = CutucaoPublicoQuerySet.as_manager()

    class Meta:
        verbose_name = 'Cutucão público'
        verbose_name_plural = 'Cutucões públicos'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.nome_exibicao} → {self.destinatario}'

    @staticmethod
    def normalizar_nickname(valor):
        normalizado = unicodedata.normalize('NFKC', valor or '')
        if any(unicodedata.category(c).startswith('C') for c in normalizado):
            raise ValueError('Nickname inválido.')
        texto = ' '.join(normalizado.split())
        if len(texto) < 2 or len(texto) > 40:
            raise ValueError('Informe um nickname entre 2 e 40 caracteres.')
        return texto

    @staticmethod
    def gerar_token():
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_token(token):
        return hashlib.sha256((token or '').encode()).hexdigest()

    def conferir_token(self, token):
        if not self.token_visita or not token:
            return False
        return secrets.compare_digest(self.token_visita, self.hash_token(token))

    @property
    def nome_exibicao(self):
        if self.remetente_id:
            return self.remetente.name or self.remetente.username
        return self.nickname

    @property
    def origem_anonima(self):
        return self.remetente_id is None

    @property
    def expirada(self):
        return self.created_at <= timezone.now() - self.TEMPO_MAXIMO_ESPERA

    @property
    def expira_em(self):
        return self.created_at + self.TEMPO_MAXIMO_ESPERA

    def rotulo_desfecho(self):
        if self.status == self.Status.RESPONDIDA and self.resposta_rapida:
            return self.get_resposta_rapida_display()
        if self.status == self.Status.RECUSADA:
            return 'Recusou'
        if self.status == self.Status.PERDIDA:
            return 'Sem resposta'
        if self.status == self.Status.CANCELADA:
            return 'Cancelado'
        if self.status == self.Status.ATENDIDA:
            return 'Atendeu'
        return self.get_status_display()

    def serializar_status(self):
        return {
            'ok': True,
            'cutucao_id': str(self.id),
            'status': self.status,
            'pendente': self.status == self.Status.PENDENTE,
            'resposta_rapida': self.resposta_rapida or '',
            'resposta_rotulo': self.rotulo_desfecho(),
            'destinatario_nome': (
                self.destinatario.name or self.destinatario.username or 'alguém'
            ),
            'expira_em': self.expira_em.isoformat(),
        }

    def payload_recebida(self):
        return {
            'tipo': 'cutucao_publico_recebido',
            'cutucao_id': str(self.id),
            'buzina_id': str(self.id),
            'remetente_nome': self.nome_exibicao,
            'remetente_avatar': (
                self.remetente.avatar.url
                if self.remetente_id and self.remetente.avatar
                else ''
            ),
            'mensagem': '',
            'origem_publica': True,
            'origem_anonima': self.origem_anonima,
            'rotulo_origem': 'pelo link público',
        }

    def payload_push(self):
        nome = self.nome_exibicao
        return {
            'tipo': 'cutucao_publico_recebido',
            'cutucao_id': str(self.id),
            'buzina_id': str(self.id),
            'remetente_nome': nome,
            'remetente_avatar': (
                self.remetente.avatar.url
                if self.remetente_id and self.remetente.avatar
                else ''
            ),
            'mensagem': '',
            'titulo': f'{nome} te cutucou',
            'corpo': f'{nome} usou seu link público. Toque para abrir.',
            'url': f'/?cutucao={self.id}',
            'origem_publica': True,
            'origem_anonima': self.origem_anonima,
        }

    def serializar_notificacao(self, usuario):
        return {
            'buzina_id': str(self.id),
            'cutucao_id': str(self.id),
            'tipo': 'cutucao_publico_recebido',
            'rotulo': (
                self.rotulo_desfecho()
                if self.status != self.Status.PENDENTE
                else 'Cutucão pelo link público'
            ),
            'contato_nome': self.nome_exibicao,
            'contato_avatar': (
                self.remetente.avatar.url
                if self.remetente_id and self.remetente.avatar
                else ''
            ),
            'membro_id': None,
            'horario': self.created_at.isoformat(),
            'lida': self.lida_em is not None,
            'status': self.status,
            'direcao': 'recebida',
            'origem_publica': True,
            'origem_anonima': self.origem_anonima,
        }

    def responder(self, resposta_rapida=None, recusar=False, atender=False):
        if recusar:
            novo_status = self.Status.RECUSADA
            rotulo = 'Recusou'
            extras = {}
        elif atender:
            novo_status = self.Status.ATENDIDA
            rotulo = 'Atendeu'
            extras = {}
        else:
            novo_status = self.Status.RESPONDIDA
            extras = {'resposta_rapida': resposta_rapida}

        atualizadas = CutucaoPublico.objects.filter(
            pk=self.pk,
            status=self.Status.PENDENTE,
        ).update(
            status=novo_status,
            lida_em=timezone.now(),
            updated_at=timezone.now(),
            **extras,
        )
        if not atualizadas:
            return False

        self.refresh_from_db()
        if novo_status == self.Status.RESPONDIDA:
            rotulo = self.get_resposta_rapida_display()
        self.notificar_visitante(rotulo, self.resposta_rapida or '')
        return True

    def dispensar(self):
        return self.responder(recusar=True)

    def cancelar(self):
        return self._encerrar(self.Status.CANCELADA)

    def marcar_perdida(self):
        return self._encerrar(self.Status.PERDIDA)

    def _encerrar(self, novo_status):
        atualizadas = CutucaoPublico.objects.filter(
            pk=self.pk,
            status=self.Status.PENDENTE,
        ).update(status=novo_status, updated_at=timezone.now())
        if not atualizadas:
            return False

        self.refresh_from_db()
        payload = {
            'tipo': 'buzina_encerrada',
            'buzina_id': str(self.id),
            'cutucao_id': str(self.id),
            'motivo': novo_status,
            'origem_publica': True,
        }
        self._notificar(str(self.destinatario_id), 'buzina_encerrada', payload)
        if self.remetente_id:
            self._notificar(str(self.remetente_id), 'buzina_encerrada', payload)
        return True

    def encerrar(self, motivo='usuario'):
        if motivo == 'timeout':
            return self.marcar_perdida()
        return self.cancelar()

    def notificar_visitante(self, resposta_rotulo, resposta=''):
        if not self.remetente_id:
            return
        self._notificar(
            str(self.remetente_id),
            'resposta_recebida',
            {
                'tipo': 'resposta_recebida',
                'buzina_id': str(self.id),
                'cutucao_id': str(self.id),
                'resposta': resposta,
                'resposta_rotulo': resposta_rotulo,
                'destinatario_nome': (
                    self.destinatario.name or self.destinatario.username
                ),
                'origem_publica': True,
            },
        )

    @classmethod
    def marcar_lidas(cls, usuario):
        return cls.objects.nao_lidas_de(usuario).update(lida_em=timezone.now())

    @classmethod
    def limpar_expiradas(cls, destinatario=None):
        filtro = cls.objects.filter(
            status=cls.Status.PENDENTE,
            created_at__lte=timezone.now() - cls.TEMPO_MAXIMO_ESPERA,
        )
        if destinatario is not None:
            filtro = filtro.filter(destinatario=destinatario)

        expiradas = list(filtro.select_related('remetente', 'destinatario'))
        for cutucao in expiradas:
            cutucao.marcar_perdida()
        return expiradas

    @classmethod
    def pendentes_para(cls, usuario):
        cls.limpar_expiradas(destinatario=usuario)
        return (
            cls.objects.do_destinatario(usuario)
            .filter(status=cls.Status.PENDENTE)
            .order_by('-created_at')[:1]
        )

    @classmethod
    def enviar(cls, canal, *, nickname='', remetente=None):
        if not canal.ativo:
            raise ValueError('Canal público indisponível.')

        if remetente is not None and remetente.pk == canal.proprietario_id:
            raise ValueError('Este é o seu próprio link público.')

        if remetente is not None:
            nickname_final = ''
        else:
            nickname_final = cls.normalizar_nickname(nickname)

        token = cls.gerar_token()
        cutucao = cls.objects.create(
            canal=canal,
            destinatario_id=canal.proprietario_id,
            remetente=remetente,
            nickname=nickname_final,
            token_visita=cls.hash_token(token),
        )
        cutucao.token_visita_claro = token
        cutucao._entregar()
        return cutucao

    def _entregar(self):
        from apps.dashboard.push import ServicoPush
        from apps.dashboard.push_nativo import ServicoPushNativo

        entregas = (
            lambda: self._notificar(
                str(self.destinatario_id),
                'cutucao_publico_recebido',
                self.payload_recebida(),
            ),
            lambda: ServicoPush.enviar_cutucao_publico(self),
            lambda: ServicoPushNativo.enviar_cutucao_publico(self),
        )
        for entregar in entregas:
            try:
                entregar()
            except Exception:
                logger.exception(
                    'Falha ao entregar cutucão público %s',
                    self.pk,
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
