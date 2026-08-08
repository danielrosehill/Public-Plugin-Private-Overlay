# The binding contract

Three legs only form one system if each can find the others at run time. All three
bindings are **indirect** — the plugin hardcodes no user path, no absolute workspace
location, and no secret.

## Plugin → its own bundled files

`${CLAUDE_PLUGIN_ROOT}` is set by Claude Code to the installed plugin directory. Use it
for anything the plugin ships and a skill needs to read or copy:

```
${CLAUDE_PLUGIN_ROOT}/template/     the workspace scaffold to copy out
${CLAUDE_PLUGIN_ROOT}/reference/    static data the skills read
```

Never write here. It is replaced on update, so a write either vanishes later or — worse
— appears to work for weeks first.

## Plugin → vault

A fixed convention rather than a variable:

```
~/.claude-plugins/<plugin-name>/
```

The plugin name is the plugin's own, so no lookup is needed and two plugins cannot
collide. Read at the start of any skill that has user-configurable behaviour; **create
only when the user asks you to save something.** A skill that writes a config file
unprompted has decided on the user's behalf that its guesses are their preferences.

The standard shape:

```yaml
# ~/.claude-plugins/<name>/config.yaml
owner: <github-user-or-org>
visibility: private
workspace_parent: ~/repos
template: <owner>/<template-repo>     # overridable — this is the fork point
```

`template` is what makes the system forkable. Ship the author's template as the
default; if the user sets their own, every workspace the plugin creates comes from
theirs instead. That single key is the difference between "works out of the box" and
"locked to the author".

## Plugin → workspace

Two steps: find the root, then confirm what it is.

**Find it** by looking for a marker file in the current directory and then upward. This
lets a user invoke a skill from a subdirectory without every path breaking, and stops
the plugin guessing that the enclosing git repo is the workspace — which is wrong
whenever the workspace is a subdirectory of something larger.

```
.<plugin-name>            or   .<plugin-name>.yaml
```

**Confirm it** from the marker's contents:

```yaml
created: 2026-08-08          # when this workspace was made
template: <owner>/<repo>     # what it was made from
template_version: 0.3.0      # so a stale-looking file can be explained
backing: github              # github | local
repo: <owner>/<name>         # if backed by a remote
workspace_root: .
```

`template_version` earns its place the first time a workspace looks broken and turns
out to predate a template change. Without it the only diagnosis available is guessing.

## Workspace → plugin

**None, deliberately.** A workspace must not depend on the plugin that created it, or
the pattern's main claim is false.

If the workspace needs instructions to be self-running, it carries **copies** — its own
`skills/`, `agents/` and `AGENTS.md`, instantiated from the template. Copies, not
references: a workspace that resolves a path into `~/.claude/plugins/` breaks the moment
the plugin is uninstalled, updated, or opened on another machine.

## Credentials

Never a value, in any leg. The vault holds a **pointer**:

```yaml
# ~/.claude-plugins/<name>/credentials.yaml
api_key:
  op: "op://Private/Some Service/credential"    # 1Password reference
  env: SOME_SERVICE_API_KEY                     # or an env var name
```

Resolve at the point of use and keep the value out of anything durable — no config
file, no log, no draft, no transcript. For MCP servers this falls out naturally, since
`.mcp.json` already supports `${ENV_VAR}` indirection:

```json
{"mcpServers": {"svc": {"type": "http", "url": "${SVC_MCP_URL}"}}}
```

## Failure modes worth handling explicitly

| Situation | Correct behaviour |
| --- | --- |
| No marker found | Offer to create a workspace. Do not assume the current directory is one |
| Marker found, wrong plugin | Say so. Two plugins' workspaces can sit side by side |
| Vault absent | Proceed with defaults and ask. Never fail because config is missing |
| Vault names a template that no longer exists | Say which key is wrong and where it lives, rather than falling back silently to the author's |
| `gh` missing or unauthenticated | Fall back to a local workspace and say what was lost |
