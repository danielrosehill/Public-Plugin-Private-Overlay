# Ship checklist

Run before publishing a plugin or cutting a release. Each item is a real failure, not a
style preference.

## Separation

- [ ] Nothing is written into `${CLAUDE_PLUGIN_ROOT}` at run time
- [ ] No secret values, and no mention of where the user keeps secrets, in any public
      repository
- [ ] No user particulars in the plugin or the template: names, usernames, hostnames,
      emails, account and project IDs, org names, home paths. Grep for them
- [ ] No parallel private fork exists; private skills, if any, live in a fitting private
      plugin and pass a "private only when" test
- [ ] MCP servers declare `${ENV_VAR}` indirection rather than embedded URLs or keys

## Overlay

- [ ] A `setup` skill writes `profile.env`, asking only for what it cannot detect
- [ ] Every skill has the load step at the top and a `## Data storage` section
- [ ] The resolver follows the order: `$<PLUGIN>_HOME`, `$CLAUDE_USER_DATA/<plugin>/`,
      `~/.claude-user-data/<plugin>/` if that root exists, the XDG `claude-plugins` root
      if it exists, then `~/.claude-user-data/<plugin>/`
- [ ] Every `profile.env` key is documented: name, skills that use it, default
- [ ] A first run works with no overlay
- [ ] Formats are looked up overlay first, by name; built-ins are read in place
- [ ] Secrets are named by environment variable only
- [ ] Nothing reads the superseded `~/.claude-plugins/<plugin>/`
- [ ] Nothing is written to the overlay unprompted, and the path is stated when it is
- [ ] Merge rules for shipped-vs-user data state conflict, list and freshness behaviour

## Plugin

- [ ] `plugin.json` parses; `name` matches the marketplace entry
- [ ] The plugin is listed in one marketplace only, the public one
- [ ] Every skill's frontmatter `name` matches its directory name
- [ ] Every skill and command has a `description` that says *when* to use it
- [ ] Version bumped, including for changes that only touched vendored files
- [ ] Plugin-owned skills are in a **list**, not hardcoded per call site

## Template repository (workspace plugins)

- [ ] Marked as a **template repository** in GitHub settings, or
      `gh repo create --template` fails
- [ ] Clones and runs standalone with the plugin uninstalled
- [ ] Carries its own `AGENTS.md` and method docs
- [ ] Its blank data files are blank: header-only CSVs, unfilled forms
- [ ] Its README describes the template; the creating skill replaces it per instance

## Sync

- [ ] `--check` passes
- [ ] Vendored copies are byte-identical to the template
- [ ] Sync works from a local checkout and from a clean clone of the upstream
- [ ] It refuses, rather than warns, if the template's data files carry rows

## Workspace creation

- [ ] Confirms before creating, showing the exact command
- [ ] Defaults to private, and states what the repository will hold
- [ ] Honours `<PLUGIN>_TEMPLATE` from the overlay
- [ ] Writes the marker file with `template`, `template_version` and `backing`
- [ ] Finds an existing workspace by searching upward for the marker
- [ ] Falls back to a local scaffold when `gh` is unavailable, and says what was lost
- [ ] Idempotent: re-running never overwrites a file that already has content

## Before announcing

- [ ] Installed from the marketplace with the overlay moved aside, and it still works
- [ ] The owner's own run, with their overlay, behaves as intended
- [ ] An update simulated (reinstall over the top) and nothing was lost
- [ ] For a converted private plugin: new repository, an old SHA returns 404
