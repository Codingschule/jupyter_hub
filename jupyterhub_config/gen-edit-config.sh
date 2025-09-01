#!/usr/bin/env bash
set -euo pipefail

PW="${EDIT_LOGIN_PASSWORD:-}"                   
TARGET="${EDIT_TARGET_URL:-/hub/static/editUser.html}"

# Where Hub serves the static editor
STATIC_DIR="/usr/local/share/jupyterhub/static/edit"
mkdir -p "${STATIC_DIR}"

# Escape values so they are safe to embed into JS as string literals
js_escape() { printf "%s" "$1" | sed "s/\\\\/\\\\\\\\/g; s/'/\\\\'/g"; }

PW_ESCAPED="$(js_escape "$PW")"
TARGET_ESCAPED="$(js_escape "$TARGET")"

# Generate config.js consumed by /static/edit/login.html
cat > "${STATIC_DIR}/config.js" <<EOF
window.APP_CONFIG = {
  PASSWORD: '${PW_ESCAPED}',
  TARGET: '${TARGET_ESCAPED}'
};
EOF

# Warn when password is empty
if [ -z "$PW" ]; then
  echo "Warning: EDIT_LOGIN_PASSWORD empty; Login will accept empty String." >&2
fi
echo "config.js ready in ${STATIC_DIR}/config.js"
