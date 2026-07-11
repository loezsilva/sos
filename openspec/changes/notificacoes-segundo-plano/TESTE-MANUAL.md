# Teste manual — notificações em segundo plano

## Pré-requisitos

- Redis em `127.0.0.1:6379`
- `VAPID_*` no `.env` (rode `python manage.py gerar_vapid`)
- Dois usuários logados em abas/navegadores diferentes (ex.: `admin` e `alex` após `popular_proximos_demo`)

## Fluxo principal

1. No destinatário: **Configurações → Ativar notificações** e conceda permissão.
2. Minimize a aba ou mude para outra aba.
3. No remetente: buzine o destinatário (contato online, não em não perturbe).
4. **Esperado:** notificação do SO com nome do remetente.
5. Clique na notificação.
6. **Esperado:** Buzz abre/foca e exibe alerta fullscreen da buzina.

## Catch-up ao voltar

1. Com buzina pendente e sem clicar na notificação, volte à aba do Buzz.
2. **Esperado:** alerta fullscreen aparece; notificação do SO some.

## Não perturbe

1. Destinatário em **Não perturbe**; remetente **não** VIP.
2. Buzine → **sem** notificação push (buzina silenciada).

## Validação PWABuilder

Antes de empacotar para lojas, valide em [pwabuilder.com](https://www.pwabuilder.com/):

- [ ] Manifest com `name`, `short_name`, `start_url`, ícones 192/512 + maskable
- [ ] Service Worker em `/sw.js` com escopo `/`
- [ ] `launch_handler.client_mode: focus-existing`
- [ ] Screenshots no manifest
- [ ] Score de installability verde

## iOS

Push no iOS exige PWA instalado na Tela de Início (iOS 16.4+). Use o banner em Configurações como guia.
