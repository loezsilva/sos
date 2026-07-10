from apps.dashboard.models import Buzina


def notificacoes(request):
    if not request.user.is_authenticated:
        return {'nao_lidas': 0, 'notificacoes_recentes': []}

    usuario = request.user
    recentes = [
        {
            'buzina': b,
            'membro_id': b.membro_id_para(usuario),
            'contato': b.contato_para(usuario),
            'rotulo': b.rotulo_atividade(usuario),
            'lida': b.lida_em is not None,
        }
        for b in Buzina.objects.atividades_recentes(usuario, 15)
    ]
    return {
        'nao_lidas': Buzina.objects.nao_lidas_de(usuario).count(),
        'notificacoes_recentes': recentes,
    }
