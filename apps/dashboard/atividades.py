from apps.dashboard.models import Buzina, CutucaoPublico


def alertas_pendentes(usuario):
    alertas = list(Buzina.pendentes_ativas_para(usuario))
    alertas.extend(CutucaoPublico.pendentes_para(usuario))
    return [
        alerta.payload_recebida()
        for alerta in sorted(alertas, key=lambda item: item.created_at)
    ]


def atividades_mescladas(usuario, limite=15):
    buzinas = list(Buzina.objects.atividades_recentes(usuario, limite))
    cutucoes = list(CutucaoPublico.objects.atividades_recentes(usuario, limite))
    juntos = sorted(
        [(b.created_at, 'buzina', b) for b in buzinas]
        + [(c.created_at, 'cutucao', c) for c in cutucoes],
        key=lambda item: item[0],
        reverse=True,
    )[:limite]
    return juntos


def nao_lidas_total(usuario):
    return (
        Buzina.objects.nao_lidas_de(usuario).count()
        + CutucaoPublico.objects.nao_lidas_de(usuario).count()
    )
