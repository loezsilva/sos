#!/usr/bin/env bash
# Ambiente compartilhado pelos scripts de build Android.

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export JAVA_HOME="${JAVA_HOME:-$RAIZ/.tools/jdk-21}"
export ANDROID_HOME="${ANDROID_HOME:-$RAIZ/.tools/android-sdk}"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

ANDROID_DIR="$RAIZ/mobile/android"
PROPS="$ANDROID_DIR/local.properties"

if [[ ! -f "$PROPS" ]]; then
  echo "sdk.dir=$ANDROID_HOME" > "$PROPS"
fi

verificar_java() {
  if [[ ! -x "$JAVA_HOME/bin/java" ]]; then
    echo "JDK 21 não encontrado em $JAVA_HOME"
    echo "Veja openspec/changes/shell-mobile-capacitor/TESTE-MANUAL.md (seção Build)"
    exit 1
  fi
}

sincronizar_capacitor() {
  cd "$RAIZ/mobile"
  npm install --silent
  npx cap sync android
}
