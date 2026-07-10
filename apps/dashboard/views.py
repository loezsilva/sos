from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, RedirectView, TemplateView
import json
import os

from apps.dashboard.models import Buzina, InscricaoPush, MembroCirculo, StatusPresenca
from apps.dashboard.presenca import Presenca
from apps.dashboard.push import ServicoPush


class PaginaInicioView(TemplateView):
    template_name = 'dashboard/index.html'

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


class PaginaCirculosView(TemplateView):
    template_name = 'dashboard/circulos.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        termo_busca = self.request.GET.get('q', '').strip()
        contexto['termo_busca'] = termo_busca

        if self.request.user.is_authenticated:
            membros = MembroCirculo.objects.do_usuario(self.request.user).buscar(termo_busca)
            contexto['membros'] = membros
            contexto['total_online'] = sum(
                1 for m in membros if m.status_para_dono() == StatusPresenca.ONLINE
            )
        else:
            contexto['membros'] = MembroCirculo.objects.none()
            contexto['total_online'] = 0

        return contexto


class PaginaConfiguracoesView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/configuracoes.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['push_configurado'] = ServicoPush.configurado()
        contexto['push_ativo'] = InscricaoPush.objects.filter(
            usuario=self.request.user,
        ).exists()
        return contexto


class RedirecionarPerfilParaChamarView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        return reverse('dashboard:chamar_contato', kwargs={'membro_id': kwargs['membro_id']})


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

        return JsonResponse({
            'ok': True,
            'buzina_id': str(buzina.id),
            'destinatario_nome': buzina.destinatario.name or buzina.destinatario.username,
            'destinatario_avatar': (
                buzina.destinatario.avatar.url if buzina.destinatario.avatar else ''
            ),
            'silenciada': getattr(buzina, 'silenciada', False),
        })


class EnviarBuzinaFavoritosView(LoginRequiredMixin, View):
    def post(self, request):
        mensagem = request.POST.get('mensagem', '').strip()[:80]
        try:
            buzinas = Buzina.enviar_favoritos(request.user, mensagem=mensagem)
        except ValueError as erro:
            return JsonResponse({'erro': str(erro)}, status=400)

        return JsonResponse({
            'ok': True,
            'buzinas': [
                {
                    'buzina_id': str(b.id),
                    'destinatario_nome': b.destinatario.name or b.destinatario.username,
                    'destinatario_avatar': (
                        b.destinatario.avatar.url if b.destinatario.avatar else ''
                    ),
                }
                for b in buzinas
            ],
        })


class AlternarDisponibilidadeView(LoginRequiredMixin, View):
    def post(self, request):
        modo = request.POST.get('modo', '').strip()
        try:
            status = Presenca.alternar_disponibilidade(request.user.id, modo)
        except ValueError as erro:
            return JsonResponse({'erro': str(erro)}, status=400)

        return JsonResponse({
            'ok': True,
            'status': status,
            'modo': 'nao_perturbe' if status == StatusPresenca.OCUPADO else 'disponivel',
        })


class AlternarFavoritoView(LoginRequiredMixin, View):
    def post(self, request, membro_id):
        membro = MembroCirculo.objects.do_usuario(request.user).filter(pk=membro_id).first()
        if not membro:
            return JsonResponse({'erro': 'Membro não encontrado.'}, status=404)

        membro.eh_vip = not membro.eh_vip
        membro.save(update_fields=['eh_vip', 'updated_at'])
        return JsonResponse({'ok': True, 'eh_favorito': membro.eh_vip})


class NotificacoesView(LoginRequiredMixin, View):
    def get(self, request):
        itens = Buzina.objects.atividades_recentes(request.user, 15)
        return JsonResponse({
            'ok': True,
            'nao_lidas': Buzina.objects.nao_lidas_de(request.user).count(),
            'itens': [b.serializar_notificacao(request.user) for b in itens],
        })


class MarcarNotificacoesLidasView(LoginRequiredMixin, View):
    def post(self, request):
        Buzina.marcar_lidas(request.user)
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
            return JsonResponse({'ok': True, 'status': buzina.status, 'ja_encerrada': True})

        motivo = request.POST.get('motivo', 'usuario')
        if motivo not in ('usuario', 'timeout'):
            motivo = 'usuario'

        ok = buzina.encerrar(motivo=motivo)
        buzina.refresh_from_db()
        return JsonResponse({
            'ok': True,
            'status': buzina.status,
            'encerrada': ok,
        })


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
            return JsonResponse({'erro': 'Push não configurado no servidor.'}, status=503)
        return JsonResponse({
            'ok': True,
            'chave_publica': settings.VAPID_PUBLIC_KEY,
        })


class InscreverPushView(LoginRequiredMixin, View):
    def post(self, request):
        if not ServicoPush.configurado():
            return JsonResponse({'erro': 'Push não configurado no servidor.'}, status=503)

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
        pendentes = [
            b.payload_recebida()
            for b in Buzina.pendentes_ativas_para(request.user)
        ]
        return JsonResponse({'ok': True, 'pendentes': pendentes})
