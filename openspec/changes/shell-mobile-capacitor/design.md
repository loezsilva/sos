## Contexto

```
Camada 1 ✅ WS + overlay     Camada 2 ✅ PWA/VAPID     Camada 3 ← esta change
App aberto                   Notificação SO (limitada)  Som + vibração + UI chamada
```

O Buzz já tem Django + Channels + `InscricaoPush` (VAPID). No mobile nativo, o WebView Capacitor carrega `https://buzz.app` (ou ngrok em dev); plugins nativos cobrem o que o browser não permite.

## Objetivos / Não-objetivos

**Objetivos:**
- Android: buzina com **som customizado** (`buzina.wav` no `res/raw`), vibração, notificação heads-up, **full-screen intent** abrindo alerta Buzz.
- iOS: push com som do bundle, abrir app na tela de buzina; PWA instalado + app nativo na loja.
- Um backend, dois canais de push: VAPID (web) + FCM/APNs (nativo).
- Empacotar com PWABuilder ou `npx cap` para Play Store / App Store.

**Não-objetivos (MVP):**
- CallKit completo no iOS (fase 2).
- Reescrever UI em React Native/Flutter.
- SMS ou VoIP real.

## Decisões

### 1. Capacitor 6 + `@capacitor/push-notifications`

Shell mínimo:
```bash
npm create @capacitor/app mobile -- --name Buzz
cd mobile && npm i @capacitor/push-notifications @capacitor/haptics @capacitor/app
```

`capacitor.config.ts`: `server.url` aponta para produção (live reload em dev).

**Por quê:** reutiliza 100% do Buzz web; time já conhece Django/templates.

### 2. Push nativo no backend (`firebase-admin`)

Modelo `InscricaoNativa`:
```python
# usuario, token (unique), plataforma (android|ios), device_id opcional
```

`ServicoPushNativo.enviar_buzina(buzina)`:
- Android: FCM data message + `notification` com `channel_id: buzz_chamada`, `sound: buzina`, `priority: high`
- iOS: APNs com `sound: buzina.wav`, `interruption-level: time-sensitive` (se entitlement)

Hook em `Buzina.enviar`: após VAPID, chamar `ServicoPushNativo` se houver tokens nativos.

**Coexistência:** usuário pode ter web + app instalado → dois pushes; deduplica por `tag`/`buzina_id` no client.

### 3. Som no Android

- Copiar `static/sounds/buzina.wav` → `mobile/android/app/src/main/res/raw/buzina.wav`
- Notification channel `buzz_chamada`: `IMPORTANCE_HIGH`, som customizado, vibração
- Plugin local ou código Java mínimo no `MainActivity` para full-screen intent → deep link `buzz://buzina/{id}` ou `https://.../?buzina=`

### 4. Cliente Capacitor (`mobile/src/push.ts`)

- No `appUrlOpen` / push `registration` → `POST /api/push/nativo/inscrever/`
- Listener `pushNotificationReceived` (foreground): `Haptics.vibrate()`, bridge para WebView (`window.BuzzNativo?.onBuzina`)
- Listener `pushNotificationActionPerformed`: abrir deep link

Bridge JS ↔ WebView:
```javascript
// injetado no WebView
window.BuzzNativo = { ehAppNativo: true, plataforma: 'android' };
```

`buzz.js` detecta `BuzzNativo` e pula restrições de gesto quando plugin nativo toca som.

### 5. PWABuilder para lojas

Fluxo documentado em [PWABuilder packaging](https://docs.pwabuilder.com/):
1. Validar PWA em pwabuilder.com
2. Gerar pacote Android (AAB) com push configurado
3. iOS: wrapper + certificados APNs

Alternativa: `npx @pwabuilder/cli package` após Capacitor build.

### 6. Variáveis de ambiente

```
FIREBASE_CREDENTIALS_JSON=...   # ou GOOGLE_APPLICATION_CREDENTIALS
APNS_KEY_ID=...
APNS_TEAM_ID=...
APNS_KEY_PATH=...
```

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Apple rejeita app "só WebView" | Destacar push nativo + som; seguir guidelines |
| Dois pushes (web + nativo) | Preferir token nativo quando `BuzzNativo` detectado; desativar VAPID no app |
| Full-screen intent Android 14+ | `USE_FULL_SCREEN_INTENT` + permissão em runtime |
| Custo Firebase/APNs | Tier gratuito suficiente para MVP |

## Plano de entrega (fases)

1. **Fase A** — Capacitor + FCM Android + som + deep link (MVP testável via APK sideload)
2. **Fase B** — Full-screen intent Android
3. **Fase C** — iOS APNs + TestFlight
4. **Fase D** — PWABuilder → Play Store / App Store
5. **Fase E** (opcional) — CallKit iOS
