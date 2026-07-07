#!/usr/bin/env bash
# envoy-loader.sh — load envoy chain from AstroMage/lilly-core/envoy.json
set -euo pipefail

CONFIG="${HOME}/AstroMage/lilly-core/envoy.json"
PROFILE="$1"
shift

if [[ ! -f "$CONFIG" ]]; then
  echo "❌ envoy config missing: $CONFIG" >&2
  exit 1
fi

# grab return-to and envoys
RETURN_TO="$(jq -r --arg p "$PROFILE" '.envoy_chains[$p].return_to // empty' "$CONFIG")"
mapfile -t ENVOYS < <(jq -r --arg p "$PROFILE" '.envoy_chains[$p].envoys[]? // empty' "$CONFIG")

if [[ -z "$RETURN_TO" && "${#ENVOYS[@]}" -gt 0 ]]; then
  # first hop under root
  NEXT="${ENVOYS[0]}"
  echo "👑 Root delegate → ${NEXT}"
  hermes profile switch "$NEXT"
  hermes skill load lilly-envoy-launch
  exec "$@"
elif [[ -n "$RETURN_TO" ]]; then
  # intermediate step → delegate downstream
  echo "🔮 ${PROFILE} envoys list:"
  printf '  - %s\n' "${ENVOYS[@]}"
  NEXT="${ENVOYS[0]}"
  hermes profile switch "$NEXT"
  hermes skill load lilly-envoy-launch
  exec "$@"
else
  # final step (astral-guardian) → return to queen
  echo "🦉 ${PROFILE} final step → returning to Mistress Lilly"
  hermes profile switch "mistress-lilly"
  exec "$@"
fi
