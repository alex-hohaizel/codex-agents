#!/bin/sh
set -eu
folder=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
case "$(uname -s)" in Darwin) system=darwin;; Linux) system=linux;; *) echo 'Use Start.cmd on Windows.'; exit 1;; esac
case "$(uname -m)" in arm64|aarch64) arch=arm64;; x86_64|amd64) arch=x64;; *) echo 'This installer requires a supported64-bit computer.'; exit 1;; esac
node="$folder/runtimes/$system-$arch/node/bin/node"
if [ ! -x "$node" ]; then
 echo 'You opened the source archive. Download the ready Universal installer:'
 echo 'https://github.com/alex-hohaizel/codex-agents/releases/latest'
 exit 1
fi
unset NODE_OPTIONS
exec "$node" "$folder/setup/launch.mjs" "$@"
