#!/bin/sh
set -eu
output="$(./bin/@NAME@)"
case "$output" in
  "@NAME@"*) printf 'OK: %s\n' "$output" ;;
  *) printf 'FAIL: output tidak sesuai: %s\n' "$output" >&2; exit 1 ;;
esac
