#!/bin/sh
set -eu
RUNTIME_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
unset NODE_OPTIONS NODE_PATH PYTHONHOME PYTHONPATH
PATH="$PATH:$RUNTIME_DIR/bin:/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin"
export PATH
AGENT_SYSTEM_NODE="$RUNTIME_DIR/bin/node"
export AGENT_SYSTEM_NODE
if [ -x "$RUNTIME_DIR/python/bin/python3" ]; then AGENT_SYSTEM_PYTHON="$RUNTIME_DIR/python/bin/python3"; export AGENT_SYSTEM_PYTHON; fi
PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
export PYTHONUTF8 PYTHONIOENCODING PYTHONDONTWRITEBYTECODE
: "${ATELIER_DATA_DIR:=$HOME/Library/Application Support/Codex Agent System/Agent Atelier}"
export ATELIER_DATA_DIR
exec "$RUNTIME_DIR/bin/node" "$RUNTIME_DIR/control.mjs" "$@"
