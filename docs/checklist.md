# Ship checklist

Run before publishing a PWV plugin or cutting a release. Each item is a real failure
that has happened, not a style preference.

## Separation

- [ ] Nothing is written into `${CLAUDE_PLUGIN_ROOT}` at run time
- [ ] No credential values in the plugin repo, the template repo, or any committed file
- [ ] No personal defaults — GitHub username, absolute home paths, machine names — in
      either public repo
- [ ] The template's blank data files are actually blank: header-only CSVs, unfilled
      forms, no leftover answers from testing in the template checkout
- [ ] MCP servers declare `${ENV_VAR}` indirection rather than embedded URLs or keys

## Template repo

- [ ] Marked as a **template repository** in GitHub settings — without this,
      `gh repo create --template` fails
- [ ] Clones and runs standalone with the plugin uninstalled
- [ ] Carries its own `AGENTS.md` and method docs, so an instance explains itself
- [ ] Its README describes the *template*; the workspace-creating skill replaces it in
      each instance

## Plugin

- [ ] `plugin.json` parses; `name` matches the marketplace entry
- [ ] Every skill's frontmatter `name` matches its directory name
- [ ] Every skill and command has a `description` that says *when* to use it, not only
      what it does
- [ ] Version bumped, including for changes that only touched vendored files
- [ ] Plugin-owned skills are in a **list**, not hardcoded per call site

## Sync

- [ ] `--check` passes
- [ ] Vendored copies are byte-identical to the template
- [ ] Sync works from a local checkout *and* from a clean clone of the upstream
- [ ] It refuses, rather than warns, if the template's data files carry rows

## Vault

- [ ] A first run works with no vault present
- [ ] Nothing is written to the vault unprompted
- [ ] The path is stated when something is written there
- [ ] The `template` override is honoured, so a fork wins over the author's default
- [ ] Merge rules for shipped-vs-user data state conflict, list and freshness behaviour
- [ ] Credentials are pointers only

## Workspace creation

- [ ] Confirms before creating, showing the exact command
- [ ] Defaults to private, and states what the repo will hold
- [ ] Writes the marker file with `template`, `template_version` and `backing`
- [ ] Finds an existing workspace by searching upward for the marker, not by assuming
      the enclosing git repo
- [ ] Falls back to a local scaffold when `gh` is unavailable, and says what was lost
- [ ] Idempotent: re-running never overwrites a file that already has content

## Before announcing

- [ ] Installed from the marketplace on a machine that is not the author's, or with the
      vault temporarily moved aside
- [ ] One full workspace created, used, and re-opened in a fresh session
- [ ] `/plugin update` simulated — reinstall over the top — and nothing was lost
