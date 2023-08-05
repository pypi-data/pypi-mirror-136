#!/bin/bash
set -euo pipefail

tmp=$(mktemp "${TMPDIR:-/tmp}/$(basename $0).XXXXXXXXXX")
finally() {
  exit_code=$?
  rm $tmp
  exit $exit_code
}
trap finally SIGINT EXIT

while true; do
  ./generate.py > $tmp
  mv $tmp data.js  # atomic
  sleep 0.1
done
