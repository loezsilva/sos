# Shell mobile Buzz — Capacitor + FCM

App nativo Android/iOS que carrega o Buzz web com push nativo (som customizado, vibração, tela cheia).

## Pré-requisitos

- Node.js 18+
- Android Studio (SDK 34+)
- Conta [Firebase](https://console.firebase.google.com/) (gratuito)
- Backend Django rodando (local, ngrok ou produção)

## 1. Firebase

1. Crie projeto no Firebase Console
2. Adicione app Android com package `com.buzz.app`
3. Baixe `google-services.json` → `mobile/android/app/google-services.json`
4. Em **Configurações do projeto → Contas de serviço**, gere chave JSON
5. No `.env` do Django:

```env
FIREBASE_CREDENTIALS_JSON={"type":"service_account",...}
# ou
GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/firebase-adminsdk.json
```

## 2. URL do servidor

Edite `mobile/capacitor.config.json`:

| Ambiente | `server.url` |
|----------|----------------|
| Emulador Android | `http://10.0.2.2:8000` |
| Celular físico (mesma rede) | `http://SEU_IP:8000` |
| ngrok | `https://sua-url.ngrok-free.app` |
| Produção | `https://buzz.app` |

Adicione a URL em `CSRF_TRUSTED_ORIGINS` no `.env`.

## 3. Build APK (sideload)

### Opção rápida (script)

```bash
./mobile/scripts/build-apk.sh
```

O script usa JDK 21 e Android SDK em `.tools/` (portáteis, sem sudo).

**Primeira vez** — se `.tools/` não existir:

```bash
# JDK 21
mkdir -p .tools && cd .tools
curl -fsSL "https://api.adoptium.net/v3/binary/latest/21/ga/linux/x64/jdk/hotspot/normal/eclipse?project=jdk" -o jdk21.tar.gz
tar -xzf jdk21.tar.gz && mv jdk-21* jdk-21 && rm jdk21.tar.gz

# Android SDK
export JAVA_HOME=$PWD/jdk-21
export ANDROID_HOME=$PWD/android-sdk
mkdir -p $ANDROID_HOME/cmdline-tools && cd $ANDROID_HOME/cmdline-tools
curl -fsSL "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip" -o ct.zip
unzip -q ct.zip && mv cmdline-tools latest && rm ct.zip
yes | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-36" "build-tools;36.0.0"
```

### Manual

```bash
cd mobile
npm install
npx cap sync android
cd android
./gradlew assembleDebug
```

APK: `mobile/android/app/build/outputs/apk/debug/app-debug.apk`

Requisitos: **Java 21+** (Capacitor 8), Android SDK 36.

Instalar no celular:

```bash
adb install -r mobile/android/app/build/outputs/apk/debug/app-debug.apk
```

## 4. Build AAB (Play Store)

A Google Play **só aceita AAB** para publicação. O APK acima é só para teste local.

### 1. Criar keystore (uma vez)

```bash
./mobile/scripts/setup-keystore.sh
```

Isso gera:
- `mobile/android/keystore/buzz-release.jks` — **faça backup** (sem ele não atualiza o app na loja)
- `mobile/android/keystore.properties` — senhas (não commitar)

### 2. Gerar AAB assinado

```bash
./mobile/scripts/build-aab.sh
```

Saída: `mobile/android/app/build/outputs/bundle/release/app-release.aab`

### 3. Publicar na Play Console

1. [Play Console](https://play.google.com/console) → criar app
2. **Produção** (ou teste interno) → **Criar nova versão**
3. Upload do `app-release.aab`
4. Preencher ficha da loja, política de privacidade, screenshots
5. Enviar para revisão

### Versões futuras

Antes de cada release, incremente em `mobile/android/app/build.gradle`:

```gradle
versionCode 2      // inteiro, sempre maior que o anterior
versionName "1.1"  // exibição para o usuário
```

## 5. Testar buzina

1. Abra o app Buzz no celular → faça login
2. Em **Configurações**, ative notificações
3. De outro dispositivo/conta, envie buzina
4. Com app em background: notificação com som `buzina.wav` + vibração
5. Com tela bloqueada: full-screen intent abre o alerta

## 6. iOS (fase C)

1. Adicione app iOS no Firebase
2. Upload da chave APNs (.p8) no Firebase
3. `npx cap add ios && npx cap sync ios`
4. Abra `ios/App/App.xcworkspace` no Xcode
5. Adicione `buzina.wav` ao bundle iOS
6. TestFlight via Apple Developer ($99/ano)

## 7. Lojas (fase D)

1. Valide PWA em [pwabuilder.com](https://www.pwabuilder.com/)
2. Android: `./mobile/scripts/build-aab.sh` → upload na Play Console
3. iOS: App Store Connect → IPA via Xcode/PWABuilder

## Arquivos-chave

| Arquivo | Função |
|---------|--------|
| `capacitor.config.json` | URL do Buzz + user-agent |
| `BuzzMessagingService.java` | FCM + som + full-screen |
| `MainActivity.java` | Canal `buzz_chamada` + deep link |
| `res/raw/buzina.wav` | Som da notificação |
| `static/js/push-nativo.js` | Registro token no Django |
