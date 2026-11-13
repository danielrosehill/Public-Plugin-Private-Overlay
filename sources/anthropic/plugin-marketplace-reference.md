# Extract: https://code.claude.com/docs/en/plugins/marketplace-reference

Verbatim sections from Anthropic's documentation, fetched 2026-11-13 by `scripts/anthropic-guidance.py`. Copyright Anthropic; quoted for reference. Don't edit by hand: run `update`.

<!-- section: Plugin entries -->
## Plugin entries

Each object in the top-level `plugins` array of `marketplace.json` names a plugin and says where to fetch it. `name` and `source` are required.

Apart from the [directory listing fields](https://code.claude.com/docs/en/plugins/manifest-reference.md#directory-listing-fields), an entry also accepts every [`plugin.json` field](https://code.claude.com/docs/en/plugins/manifest-reference), such as `description`, `version`, `author`, `commands`, and `hooks`. For when those fields apply, see [How an entry combines with plugin.json](#entry-and-plugin-json).

The table lists the entry's own fields and the manifest fields whose meaning changes in an entry.

| Field | Type | Description |
| :- | :- | :- |
| `name` | string | Plugin identifier: letters, digits, `.`, `_`, and `-`, starting with a letter or digit. `claude plugin validate` fails other names, which Claude Code can't install. Users type it before `@` when they install, even when the plugin's own `plugin.json` sets a different `name` |
| `source` | string or object | Where to fetch the plugin. See [Plugin sources](#plugin-sources) |
| `description` | string | Shown in [`/plugin`](https://code.claude.com/docs/en/plugins/install) listings and details |
| `version` | string | Version string for the plugin. When `plugin.json` also sets `version`, `plugin.json` takes precedence and `claude plugin validate` warns. See [Plugin loading reference](https://code.claude.com/docs/en/plugins/loading.md) |
| `category` | string | Free-form category for organizing the catalog |
| `tags` | array of strings | Free-form tags for search |
| `strict` | boolean | Default `true`. Whether `plugin.json` is the definitive source for the plugin's components. See [Strict mode](#strict-mode) |
| `relevance` | object | Signals that tell Claude Code when to suggest the plugin. See [Recommend plugins for your org](https://code.claude.com/docs/en/plugins/relevance.md) |
| `dependencies` | array | Plugins that must be enabled for this one to work. Each item is `"name"`, `"name@marketplace"`, or an object. See [Plugin dependencies](https://code.claude.com/docs/en/plugins/dependencies.md) |
| `defaultEnabled` | boolean | Default `true`. Whether the plugin starts enabled when the user hasn't set it in [`enabledPlugins`](https://code.claude.com/docs/en/settings-reference#enabledplugins). The entry value takes precedence over `plugin.json` |
| `displayName` | string | Human-readable name shown in the UI. When neither the entry nor the plugin's `plugin.json` sets one, users see the plugin's `name` |
| `metadata` | object | Free-form object for your own fields. Claude Code doesn't read it |
| `headers` | object | HTTP headers Claude Code sends when it downloads this entry's [archive](#archive-plugin-source). A header set here replaces a header of the same name from the marketplace source's [`headers`](#fields-by-type). Requires Claude Code v2.1.238 or later |
| `headersHelper` | string | Command that prints this entry's archive-download headers as one JSON object, for a credential that expires. The entry must also set [`"strict": false`](#strict-mode). Requires Claude Code v2.1.238 or later. See [Authenticate archive downloads](https://code.claude.com/docs/en/plugins/host-marketplace.md#authenticate-archive-downloads) |

### How an entry combines with plugin.json

The entry's fields apply differently to a fetched plugin that has its own `.claude-plugin/plugin.json` and to one that doesn't:

* **No `plugin.json`**: the entry is the manifest regardless of `strict`. Every manifest field that the entry accepts applies, including [`mcpServers`, `lspServers`, `userConfig`, and `channels`](https://code.claude.com/docs/en/plugins/manifest-reference).
* **`plugin.json` present**: `plugin.json` is the manifest. [Strict mode](#strict-mode) decides whether the entry's six component fields, `commands`, `agents`, `skills`, `hooks`, `outputStyles`, and `themes`, are combined with it or rejected as a conflict. Entry `mcpServers`, `lspServers`, `userConfig`, and `channels` don't apply. Declare them in `plugin.json`.

#### Hooks in an entry

Write entry `hooks` as an inline object that maps hook event names to matcher arrays. If you write a file path or an array instead, `claude plugin validate` passes it. Those hooks never run, and Claude Code reports a `not yet supported in a marketplace entry` error for the plugin. Put file-based hooks in the plugin's own [`hooks/hooks.json`](https://code.claude.com/docs/en/plugins/components) or `plugin.json`.

#### Display fields

Both the entry and the plugin's own `plugin.json` can set the display fields `displayName`, `description`, `author`, `homepage`, `repository`, `license`, and `keywords`. Users see these values in plugin listings and details, before and after install:

* For a field you set on the entry, users see the entry's value, even when `plugin.json` sets a different one.
* For a field the entry leaves unset, users see the `plugin.json` value.

Before install, Claude Code can read `plugin.json` only for entries with a [relative-path source](#relative-path-plugin-source), whose plugin files are inside the marketplace itself. For an entry with any other source type, users see only the entry's own fields until they install the plugin.

### Strict mode

`strict` decides what happens when the fetched plugin has its own `plugin.json` and the entry also declares any of the [component fields](#entry-and-plugin-json): `commands`, `agents`, `skills`, `hooks`, `outputStyles`, or `themes`. With `strict: true`, the default, Claude Code appends the entry's component fields to `plugin.json`, except `hooks`, whose matchers replace the manifest's per event. With `strict: false`, an entry that declares any component field is a conflict, and the plugin fails to load. The table shows each combination of `strict`, `plugin.json`, and the entry's component fields.

| `strict` | `plugin.json` | Entry component fields | Result |
| :- | :- | :- | :- |
| any | absent | any | The entry is the manifest |
| `true`, the default | present | any | `plugin.json` is the authority. Claude Code appends the entry's component fields to it, except `hooks`, whose matchers [replace the manifest's per event](https://code.claude.com/docs/en/plugins/manifest-reference.md#how-entry-fields-combine-with-plugin-json) |
| `false` | present | none | `plugin.json` is the manifest, as with `true` |
| `false` | present | one or more | Conflict. The plugin fails to load with `Plugin <name> has conflicting manifests: both plugin.json and marketplace entry specify components` |

<!-- section: github plugin source -->
### github plugin source

`repo` takes `owner/repo`. `ref` and `sha` are optional.

```json theme={null}
{
  "name": "formatter",
  "source": {
    "source": "github",
    "repo": "your-org/formatter",
    "ref": "v2.0.0",
    "sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"
  }
}
```
