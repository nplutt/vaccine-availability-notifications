#!/usr/bin/env bash

set -e

function cleanup {
  echo "Cleaning up chalice config"
  rm ./.chalice/config.json
}

trap cleanup EXIT

cd "$(dirname "$0")/.."

bash bin/format_code.sh
bash bin/lint_code.sh

python ./.chalice/config.py
chalice deploy --stage prod