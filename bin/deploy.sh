#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

chalice deploy --stage prod