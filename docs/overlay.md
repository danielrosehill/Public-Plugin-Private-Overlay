# The overlay

The user's own data for one plugin, in a folder outside the plugin. The plugin is
public and generic. The overlay holds everything that is specific to this user, and the
skills read it every time they run.

## Where it lives

Stop at the first match:

1. `$<PLUGIN>_HOME`: an explicit override for this plugin.
2. `$CLAUDE_USER_DATA/<plugin>/`: a shared user-data root, if the variable is set.
3. `~/.claude-user-data/<plugin>/`, if `~/.claude-user-data` exists.
4. `${XDG_DATA_HOME:-~/.local/share}/claude-plugins/<plugin>/`, if that `claude-plugins`
   root exists.
5. `~/.claude-user-data/<plugin>/`: the default. The setup skill creates it.

`<PLUGIN>` is the plugin name in upper case with hyphens as underscores, or a shorter
prefix the plugin documents (typst-document-generator uses `TYPST_DOCGEN_HOME`).

Not `${CLAUDE_PLUGIN_DATA}`: Claude Code deletes that directory on uninstall and keys it by
marketplace, while the overlay holds what the user wrote. Caches belong there, but the overlay
doesn't. See [anthropic-alignment.md](anthropic-alignment.md).

Ship a small script that prints the resolved folder and the rule that picked it, so a
user can see why the plugin is reading where it is. A generic one is in
[reference/overlay-paths.sh](../reference/overlay-paths.sh).

### Why outside the plugin

It is the only kind of place with both properties user settings need:

- **Not replaced by a plugin update.** The plugin directory is. Settings written there
  work until the first update and then vanish, with no error. The failure looks like the
  user never saved them.
- **Not in the plugin's repository.** Nothing in it can be published by accident.

Never the plugin install directory, and never the agent's own config directory
(`~/.claude/` for Claude Code), which belongs to the agent.

### Why a shared root

One root (`~/.claude-user-data/`) holding a folder per plugin means a user backs up,
syncs or version-controls all their plugin settings in one place, with no collisions
between plugins. If that root is a git repository, a skill that writes to it stages only
its own plugin's folder.

## What it holds

```
<data folder>/
  profile.env        KEY=value. Comments are instructions for this user
  <skill-name>.md    Private notes for one skill. They win over the skill's defaults
  templates/         Same names as the plugin's built-ins. The user's copy wins
```

A plugin may add folders of its own (`exports/`, `registry/`, `logs/`). If a plugin
already has its own layout in this folder, keep it.

### `profile.env`

Plain `KEY=value` lines, prefixed with the plugin's name so keys from different plugins
never clash:

```sh
# Repositories I create are public unless I say otherwise.
MYPLUGIN_DEFAULT_VISIBILITY=public
MYPLUGIN_DEFAULT_OWNER=example-org
# Run scripts through my secrets wrapper: <wrapper> python3 ...
```

Every key is optional and has a default written in the skill that uses it. Comments are
instructions too, and the skills follow them. That is how a user says something the
plugin has no key for, such as how their secrets reach the process.

Document every key in the plugin, in one table: key, which skills use it, default.

### `<skill-name>.md`

Free-text notes for one skill: the user's procedure, their exceptions, "in my setup,
always do X first". The skill reads its own file after `profile.env`, and the notes win
over the skill's defaults. This is where procedure lives that would otherwise tempt
someone to fork the skill.

### `templates/`

The user's own formats, named like the plugin's built-ins. Lookup is overlay first:

1. `<data folder>/templates/<name>`, if it exists.
2. The built-in in the plugin.

Built-ins are read from the plugin in place, never copied into the overlay, so they keep
getting fixes. A user file with a new name adds a format. A user file with a built-in's
name replaces it for that user only.

## The load step

Every skill starts with it:

```markdown
## 1. Load your settings

Find the data folder: `$<PLUGIN>_HOME`, `$CLAUDE_USER_DATA/<plugin>/`, then
`~/.claude-user-data/<plugin>/`. Read `profile.env` and `<skill-name>.md` if they
exist. They win over the defaults below. If there is no profile, use the defaults
and offer `setup` at the end.
```

And every skill ends with a `## Data storage` section that says which overlay files it
reads and which it writes.

## Secrets: by environment variable name only

The plugin never stores a secret, never asks for one to be written to the overlay, and
never says where the user keeps theirs. It names the variable it reads:

```
Reads: SERVICE_API_TOKEN, else the CLI's own login cache.
```

The user's own route fills the variable: their shell, a secrets manager, a wrapper
command. If they need a wrapper, they say so in a `profile.env` comment and the skills
follow it. MCP servers get the same treatment through `${ENV_VAR}` indirection in
`.mcp.json`.

Resolve at the point of use. The value must not reach a file, a log, a draft, a report
or the transcript. A name stays correct when the secret is rotated; a copied value goes
stale and fails in a way that looks like a plugin bug.

## Shipped data the user extends

When a plugin ships reference data that users can extend from the overlay, state all
three merge rules:

| Rule | Sensible default |
| --- | --- |
| Conflict on the same key | User entry wins |
| Lists on the same key | Concatenate, user's first |
| Freshness metadata | The **older** verification date governs the merged entry |

The last one is the non-obvious one. A user override dated today, merged with a shipped
entry verified two years ago, should not make the whole record look fresh.

## Rules for the plugin

- **Never fail because the overlay is missing.** No overlay means defaults, then an offer
  of `setup` at the end. A first run works with no setup.
- **Write only through `setup` or when asked.** A skill that saves its guesses as
  preferences has decided something for the user.
- **Say the path when you write.** "Saved to `~/.claude-user-data/<plugin>/profile.env`."
  One line, so the user can find, edit and delete it.
- **Ship documentation, not a populated file.** Document the keys. Do not write a filled
  profile on install.

## Portability

The overlay is a plain folder of text files. If the user keeps the shared root in a
private git repository, it follows them to a new machine. If not, recreating it is cheap
as long as `profile.env` stays small and documented.

## Migrating from `~/.claude-plugins/<name>/`

The earlier version of this standard used `~/.claude-plugins/<name>/config.yaml` and a
`credentials.yaml` of secret pointers. That location is superseded. Move the contents to
the resolved overlay folder, turn `config.yaml` keys into `profile.env` lines, and
replace credential pointers with the environment variable names the skills read. A
plugin may detect the old folder and offer to move it, but should not read from it.
