# Extract: https://code.claude.com/docs/en/plugins/manifest-reference

Verbatim sections from Anthropic's documentation, fetched 2026-11-13 by `scripts/anthropic-guidance.py`. Copyright Anthropic; quoted for reference. Don't edit by hand: run `update`.

<!-- section: Fields -->
## Fields

The table lists top-level keys in `plugin.json`. `name` is the only required key. Where a field name is a link, the linked section has its full rules.

For component keys such as `commands` and `hooks`, [Component path forms](#component-path-forms) shows each accepted shape with an example, and every path follows the [path rules](#path-rules) for the `./` prefix, extensions, and containment.

| Field | Type | Description |
| :- | :- | :- |
| `$schema` | String | JSON Schema URL for editor autocomplete. Claude Code ignores it at load time |
| [`name`](#name) | String | Plugin identifier, required. Use kebab-case. Every component is namespaced under it |
| [`displayName`](#displayname) | String | Name shown in UI in place of `name` |
| [`version`](#version) | String | Version string. Setting it keeps users on that version until you change it |
| `description` | String | Short explanation of what the plugin provides |
| `author` | Object | `name`, which is required, plus optional `email` and `url` |
| `homepage` | String | Documentation URL. Must parse as a URL, or the plugin fails to load |
| `repository` | String | Source repository URL. Not validated |
| `license` | String | SPDX identifier such as `MIT` or `Apache-2.0` |
| `keywords` | Array of strings | Discovery tags |
| [`metadata`](#metadata) | Object | Free-form object for your own data. Claude Code doesn't read it |
| [`icon`](#directory-listing-fields) | String | Icon for the plugin's listing in Anthropic's directory. Claude Code doesn't read it |
| [`documentationUrl`](#directory-listing-fields) | String | Documentation link for the plugin's listing in Anthropic's directory. Claude Code doesn't read it |
| [`supportUrl`](#directory-listing-fields) | String | Support link for the plugin's listing in Anthropic's directory. Claude Code doesn't read it |
| [`privacyPolicyUrl`](#directory-listing-fields) | String | Privacy policy link for the plugin's listing in Anthropic's directory. Claude Code doesn't read it |
| [`termsOfServiceUrl`](#directory-listing-fields) | String | Terms of service link for the plugin's listing in Anthropic's directory. Claude Code doesn't read it |
| [`defaultEnabled`](#defaultenabled) | Boolean | Whether the plugin starts enabled when the user hasn't set it. Defaults to `true` |
| [`dependencies`](#dependencies) | Array of strings or objects | Plugins that must be enabled for this one to work |
| [`userConfig`](#user-configuration) | Object | Values Claude Code prompts the user for when the plugin is enabled |
| `types` | Path | A `.d.ts` file that declares the `$.state` values and `$` nouns of a [mod](https://code.claude.com/docs/en/plugins/mods/reference.md#files) |
| [`channels`](#channels) | Array of objects | Message channels the plugin provides, each bound to one of its MCP servers |
| `skills` | Path, or array of paths | Directories to scan for skills, each a directory of `<name>/SKILL.md` folders or one folder holding `SKILL.md` directly. `"."` names the plugin root. Adds to the default `skills/` scan |
| [`commands`](#commands) | Path, array of paths, or object | Flat `.md` command files, directories of them, or an object map of command name to `source` or `content`. Replaces the default `commands/` scan |
| `agents` | Path, or array of paths | Agent `.md` files. Directories aren't accepted. Replaces the default `agents/` scan |
| [`hooks`](#hooks) | Path, object, or array of either | `.json` hook files or inline hook config. Loaded together with `hooks/hooks.json` |
| [`mcpServers`](#mcpservers) | Path, object, or array of either | `.json` MCP config files, `.mcpb` or `.dxt` bundles, or inline server configs keyed by name. Loaded together with `.mcp.json`; a server name declared later replaces an earlier one |
| [`lspServers`](#lspservers) | Path, object, or array of either | `.json` LSP config files or inline server configs keyed by name. Loaded together with `.lsp.json` |
| `outputStyles` | Path, or array of paths | Output style files or directories. Replaces the default `output-styles/` scan |
| `workflows` | Path, or array of paths | [Workflow](https://code.claude.com/docs/en/workflows.md#distribute-a-workflow-in-a-plugin) `.js` files or directories. Replaces the default `workflows/` scan |
| `experimental` | Object | Container for `themes`, `monitors`, and `evals`, whose manifest shape may still change |
| `experimental.themes` | Path, or array of paths | Theme files or directories. Replaces the default `themes/` scan. A top-level `themes` key still loads, with a `claude plugin validate` warning |
| [`experimental.monitors`](#monitors) | Path, or inline array | A `.json` file holding the monitors array, or the array itself. Defaults to `monitors/monitors.json`. A top-level `monitors` key still loads, with a `claude plugin validate` warning. Monitors [don't start with the `-p` flag](https://code.claude.com/docs/en/plugins/components#monitors) |
| `experimental.evals` | Path, or array of paths | Directory that holds the plugin's [eval cases](https://code.claude.com/docs/en/plugin-evals.md#use-a-different-eval-directory) when it isn't the default `evals/`. `claude plugin eval --eval-dir` overrides it |

In the Type column, a path is a string relative to the plugin root, such as `"./custom/commands"`.

### `name`

The plugin identifier. It must be non-empty, with no spaces, `@`, `:`, path separators, control characters, or bidirectional-formatting characters; use kebab-case.

Claude Code namespaces every component under it, so an agent `reviewer` in plugin `deploy-tools` appears as `deploy-tools:reviewer`.

`claude plugin validate` also checks that the name doesn't pass as one of Anthropic's own plugins. The check ignores case and treats any run of separators as one:

| Name | Result |
| :- | :- |
| Starts with `claude-`, `anthropic-`, `anthropics-`, or `cc-plugin-` | Error |
| Is `claude`, `anthropic`, `anthropics`, `claude-code`, or `claude-mods` | Error |
| Puts `official` beside `claude` or `anthropic`, such as `official-claude-tools` | Error |
| Has `claude`, `anthropic`, or `anthropics` as a whole word anywhere else, such as `mcp-for-claude` | Warning |

The error reads `Plugin name "<name>" is reserved: it passes as one of Anthropic's own`, and the warning reads `Plugin name "<name>" reads as one of Anthropic's own`. `claude plugin init` and `claude plugin tag` refuse a name that draws the error. Claude Code still installs and loads a plugin whose name they refuse.

### `displayName`

The name shown in UI in place of `name`. It may contain spaces and any casing, and it isn't used for namespacing or lookup.

For a marketplace-installed plugin, a `displayName` on the [marketplace entry](https://code.claude.com/docs/en/plugins/marketplace-reference.md#plugin-entries) takes precedence over this value.

### `version`

A version string, not checked against semver. Setting it pins the plugin to that version until you change it; see [Versions and updates](https://code.claude.com/docs/en/plugins/loading.md#versions-and-updates). A plugin with a [`command` source](https://code.claude.com/docs/en/plugins/marketplace-reference), a plugin from a [marketplace hosted on claude.ai](https://code.claude.com/docs/en/plugins/install.md#add-from-claude-ai), and a plugin [loaded in place](https://code.claude.com/docs/en/plugins/loading.md#find-plugins-on-disk) from a marketplace added from a local path aren't pinned by this field.

### `metadata`

A free-form object for your own data, such as catalog or entitlement fields. Claude Code doesn't read it.

### Directory listing fields

Anthropic's directory reads the `icon`, `documentationUrl`, `supportUrl`, `privacyPolicyUrl`, and `termsOfServiceUrl` fields from `plugin.json` for your plugin's listing when you [submit the plugin](https://code.claude.com/docs/en/plugins/publish.md#submit-to-anthropics-directory). Claude Code ignores them at load time. Set them only in `plugin.json`. In a [marketplace entry](#marketplace-entries-and-the-manifest), `claude plugin validate` reports each one as an unknown field.

Set `icon` to the path of an image file inside the plugin, such as `./logo.png`, and each of the four URL fields to an `https://` URL.

> [!NOTE]
>
> `claude plugin validate` doesn't report these fields in `plugin.json` as unknown on Claude Code v2.1.281 or later. Earlier versions print an `Unknown field` warning for each one, so a `--strict` run fails on those versions.

### `defaultEnabled`

Whether the plugin starts enabled when the user hasn't set it in [`enabledPlugins`](https://code.claude.com/docs/en/settings-reference#enabledplugins). Defaults to `true`. A plugin that an enabled plugin depends on starts enabled regardless. The same field in the marketplace entry overrides this one.

Once a user's `enabledPlugins` entry is written, it persists across plugin updates, so changing `defaultEnabled` in a later release doesn't change the setting for an existing user.

### `dependencies`

Plugins that must be enabled for this one to work. Each entry is `"name"`, `"name@marketplace"`, or `{ "name": "...", "marketplace": "...", "version": "..." }`. Bare names resolve against this plugin's own marketplace. See [dependency constraints](https://code.claude.com/docs/en/plugins/dependencies.md).

<!-- section: User configuration -->
## User configuration

`userConfig` declares values Claude Code prompts the user for when the plugin is enabled, so users don't edit `settings.json` themselves.

Keys are identifiers made of letters, digits, and underscores, and can't start with a digit.

Each value is a strict object with these fields. An unknown key fails validation.

| Field | Required | Description |
| :- | :- | :- |
| `type` | Yes | One of `string`, `number`, `boolean`, `directory`, or `file` |
| `title` | Yes | Label shown in the configuration dialog |
| `description` | Yes | Help text shown beneath the field |
| `required` | No | If `true`, the configuration dialog doesn't accept an empty value |
| `default` | No | Value used when the user provides nothing: a string, number, boolean, or array of strings |
| `options` | No | For `string`, the values the field accepts, shown as a picker in `/config`. See [Limit a field to fixed options](#limit-a-field-to-fixed-options). Requires Claude Code v2.1.271 or later |
| `multiple` | No | For `string`, allows an array of strings |
| `sensitive` | No | If `true`, masks input and stores the value in secure storage instead of `settings.json` |
| `min` / `max` | No | Bounds for `number` |

Each option of each enabled plugin also appears as a row in the `/config` panel, except `sensitive` options and `multiple` lists. The `/config` rows require Claude Code v2.1.269 or later.

This `userConfig` declares an endpoint and a masked token:

```json theme={null}
{
  "userConfig": {
    "api_endpoint": {
      "type": "string",
      "title": "API endpoint",
      "description": "Your team's API endpoint"
    },
    "api_token": {
      "type": "string",
      "title": "API token",
      "description": "API authentication token",
      "sensitive": true
    }
  }
}
```

### Limit a field to fixed options

Set `options` on a `userConfig` field to make users pick its value from a fixed list.

To limit a `tone` field to three options, list them in `options` and set `default` to one of them:

```json theme={null}
{
  "userConfig": {
    "tone": {
      "type": "string",
      "title": "Tone",
      "description": "Voice for generated replies",
      "options": ["neutral", "warm", "formal"],
      "default": "neutral"
    }
  }
}
```

If you declare `options` on any field, users on Claude Code versions before v2.1.271 can't load the plugin.

`options` applies to a `string` field that isn't `multiple` or `sensitive`. Set `default` to one of the listed values, or set `required: true` so the user must pick one. Each option is a plain label of 1 to 64 characters, and `claude plugin validate`, which you run in your shell, reports anything else it rejects. A plugin whose `options` break these rules fails to load.

### Where values are stored

Non-sensitive values are saved under [`pluginConfigs`](https://code.claude.com/docs/en/settings-reference#pluginconfigs) in the user's `settings.json`. Sensitive values go to the platform's secure credential store instead. The [settings page](https://code.claude.com/docs/en/settings-reference.md#pluginconfigs) lists which settings files `pluginConfigs` is read from.

### Reference a saved value

Reference a saved value where the plugin needs it, in one of two forms:

* **`${user_config.KEY}`**: substituted in MCP server config, LSP server config, [exec-form](https://code.claude.com/docs/en/hooks.md#exec-form-and-shell-form) hook `args`, and skill and agent content. In skill and agent content, only non-sensitive values are substituted, and a sensitive value there becomes a placeholder
* **`CLAUDE_PLUGIN_OPTION_<KEY>`**: exported to hook processes for every option, with `<KEY>` uppercased. A shell-form hook reads `$CLAUDE_PLUGIN_OPTION_API_TOKEN` for `api_token`

### Fields that run through a shell

Shell-form hook commands, monitor commands, and MCP [`headersHelper`](https://code.claude.com/docs/en/mcp#use-dynamic-headers-for-custom-authentication) reject `${user_config.*}`. A component that references it in one of these fields fails with an [error](https://code.claude.com/docs/en/errors.md#plugin-command-references-user-config) instead of running, because the field's value is passed to a shell that would re-parse the substituted value.

The table shows how the value can reach each of these fields instead.

| Field | How the value can reach it |
| :- | :- |
| Shell-form hook commands | Use [exec form](https://code.claude.com/docs/en/hooks.md#exec-form-and-shell-form) with `args`, or read `CLAUDE_PLUGIN_OPTION_<KEY>` from the hook's environment |
| Monitor commands | Not through Claude Code. Monitor processes don't receive `CLAUDE_PLUGIN_OPTION_<KEY>`, so the monitor script has to obtain the value on its own |
| MCP `headersHelper` | Not through Claude Code. The helper's environment carries `CLAUDE_PLUGIN_ROOT`, `CLAUDE_CODE_MCP_SERVER_NAME`, and `CLAUDE_CODE_MCP_SERVER_URL` but no option values, so the helper script has to obtain the value on its own |

<!-- section: Environment variables -->
## Environment variables

Claude Code provides three path variables to plugin components. Reference them as `${NAME}` in the fields listed under [Where each variable resolves](#where-each-variable-resolves), and read them as environment variables in the processes that receive them.

| Variable | Resolves to | Use it for |
| :- | :- | :- |
| `${CLAUDE_PLUGIN_ROOT}` | Absolute path of the plugin's installed version | Scripts, binaries, and config files bundled with the plugin |
| `${CLAUDE_PLUGIN_DATA}` | `~/.claude/plugins/data/<id>/`, created on first reference and kept across plugin updates. `<id>` is the plugin identifier with every character other than a letter, digit, `_`, or `-` replaced by `-` | Installed dependencies such as `node_modules`, generated code, and caches |
| `${CLAUDE_PROJECT_DIR}` | The project root | Project-local scripts and config files |

`${CLAUDE_PLUGIN_ROOT}` changes when the plugin updates, so don't write state there. For where the root moves and when the old directory is cleaned up, see the [loading page](https://code.claude.com/docs/en/plugins/loading.md).

By default, Claude Code deletes the `${CLAUDE_PLUGIN_DATA}` directory when you uninstall the plugin from the last place it's installed. For `--keep-data` and the other cases where it stays, see [plugin uninstall](https://code.claude.com/docs/en/plugins/cli-reference.md#plugin-uninstall).

### Where each variable resolves

In each plugin component, `${...}` references resolve inline in specific fields, and some components also receive the variables in their process environment:

| Plugin component | Fields where `${...}` resolves | Exported to the process |
| :- | :- | :- |
| Hook commands | Anywhere in `command` and `args` | `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_PROJECT_DIR`, and `CLAUDE_PLUGIN_OPTION_<KEY>` |
| Monitor commands | Anywhere in `command` | Not exported |
| MCP `stdio` servers | `command`, `args`, `env` | `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_PROJECT_DIR` |
| MCP `http`, `sse`, `ws` servers | `url`, `headers`, `headersHelper` | Not applicable |
| LSP servers | `command`, `args`, `env`, `workspaceFolder` | `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_PROJECT_DIR` |
| Skill, command, and agent content | Anywhere in the Markdown body | Not applicable |

The variables aren't present in the environment of commands Claude runs through the Bash tool, in the main session or in a subagent. In skill, command, and agent content, write the `${...}` reference in the Markdown body instead, and Claude Code substitutes the path inline when it loads the content.

### Quoting and path separators

Keep each substituted path a single argument:

* **Hook commands**: use [exec form](https://code.claude.com/docs/en/hooks.md#exec-form-and-shell-form) with `args` so each path is one argument with no quoting
* **Shell-form hooks and monitor commands**: wrap the variable in double quotes so a path with spaces stays one word

If you leave one of these variables outside quotes in a shell-form command in a hooks file, `claude plugin validate` warns about it unless the hook sets [`shell`](https://code.claude.com/docs/en/hooks#command-hook-fields) to `"powershell"`.

This shell-form hook runs a script bundled with the plugin:

```json theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/process.sh"
          }
        ]
      }
    ]
  }
}
```

On Windows, most substituted paths use forward slashes, as in `C:/Users/you/...`. They keep their native backslashes in an [exec-form hook](https://code.claude.com/docs/en/hooks.md#exec-form-and-shell-form) and in a hook that runs through PowerShell, which is the default shell on Windows when Git Bash isn't installed.

<!-- section: Standard layout -->
## Standard layout

Each component type has a default location under the plugin root, used when the manifest doesn't point elsewhere.

| Component | Default location | Contents |
| :- | :- | :- |
| Manifest | `.claude-plugin/plugin.json` | Plugin metadata and configuration. Optional |
| Skills | `skills/` | One `<name>/SKILL.md` per skill. A plugin with `SKILL.md` at its root, no `skills/`, and no `skills` key loads as a single skill |
| Commands | `commands/` | Flat Markdown command files. Prefer `skills/` for new plugins |
| Agents | `agents/` | Agent Markdown files. Subfolders are part of the [agent name](https://code.claude.com/docs/en/plugins/components.md#agents) |
| Hooks | `hooks/hooks.json` | Hook configuration |
| MCP servers | `.mcp.json` | MCP server definitions |
| LSP servers | `.lsp.json` | LSP server configurations |
| Output styles | `output-styles/` | Output style Markdown files |
| Workflows | `workflows/` | Workflow `.js` files |
| Themes | `themes/` | Theme JSON files |
| Monitors | `monitors/monitors.json` | The monitors array |
| Executables | `bin/` | Files here are on the Bash tool's `PATH` while the plugin is enabled, so Claude runs them as bare commands. claude.ai and Cowork don't install a plugin that has this directory, including one you [distribute through claude.ai organization settings](https://claude.com/docs/plugins/org-sync#keep-executables-out-of-the-top-level-bin-directory) |

A plugin that uses default locations, plus a `scripts/` folder that its hooks call, is laid out like this:

```text theme={null}
deploy-tools/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── deploy/
│       └── SKILL.md
├── commands/
│   └── status.md
├── agents/
│   └── reviewer.md
├── hooks/
│   └── hooks.json
├── monitors/
│   └── monitors.json
├── output-styles/
│   └── terse.md
├── themes/
│   └── dracula.json
├── workflows/
│   └── release-audit.js
├── bin/
│   └── deploy-tool
├── scripts/
│   └── format.sh
├── .mcp.json
└── .lsp.json
```

To click through this layout and read what each file does, open the [plugin explorer](https://code.claude.com/docs/en/plugins/components.md#explore-the-plugin-directory).

A `CLAUDE.md` at the plugin root isn't loaded as context, and `claude plugin validate` warns when it finds one. To include instructions that load into Claude's context, put them in a skill.

<!-- section: Marketplace entries and the manifest -->
## Marketplace entries and the manifest

A [marketplace entry](https://code.claude.com/docs/en/plugins/marketplace-reference.md) accepts [its own fields](https://code.claude.com/docs/en/plugins/marketplace-reference.md#plugin-entries), including `strict`, and every field on this page except the [directory listing fields](#directory-listing-fields).

The `strict` field decides whether the entry may add components to a plugin that has its own `plugin.json`. It defaults to `true`.

### How entry fields combine with `plugin.json`

The entry either serves as the manifest, adds components to it, or conflicts with it:

* **No `plugin.json`**: the entry is the manifest, regardless of `strict`. Entry `hooks` loads only in the inline object form. For a file path or array there, the `/plugin` **Errors** tab shows a `not yet supported in a marketplace entry` error
* **`plugin.json` present, `strict` unset or `true`**: Claude Code loads the manifest and appends the entry's `commands`, `agents`, `skills`, `outputStyles`, and `themes` to it. For `hooks`, the entry's matchers for an event replace the manifest's matchers for that same event, and events only the manifest declares keep theirs
* **`plugin.json` present, `strict: false`**: an entry that declares any of `commands`, `agents`, `skills`, `hooks`, `outputStyles`, or `themes` is a conflict, and the plugin fails to load with `Plugin <name> has conflicting manifests`

When a [marketplace entry whose `source` is the marketplace root](https://code.claude.com/docs/en/plugins/marketplace-reference) lists specific `skills` subdirectories, only those subdirectories load, and the plugin's default `skills/` directory isn't scanned. A `skills` key in the manifest instead [adds to the default](#how-each-key-combines-with-its-default-location).

### Metadata precedence

Some metadata fields have a fixed precedence regardless of `strict`:

* **`defaultEnabled` and display fields**: the entry's `defaultEnabled` and its [display fields](https://code.claude.com/docs/en/plugins/marketplace-reference.md#entry-and-plugin-json) such as `displayName` override the manifest's
* **`version`**: the manifest's `version` overrides the entry's
* **`name`**: when the entry lists the plugin under a different `name` than the manifest, `enabledPlugins` uses the entry name, and components are namespaced under the manifest name

For the full precedence table, see [Strict mode](https://code.claude.com/docs/en/plugins/marketplace-reference.md).
