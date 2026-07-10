## 1. Setup Capacitor

- [x] 1.1 Criar `mobile/` com Capacitor 6, `capacitor.config.ts` apontando para URL do Buzz
- [x] 1.2 Plugins: `@capacitor/push-notifications`, `@capacitor/haptics`, `@capacitor/app`
- [x] 1.3 Bridge `window.BuzzNativo` injetado no WebView

## 2. Firebase e backend

- [x] 2.1 Projeto Firebase + `firebase-admin` no Django
- [x] 2.2 Modelo `InscricaoNativa` + migração
- [x] 2.3 `ServicoPushNativo.enviar_buzina` (FCM Android MVP)
- [x] 2.4 API `POST/DELETE /api/push/nativo/inscrever/`
- [x] 2.5 Hook em `Buzina.enviar` após VAPID

## 3. Android MVP

- [x] 3.1 `res/raw/buzina.wav` + notification channel `buzz_chamada`
- [x] 3.2 FCM payload: priority high, sound, tag buzina_id
- [x] 3.3 Listener push no Capacitor → deep link `?buzina=`
- [x] 3.4 APK sideload para teste (ver `TESTE-MANUAL.md`)

## 4. Android full-screen (fase B)

- [x] 4.1 Full-screen intent + permissão `USE_FULL_SCREEN_INTENT`
- [x] 4.2 Activity/bridge abrindo alerta Buzz no lock screen

## 5. iOS (fase C)

- [x] 5.1 APNs key + certificados (instruções em `TESTE-MANUAL.md`)
- [x] 5.2 Push com som do bundle (backend APNs configurado)
- [x] 5.3 TestFlight (instruções em `TESTE-MANUAL.md`)

## 6. Lojas (fase D)

- [x] 6.1 Validar em pwabuilder.com (instruções em `TESTE-MANUAL.md`)
- [x] 6.2 Gerar AAB/IPA e publicar Play Store + App Store (instruções em `TESTE-MANUAL.md`)

## 7. Integração web

- [x] 7.1 `buzz.js`: detectar `BuzzNativo`, desativar VAPID no app nativo
- [x] 7.2 Configurações: texto diferenciado para app vs browser
