# Public plugin, private overlay: directives for agents

For an agent asked to build, convert, extend or audit an agent plugin (Claude Code or
similar). Reasoning is in [README.md](README.md) and `docs/`. This is what to do.

The standard follows Anthropic's plugin and skill guidance and adds only what that guidance
leaves open: a home for user-authored content. Mapping and sources:
[docs/anthropic-alignment.md](docs/anthropic-alignment.md). If Anthropic's docs and this
file disagree, the docs win; update this file.

## The shape

- One public, generic plugin.
- Everything about the user in the overlay, a data folder outside the plugin.
- Never a parallel private fork.
- A private companion plugin only if a skill passes a "private only when" test:
  nothing useful is left without the particulars; its existence is sensitive or
  belongs to a client or employer; or the owner has a standing rule covering it.
- A private workspace repository, from a public template, only for plugins that
  accumulate work.

## Placing a particular

| Particular | Home |
| --- | --- |
| Values: hosts, IDs, emails, paths, account names | Overlay `profile.env` |
| Secrets | Environment variable name in the skill. Never a value, never a location |
| Formats: templates, presets, voices, layouts | Overlay `templates/`, same name as the built-in |
| Procedure: "in my setup, always do X first" | Overlay `<skill-name>.md` |
| Records: logs, history, state | Private workspace repository |
| Caches, downloads, generated files, rebuildable snapshots, dependencies | `${CLAUDE_PLUGIN_DATA}`, else overlay `cache/` |
| Required scalar settings and secrets in Claude Code | `userConfig` (`sensitive: true` for secrets), mirrored in `profile.env` except secrets |
| Code, built-in templates, defaults | Plugin (`${CLAUDE_PLUGIN_ROOT}`, read only) |

Unsure? Ask which clock it runs on: replaced on update (plugin), true about the user
(overlay), the thing being worked on (workspace).

## Overlay location

First match wins:

1. `$<PLUGIN>_HOME`
2. `$CLAUDE_USER_DATA/<plugin>/`
3. `~/.claude-user-data/<plugin>/` if `~/.claude-user-data` exists
4. `${XDG_DATA_HOME:-~/.local/share}/claude-plugins/<plugin>/` if that root exists
5. `~/.claude-user-data/<plugin>/`

Never `${CLAUDE_PLUGIN_ROOT}`. Never `${CLAUDE_PLUGIN_DATA}` or anything else under
`~/.claude`: Claude Code deletes the data directory on uninstall, and user content must
outlive that. `~/.claude-plugins/` is the superseded location: offer to migrate it, don't
read it.

## Build order

1. **Sort the particulars** with the table above.
2. **Write the generic skill** in the public plugin: load step at the top, `## Data
   storage` section at the end, defaults that work with no overlay, overlay-first
   lookup for formats.
3. **Add or extend `setup`** with any new `profile.env` keys. Document each key: name,
   skills that use it, default.
4. **Write the user's particulars to their overlay** so their first run behaves as
   intended. If the user-data root is a git repository, stage only this plugin's folder.
5. **Grep the public diff** for the user's names, hosts, IDs and emails. Hits go to the
   overlay.
6. **Workspace, if needed:** template repository first (usable standalone), plugin
   second.
7. **Report both halves:** what is public, and what was kept private and where.

The load step, verbatim:

```markdown
## 1. Load your settings

Find the data folder: `$<PLUGIN>_HOME`, `$CLAUDE_USER_DATA/<plugin>/`, then
`~/.claude-user-data/<plugin>/`. Read `profile.env` and `<skill-name>.md` if they
exist. They win over the defaults below. If there is no profile, use the defaults
and offer `setup` at the end.
```

## Converting a private plugin

Follow [docs/converting-a-private-plugin.md](docs/converting-a-private-plugin.md). The
steps that cannot be skipped:

- Get the owner's yes before anything is published.
- Write their particulars to the overlay in the same pass.
- Private history: keep a git bundle, create a **new** repository from one clean commit,
  confirm an old SHA returns 404, then make it public. Never flip visibility. Never
  trust a squash or force-push: GitHub serves old commits by SHA.
- Skills with nothing generic left move to a fitting private plugin.
- Move the marketplace entry from private to public in the same change.
- Delete the old repository once the new one is live.

## Non-negotiables

- No user particulars in the plugin or the template repository. Author credit is fine.
- No secret values anywhere, and no mention of where the user keeps them.
- Never write into `${CLAUDE_PLUGIN_ROOT}` at run time.
- Caches go to `${CLAUDE_PLUGIN_DATA}`, user content to the overlay, never the reverse.
- Skills meet Anthropic's limits: `SKILL.md` under 500 lines; `name` of 64 characters or fewer,
  lowercase and hyphenated, without "claude" or "anthropic"; `description` of 1,024 characters
  or fewer, third person, key use case first.
- `plugin.json` `version` matches the marketplace entry, or the entry omits it.
- Never fail because the overlay is missing.
- Write the overlay only through `setup` or when asked, and say the path.
- Built-in templates are read in place, never copied into the overlay.
- The template repository is canonical for shared files; vendored copies stay
  byte-identical.

## Workspace creation

```bash
gh repo create <name> --template <owner>/<template> --private --clone
```

- Private by default. Show the exact command and get a yes; say what the repository
  will hold.
- Read the template from the overlay (`<PLUGIN>_TEMPLATE`) if set, so a fork wins.
- Write the marker file `.<plugin>` ([reference/marker-file.md](reference/marker-file.md)),
  replace the template README with a status page, commit, push.
- No `gh`: fall back to a local scaffold and say what was lost.

## Audit checklist

Each finding is a bug, not a style note:

1. Anything written into the plugin directory at run time?
2. Any name, username, host, email, ID, home path or secret location in a public repo?
3. A private fork or a private duplicate of a public skill?
4. Does every skill have the load step and a `## Data storage` section?
5. Does a first run work with no overlay?
6. Is there a `setup` skill, and are all `profile.env` keys documented with defaults?
7. Are formats looked up overlay first, by name?
8. Are secrets named by variable only?
9. Anything still reading `~/.claude-plugins/`?
10. Caches in `${CLAUDE_PLUGIN_DATA}`, nothing else written under `~/.claude`?
11. Skill limits met (500 lines, name, description)? Manifest and marketplace versions agree?
12. Workspace plugins: does the template run standalone, does `--check` pass, does
    creation confirm and default to private?

Full list: [docs/checklist.md](docs/checklist.md). To audit a whole marketplace and bring
it into line, use the `audit-plugins` skill in this repository (it is also a plugin).

## Reference material

| File | Use |
| --- | --- |
| [sources/anthropic/](sources/anthropic/) | Verbatim extracts of the Anthropic docs the rules rest on; `scripts/anthropic-guidance.py check` detects drift |
| [scripts/audit-plugins.py](scripts/audit-plugins.py) | The audit, used by the `audit-plugins` skill |
| [reference/overlay-paths.sh](reference/overlay-paths.sh) | Overlay resolver and overlay-first template lookup. Set the variables at the top |
| [reference/sync-from-template.sh](reference/sync-from-template.sh) | Template sync with drift check |
| [reference/create-workspace.SKILL.md](reference/create-workspace.SKILL.md) | Workspace creation skill |
