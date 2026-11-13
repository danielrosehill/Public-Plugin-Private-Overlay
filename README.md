# Public Plugin, Private Overlay

A standard for agent plugins (Claude Code plugins and skills, and similar systems) that
have to work for one specific person without being written for only that person.

**Ship one public, generic plugin. Keep everything about the user in a private data
folder outside it: the overlay.** The plugin reads the overlay every time it runs, so
the same published plugin serves its author and a stranger, and a plugin update never
touches anyone's settings.

Three rules follow from that:

1. **Never a parallel private fork.** A private copy of a public plugin drifts on the
   first fix and is never reconciled. Put the differences in the overlay instead.
2. **A private companion plugin only as a last resort**, when one of the tests below is
   met.
3. **Secrets by environment variable name only.** The plugin says which variable it
   needs. The user's own secrets route fills it. The plugin never stores a value and
   never says where the user keeps them.

Author: Daniel Rosehill.

## Private only when

Make a plugin, or a skill, private only if one of these holds:

- Nothing useful is left once the user's particulars are taken out.
- The workflow's existence is itself sensitive, or it belongs to a client or employer.
- The owner has a standing rule that covers it.

Otherwise it is public, and the particulars go to the overlay.

## Sort every particular

List what in the workflow is specific to the user, and give each item a home.

| Particular | Home |
| --- | --- |
| Values: hosts, IDs, emails, paths, account names | `profile.env` in the overlay |
| Secrets | Neither. The skill names the environment variable; the user's secrets route fills it |
| Formats: templates, presets, voices, layouts | Overlay files, named like the built-ins |
| Procedure: "in my setup, always do X first" | `<skill-name>.md` in the overlay, the skill's private notes |
| Records: logs, history, state | The plugin's workspace repository, private |

If the generic skill still does something useful after that, it is public.

## The three parts

Each part runs on a different clock.

| Part | What it is | Lifecycle | Privacy |
| --- | --- | --- | --- |
| **Plugin** | Skills, agents, commands, MCP declarations, built-in templates | Replaced wholesale on update | Public |
| **Overlay** | A data folder outside the plugin: `profile.env`, per-skill notes, `templates/` | Survives every plugin update | Private, one per user per plugin |
| **Workspace** | A private repository made from a public template repository, holding one project's working state | Created once per project, then diverges | Private, one per project |

Most plugins need the plugin and the overlay. The workspace is for plugins that do
sustained work on something, not ones that answer a question and exit.

### Which clock does it run on

Almost every "where does this file go" question is answered by that:

- Thrown away and replaced when the plugin updates? **Plugin.**
- True about the *user* rather than the project, and you would be unhappy to publish
  it? **Overlay.**
- The thing being worked on, and you would want its history? **Workspace.**

Put a file on the wrong clock and the failure is predictable:

| Mistake | What happens |
| --- | --- |
| User settings inside the plugin directory | Silently wiped by the next update |
| User particulars in the plugin repository | Published to everyone who installs it |
| A private fork to hold the particulars | Drifts from the public plugin and misses every fix |
| Working data in the plugin repository | Published, and mixed into every user's install |
| User preferences in the template repository | Copied into everyone's workspace as defaults |
| Secret values anywhere | Committed, eventually |

## The overlay

```
<data folder>/
  profile.env        KEY=value. Comments are instructions for this user
  <skill-name>.md    Private notes for one skill. They win over the skill's defaults
  templates/         Same names as the plugin's built-ins. The user's copy wins
```

Find the data folder in this order, and stop at the first match:

1. `$<PLUGIN>_HOME`
2. `$CLAUDE_USER_DATA/<plugin>/`
3. `~/.claude-user-data/<plugin>/`, if `~/.claude-user-data` exists
4. `${XDG_DATA_HOME:-~/.local/share}/claude-plugins/<plugin>/`, if that root exists
5. `~/.claude-user-data/<plugin>/` (the default; the setup skill creates it)

Never the plugin install directory, and never the agent's own config directory. Full
detail: [docs/overlay.md](docs/overlay.md).

## What the plugin ships

1. **A `setup` skill** that writes `profile.env`, asking only for what it cannot detect.
2. **A load step at the top of each skill**, which can be copied as is:

   ```markdown
   ## 1. Load your settings

   Find the data folder: `$<PLUGIN>_HOME`, `$CLAUDE_USER_DATA/<plugin>/`, then
   `~/.claude-user-data/<plugin>/`. Read `profile.env` and `<skill-name>.md` if they
   exist. They win over the defaults below. If there is no profile, use the defaults
   and offer `setup` at the end.
   ```

3. **Overlay-first lookup** for formats: the user's file by name, then the built-in.
   Built-ins are read from the plugin, not copied out, so they keep getting fixes.
4. **A `## Data storage` section** in each skill, saying what it reads and writes in the
   overlay.
5. **Defaults that work with no overlay**, since a stranger has none.

A new format is data, not a skill. One generic skill serves every template, and the
template's own fields hold what is particular to it.

## The workspace

For plugins that accumulate work, the third part is a private repository made from a
public **template repository**:

```bash
gh repo create <name> --template <owner>/<template> --private --clone
```

This gives four things at once:

1. The folder structure is defined in one public, reviewable place.
2. The workspace starts private and stays private. It is a fresh repository with no
   upstream link, so nothing in it flows back.
3. History is evidence. Where the order of operations is the guarantee, a commit
   timestamp proves it.
4. The workspace carries its own instructions. If the template includes the skills, the
   repository is runnable by any agent with the plugin uninstalled.

The overlay can name a different template (`<PLUGIN>_TEMPLATE` in `profile.env`), so a
user's fork of the template wins over the author's.

Use a workspace when at least two of these hold:

- The work accumulates across sessions and the user comes back to it.
- There is state the user would want to read, correct, diff or keep.
- The output should stay usable if the plugin is uninstalled or replaced.
- The order in which things happened needs to be provable.

## Superseded: `~/.claude-plugins/<name>/`

An earlier version of this standard (August 2026, then called Plugin-Workspace-Vault)
kept user settings in a "vault" at `~/.claude-plugins/<name>/config.yaml` with a
`credentials.yaml` of secret pointers. That location is superseded by the overlay
resolution order above. To migrate, move the folder's contents to the overlay folder,
turn `config.yaml` keys into `profile.env` lines, and replace credential pointers with
the environment variable names the skills read. A plugin may report the old location
and offer to move it. It should not keep reading from it.

## Read next

| Document | Covers |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Directives for an agent building, converting or auditing a plugin |
| [docs/overlay.md](docs/overlay.md) | The data folder: resolution, contents, load step, secrets, merge rules |
| [docs/converting-a-private-plugin.md](docs/converting-a-private-plugin.md) | Turning an existing private plugin into a public one plus an overlay |
| [docs/anatomy.md](docs/anatomy.md) | What belongs in each part, file by file, with the awkward cases |
| [docs/variables.md](docs/variables.md) | How the plugin finds its own files, the overlay and the workspace |
| [docs/sync.md](docs/sync.md) | Keeping a vendored copy of a template in step, and detecting drift |
| [docs/worked-example.md](docs/worked-example.md) | Real plugins built this way |
| [docs/checklist.md](docs/checklist.md) | Ship checklist |
| [reference/](reference/) | A resolver script, a sync script and skill templates to copy |

## Licence

MIT. See [LICENSE](LICENSE).
