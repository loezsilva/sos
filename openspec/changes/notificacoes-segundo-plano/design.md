## Contexto

O Buzz já entrega buzinas em tempo real via **WebSocket** (`BuzzConsumer`), com overlay fullscreen, som (Web Audio) e vibração quando a aba está ativa. A central de notificações in-app e o histórico cobrem leitura posterior, mas não substituem um alerta quando o usuário está em outra aba ou com o navegador minimizado.

O roadmap em `presenca-tempo-real` define três camadas: (1) WS com app aberto, (2) **Web Push** com app em segundo plano/fechado, (3) shell nativo. Esta change implementa a camada 2 como **PWA + Service Worker + VAPID**.

Restrições conhecidas:
- iOS Safari suporta Web Push apenas para PWAs instalados na home screen (iOS 16.4+).
- Android/Chrome desktop funcionam com permissão de notificação.
- HTTPS é obrigatório (exceto localhost).
- Push não substitui UI de chamada tipo telefone — apenas alerta e deep link.

## Objetivos / Não-objetivos

**Objetivos:**
- Destinatário recebe **notificação do SO** ao ser buzinado (buzina não silenciada), mesmo com aba em segundo plano.
- Toque na notificação abre o Buzz e exibe o alerta da buzina.
- Usuário pode **ativar/desativar** push nas configurações.
- Ao voltar ao primeiro plano, sincronizar buzinas pendentes (catch-up).
- Respeitar **não perturbe**: buzina silenciada não envia push.

**Não-objetivos:**
- Capacitor, CallKit, ConnectionService, FCM/APNs nativo.
- Push para respostas ou encerramentos (apenas buzina recebida nesta MVP).
- Sons customizados na notificação do SO (usa som padrão do sistema).
- Perfil do contato / histórico no card (change separada; usuário mencionou mas fora deste escopo).

## Decisões

### 1. Web Push com VAPID (pywebpush)

Par de chaves VAPID em variáveis de ambiente (`VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_ADMIN_EMAIL`). Biblioteca `pywebpush` no backend.

**Alternativa rejeitada:** FCM direto — exige app nativo ou config extra; VAPID é padrão web e funciona com SW.

### 2. Modelo `InscricaoPush`

```python
# usuario, endpoint (unique), p256dh, auth, user_agent, created_at
```

Uma inscrição por endpoint; `update_or_create` no subscribe. Limpar inscrições com resposta 410 Gone do push service.

### 3. Envio no fluxo da buzina

Após `Buzina.enviar` criar registro e `_notificar` WS, chamar `Push.enviar_buzina(destinatario, buzina)` **somente se não silenciada**.

Push em thread/async_to_sync ou task leve — não bloquear resposta HTTP da buzina.

Payload JSON:
```json
{
  "tipo": "buzina_recebida",
  "buzina_id": "...",
  "remetente_nome": "...",
  "url": "/?buzina=<id>"
}
```

### 4. Alinhamento com [PWABuilder](https://docs.pwabuilder.com/)

O Buzz seguirá as práticas do **PWA Starter** (template oficial do PWABuilder) e será validado em [pwabuilder.com](https://www.pwabuilder.com/) antes do empacotamento para lojas (Microsoft, Google Play, iOS via wrapper).

**Campos obrigatórios** (PWABuilder não gera pacote sem eles): `name`, `short_name`, `start_url`, `icons` (192 + 512).

**Campos recomendados** (Lighthouse / score PWABuilder): `description`, `display`, `theme_color`, `background_color`, `orientation`, ícone **maskable**, `screenshots`, `categories`, `shortcuts`.

Referência: [manifest do pwa-starter](https://github.com/pwa-builder/pwa-starter/blob/main/public/manifest.json).

### 5. PWA manifest (`static/manifest.webmanifest`)

Estrutura adaptada do PWA Starter para o Buzz:

```json
{
  "id": "/",
  "scope": "/",
  "name": "Buzz — Atenção imediata",
  "short_name": "Buzz",
  "description": "Chame quem importa com um toque.",
  "start_url": "/?source=pwa",
  "display": "standalone",
  "display_override": ["standalone", "minimal-ui"],
  "orientation": "portrait-primary",
  "theme_color": "#0b1326",
  "background_color": "#0b1326",
  "prefer_related_applications": false,
  "launch_handler": { "client_mode": "focus-existing" },
  "categories": ["social", "lifestyle"],
  "icons": [
    { "src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any" },
    { "src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any" },
    { "src": "/static/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "shortcuts": [
    { "name": "Meus círculos", "short_name": "Círculos", "url": "/circulos/", "icons": [{ "src": "/static/icons/icon-192.png", "sizes": "192x192" }] },
    { "name": "Configurações", "short_name": "Config", "url": "/configuracoes/", "icons": [{ "src": "/static/icons/icon-192.png", "sizes": "192x192" }] }
  ]
}
```

`base.html`: `<link rel="manifest" href="{% static 'manifest.webmanifest' %}">`, `<meta name="theme-color" content="#0b1326">`, meta Apple (`apple-mobile-web-app-capable`, `apple-touch-icon`).

Ícones e splash: gerar via **PWABuilder Studio** ou editor em pwabuilder.com a partir do logo Buzz (cores do `docs/DESIGN.md`).

### 6. Service Worker (`/sw.js` na raiz)

Padrão **pwa-starter**: Workbox 7.x via CDN + handlers customizados **acima** da linha de precache ([docs SW](https://docs.pwabuilder.com/#/home/sw-intro)).

```js
importScripts('https://storage.googleapis.com/workbox-cdn/releases/7.3.0/workbox-sw.js');

// --- handlers customizados (push, notificationclick, message) ---

const PRECACHE = [
  { url: '/static/css/buzz.css', revision: null },
  { url: '/static/js/buzz.js', revision: null },
  { url: '/', revision: null },
];
workbox.precaching.precacheAndRoute(PRECACHE);

// API e WebSocket: sempre rede
workbox.routing.registerRoute(({ url }) => url.pathname.startsWith('/api/'), new workbox.strategies.NetworkOnly());

self.addEventListener('activate', (event) => event.waitUntil(self.clients.claim()));
```

**Push** (`push`): `showNotification` — título "Buzz — {nome}", `tag: buzina_id`, `renotify: true`, `requireInteraction: true`, `data.url`.

**Clique** (`notificationclick`): `launch_handler` + `clients.matchAll` → focar janela existente ou `openWindow(url)` ([pwa-starter usa `focus-existing`](https://github.com/pwa-builder/pwa-starter/blob/main/public/manifest.json)).

**Escopo**: SW servido em **`/sw.js`** (raiz), não em `/static/`, para cobrir todo o app. View Django com header `Service-Worker-Allowed: /`.

Sem webpack: lista de precache manual (em vez de `self.__WB_MANIFEST` do starter). Revisões podem usar hash de `collectstatic` no futuro.

### 7. Cliente (`push.js` ou trecho em `buzz.js`)

- `GET /api/push/vapid/` → chave pública.
- `POST /api/push/inscrever/` → salva subscription (PushSubscription JSON do browser).
- `DELETE /api/push/inscrever/` → remove endpoint.
- Registrar SW após login; subscribe após permissão `granted`.
- `document.visibilitychange` → se `visible`, chamar endpoint existente de pendentes / reutilizar lógica do consumer connect.

### 8. UX de permissão

Seção em **Configurações**: toggle "Notificações em segundo plano" + botão "Ativar" que dispara `Notification.requestPermission()` + subscribe.

Não bloquear uso do app se negado.

### 9. Coexistência com WS

- App em primeiro plano: WS continua primário (overlay imediato); push pode chegar em duplicata — SW só mostra notificação se `document.hidden` (via `postMessage` do client ao SW) ou tag deduplica.
- Simplificação MVP: SW sempre mostra push; client ao receber WS fecha notificação com mesmo `tag` via `registration.getNotifications()`.

## Riscos / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Usuário nega permissão | Fluxo opcional; app continua com WS em primeiro plano |
| iOS sem PWA instalado | Documentar "Adicionar à tela inicial"; banner discreto em iOS |
| Push duplicado com WS aberto | Tag por `buzina_id`; client limpa notificação ao mostrar overlay |
| Chaves VAPID vazam | Private key só no servidor; rotate com nova change se comprometida |
| Endpoint push expira | Tratar 410/404 e apagar `InscricaoPush` |
| Heroku sem HTTPS local | Push só em staging/prod; dev usa WS apenas |
| Manifest incompleto no PWABuilder | Seguir checklist obrigatório + recomendado; validar em pwabuilder.com antes de empacotar |

## Plano de migração

1. Gerar chaves VAPID e adicionar ao `.env` / Heroku.
2. Deploy backend (modelo + API) — aditivo, sem breaking change.
3. Deploy SW + manifest; usuários existentes precisam ativar nas configurações.
4. Rollback: remover hook de push em `enviar`; SW inativo não quebra app.

## Questões em aberto

- Enviar push também quando app está em primeiro plano mas sem foco na aba? **Sim** (comportamento padrão do SO).
- Badge no ícone do PWA com contador? **Futuro** — MVP só notificação por buzina.
- Push para buzina em massa (favoritos)? **Sim**, uma push por destinatário (já é por `enviar`).
