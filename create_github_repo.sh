#!/usr/bin/env bash
# =============================================================================
# create_github_repo.sh
# One-shot script to:
#   1) Create the GitHub repository conexocasa/solar-of-things-ha (if missing)
#   2) Push main branch + all tags (v2.1.0, v2.1.1)
#   3) Create a DRAFT GitHub Release for v2.1.1 and upload solar-of-things-ha.zip
#
# Usage:
#   export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
#   bash create_github_repo.sh
#
# Requirements: git, curl, jq (installed by script if missing)
# =============================================================================

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
GITHUB_USERNAME="conexocasa"
GITHUB_EMAIL="bob@conexo.casa"
REPO_NAME="solar-of-things-ha"
REPO_DESC="Home Assistant custom integration for Solar of Things (Siseli) solar inverters — monitoring + control"
RELEASE_TAG="v2.1.1"
RELEASE_TITLE="v2.1.1 — HACS metadata, GitHub Actions, issue templates"
ZIP_ASSET="solar-of-things-ha.zip"
# ─────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
err()  { echo -e "${RED}✗${NC}  $*"; exit 1; }

# ── Token ─────────────────────────────────────────────────────────────────────
if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo -n "GitHub Personal Access Token (repo scope): "
  read -s GITHUB_TOKEN
  echo
fi
[ -z "$GITHUB_TOKEN" ] && err "GITHUB_TOKEN is required."

API="https://api.github.com"
AUTH_HEADER="Authorization: token $GITHUB_TOKEN"
ACCEPT="Accept: application/vnd.github.v3+json"

# ── Dependencies ──────────────────────────────────────────────────────────────
if ! command -v jq &>/dev/null; then
  warn "jq not found — installing…"
  apt-get install -y -q jq 2>/dev/null || brew install jq 2>/dev/null || err "Install jq manually."
fi

# ── Git identity ──────────────────────────────────────────────────────────────
git config --global user.email "$GITHUB_EMAIL"
git config --global user.name  "$GITHUB_USERNAME"
ok "Git identity set ($GITHUB_EMAIL)"

# ── Step 1: Create repository (idempotent) ────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════"
echo " STEP 1 · Create GitHub repository"
echo "══════════════════════════════════════════════"

RESP=$(curl -s -o /tmp/gh_create.json -w "%{http_code}" \
  -X POST "$API/user/repos" \
  -H "$AUTH_HEADER" -H "$ACCEPT" \
  -d "{
    \"name\":\"$REPO_NAME\",
    \"description\":\"$REPO_DESC\",
    \"private\":false,
    \"has_issues\":true,
    \"has_projects\":false,
    \"has_wiki\":false,
    \"default_branch\":\"main\"
  }")

if [ "$RESP" = "201" ]; then
  ok "Repository created: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
elif [ "$RESP" = "422" ]; then
  warn "Repository already exists — continuing."
else
  cat /tmp/gh_create.json
  err "Unexpected HTTP $RESP from repo creation."
fi

# ── Step 2: Push main + all tags ──────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════"
echo " STEP 2 · Push main branch + tags"
echo "══════════════════════════════════════════════"

REMOTE_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE_URL"

git branch -M main

if git push origin main --force; then
  ok "Pushed branch main"
else
  err "Failed to push main"
fi

if git push origin --tags --force; then
  ok "Pushed all tags ($(git tag --list | tr '\n' ' '))"
else
  err "Failed to push tags"
fi

# Clean up token from remote URL
git remote set-url origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

# ── Step 3: Create draft GitHub Release for RELEASE_TAG ───────────────────────
echo ""
echo "══════════════════════════════════════════════"
echo " STEP 3 · Create draft release $RELEASE_TAG"
echo "══════════════════════════════════════════════"

# Extract changelog section for RELEASE_TAG
VER="${RELEASE_TAG#v}"
RELEASE_BODY=$(awk "/^## \[$VER\]/{flag=1; next} /^## \[/{flag=0} flag" CHANGELOG.md || true)
if [ -z "$RELEASE_BODY" ]; then
  RELEASE_BODY="See CHANGELOG.md for full details."
fi
RELEASE_BODY_JSON=$(jq -Rs . <<< "$RELEASE_BODY")

# Delete existing draft for same tag if any
EXISTING_ID=$(curl -s -H "$AUTH_HEADER" -H "$ACCEPT" \
  "$API/repos/$GITHUB_USERNAME/$REPO_NAME/releases" \
  | jq -r ".[] | select(.tag_name==\"$RELEASE_TAG\") | .id" | head -1)

if [ -n "$EXISTING_ID" ]; then
  warn "Deleting existing release id=$EXISTING_ID for $RELEASE_TAG"
  curl -s -X DELETE "$API/repos/$GITHUB_USERNAME/$REPO_NAME/releases/$EXISTING_ID" \
    -H "$AUTH_HEADER" -H "$ACCEPT" > /dev/null
fi

RELEASE_RESP=$(curl -s -X POST \
  "$API/repos/$GITHUB_USERNAME/$REPO_NAME/releases" \
  -H "$AUTH_HEADER" -H "$ACCEPT" \
  -d "{
    \"tag_name\":\"$RELEASE_TAG\",
    \"target_commitish\":\"main\",
    \"name\":\"$RELEASE_TITLE\",
    \"body\":$RELEASE_BODY_JSON,
    \"draft\":true,
    \"prerelease\":false
  }")

RELEASE_ID=$(echo "$RELEASE_RESP" | jq -r '.id // empty')
UPLOAD_URL=$(echo "$RELEASE_RESP" | jq -r '.upload_url // empty' | sed 's/{.*}//')

if [ -z "$RELEASE_ID" ]; then
  echo "$RELEASE_RESP"
  err "Failed to create draft release."
fi
ok "Draft release created (id=$RELEASE_ID)"

# ── Step 4: Upload ZIP asset ──────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════"
echo " STEP 4 · Upload $ZIP_ASSET"
echo "══════════════════════════════════════════════"

# Locate the zip file (same dir as script, or outputs dir)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ZIP_PATH=""
for candidate in \
    "$SCRIPT_DIR/$ZIP_ASSET" \
    "/mnt/user-data/outputs/$ZIP_ASSET" \
    "$(pwd)/$ZIP_ASSET"; do
  if [ -f "$candidate" ]; then
    ZIP_PATH="$candidate"
    break
  fi
done

if [ -z "$ZIP_PATH" ]; then
  warn "Could not find $ZIP_ASSET — skipping upload."
  warn "To upload manually: attach '$ZIP_ASSET' on the draft release page:"
  echo "  https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/edit/$RELEASE_ID"
else
  UPLOAD_RESP=$(curl -s -X POST \
    "${UPLOAD_URL}?name=${ZIP_ASSET}&label=${ZIP_ASSET}" \
    -H "$AUTH_HEADER" \
    -H "Content-Type: application/zip" \
    --data-binary @"$ZIP_PATH")
  ASSET_URL=$(echo "$UPLOAD_RESP" | jq -r '.browser_download_url // empty')
  if [ -n "$ASSET_URL" ]; then
    ok "Asset uploaded: $ASSET_URL"
  else
    warn "Asset upload may have failed:"
    echo "$UPLOAD_RESP" | jq '.' 2>/dev/null || echo "$UPLOAD_RESP"
  fi
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════"
echo " SUCCESS"
echo "══════════════════════════════════════════════"
echo ""
echo "  Repository : https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "  Branch     : main"
echo "  Tags       : $(git tag --list | tr '\n' ' ')"
echo "  Draft release page:"
echo "  https://github.com/$GITHUB_USERNAME/$REPO_NAME/releases/edit/$RELEASE_ID"
echo ""
echo "  Next steps:"
echo "  1. Visit the draft release link above."
echo "  2. Review release notes and attached ZIP."
echo "  3. Click 'Publish release' when ready."
echo "  4. For HACS: Settings → Devices & Services → Add Integration → Solar of Things"
echo ""
