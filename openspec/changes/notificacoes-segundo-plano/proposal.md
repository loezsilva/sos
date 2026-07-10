## Por quê

Hoje a buzina só alerta de forma confiável com a aba do Buzz **aberta e em primeiro plano** (WebSocket + overlay + som). Com o app em segundo plano ou com a aba suspensa, o navegador pode congelar o WS e o usuário não ouve nem vê a chamada — o produto perde o core de "atenção imediata". O roadmap de presença já previa a **camada 2 (Web Push)**; é o momento de implementá-la como PWA.

## O que muda

- Buzz vira **PWA instalável** alinhado ao [PWA Starter / PWABuilder](https://docs.pwabuilder.com/): `manifest.webmanifest` (campos obrigatórios + recomendados, shortcuts, `launch_handler`) + **Service Worker** com Workbox (CDN) na raiz `/sw.js`.
- **Web Push (VAPID)**: o destinatário pode receber notificação do sistema operacional quando a aba está em segundo plano ou fechada (dentro dos limites do navegador).
- Backend persiste **inscrições push** por usuário/dispositivo e envia push ao criar buzina **não silenciada** (respeita não perturbe).
- Toque na notificação **abre o Buzz** na tela de alerta da buzina correspondente.
- Fluxo de **permissão** na central de configurações (e reforço contextual após primeiro login).
- **Sincronização ao voltar ao primeiro plano**: ao focar a aba, busca buzinas pendentes e exibe alerta se o push/WS não tiver sido consumido.
- **Não inclui** nesta change: shell nativo (Capacitor), CallKit, ConnectionService, FCM/APNs direto.

## Capacidades

### Novas capacidades

- `notificacoes-segundo-plano`: PWA, Service Worker, Web Push (VAPID), inscrições, envio de push em buzina, clique na notificação e sync ao retornar ao app.

### Capacidades modificadas

- `buzz`: requisito de chamada recebida passa a exigir alerta também em segundo plano via notificação do SO (quando permissão concedida); buzinas silenciadas não disparam push.

## Impacto

- **Backend**: modelo `InscricaoPush`, envio via `pywebpush`, chaves VAPID em `.env`, hooks em `Buzina.enviar` / notificação.
- **Views/API**: registrar/remover inscrição push, expor chave pública VAPID.
- **Static**: `manifest.webmanifest`, `/sw.js` (Workbox + push), ícones (any + maskable), screenshots para PWABuilder.
- **Templates/JS**: registro do SW, subscribe/unsubscribe, handler de clique na notificação, `visibilitychange` para catch-up.
- **Deploy**: HTTPS obrigatório (já em produção); novas vars `VAPID_*` no Heroku.
- **Testes**: envio push mockado, API de inscrição, regra de não enviar em buzina silenciada.
