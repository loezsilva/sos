MAPA_ROTAS = {
    'index': 'inicio',
    'circulos': 'circulos',
    'configuracoes': 'configuracoes',
}


def rota_ativa(request):
    correspondencia = getattr(request, 'resolver_match', None)
    if correspondencia and correspondencia.namespace == 'dashboard':
        return {'rota_ativa': MAPA_ROTAS.get(correspondencia.url_name, '')}
    return {'rota_ativa': ''}
