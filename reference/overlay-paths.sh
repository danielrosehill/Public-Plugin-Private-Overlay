#!/usr/bin/env bash
# Reference implementation for the Public Plugin, Private Overlay standard:
#   https://github.com/danielrosehill/Public-Plugin-Private-Overlay
#
# Resolve a plugin's overlay (its user data folder) and look up templates
# overlay first. Copy to scripts/overlay-paths.sh and set the variables at the top.
#
#   overlay-paths.sh              data folder, the rule that picked it, profile state
#   overlay-paths.sh dir          data folder only
#   overlay-paths.sh templates    every template, overlay first: <name>\t<user|builtin>\t<path>
#   overlay-paths.sh template N   path of template N (user copy wins), exit 1 if none
#
# Resolution order (first match wins):
#   1. $<PLUGIN>_HOME
#   2. $CLAUDE_USER_DATA/<plugin>
#   3. ~/.claude-user-data/<plugin>                      if ~/.claude-user-data exists
#   4. ${XDG_DATA_HOME:-~/.local/share}/claude-plugins/<plugin>   if that root exists
#   5. ~/.claude-user-data/<plugin>                      default
set -euo pipefail

NAME=my-plugin                   # the plugin's name
HOME_VAR=MY_PLUGIN_HOME          # its override variable
TEMPLATE_GLOB='*'                # e.g. '*.yaml'
BUILTIN_TEMPLATES=templates      # built-ins, relative to the plugin root
LEGACY="$HOME/.claude-plugins/$NAME"   # superseded location: reported, never read

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
XDG_ROOT="${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins"

if [[ -n "${!HOME_VAR:-}" ]]; then
  DIR="${!HOME_VAR}"; RULE="$HOME_VAR"
elif [[ -n "${CLAUDE_USER_DATA:-}" ]]; then
  DIR="$CLAUDE_USER_DATA/$NAME"; RULE="CLAUDE_USER_DATA"
elif [[ -d "$HOME/.claude-user-data" ]]; then
  DIR="$HOME/.claude-user-data/$NAME"; RULE="existing ~/.claude-user-data"
elif [[ -d "$XDG_ROOT" ]]; then
  DIR="$XDG_ROOT/$NAME"; RULE="existing $XDG_ROOT"
else
  DIR="$HOME/.claude-user-data/$NAME"; RULE="default"
fi

list_templates() {
  declare -A seen=()
  if [[ -d "$DIR/templates" ]]; then
    for f in "$DIR/templates"/$TEMPLATE_GLOB; do
      [[ -e "$f" ]] || continue
      b=$(basename "$f"); seen[$b]=1
      printf '%s\tuser\t%s\n' "$b" "$f"
    done
  fi
  for f in "$PLUGIN_ROOT/$BUILTIN_TEMPLATES"/$TEMPLATE_GLOB; do
    [[ -e "$f" ]] || continue
    b=$(basename "$f")
    [[ -n "${seen[$b]:-}" ]] && continue
    printf '%s\tbuiltin\t%s\n' "$b" "$f"
  done
}

case "${1:-}" in
  dir) echo "$DIR" ;;
  templates) list_templates ;;
  template)
    n="${2:?template name}"
    if [[ -e "$DIR/templates/$n" ]]; then echo "$DIR/templates/$n"
    elif [[ -e "$PLUGIN_ROOT/$BUILTIN_TEMPLATES/$n" ]]; then echo "$PLUGIN_ROOT/$BUILTIN_TEMPLATES/$n"
    else echo "no template named '$n'" >&2; exit 1; fi ;;
  "")
    echo "data_dir: $DIR"
    echo "rule: $RULE"
    echo "plugin_root: $PLUGIN_ROOT"
    echo "profile: $([[ -f "$DIR/profile.env" ]] && echo present || echo missing)"
    if [[ -d "$LEGACY" ]]; then echo "legacy_dir: $LEGACY (superseded; offer to move it)"; fi
    ;;
  *) echo "usage: $0 [dir|templates|template NAME]" >&2; exit 2 ;;
esac
