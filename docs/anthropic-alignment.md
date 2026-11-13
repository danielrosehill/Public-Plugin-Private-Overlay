# Alignment with Anthropic's plugin and skill guidance

This standard is built on what Claude Code provides, not around it. This page records what
Anthropic's documentation says, where it says it, and how each part of the standard maps to it.
Docs read on **2026-11-13**. The exact text relied on is kept verbatim in
[`sources/anthropic/`](../sources/anthropic/), one file per page. The `check-guidance`
skill re-reads those pages, shows what changed, and updates this page first, then the rules.

## What Claude Code provides

| Mechanism | What the docs say | Source |
| --- | --- | --- |
| `${CLAUDE_PLUGIN_ROOT}` | The installed version's directory, `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. "The path changes when the plugin updates. Don't write state there." Old versions are removed 14 days after an update | [components](https://code.claude.com/docs/en/plugins/components.md), [loading](https://code.claude.com/docs/en/plugins/loading.md) |
| `${CLAUDE_PLUGIN_DATA}` | `~/.claude/plugins/data/<id>/`, "created on first reference and kept across plugin updates", meant for "installed dependencies such as `node_modules`, generated code, and caches". **Deleted when the plugin is uninstalled**, unless `claude plugin uninstall --keep-data` | [manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference.md#environment-variables), [CLI reference](https://code.claude.com/docs/en/plugins/cli-reference.md#plugin-uninstall) |
| `userConfig` in `plugin.json` | Options the user is prompted for on install or enable (`/plugin configure` re-opens it). Types: `string`, `number`, `boolean`, `directory`, `file`. `sensitive: true` masks the value and stores it in the platform's secure credential store. Other values are stored under `pluginConfigs` in the user's `settings.json`. Read as `${user_config.KEY}` in MCP and LSP config, exec-form hook args, and skill and agent content (non-sensitive only), and as `CLAUDE_PLUGIN_OPTION_<KEY>` in hook processes. Uninstall deletes the stored options and secrets | [manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference.md#user-configuration) |
| `${CLAUDE_SKILL_DIR}` | The skill's own folder | [skills](https://code.claude.com/docs/en/skills.md) |
| Skill size and shape | "Keep the `SKILL.md` body under 500 lines." References one level deep. A table of contents for reference files over 100 lines. `name` at most 64 characters, lowercase letters, digits and hyphens, without "anthropic" or "claude". `description` at most 1,024 characters, written in the third person, saying what the skill does and when to use it, key use case first | [best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [skills](https://code.claude.com/docs/en/skills.md) |
| Marketplace versions | "The manifest's `version` overrides the entry's." A pinned version keeps users on the cached copy until the string changes. Leave `version` out of both to track commits | [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md) |

Not covered by the docs (as of 2026-11-13): a home for user-authored content that outlives an
uninstall, can be version-controlled, and works with agents other than Claude Code. Writing to
`~/.claude` in general isn't addressed either.

## How the standard maps onto it

Each kind of data has exactly one home:

| Kind of data | Home | Why |
| --- | --- | --- |
| Code, built-in templates, defaults | the plugin, read through `${CLAUDE_PLUGIN_ROOT}` | Anthropic's rule. Never written at run time |
| Caches, downloaded or generated files, dependencies, snapshots the plugin can rebuild | `${CLAUDE_PLUGIN_DATA}` when set. Otherwise `<overlay>/cache/` | Anthropic's designated place. Losing it on uninstall costs nothing |
| A few scalar settings the user must give before first use (an account name, an endpoint) | `userConfig`, optionally, **mirrored** in `profile.env` | Anthropic's prompt-on-install flow. The overlay copy keeps the plugin usable outside Claude Code and after a reinstall |
| Secrets | `userConfig` with `sensitive: true` in Claude Code, or an environment variable the skill names | Anthropic's secure store. Never in the overlay, never in the plugin |
| User-authored content: `profile.env`, `<skill-name>.md` notes, `templates/`, groups and lists | **the overlay**, `~/.claude-user-data/<plugin>/` | The user wrote it, so it must survive uninstall, sit outside the directory Claude Code manages, and be committable to the user's own private repository. `${CLAUDE_PLUGIN_DATA}` does none of these |
| Work products and history | the private workspace repository | Needs its own history and lifecycle |

**Why the overlay is not `${CLAUDE_PLUGIN_DATA}`.** The data directory is deleted with the
plugin, lives inside `~/.claude` (which Claude Code manages), and is keyed by
`<plugin>@<marketplace>`. Moving a plugin to another marketplace therefore gives it a new,
empty folder. A user's notes and templates need none of those properties. Keeping them in
one consistent root outside `~/.claude` also lets one private repository (`git init
~/.claude-user-data`) back up every plugin's overlay at once.

**Why the overlay is not `userConfig`.** `userConfig` holds typed scalars entered in a
dialog. Notes, templates and lists don't fit, and the values aren't visible to other agents.
Use `userConfig` for the handful of values the plugin can't run without, and for secrets.

## Optional: let `userConfig` point at the overlay

A plugin can declare a `directory` option so the install dialog shows where the overlay
is and lets the user move it:

```json
"userConfig": {
  "overlay_dir": {
    "type": "directory",
    "title": "Settings folder",
    "description": "Private folder for your profile, notes and templates. Leave empty for ~/.claude-user-data/<plugin>/",
    "required": false
  }
}
```

The resolution order then starts with `${user_config.overlay_dir}` when it is set, before
`$<PLUGIN>_HOME`. This is **not yet verified** in a released plugin. Before relying on it,
check what an unset option substitutes in skill content.

## Rules this adds to the audit

- Writes go to `${CLAUDE_PLUGIN_DATA}` (caches and generated files) or the overlay (user
  content), never to `${CLAUDE_PLUGIN_ROOT}` or elsewhere under `~/.claude`.
- Caches don't go in the overlay when `${CLAUDE_PLUGIN_DATA}` is available.
- User content doesn't go in `${CLAUDE_PLUGIN_DATA}`.
- `SKILL.md` stays under 500 lines. `name` is at most 64 characters, lowercase and hyphenated,
  and contains neither "claude" nor "anthropic". `description` is at most 1,024 characters.
- `plugin.json` `version` and the marketplace entry's `version` agree, or the entry omits it.
- Secrets that a Claude Code plugin prompts for use `sensitive: true`.
