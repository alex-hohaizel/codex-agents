#!/bin/zsh
set -e
ATELIER_APP_DIR="${0:A:h}/.."
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$PATH"
cd "$ATELIER_APP_DIR"
if command -v node >/dev/null 2>&1 && node -e "process.exit(Number(process.versions.node.split('.')[0]) >= 24 ? 0 : 1)"; then
  node launcher/atelier.mjs start
elif command -v fnm >/dev/null 2>&1; then
  fnm exec --using=24 -- node launcher/atelier.mjs start
else
  echo 'Agent Atelier requires Node.js24+. Install a supported Node runtime, then reopen this launcher.'
  read -k 1 '?Press any key to close.'
  exit 1
fi
