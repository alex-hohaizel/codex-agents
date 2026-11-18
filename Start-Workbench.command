#!/bin/sh
set -eu
folder=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)
exec "$folder/Start.command" --workbench "$@"
