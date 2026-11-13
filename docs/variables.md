# The binding contract

The parts only form one system if each can find the others at run time. Every binding is
**indirect**: the plugin hardcodes no user path, no workspace location and no secret.

## Plugin → its own bundled files

`${CLAUDE_PLUGIN_ROOT}` is set by Claude Code to the installed plugin directory (other
agents have an equivalent). Use it for anything the plugin ships and a skill reads:

```
${CLAUDE_PLUGIN_ROOT}/templates/    built-in formats, read in place
${CLAUDE_PLUGIN_ROOT}/template/     a vendored workspace scaffold, if any
${CLAUDE_PLUGIN_ROOT}/reference/    static data the skills read
```

Never write here. It is replaced on update, so a write either vanishes later or appears
to work for weeks first.

## Plugin → overlay

Resolved, first match wins:

```
1. $<PLUGIN>_HOME
2. $CLAUDE_USER_DATA/<plugin>/
3. ~/.claude-user-data/<plugin>/                              if ~/.claude-user-data exists
4. ${XDG_DATA_HOME:-~/.local/share}/claude-plugins/<plugin>/  if that root exists
5. ~/.claude-user-data/<plugin>/                              default
```

The plugin name is the plugin's own, so two plugins cannot collide. Every skill reads the
overlay in its load step. Only `setup`, or a skill the user asks to save something,
writes it.

The standard shape of `profile.env`:

```sh
MYPLUGIN_DEFAULT_OWNER=<user-or-org>
MYPLUGIN_DEFAULT_VISIBILITY=private
MYPLUGIN_WORKSPACE_PARENT=~/repos
MYPLUGIN_TEMPLATE=<owner>/<template-repo>   # the fork point
# Comments are instructions the skills follow.
```

`<PLUGIN>_TEMPLATE` is what makes a workspace plugin forkable. Ship the author's template
as the default. If the user sets their own, every workspace comes from theirs. That one
key is the difference between "works out of the box" and "locked to the author".

Full detail: [overlay.md](overlay.md).

## Plugin → workspace

Two steps: find the root, then confirm what it is.

**Find it** by looking for a marker file in the current directory and then upward. A
user can then invoke a skill from a subdirectory, and the plugin never guesses that the
enclosing git repository is the workspace, which is wrong whenever the workspace sits
inside something larger.

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

`template_version` earns its place the first time a workspace looks broken and turns out
to predate a template change.

## Workspace → plugin

**None, deliberately.** A workspace must not depend on the plugin that created it.

If the workspace needs instructions to be self-running, it carries **copies**: its own
`skills/`, `agents/` and `AGENTS.md`, from the template. A workspace that resolves a path
into the plugin install directory breaks when the plugin is uninstalled, updated or
opened on another machine.

## Secrets

Never a value, in any part. The skill names the environment variable it reads:

```
Reads: SOME_SERVICE_API_KEY
```

The user's own route fills it. The plugin does not say where secrets live and does not
store pointers to them. For MCP servers, `.mcp.json` supports `${ENV_VAR}` indirection:

```json
{"mcpServers": {"svc": {"type": "http", "url": "${SVC_MCP_URL}"}}}
```

## Failure modes worth handling explicitly

| Situation | Correct behaviour |
| --- | --- |
| No overlay | Proceed with defaults and offer `setup` at the end. Never fail |
| Overlay key with a bad value | Say which key and which file, rather than silently using the default |
| `<PLUGIN>_TEMPLATE` names a template that no longer exists | Say so, rather than falling back to the author's |
| Old `~/.claude-plugins/<plugin>/` present | Report it and offer to move it. Do not read it |
| No marker found | Offer to create a workspace. Do not assume the current directory is one |
| Marker found, wrong plugin | Say so. Two plugins' workspaces can sit side by side |
| Secret variable unset | Name the variable. Do not suggest where to get it |
| `gh` missing or unauthenticated | Fall back to a local workspace and say what was lost |
