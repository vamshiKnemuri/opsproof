#!/usr/bin/env sh
set -eu
python3 -m opsproof setup
python3 -m opsproof demo --backend kind
