from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, RedirectView, TemplateView
import io
import json
import os

import qrcode

from apps.accounts.models import User
from apps.dashboard.models import (
    Buzina,
    CanalPublico,
    ConviteCirculo,
    CutucaoPublico,
    InscricaoNativa,
    InscricaoPush,
    MembroCirculo,
    StatusConvite,
    StatusPresenca,
)
from apps.dashboard.atividades import (
    alertas_pendentes,
    atividades_mescladas,
    nao_lidas_total,
)
from apps.dashboard.forms import FormCutucaoPublico
from apps.dashboard.limite_publico import LimiteCutucaoPublico
from apps.dashboard.presenca import Presenca
from apps.dashboard.push import ServicoPush
from apps.dashboard.push_nativo import ServicoPushNativo


SESSAO_NICKNAME_PUBLICO = 'cutucao_publico_nickname'


class PaginaInicioView(TemplateView):
    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ['dashboard/index.html']
        return ['landing/index.html']

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            membros = MembroCirculo.objects.do_usuario(self.request.user)
            favoritos = membros.filter(eh_vip=True)
            contexto['total_chamadas'] = Buzina.objects.filter(
                destinatario=self.request.user,
            ).count()
            contexto['membros'] = membros
            contexto['total_online'] = sum(
                1 for m in membros if m.status_para_dono() == StatusPresenca.ONLINE
            )
            contexto['favoritos'] = favoritos
            contexto['pode_buzinar_favoritos'] = any(m.pode_buzinar for m in favoritos)
        else:
            contexto['total_chamadas'] = 0
            contexto['membros'] = MembroCirculo.objects.none()
            contexto['favoritos'] = MembroCirculo.objects.none()
            contexto['total_online'] = 0
            contexto['pode_buzinar_favoritos'] = False
        return contexto


class PaginaProximosView(TemplateView):
    template_name = 'dashboard/proximos.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        termo_busca = self.request.GET.get('q', '').strip()
        contexto['termo_busca'] = termo_busca

        if self.request.user.is_authenticated:
            membros = MembroCirculo.objects.do_usuario(self.request.user).buscar(
                termo_busca
            )
            contexto['membros'] = membros
            contexto['total_online'] = sum(
                1 for m in membros if m.status_para_dono() == StatusPresenca.ONLINE
            )
            contexto['convites_recebidos'] = ConviteCirculo.objects.pendentes_para(
                self.request.user
            )
            contexto['url_conectar'] = self.request.build_absolute_uri(
                reverse(
                    'dashboard:conectar_usuario',
                    kwargs={'username': self.request.user.username},
                )
            )
            canal = CanalPublico.obter_ou_criar_para(self.request.user)
            contexto['canal_publico'] = canal
            contexto['url_cutucar'] = self.request.build_absolute_uri(
                reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
            )
        else:
            contexto['membros'] = MembroCirculo.objects.none()
            contexto['total_online'] = 0
            contexto['convites_recebidos'] = ConviteCirculo.objects.none()

        return contexto


class MeuQrCodeView(LoginRequiredMixin, View):
    def get(self, request):
        url = request.build_absolute_uri(
            reverse(
                'dashboard:conectar_usuario',
                kwargs={'username': request.user.username},
            )
        )
        imagem = qrcode.make(url)
        buffer = io.BytesIO()
        imagem.save(buffer, format='PNG')
        return HttpResponse(buffer.getvalue(), content_type='image/png')


class ConectarUsuarioView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/conectar.html'

    def dispatch(self, request, *args, **kwargs):
        self.destino = get_object_or_404(User, username__iexact=kwargs['username'])
        if request.user.is_authenticated and request.user.pk == self.destino.pk:
            messages.info(request, 'Este é o seu próprio link de conexão.')
            return HttpResponseRedirect(reverse('dashboard:proximos'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['destino'] = self.destino
        contexto['ja_nos_proximos'] = MembroCirculo.objects.filter(
            dono=self.request.user,
            contato=self.destino,
        ).exists()
        contexto['convite_pendente'] = ConviteCirculo.objects.filter(
            remetente=self.request.user,
            destinatario=self.destino,
            status='pendente',
        ).exists()
        return contexto

    def post(self, request, *args, **kwargs):
        try:
            convite = ConviteCirculo.enviar(request.user, self.destino)
            if convite.status == StatusConvite.ACEITO:
                messages.success(
                    request,
                    f'Vocês agora estão conectados com {self.destino.name or self.destino.username}.',
                )
            else:
                messages.success(
                    request,
                    f'Convite enviado para {self.destino.name or self.destino.username}.',
                )
        except ValidationError as erro:
            messages.error(request, erro.messages[0])
        return HttpResponseRedirect(reverse('dashboard:proximos'))


class ConvidarPorUsernameView(LoginRequiredMixin, View):
    def post(self, request):
        username = request.POST.get('username', '').strip().lstrip('@')
        if not username:
            messages.error(request, 'Informe um username.')
            return HttpResponseRedirect(reverse('dashboard:proximos'))
        destino = User.objects.filter(username__iexact=username).first()
        if not destino:
            messages.error(request, f'Ninguém encontrado com o username “{username}”.')
            return HttpResponseRedirect(reverse('dashboard:proximos'))
        try:
            convite = ConviteCirculo.enviar(request.user, destino)
            if convite.status == StatusConvite.ACEITO:
                messages.success(
                    request,
                    f'Vocês agora estão conectados com {destino.name or destino.username}.',
                )
            else:
                messages.success(
                    request,
                    f'Convite enviado para {destino.name or destino.username}.',
                )
        except ValidationError as erro:
            messages.error(request, erro.messages[0])
        return HttpResponseRedirect(reverse('dashboard:proximos'))


class ResponderConviteView(LoginRequiredMixin, View):
    def post(self, request, convite_id):
        convite = get_object_or_404(
            ConviteCirculo,
            pk=convite_id,
            destinatario=request.user,
        )
        acao = request.POST.get('acao')
        if acao == 'aceitar':
            convite.aceitar()
            messages.success(
                request,
                f'{convite.remetente.name or convite.remetente.username} agora está entre os seus próximos.',
            )
        elif acao == 'recusar':
            convite.recusar()
            messages.info(request, 'Convite recusado.')
        return HttpResponseRedirect(reverse('dashboard:proximos'))


class PaginaConfiguracoesView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/configuracoes.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        canal = CanalPublico.obter_ou_criar_para(self.request.user)
        contexto['canal_publico'] = canal
        contexto['url_cutucar'] = self.request.build_absolute_uri(
            reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        )
        contexto['url_conectar'] = self.request.build_absolute_uri(
            reverse(
                'dashboard:conectar_usuario',
                kwargs={'username': self.request.user.username},
            )
        )
        contexto['push_configurado'] = ServicoPush.configurado()
        contexto['push_nativo_configurado'] = ServicoPushNativo.configurado()
        contexto['push_ativo'] = InscricaoPush.objects.filter(
            usuario=self.request.user,
        ).exists()
        contexto['push_nativo_ativo'] = InscricaoNativa.objects.filter(
            usuario=self.request.user,
        ).exists()
        return contexto


class RedirecionarPerfilParaChamarView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            'dashboard:chamar_contato', kwargs={'membro_id': kwargs['membro_id']}
        )


class PaginaChamarContatoView(LoginRequiredMixin, DetailView):
    model = MembroCirculo
    template_name = 'dashboard/chamar_contato.html'
    context_object_name = 'membro'
    pk_url_kwarg = 'membro_id'

    def get_queryset(self):
        return MembroCirculo.objects.do_usuario(self.request.user)


class EnviarBuzinaView(LoginRequiredMixin, View):
    def post(self, request):
        destinatario_id = request.POST.get('destinatario_id')
        if not destinatario_id:
            return JsonResponse({'erro': 'Destinatário obrigatório.'}, status=400)

        mensagem = request.POST.get('mensagem', '').strip()[:80]

        try:
            buzina = Buzina.enviar(request.user, destinatario_id, mensagem=mensagem)
        except ValueError as erro:
            return JsonResponse({'erro': str(erro)}, status=400)

        return JsonResponse(
            {
                'ok': True,
                'buzina_id': str(buzina.id),
                'destinatario_nome': buzina.destinatario.name
                or buzina.destinatario.username,
                'destinatario_avatar': (
                    buzina.destinatario.avatar.url if buzina.destinatario.avatar else ''
                ),
                'silenciada': getattr(buzina, 'silenciada', False),
            }
        )


class EnviarBuzinaFavoritosView(LoginRequiredMixin, View):
    def post(self, request):
        mensagem = request.POST.get('mensagem', '').strip()[:80]
        try:
            buzinas = Buzina.enviar_favoritos(request.user, mensagem=mensagem)
        except ValueError as erro:
            return JsonResponse({'erro': str(erro)}, status=400)

        return JsonResponse(
            {
                'ok': True,
                'buzinas': [
                    {
                        'buzina_id': str(b.id),
                        'destinatario_nome': b.destinatario.name
                        or b.destinatario.username,
                        'destinatario_avatar': (
                            b.destinatario.avatar.url if b.destinatario.avatar else ''
                        ),
                    }
                    for b in buzinas
                ],
            }
        )


class AlternarDisponibilidadeView(LoginRequiredMixin, View):
    def post(self, request):
        modo = request.POST.get('modo', '').strip()
        try:
            status = Presenca.alternar_disponibilidade(request.user.id, modo)
        except ValueError as erro:
            return JsonResponse({'erro': str(erro)}, status=400)

        return JsonResponse(
            {
                'ok': True,
                'status': status,
                'modo': 'nao_perturbe'
                if status == StatusPresenca.OCUPADO
                else 'disponivel',
            }
        )


class AlternarFavoritoView(LoginRequiredMixin, View):
    def post(self, request, membro_id):
        membro = (
            MembroCirculo.objects.do_usuario(request.user).filter(pk=membro_id).first()
        )
        if not membro:
            return JsonResponse({'erro': 'Membro não encontrado.'}, status=404)

        membro.eh_vip = not membro.eh_vip
        membro.save(update_fields=['eh_vip', 'updated_at'])
        return JsonResponse({'ok': True, 'eh_favorito': membro.eh_vip})


class NotificacoesView(LoginRequiredMixin, View):
    def get(self, request):
        itens = []
        for _, tipo, obj in atividades_mescladas(request.user, 15):
            itens.append(obj.serializar_notificacao(request.user))
        return JsonResponse(
            {
                'ok': True,
                'nao_lidas': nao_lidas_total(request.user),
                'itens': itens,
            }
        )


class MarcarNotificacoesLidasView(LoginRequiredMixin, View):
    def post(self, request):
        Buzina.marcar_lidas(request.user)
        CutucaoPublico.marcar_lidas(request.user)
        return JsonResponse({'ok': True, 'nao_lidas': 0})


class ResponderBuzinaView(LoginRequiredMixin, View):
    def post(self, request, buzina_id):
        buzina = Buzina.objects.filter(
            id=buzina_id,
            destinatario=request.user,
            status=Buzina.Status.PENDENTE,
        ).first()

        if not buzina:
            return JsonResponse({'erro': 'Buzina não encontrada.'}, status=404)

        recusar = request.POST.get('recusar') == '1'
        resposta = request.POST.get('resposta_rapida')

        if recusar:
            ok = buzina.responder(recusar=True)
        elif resposta in Buzina.RespostaRapida.values:
            ok = buzina.responder(resposta_rapida=resposta)
        else:
            ok = buzina.responder(atender=True)

        if not ok:
            return JsonResponse({'erro': 'Buzina já foi encerrada.'}, status=409)

        return JsonResponse({'ok': True})


class EncerrarBuzinaView(LoginRequiredMixin, View):
    def post(self, request, buzina_id):
        buzina = Buzina.objects.filter(
            id=buzina_id,
            remetente=request.user,
        ).first()

        if not buzina:
            return JsonResponse({'erro': 'Buzina não encontrada.'}, status=404)

        if buzina.status != Buzina.Status.PENDENTE:
            return JsonResponse(
                {'ok': True, 'status': buzina.status, 'ja_encerrada': True}
            )

        motivo = request.POST.get('motivo', 'usuario')
        if motivo not in ('usuario', 'timeout'):
            motivo = 'usuario'

        ok = buzina.encerrar(motivo=motivo)
        buzina.refresh_from_db()
        return JsonResponse(
            {
                'ok': True,
                'status': buzina.status,
                'encerrada': ok,
            }
        )


class ServiceWorkerView(View):
    def get(self, request):
        caminho = os.path.join(settings.BASE_DIR, 'static', 'sw.js')
        with open(caminho, 'rb') as arquivo:
            conteudo = arquivo.read()
        resposta = HttpResponse(conteudo, content_type='application/javascript')
        resposta['Service-Worker-Allowed'] = '/'
        resposta['Cache-Control'] = 'no-cache'
        return resposta


class ChaveVapidView(LoginRequiredMixin, View):
    def get(self, request):
        if not ServicoPush.configurado():
            return JsonResponse(
                {'erro': 'Push não configurado no servidor.'}, status=503
            )
        return JsonResponse(
            {
                'ok': True,
                'chave_publica': settings.VAPID_PUBLIC_KEY,
            }
        )


class InscreverPushView(LoginRequiredMixin, View):
    def post(self, request):
        if not ServicoPush.configurado():
            return JsonResponse(
                {'erro': 'Push não configurado no servidor.'}, status=503
            )

        endpoint = request.POST.get('endpoint')
        p256dh = request.POST.get('p256dh')
        auth = request.POST.get('auth')

        if not endpoint:
            try:
                dados = json.loads(request.body or '{}')
            except json.JSONDecodeError:
                dados = {}
            endpoint = dados.get('endpoint')
            chaves = dados.get('keys') or {}
            p256dh = p256dh or chaves.get('p256dh')
            auth = auth or chaves.get('auth')

        if not endpoint or not p256dh or not auth:
            return JsonResponse({'erro': 'Inscrição push incompleta.'}, status=400)

        ServicoPush.inscrever(
            request.user,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        return JsonResponse({'ok': True})


class DesinscreverPushView(LoginRequiredMixin, View):
    def post(self, request):
        endpoint = request.POST.get('endpoint')
        if not endpoint:
            try:
                dados = json.loads(request.body or '{}')
            except json.JSONDecodeError:
                dados = {}
            endpoint = dados.get('endpoint')
        removidas = ServicoPush.desinscrever(request.user, endpoint=endpoint)
        return JsonResponse({'ok': True, 'removidas': removidas})


class BuzinasPendentesView(LoginRequiredMixin, View):
    def get(self, request):
        return JsonResponse(
            {'ok': True, 'pendentes': alertas_pendentes(request.user)}
        )


class InscreverPushNativoView(LoginRequiredMixin, View):
    def post(self, request):
        if not ServicoPushNativo.configurado():
            return JsonResponse(
                {'erro': 'Push nativo não configurado no servidor.'}, status=503
            )

        token = request.POST.get('token')
        plataforma = request.POST.get('plataforma')
        device_id = request.POST.get('device_id', '')

        if not token:
            try:
                dados = json.loads(request.body or '{}')
            except json.JSONDecodeError:
                dados = {}
            token = dados.get('token')
            plataforma = plataforma or dados.get('plataforma')
            device_id = device_id or dados.get('device_id', '')

        if not token or plataforma not in ('android', 'ios'):
            return JsonResponse({'erro': 'Token ou plataforma inválidos.'}, status=400)

        ServicoPushNativo.inscrever(
            request.user,
            token=token,
            plataforma=plataforma,
            device_id=device_id,
        )
        return JsonResponse({'ok': True})


class DesinscreverPushNativoView(LoginRequiredMixin, View):
    def post(self, request):
        token = request.POST.get('token')
        if not token:
            try:
                dados = json.loads(request.body or '{}')
            except json.JSONDecodeError:
                dados = {}
            token = dados.get('token')
        removidas = ServicoPushNativo.desinscrever(request.user, token=token)
        return JsonResponse({'ok': True, 'removidas': removidas})


class PaginaCutucarPublicoView(TemplateView):
    template_name = 'dashboard/cutucar_publico.html'

    def dispatch(self, request, *args, **kwargs):
        self.canal = CanalPublico.ativo_por_chave(kwargs['chave'])
        if not self.canal:
            from django.http import Http404

            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        autenticado = self.request.user.is_authenticated
        nickname_sessao = self.request.session.get(SESSAO_NICKNAME_PUBLICO, '')
        form = getattr(self, 'form', None) or FormCutucaoPublico(
            autenticado=autenticado,
            initial={'nickname': nickname_sessao} if not autenticado else None,
        )
        contexto.update(
            {
                'canal': self.canal,
                'nome_publico': self.canal.nome_publico,
                'form': form,
                'eh_proprietario': (
                    autenticado and self.request.user.pk == self.canal.proprietario_id
                ),
                'enviado': getattr(self, 'enviado', False),
            }
        )
        return contexto

    def post(self, request, *args, **kwargs):
        autenticado = request.user.is_authenticated
        if autenticado and request.user.pk == self.canal.proprietario_id:
            if request.headers.get('HX-Request') or 'application/json' in (
                request.headers.get('Accept') or ''
            ):
                return JsonResponse(
                    {'ok': False, 'erro': 'Este é o seu próprio link público.'},
                    status=400,
                )
            messages.info(request, 'Este é o seu próprio link público.')
            return self.get(request, *args, **kwargs)

        form = FormCutucaoPublico(request.POST, autenticado=autenticado)
        self.form = form
        quer_json = (
            request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            or 'application/json' in (request.headers.get('Accept') or '')
        )

        if not form.is_valid():
            if quer_json:
                erros = form.errors.get('nickname') or form.non_field_errors()
                return JsonResponse(
                    {'ok': False, 'erro': erros[0] if erros else 'Dados inválidos.'},
                    status=400,
                )
            return self.get(request, *args, **kwargs)

        ok, codigo, restante = LimiteCutucaoPublico.reservar(request, self.canal)
        if not ok:
            msg = (
                f'Aguarde {restante}s antes de cutucar de novo.'
                if codigo == 'cooldown'
                else f'Muitos cutucões. Tente novamente em {restante}s.'
            )
            if quer_json:
                return JsonResponse(
                    {'ok': False, 'erro': msg, 'codigo': codigo, 'aguardar': restante},
                    status=429,
                )
            form.add_error(None, msg)
            return self.get(request, *args, **kwargs)

        try:
            CutucaoPublico.enviar(
                self.canal,
                nickname=form.cleaned_data.get('nickname', ''),
                remetente=request.user if autenticado else None,
            )
        except ValueError as erro:
            if quer_json:
                return JsonResponse({'ok': False, 'erro': str(erro)}, status=400)
            form.add_error(None, str(erro))
            return self.get(request, *args, **kwargs)

        if not autenticado:
            request.session[SESSAO_NICKNAME_PUBLICO] = form.cleaned_data['nickname']

        if quer_json:
            return JsonResponse({'ok': True, 'mensagem': 'Cutucão enviado'})

        self.enviado = True
        return self.get(request, *args, **kwargs)


class CanalPublicoQrView(LoginRequiredMixin, View):
    def get(self, request):
        canal = CanalPublico.obter_ou_criar_para(request.user)
        if not canal.ativo:
            from django.http import Http404

            raise Http404
        url = request.build_absolute_uri(
            reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        )
        imagem = qrcode.make(url)
        buffer = io.BytesIO()
        imagem.save(buffer, format='PNG')
        return HttpResponse(buffer.getvalue(), content_type='image/png')


class GerenciarCanalPublicoView(LoginRequiredMixin, View):
    def post(self, request):
        canal = CanalPublico.obter_ou_criar_para(request.user)
        acao = request.POST.get('acao')
        if acao == 'desativar':
            canal.desativar()
        elif acao == 'ativar':
            canal.ativar()
        elif acao == 'regenerar':
            canal.regenerar()
        else:
            return JsonResponse({'erro': 'Ação inválida.'}, status=400)

        url = request.build_absolute_uri(
            reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {
                    'ok': True,
                    'ativo': canal.ativo,
                    'chave': str(canal.chave),
                    'url': url,
                }
            )
        messages.success(request, 'Canal público atualizado.')
        return HttpResponseRedirect(reverse('dashboard:proximos'))


class DispensarCutucaoPublicoView(LoginRequiredMixin, View):
    def post(self, request, cutucao_id):
        cutucao = CutucaoPublico.objects.filter(
            id=cutucao_id,
            destinatario=request.user,
        ).first()
        if not cutucao:
            return JsonResponse({'erro': 'Cutucão não encontrado.'}, status=404)
        cutucao.dispensar()
        return JsonResponse({'ok': True})
