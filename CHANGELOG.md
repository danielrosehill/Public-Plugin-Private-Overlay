# Changelog

## 1.0.0 (2026-11-13)

- Renamed from Claude-Plugin-Workspace-Vault and rewritten as the Public Plugin, Private Overlay
  standard. The vault became the overlay at `~/.claude-user-data/<plugin>/`.
- Aligned with Anthropic's plugin and skill docs (`docs/anthropic-alignment.md`):
  - `${CLAUDE_PLUGIN_DATA}` is used for caches.
  - `userConfig` with `sensitive: true` is used for secrets.
  - The overlay stays outside `~/.claude`, so user content survives uninstall.
  - Skill limits are now checked.
- `sources/anthropic/`: verbatim extracts of seven doc pages, plus `scripts/anthropic-guidance.py`
  to detect drift.
- The repository is now a plugin (`public-private-overlay`) with three skills:
  - `audit-plugins`, backed by `scripts/audit-plugins.py`
  - `check-guidance`
  - `setup`
