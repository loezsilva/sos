import hashlib
import time

from django.conf import settings
from django.core.cache import cache


class LimiteCutucaoPublico:
    """Rate limit e cooldown por canal + origem (IP hasheado ou usuário)."""

    @classmethod
    def max_por_minuto(cls):
        return getattr(settings, 'CUTUCAO_PUBLICO_MAX_POR_MINUTO', 3)

    @classmethod
    def cooldown_segundos(cls):
        return getattr(settings, 'CUTUCAO_PUBLICO_COOLDOWN_SEGUNDOS', 15)

    @classmethod
    def chave_origem(cls, request, canal):
        if request.user.is_authenticated:
            origem = f'u:{request.user.pk}'
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
            if getattr(settings, 'CUTUCAO_PUBLICO_CONFIAR_X_FORWARDED_FOR', False):
                encaminhado = request.META.get('HTTP_X_FORWARDED_FOR', '')
                ip = encaminhado.split(',')[0].strip() or ip
            origem = f'ip:{hashlib.sha256(ip.encode()).hexdigest()[:32]}'
        return f'cutucao_publico:{canal.pk}:{origem}'

    @classmethod
    def _restante(cls, chave):
        dados = cache.get(chave)
        if not dados:
            return 0
        if isinstance(dados, dict):
            return max(0, int(dados.get('expira_em', 0) - time.time()))
        return 0

    @classmethod
    def reservar(cls, request, canal):
        """Reserva atomicamente o envio e retorna (ok, código, espera)."""
        base = cls.chave_origem(request, canal)
        agora = time.time()
        cooldown = cls.cooldown_segundos()
        chave_cooldown = f'{base}:cd'

        if cooldown > 0 and not cache.add(
            chave_cooldown,
            {'expira_em': agora + cooldown},
            timeout=cooldown,
        ):
            return False, 'cooldown', cls._restante(chave_cooldown) or cooldown

        chave_rl = f'{base}:rl'
        chave_expiracao = f'{base}:rl:expira'
        cache.add(chave_rl, 0, timeout=60)
        cache.add(chave_expiracao, {'expira_em': agora + 60}, timeout=60)
        quantidade = cache.incr(chave_rl)

        if quantidade > cls.max_por_minuto():
            cache.delete(chave_cooldown)
            return False, 'rate_limit', cls._restante(chave_expiracao) or 60

        return True, '', 0
