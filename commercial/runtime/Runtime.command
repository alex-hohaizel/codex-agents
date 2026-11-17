#!/bin/sh
set -eu
RUNTIME_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
unset NODE_OPTIONS NODE_PATH
PATH="$RUNTIME_DIR/bin:/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"
export PATH
: "${ATELIER_DATA_DIR:=$HOME/Library/Application Support/Codex Agent System/Agent Atelier}"
export ATELIER_DATA_DIR
exec "$RUNTIME_DIR/bin/node" "$RUNTIME_DIR/control.mjs" "$@"
