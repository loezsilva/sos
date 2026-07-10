from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.views.generic import DetailView, TemplateView

from apps.dashboard.models import Buzina, MembroCirculo, StatusPresenca


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
            contexto['total_online'] = membros.filter(status=StatusPresenca.ONLINE).count()
            contexto['favoritos'] = favoritos
            contexto['pode_buzinar_favoritos'] = favoritos.exclude(
                status=StatusPresenca.OFFLINE,
            ).exists()
        else:
            contexto['total_chamadas'] = 0
            contexto['total_online'] = 0
            contexto['favoritos'] = MembroCirculo.objects.none()
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
            contexto['total_online'] = membros.filter(status=StatusPresenca.ONLINE).count()
        else:
            contexto['membros'] = MembroCirculo.objects.none()
            contexto['total_online'] = 0

        return contexto


class PaginaConfiguracoesView(TemplateView):
    template_name = 'dashboard/configuracoes.html'


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


class AlternarFavoritoView(LoginRequiredMixin, View):
    def post(self, request, membro_id):
        membro = MembroCirculo.objects.do_usuario(request.user).filter(pk=membro_id).first()
        if not membro:
            return JsonResponse({'erro': 'Membro não encontrado.'}, status=404)

        membro.eh_vip = not membro.eh_vip
        membro.save(update_fields=['eh_vip', 'updated_at'])
        return JsonResponse({'ok': True, 'eh_favorito': membro.eh_vip})


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
