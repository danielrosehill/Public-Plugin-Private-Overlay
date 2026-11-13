# Extract: https://code.claude.com/docs/en/plugins/components

Verbatim sections from Anthropic's documentation, fetched 2026-11-13 by `scripts/anthropic-guidance.py`. Copyright Anthropic; quoted for reference. Don't edit by hand: run `update`.

<!-- section: Ask the user for configuration values -->
## Ask the user for configuration values

Declare the values your plugin needs from the user in the `userConfig` manifest key, so users don't edit `settings.json` themselves. Each option appears in a dialog with its `title` as the label and its `description` beneath it.

Set `"sensitive": true` for a token or password. The dialog then masks the input, and the value is stored in secure storage rather than `settings.json`.

This manifest asks for an endpoint and a token:

```json .claude-plugin/plugin.json theme={null}
{
  "name": "my-plugin",
  "userConfig": {
    "api_url": {
      "type": "string",
      "title": "API URL",
      "description": "Base URL of your team's API"
    },
    "api_token": {
      "type": "string",
      "title": "API token",
      "description": "Token for your team's API",
      "sensitive": true
    }
  }
}
```

### When the configuration dialog appears

The dialog is part of the interactive `/plugin` interface. When the user does any of the following, it opens for any option that isn't set yet:

* Installs the plugin in `/plugin`
* Runs `/plugin install <plugin>@<marketplace>` inside a session
* Enables the plugin from the **Installed** tab in `/plugin`

To open the same dialog at any time, the user runs `/plugin configure <plugin>@<marketplace>`.

The VS Code extension's [Manage plugins dialog](https://code.claude.com/docs/en/vs-code.md#install-plugins) asks for unset options as a form after an install, and a gear icon on the plugin's row opens the form again with every option.

The `claude plugin install` shell command never prompts for `userConfig` values. To set values from the shell, pass each one as `--config KEY=VALUE` when you install, or pipe a JSON object to [`claude plugin configure --values-stdin`](https://code.claude.com/docs/en/plugins/cli-reference#plugin-configure) afterward.

When options remain unset, `claude plugin install` prints a `userConfig options not yet set` line. For the line's exact text, see [The `userConfig` dialog never appears](https://code.claude.com/docs/en/plugins/troubleshooting#the-userconfig-dialog-never-appears).

For the option fields, where each value is stored, how a component references a saved value, and which fields reject `${user_config.*}`, see [User configuration](https://code.claude.com/docs/en/plugins/manifest-reference.md#user-configuration).

<!-- section: Reference plugin paths and store data -->
## Reference plugin paths and store data

You don't know where your plugin will be installed, so refer to its files and data through these variables rather than fixed paths. They're substituted in skill, command, and agent content, in hook and monitor commands, and in MCP and LSP server configurations. They're also exported to hook, MCP, and LSP processes:

* **`${CLAUDE_PLUGIN_ROOT}`**: the plugin's install directory. Each version has its own [cache directory](https://code.claude.com/docs/en/plugins/loading.md#find-plugins-on-disk), so the path changes when the plugin updates. Don't write state there
* **`${CLAUDE_PLUGIN_DATA}`**: a directory that survives updates, for `node_modules`, virtual environments, and caches. It resolves to `~/.claude/plugins/data/<id>/` and is created when first referenced
* **`${CLAUDE_PROJECT_DIR}`**: the project root, the same value hooks receive

In the data directory path, `<id>` is the plugin identifier with every character other than letters, digits, `_`, and `-` replaced by `-`, so `my-plugin@my-marketplace` becomes `my-plugin-my-marketplace`.

On Windows, most substituted paths use forward slashes, as in `C:/Users/you/...`. They keep their native backslashes in an [exec-form hook](https://code.claude.com/docs/en/hooks.md#exec-form-and-shell-form) and in a hook that runs through PowerShell, which is the default shell on Windows when Git Bash isn't installed.

### Install dependencies into the data directory

For a marketplace-installed plugin, Claude Code installs eligible [Node.js package dependencies](https://code.claude.com/docs/en/plugins/loading.md#node-js-package-dependencies) automatically when it caches the plugin, so you may not need to install them yourself. When you do, this `SessionStart` hook installs `node_modules` into `${CLAUDE_PLUGIN_DATA}` on first run and again after an update changes `package.json`:

```json hooks/hooks.json theme={null}
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "diff -q \"${CLAUDE_PLUGIN_ROOT}/package.json\" \"${CLAUDE_PLUGIN_DATA}/package.json\" >/dev/null 2>&1 || (cd \"${CLAUDE_PLUGIN_DATA}\" && cp \"${CLAUDE_PLUGIN_ROOT}/package.json\" . && npm install) || rm -f \"${CLAUDE_PLUGIN_DATA}/package.json\""
          }
        ]
      }
    ]
  }
}
```

After the first session, `~/.claude/plugins/data/<id>/node_modules` exists. An MCP server can then set `NODE_PATH` to `${CLAUDE_PLUGIN_DATA}/node_modules` in its `env`. For which fields substitute which variable, see [Environment variables](https://code.claude.com/docs/en/plugins/manifest-reference.md#environment-variables).
