#!/usr/bin/env bash
# Deploy a built portfolio folder to GitHub Pages and print the live URL.
#
# Usage:  deploy.sh <folder> <repo-name> [--private]
#   <folder>     folder containing index.html (+ photo, etc.)
#   <repo-name>  e.g. priyanka-portfolio
#
# Auth (in priority order):
#   1) GitHub CLI already logged in  ->  uses it (most secure; token in OS keyring)
#   2) GH_TOKEN env var (a Personal Access Token with 'repo' scope)
#
# Prints:  DEPLOYED <url>   on success.
set -euo pipefail

FOLDER="${1:?usage: deploy.sh <folder> <repo-name> [--private]}"
REPO="${2:?usage: deploy.sh <folder> <repo-name> [--private]}"
VIS="public"; [ "${3:-}" = "--private" ] && VIS="private"
[ -f "$FOLDER/index.html" ] || { echo "ERROR: $FOLDER/index.html not found"; exit 1; }

# resolve owner + token
OWNER=""; TOKEN="${GH_TOKEN:-}"
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  OWNER="$(gh api user -q .login)"
  TOKEN="$(gh auth token 2>/dev/null || echo "${GH_TOKEN:-}")"
elif [ -n "$TOKEN" ]; then
  OWNER="$(curl -fsSL -H "Authorization: token $TOKEN" https://api.github.com/user | sed -n 's/.*"login": *"\([^"]*\)".*/\1/p' | head -1)"
fi
[ -n "$OWNER" ] && [ -n "$TOKEN" ] || {
  echo "NEED_AUTH: run 'gh auth login' (recommended) or pass GH_TOKEN=<token with repo scope>"; exit 3; }

API="https://api.github.com"
AUTH=(-H "Authorization: token $TOKEN" -H "Accept: application/vnd.github+json")

# create repo if it does not exist
if ! curl -fsSL "${AUTH[@]}" "$API/repos/$OWNER/$REPO" >/dev/null 2>&1; then
  PRIV=false; [ "$VIS" = "private" ] && PRIV=true
  curl -fsSL "${AUTH[@]}" -X POST "$API/user/repos" \
    -d "{\"name\":\"$REPO\",\"private\":$PRIV,\"description\":\"Portfolio built with Portfolio Pro\"}" >/dev/null
fi

# push the folder contents to main
TMP="$(mktemp -d)"
cp -R "$FOLDER"/. "$TMP"/
( cd "$TMP"
  git init -q -b main
  printf '.DS_Store\n' > .gitignore
  git add -A
  git -c user.name="$OWNER" -c user.email="$OWNER@users.noreply.github.com" commit -q -m "Deploy portfolio"
  git remote add origin "https://x-access-token:$TOKEN@github.com/$OWNER/$REPO.git"
  git push -q -f origin main )
rm -rf "$TMP"

# enable GitHub Pages from main / root (ignore error if already enabled)
curl -fsSL "${AUTH[@]}" -X POST "$API/repos/$OWNER/$REPO/pages" \
  -d '{"source":{"branch":"main","path":"/"}}' >/dev/null 2>&1 || \
curl -fsSL "${AUTH[@]}" -X PUT "$API/repos/$OWNER/$REPO/pages" \
  -d '{"source":{"branch":"main","path":"/"}}' >/dev/null 2>&1 || true

echo "DEPLOYED https://$OWNER.github.io/$REPO/"
