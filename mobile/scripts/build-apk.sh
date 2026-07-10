#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/_env.sh"
verificar_java
sincronizar_capacitor

cd "$ANDROID_DIR"
./gradlew assembleDebug "$@"

APK="app/build/outputs/apk/debug/app-debug.apk"
if [[ -f "$APK" ]]; then
  echo ""
  echo "✓ APK gerado: $ANDROID_DIR/$APK"
  echo "  Instalar: adb install -r $ANDROID_DIR/$APK"
fi
