# Anatomy

What belongs in each leg, and how to decide the awkward cases.

## Plugin

The published capability. One public repo, installed through a marketplace, replaced
wholesale by `/plugin update`.

```
<name>-plugin/
├── .claude-plugin/plugin.json    name, version, description, keywords
├── .mcp.json                     MCP server declarations (env-var indirection only)
├── commands/                     slash commands
├── skills/                       SKILL.md per skill
├── agents/                       subagent definitions
├── template/                     vendored copy of the workspace scaffold (optional)
├── scripts/                      maintenance, e.g. the template sync
└── reference/                    static data the skills read
```

**Everything here is public and disposable.** Two consequences authors get wrong:

- **Nothing user-specific.** No API keys, no personal defaults, no "my GitHub
  username". If a skill needs one, it reads it from the vault at run time.
- **Nothing durable.** Anything written into the plugin directory is gone at the next
  update. This is the failure that catches people, because it works fine until the
  first update and then loses data silently, with no error.

### MCP servers

MCP declarations are plugin-leg; their **credentials are vault-leg**. Declare the
server with environment-variable indirection and let the value come from the user's
environment or vault:

```json
{"mcpServers": {"label-printer": {"type": "http", "url": "${LABEL_PRINTER_MCP_URL}"}}}
```

The plugin repo then contains the shape of the connection and none of the secret. This
is the same separation as the rest of the pattern, applied to configuration that
happens to be JSON.

## Workspace

One private repo per project, instantiated from a public **template repo**.

Two repos, distinct roles:

| Repo | Visibility | Role |
| --- | --- | --- |
| Template | Public, marked *Template repository* on GitHub | Defines the folder structure and starting files. Canonical |
| Workspace | Private, one per project | An instance. Diverges immediately and forever |

```
<template>/                       ← public, canonical
├── <working dirs>/               the structure the skills operate on
├── skills/  agents/              optional: makes an instance self-running
├── docs/                         the method, so an instance explains itself
├── AGENTS.md                     rules for any agent opening an instance
└── README.md                     describes the template
```

**Put the skills in the template as well as the plugin** when you want the workspace to
survive the plugin. It looks like duplication and it is the difference between a
directory that needs your plugin installed and one that any agent can pick up. Keep the
two copies in step with a sync script and a drift check — see [sync.md](sync.md).

**A new workspace should not keep the template's README.** It describes the template,
not the project, so the instance's landing page never says what it is. Have the
workspace-creating skill replace it with a short status page.

## Vault

`~/.claude-plugins/<name>/`. One per user, per plugin. Not a repo, not inside the
plugin, never committed.

```
~/.claude-plugins/<name>/
├── config.yaml        preferences and defaults
├── credentials.yaml   pointers only — op:// refs, env var names, item titles
├── registry/          user-authored entries that override or extend shipped ones
└── logs/              anything the plugin needs to remember between runs
```

Covered in full in [vault.md](vault.md).

## The awkward cases

**Defaults that are "mine" but useful to others.** Ship a documented example in the
plugin; write the real values to the vault. The example is documentation, the vault
copy is configuration, and they are allowed to disagree.

**Data shipped with the plugin that the user extends.** Two layers: the shipped
registry is plugin-leg and read-only, user entries are vault-leg, and the merge rule is
explicit — usually user wins on conflict, lists concatenate. Say what happens when the
two disagree, because that is the case people hit.

**Output that is both a deliverable and a record.** Workspace. If it should be shared,
export a copy out; do not move the record.

**Credentials for a workspace's own remote.** Neither leg — that is `gh auth` and the
user's git config. A plugin should never store a token to reach a repo it created.

**Templates, forms and blank files the workspace starts with.** Template repo, not the
plugin, even though the plugin may vendor a copy to scaffold from. The template is
canonical; the vendored copy is a build artefact.

## The counter-test

For any file, ask what happens on each of three events:

| Event | Plugin | Workspace | Vault |
| --- | --- | --- | --- |
| `/plugin update` | Replaced | Untouched | Untouched |
| Project finishes | Untouched | Archived with the project | Untouched |
| User switches machine | Reinstalled | Cloned | Must be recreated or synced by them |

If the answers you want for a file do not match any column, the file is doing two jobs
and should be split.
