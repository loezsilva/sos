from types import SimpleNamespace

from apps.dashboard.atividades import atividades_mescladas, nao_lidas_total
from apps.dashboard.models import MembroCirculo, StatusPresenca
from apps.dashboard.presenca import Presenca


def notificacoes(request):
    if not request.user.is_authenticated:
        return {'nao_lidas': 0, 'notificacoes_recentes': []}

    usuario = request.user
    recentes = []
    for _, tipo, obj in atividades_mescladas(usuario, 15):
        if tipo == 'buzina':
            recentes.append(
                {
                    'buzina': obj,
                    'membro_id': obj.membro_id_para(usuario),
                    'contato': obj.contato_para(usuario),
                    'rotulo': obj.rotulo_atividade(usuario),
                    'lida': obj.lida_em is not None,
                    'origem_publica': False,
                }
            )
        else:
            contato = obj.remetente or SimpleNamespace(
                name=obj.nickname,
                username=obj.nickname,
                avatar=None,
            )
            recentes.append(
                {
                    'buzina': obj,
                    'membro_id': None,
                    'contato': contato,
                    'rotulo': 'Cutucão pelo link público',
                    'lida': obj.lida_em is not None,
                    'origem_publica': True,
                }
            )

    return {
        'nao_lidas': nao_lidas_total(usuario),
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
    alcancavel = Presenca.esta_alcancavel(request.user.id)

    if not alcancavel:
        status_efetivo = StatusPresenca.OFFLINE
    elif status_orm == StatusPresenca.OFFLINE:
        status_efetivo = StatusPresenca.ONLINE
    else:
        status_efetivo = status_orm

    return {
        'disponibilidade_status': status_efetivo,
        'disponibilidade_preferencia': status_orm,
        'disponibilidade_conectado': alcancavel,
        'disponibilidade_usuario_id': str(request.user.id),
    }
