#!/usr/bin/env bash
# Refresh this plugin's vendored copy of its template repo.
#
# Reference implementation for the Plugin-Workspace-Vault pattern:
#   https://github.com/danielrosehill/Claude-Plugin-Workspace-Vault
#
# Set the four variables below and drop this in at scripts/sync-from-template.sh.
#
# The template repo is canonical; this plugin's copy is a build artefact. A change to
# a shared file goes to the template FIRST and reaches the plugin through this script.
# The other direction works exactly once, and then the next sync silently reverts it.
#
# Keeping the vendored copies byte-identical is what makes --check meaningful: any
# difference is drift, and drift means someone edited the wrong copy.
#
# Usage:
#   ./scripts/sync-from-template.sh                  pull from GitHub
#   ./scripts/sync-from-template.sh --from ../path   pull from a local checkout
#   ./scripts/sync-from-template.sh --check          report drift, write nothing

set -euo pipefail
cd "$(dirname "$0")/.."

# ─── Configure ───────────────────────────────────────────────────────────────

UPSTREAM_REPO="<owner>/<template-repo>"
DEFAULT_LOCAL="$HOME/repos/<owner>/<template-repo>"   # preferred when present

# Skills that exist only here — they have no upstream counterpart, so they must
# survive the wipe and must not be reported as drift.
PLUGIN_OWNED_SKILLS=(create-workspace scaffold-workspace)

src=""
check_only=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --from) src="$2"; shift 2 ;;
    --check) check_only=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

tmp=""
# Must return 0: an EXIT trap's exit status becomes the script's, so a bare
# `[[ -n "$tmp" ]] && rm -rf "$tmp"` makes every clean run exit 1 when tmp is unset.
cleanup() { [[ -n "$tmp" ]] && rm -rf "$tmp"; return 0; }
trap cleanup EXIT

if [[ -z "$src" ]]; then
  if [[ -d "$DEFAULT_LOCAL/.git" ]]; then
    src="$DEFAULT_LOCAL"
    echo "Source: local checkout at $src"
  else
    tmp="$(mktemp -d)"
    echo "Source: github.com/$UPSTREAM_REPO"
    git clone --depth 1 -q "https://github.com/$UPSTREAM_REPO.git" "$tmp/template"
    src="$tmp/template"
  fi
else
  echo "Source: $src"
fi

[[ -d "$src/skills" ]] || { echo "not a $UPSTREAM_REPO checkout: $src" >&2; exit 1; }

# Everything the plugin vendors, and where it lands here.
#   skills/ and agents/   → used directly by Claude Code
#   the workspace files   → template/, copied into the user's directory by scaffold-workspace
WORKSPACE_PATHS=(data docs AGENTS.md)   # ← your template's working dirs

stage="$(mktemp -d)"
mkdir -p "$stage/skills" "$stage/agents" "$stage/template"

# The upstream stage skills. Plugin-owned ones are not synced.
is_plugin_owned() {
  local n="$1"
  for o in "${PLUGIN_OWNED_SKILLS[@]}"; do [[ "$n" == "$o" ]] && return 0; done
  return 1
}

for d in "$src"/skills/*/; do
  name="$(basename "$d")"
  is_plugin_owned "$name" && continue
  cp -r "$d" "$stage/skills/$name"
done

cp -r "$src"/agents/. "$stage/agents/"

for p in "${WORKSPACE_PATHS[@]}"; do
  [[ -e "$src/$p" ]] || continue
  cp -r "$src/$p" "$stage/template/"
done

# Files that must ship empty — header-only CSVs, unfilled forms. A template checkout
# quietly acquires real content when someone tries the workflow in it instead of in an
# instance, and without this guard that content ships to every user. Refuse, don't warn.
EMPTY_ON_SHIP=()                        # ← e.g. (data/records.csv data/scores.csv)

for rel in "${EMPTY_ON_SHIP[@]}"; do
  f="$stage/template/$rel"
  [[ -f "$f" ]] || continue
  if [[ "$(wc -l < "$f")" -gt 1 ]]; then
    echo "REFUSING: $rel carries data rows. The template's data files must ship empty." >&2
    exit 1
  fi
done

if [[ $check_only -eq 1 ]]; then
  rc=0
  # Plugin-owned skills have no upstream counterpart, so they are excluded rather
  # than reported as drift on every run.
  excl=()
  for o in "${PLUGIN_OWNED_SKILLS[@]}"; do excl+=(--exclude="$o"); done
  if ! diff -rq "${excl[@]}" "$stage/skills" skills >/dev/null 2>&1; then
    echo "DRIFT in skills/:"
    diff -rq "${excl[@]}" "$stage/skills" skills 2>&1 | sed 's/^/  /'
    rc=1
  fi
  for d in agents template; do
    if ! diff -rq "$stage/$d" "$d" >/dev/null 2>&1; then
      echo "DRIFT in $d/:"
      diff -rq "$stage/$d" "$d" 2>&1 | sed 's/^/  /'
      rc=1
    fi
  done
  rm -rf "$stage"
  [[ $rc -eq 0 ]] && echo "In sync with the template repo."
  exit $rc
fi

# Preserve the plugin's own skills across the wipe.
for o in "${PLUGIN_OWNED_SKILLS[@]}"; do
  [[ -d "skills/$o" ]] && cp -r "skills/$o" "$stage/skills/$o"
done

rm -rf skills agents template
mv "$stage/skills" "$stage/agents" "$stage/template" .
rm -rf "$stage"

echo "Synced: $(ls skills | wc -l) skills, $(ls agents | wc -l) agents, workspace template."
