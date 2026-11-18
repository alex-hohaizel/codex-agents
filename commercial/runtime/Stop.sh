#!/bin/sh
set -eu
RUNTIME_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
exec "$RUNTIME_DIR/Runtime.sh" stop "$@"
