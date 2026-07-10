#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/_env.sh"
verificar_java

KEYSTORE_PROPS="$ANDROID_DIR/keystore.properties"
if [[ ! -f "$KEYSTORE_PROPS" ]]; then
  echo "Assinatura release não configurada."
  echo ""
  echo "Execute primeiro:"
  echo "  ./mobile/scripts/setup-keystore.sh"
  echo ""
  echo "Ou copie keystore.properties.example → keystore.properties e ajuste os caminhos."
  exit 1
fi

sincronizar_capacitor

cd "$ANDROID_DIR"
./gradlew bundleRelease "$@"

AAB="app/build/outputs/bundle/release/app-release.aab"
if [[ -f "$AAB" ]]; then
  echo ""
  echo "✓ AAB gerado: $ANDROID_DIR/$AAB"
  echo "  Upload: Play Console → Produção → Criar nova versão → enviar este arquivo"
fi
