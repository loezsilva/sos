from apps.dashboard.models import Buzina, MembroCirculo, StatusPresenca
from apps.dashboard.presenca import Presenca


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


def disponibilidade(request):
    if not request.user.is_authenticated:
        return {}

    status_orm = (
        MembroCirculo.objects.filter(contato=request.user)
        .values_list('status', flat=True)
        .first()
    ) or StatusPresenca.OFFLINE
    conectado = Presenca.esta_conectado(request.user.id)

    if not conectado:
        status_efetivo = StatusPresenca.OFFLINE
    else:
        status_efetivo = status_orm

    return {
        'disponibilidade_status': status_efetivo,
        'disponibilidade_preferencia': status_orm,
        'disponibilidade_conectado': conectado,
        'disponibilidade_usuario_id': str(request.user.id),
    }
