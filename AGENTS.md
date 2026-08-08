# Building a PWV plugin — instructions for an agent

Directives for an agent asked to build, extend or audit a Claude Code plugin following
the Plugin–Workspace–Vault pattern. The reasoning is in [README.md](README.md) and
`docs/`; this is what to *do*.

## First, check the pattern applies

PWV is overhead. Do not apply it because it was asked for by name if the plugin does not
need it — say so instead. It fits when **at least two** hold:

- Work accumulates across sessions and the user returns to it
- There is state a user would want to read, correct, diff or keep
- Settings must survive `/plugin update`
- Output must stay usable with the plugin uninstalled

One of these alone is usually a vault and nothing more.

## Placing a file

Ask which clock it runs on. This answers nearly every case:

| Question | Leg |
| --- | --- |
| Thrown away and replaced on `/plugin update`? | Plugin |
| The thing being worked on; would you want its history? | Workspace |
| True about the *user*, not the project; unhappy to commit it? | Vault |

Never write into `${CLAUDE_PLUGIN_ROOT}` at run time. It works until the first update
and then loses data silently.

## Build order

1. **Template repo first.** Define the working structure and the skills that operate on
   it. Mark it as a template repository on GitHub. It must be usable standalone by
   cloning — if it needs the plugin, the split is wrong.
2. **Plugin second**, vendoring from the template. Add only the skills that create or
   manage a workspace, plus commands and MCP declarations.
3. **Vault last**, once you know which questions the plugin asks every time. Those are
   the config keys, and no others.

Doing it in this order stops the template becoming a dumping ground for whatever the
plugin found inconvenient.

## Non-negotiables

**The template repo is canonical.** A change to a shared file goes there first, then
reaches the plugin through the sync. The other direction works once, then the next sync
reverts it.

**Vendored copies stay byte-identical.** No local adjustments. `--check` is worthless
the moment one file legitimately differs.

**Plugin-owned skill names live in a list**, not hardcoded in each place the sync
touches them. Two of them arrives sooner than expected.

**No credential values anywhere.** Vault holds pointers — `op://` references, env var
names. MCP servers use `${ENV_VAR}` indirection in `.mcp.json`.

**No user-specific defaults in the plugin or the template.** A GitHub username in a
public template becomes every fork's default.

**Never write the vault unprompted.** Read it always; write only when asked; say the
path when you do.

**Never fail because the vault is missing.** A first run works with no setup.

## Creating a workspace

```bash
gh repo create <name> --template <owner>/<template> --private --clone
```

- **Private by default.** Confirm explicitly before running — creating a repo is
  outward-facing and not something to do on inference. Show the exact command.
- **State what the repo will hold** in that confirmation, so a `--public` choice is made
  knowingly rather than by an unread default.
- Read `template` from the vault if set, so a user's fork wins over the author's.
- No wait loop needed; `gh` handles the instantiation race.
- Afterwards: write the marker file, replace the template's README with a status page
  for this project, commit, push.
- Fall back to a local scaffold if `gh` is missing, and say what was lost.

## The marker file

`.<plugin-name>` at the workspace root. Find it by searching the current directory and
then upward — never assume the enclosing git repo is the workspace.

```yaml
created: <YYYY-MM-DD>
template: <owner>/<repo>
template_version: <plugin version>
backing: github          # github | local
repo: <owner>/<name>
workspace_root: .
```

## Auditing an existing plugin

Check, in this order — each finding is a real bug, not a style note:

1. Does anything write into the plugin directory at run time? → will be wiped
2. Any credential value, GitHub username or personal path in either public repo?
3. Does the template clone and run standalone, with the plugin uninstalled?
4. Does `--check` pass, and are vendored copies byte-identical?
5. Is the plugin-owned skill list a list?
6. Does a first run work with no vault present?
7. Does workspace creation confirm before creating, and default to private?
8. Do the shipped/user merge rules state conflict, list and freshness behaviour?

## Reference material to copy

| File | Use |
| --- | --- |
| [`reference/sync-from-template.sh`](reference/sync-from-template.sh) | Drop in, set four variables at the top |
| [`reference/create-workspace.SKILL.md`](reference/create-workspace.SKILL.md) | Fill-in-the-blanks workspace creation skill |
| [`docs/checklist.md`](docs/checklist.md) | Run before shipping |
