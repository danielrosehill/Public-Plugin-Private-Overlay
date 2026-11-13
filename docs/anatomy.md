# Anatomy

What belongs in each part, and how to decide the awkward cases.

## Plugin

The published capability. One public repository, installed through a marketplace,
replaced wholesale on update.

```
<name>-plugin/
├── .claude-plugin/plugin.json    name, version, description, keywords
├── .mcp.json                     MCP server declarations (env-var indirection only)
├── commands/                     slash commands
├── skills/                       SKILL.md per skill, including setup
├── agents/                       subagent definitions
├── templates/                    built-in formats, overridden by name from the overlay
├── template/                     vendored workspace scaffold (optional)
├── scripts/                      overlay resolver, template sync
└── reference/                    static data the skills read
```

**Everything here is public and disposable.**

- **Nothing user-specific.** No names, hosts, IDs, emails, home paths, account names or
  secret locations. If a skill needs one, it reads a `profile.env` key and has a default
  that works for a stranger.
- **Nothing durable.** Anything written into the plugin directory is gone at the next
  update, with no error.
- **Every skill** starts with the load step and ends with a `## Data storage` section.

### MCP servers

MCP declarations are plugin; their credentials are the user's. Declare the server with
environment variable indirection:

```json
{"mcpServers": {"label-printer": {"type": "http", "url": "${LABEL_PRINTER_MCP_URL}"}}}
```

The repository holds the shape of the connection and none of the secret.

## Overlay

One folder per user, per plugin, outside the plugin. Not inside the plugin, not in the
plugin's repository.

```
<data folder>/
  profile.env        KEY=value. Comments are instructions for this user
  <skill-name>.md    Private notes for one skill
  templates/         User formats; same name as a built-in wins
```

Covered in full in [overlay.md](overlay.md).

## Workspace

One private repository per project, made from a public **template repository**.

| Repository | Visibility | Role |
| --- | --- | --- |
| Template | Public, marked *Template repository* on GitHub | Defines the folder structure and starting files. Canonical |
| Workspace | Private, one per project | An instance. Diverges immediately |

```
<template>/                       public, canonical
├── <working dirs>/               the structure the skills operate on
├── skills/  agents/              optional: makes an instance self-running
├── docs/                         the method, so an instance explains itself
├── AGENTS.md                     rules for any agent opening an instance
└── README.md                     describes the template
```

**Put the skills in the template as well as the plugin** when the workspace should
survive the plugin. Keep the two copies in step with a sync script and a drift check.
See [sync.md](sync.md).

**A new workspace should not keep the template's README.** Have the creating skill
replace it with a short status page.

## Private companion plugin

Only for skills that pass a "private only when" test: nothing useful left without the
particulars, existence itself sensitive or owned by a client or employer, or a standing
rule from the owner. Put such skills in a private plugin that already fits the subject.
Never a private fork of the public plugin.

## The awkward cases

**Defaults that are "mine" but useful to others.** The plugin ships a generic default
and documents the key. The real value goes in `profile.env`.

**A procedure only the owner follows.** `<skill-name>.md` in the overlay, not a second
skill and not a flag in the public one.

**A format only the owner uses.** A file in the overlay's `templates/`. A new format is
data, not a skill.

**Data shipped with the plugin that the user extends.** The shipped data is plugin and
read-only; user entries are overlay; the merge rule is explicit. See
[overlay.md](overlay.md#shipped-data-the-user-extends).

**Output that is both a deliverable and a record.** Workspace. If it should be shared,
export a copy.

**Credentials for a workspace's own remote.** Neither. That is `gh auth` and the user's
git config.

**Blank files a workspace starts with.** Template repository, even if the plugin vendors
a copy. The template is canonical; the vendored copy is a build artefact.

## The counter-test

For any file, ask what happens on each event:

| Event | Plugin | Overlay | Workspace |
| --- | --- | --- | --- |
| Plugin update | Replaced | Untouched | Untouched |
| Plugin published | Public | Unaffected | Unaffected |
| Project finishes | Untouched | Untouched | Archived with the project |
| User switches machine | Reinstalled | Copied or synced by the user | Cloned |

If the answers you want for a file do not match any column, the file is doing two jobs
and should be split.
