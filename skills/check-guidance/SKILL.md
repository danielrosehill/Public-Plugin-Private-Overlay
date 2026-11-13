---
name: check-guidance
description: Maintainer skill for the Public Plugin, Private Overlay standard. It re-reads the Anthropic documentation the standard relies on (plugin manifest, components, CLI, loading, marketplace, skills, Agent Skills best practices) and compares it with the verbatim extracts stored in sources/anthropic/. It reports changed or vanished sections and new ones worth tracking, then updates the extracts, the alignment doc, the directives, the checklist and the audit rules so the standard follows Anthropic's current recommendations. Use on "check Anthropic's guidance", "has the plugin guidance changed", "update the standard to the latest docs", or periodically (monthly, and after Claude Code releases that mention plugins or skills).
---

# Check Anthropic's guidance and update the standard

The standard defers to Anthropic's docs. Where they disagree, the docs win. This skill keeps it
that way. It works on a clone of this repository, not on an installed copy, because it edits
the repository.

## 1. Load your settings

Read `check-guidance.md` from the data folder (`$PPO_HOME`,
`$CLAUDE_USER_DATA/public-private-overlay/`, then `~/.claude-user-data/public-private-overlay/`)
if it exists: it may say where the clone lives. Otherwise find or clone
`Public-Plugin-Private-Overlay` and pull it.

## 2. Check

```bash
python3 scripts/anthropic-guidance.py check > /tmp/guidance-check.json
```

The script fetches each page listed in `sources/anthropic/sources.json` as markdown and
compares every tracked section with its stored extract. It writes nothing. The output gives:

- `changed`: tracked sections whose text differs, each with a diff.
- `missing`: a tracked heading that no longer exists. The section was renamed, moved or
  removed: find where it went.
- `new_headings`: untracked sections on the tracked pages. Most are irrelevant. Add one to
  `sources.json` when it concerns plugin storage, configuration, secrets, versions,
  marketplaces or skill authoring.
- `errors`: a page that didn't load. Retry. If it has moved, find the new URL from the docs
  index (`https://code.claude.com/docs/llms.txt`) and update `sources.json`.

Also look for new pages that should be tracked. Search the docs index for plugin and skill
topics that aren't in `sources.json`.

## 3. Judge each change

For each change, decide whether it affects the standard:

- **Changes the standard:** new or changed storage locations or lifetimes (`${CLAUDE_PLUGIN_DATA}`,
  uninstall behaviour), `userConfig` features, secret handling, skill limits (lines, name,
  description), version and marketplace rules, or new places a plugin must not write.
- **Wording only:** no change beyond refreshing the extract.

## 4. Update, in one commit

1. `python3 scripts/anthropic-guidance.py update` refreshes the extracts and
   `sources/anthropic/index.json`.
2. `docs/anthropic-alignment.md`: update the tables and quotes, and the "read on" date.
3. `AGENTS.md`, `docs/checklist.md` and `docs/overlay.md`, where a rule changed.
4. `scripts/audit-plugins.py`, if a rule's check or limit changed, and the rule table in
   `skills/audit-plugins/SKILL.md`. Then test the script on two or three plugins.
5. `CHANGELOG.md`: what changed in Anthropic's docs, and what changed in the standard.
6. Bump the version in `.claude-plugin/plugin.json` and the marketplace entry. Commit and push.

If a change makes existing plugins non-conforming (for example a new limit), say so and offer
`audit-plugins` to find and fix them.

## 5. Report

List the pages checked and the sections changed. Give the standard's changes in one line each,
or say "no change". Include the commit.

## Data storage

Reads `check-guidance.md` from the data folder. Writes only to this repository's
clone: `sources/anthropic/`, docs, scripts and skills.
