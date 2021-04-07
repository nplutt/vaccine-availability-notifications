#!/usr/bin/env bash

function cleanup {
  echo "Cleaning up chalice config"
  rm ./.chalice/config.json
}

trap cleanup EXIT

cd "$(dirname "$0")/.."

python ./.chalice/config.py
chalice local
