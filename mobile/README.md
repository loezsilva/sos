# Buzz Mobile (Capacitor)

Shell nativo Android/iOS para o Buzz web. Ver `openspec/changes/shell-mobile-capacitor/TESTE-MANUAL.md` para setup completo.

## Scripts

| Script | Saída | Uso |
|--------|-------|-----|
| `./mobile/scripts/build-apk.sh` | APK debug | Testar no celular (`adb install`) |
| `./mobile/scripts/setup-keystore.sh` | Keystore + config | Uma vez, antes do release |
| `./mobile/scripts/build-aab.sh` | AAB assinado | Upload na Play Store |

## Quick start (teste)

```bash
# google-services.json em android/app/
# server.url em capacitor.config.json
./mobile/scripts/build-apk.sh
adb install -r mobile/android/app/build/outputs/apk/debug/app-debug.apk
```

## Play Store (release)

```bash
./mobile/scripts/setup-keystore.sh   # primeira vez
./mobile/scripts/build-aab.sh
# → mobile/android/app/build/outputs/bundle/release/app-release.aab
```

Requisitos: Node 18+, Java 21+ (`.tools/jdk-21`), Android SDK 36 (`.tools/android-sdk`).
