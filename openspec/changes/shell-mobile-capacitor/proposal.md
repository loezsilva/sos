## Por quê

A **camada 2 (PWA + Web Push)** entrega notificação visual no celular, mas browsers impõem teto rígido: sem som customizado confiável, sem vibração sem gesto, sem UI tipo chamada com app fechado. O core do Buzz — **atenção imediata** — no mobile exige **camada 3: shell nativo** empacotado para as lojas.

## O que muda

- App **Capacitor** (Android + iOS) empacotando o Buzz web existente — mesmo backend Django.
- Push nativo via **FCM** (Android) e **APNs** (iOS), com **som customizado** no bundle do app.
- Android: canal de notificação de alta prioridade + **full-screen intent** ao receber buzina (UI tipo chamada).
- iOS: notificação rica com som do bundle; **CallKit** fica como fase opcional posterior.
- Backend: modelo `InscricaoNativa` (token FCM/APNs) + envio via `firebase-admin`; coexistência com Web Push (VAPID) para quem usa só o browser.
- Empacotamento para lojas com **[PWABuilder](https://docs.pwabuilder.com/)** (Google Play, App Store) ou CLI Capacitor.
- **Não inclui** reescrever o frontend — o shell carrega a URL do Buzz (ngrok/produção).

## Capacidades

### Novas capacidades

- `shell-mobile`: projeto Capacitor, plugins push, som nativo, deep link de buzina, build Android/iOS.
- `push-nativo`: tokens FCM/APNs, API de inscrição, envio paralelo ao VAPID, som e prioridade no SO.

### Capacidades modificadas

- `buzz`: chamada recebida no mobile nativo SHALL usar som e vibração do SO sem depender de gesto no WebView; Android SHALL poder exibir tela cheia de chamada.

## Impacto

- **Novo diretório** `mobile/` (Capacitor) no repo ou repo irmão.
- **Backend**: `firebase-admin`, credenciais FCM, endpoint `POST /api/push/nativo/inscrever/`, hook em `Buzina.enviar`.
- **Deploy**: Firebase project, APNs key (iOS), Google Play + Apple Developer accounts.
- **Web/PWA**: permanece para desktop e quem não instala o app; push VAPID continua.
