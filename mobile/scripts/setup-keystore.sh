#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/_env.sh"
verificar_java

KEYSTORE_DIR="$ANDROID_DIR/keystore"
KEYSTORE_FILE="$KEYSTORE_DIR/buzz-release.jks"
KEYSTORE_PROPS="$ANDROID_DIR/keystore.properties"
KEYSTORE_PROPS_EXAMPLE="$ANDROID_DIR/keystore.properties.example"

mkdir -p "$KEYSTORE_DIR"

if [[ -f "$KEYSTORE_FILE" ]]; then
  echo "Keystore já existe: $KEYSTORE_FILE"
  echo "Para recriar, apague o arquivo e execute de novo."
  exit 1
fi

echo "=== Criar keystore de release do Buzz ==="
echo ""
echo "Guarde a senha em local seguro — sem ela não atualiza o app na Play Store."
echo ""

read -r -p "Senha do keystore (mín. 6 caracteres): " STORE_PASS
read -r -p "Senha da chave [mesma do keystore]: " KEY_PASS
KEY_PASS="${KEY_PASS:-$STORE_PASS}"

read -r -p "Alias da chave [buzz]: " KEY_ALIAS
KEY_ALIAS="${KEY_ALIAS:-buzz}"

"$JAVA_HOME/bin/keytool" -genkeypair -v \
  -storetype PKCS12 \
  -keystore "$KEYSTORE_FILE" \
  -alias "$KEY_ALIAS" \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -storepass "$STORE_PASS" \
  -keypass "$KEY_PASS" \
  -dname "CN=Buzz, OU=Mobile, O=Buzz, L=SaoPaulo, ST=SP, C=BR"

cat > "$KEYSTORE_PROPS" <<EOF
storeFile=keystore/buzz-release.jks
storePassword=$STORE_PASS
keyAlias=$KEY_ALIAS
keyPassword=$KEY_PASS
EOF

chmod 600 "$KEYSTORE_PROPS"

echo ""
echo "✓ Keystore: $KEYSTORE_FILE"
echo "✓ Config:   $KEYSTORE_PROPS (não commitar)"
echo ""
echo "Próximo passo: ./mobile/scripts/build-aab.sh"
