# Extract: https://code.claude.com/docs/en/plugins/cli-reference

Verbatim sections from Anthropic's documentation, fetched 2026-11-13 by `scripts/anthropic-guidance.py`. Copyright Anthropic; quoted for reference. Don't edit by hand: run `update`.

<!-- section: plugin uninstall -->
### plugin uninstall

Remove an installed plugin from one scope. `remove` and `rm` are aliases for `uninstall`.

```bash theme={null}
claude plugin uninstall <plugin> [options]
```

| Flag | Description |
| :- | :- |
| `-s, --scope <scope>` | Uninstall from scope: `user`, `project`, or `local`. Defaults to `user` |
| `--keep-data` | Preserve the plugin's persistent data directory, `~/.claude/plugins/data/<id>/` |
| `--prune` | Also remove auto-installed [dependencies](https://code.claude.com/docs/en/plugins/dependencies.md) that no remaining plugin needs |
| `-y, --yes` | Skip the `--prune` confirmation prompt. Required with `--prune` when stdin or stdout isn't a TTY |
| `--json` | Print the result as one JSON object on the last line of stdout, in the [same format as `plugin install --json`](#plugin-json-result). Can't be combined with `--prune`. Requires Claude Code v2.1.268 or later |

Uninstall a plugin from project scope:

```bash theme={null}
claude plugin uninstall formatter@my-marketplace --scope project
```

Claude Code prints `Successfully uninstalled plugin: formatter (scope: project)`. When the plugin isn't installed at that scope, the command prints a line that starts `Failed to uninstall plugin "formatter@my-marketplace":` and exits `1`.

If the failure line continues with `"formatter" was not uninstalled:` and names a settings file, Claude Code couldn't confirm that the scope's settings no longer switch the plugin on, so the plugin stays installed with everything it saved. With `--json`, the result carries `failureCode: "settings_still_on"`. This settings check requires Claude Code v2.1.282 or later.

#### What an uninstall deletes and keeps

When you uninstall a plugin from the last scope it's installed at, Claude Code also deletes the plugin's stored [options and secrets](https://code.claude.com/docs/en/plugins/manifest-reference.md#user-configuration) and its data directory, `~/.claude/plugins/data/<id>/`. There are three exceptions:

* With `--keep-data`, the data directory stays
* When another installed plugin uses the same folder, such as one whose ID differs from this one only in letter case, the data directory stays
* When Claude Code can't read the list of installed plugins back after it removes the plugin from that scope, the options, secrets, and data directory all stay, because the plugin may still be installed at another scope. The uninstall still succeeds. The message lists what stayed and how to delete it, and with `--json` the result carries `savedKept: "install_records_unreadable"`

With `--json`, `keptData` reports whether the directory stayed, and `/plugin` shows `· data preserved` when it did. For a directory that stays without `--keep-data`, this reporting requires Claude Code v2.1.281 or later. The `savedKept` field requires Claude Code v2.1.282 or later.

<!-- section: plugin configure -->
### plugin configure

Show an installed plugin's [`userConfig`](https://code.claude.com/docs/en/plugins/manifest-reference#user-configuration) options and which are set, or save values piped in on stdin. Requires Claude Code v2.1.285 or later.

```bash theme={null}
claude plugin configure <plugin>
```

| Flag | Description |
| :- | :- |
| `--values-stdin` | Read option values from stdin as a JSON object of single-line strings and save them. Options you leave out keep their saved values |
| `--json` | Print the result as one JSON object on stdout. Without `--values-stdin`, the object carries the options' `schema` and `choices`, their starting `inputs`, and the `configured` and `unconfigured` option names. With `--values-stdin`, it carries the `saved` option names and, when they could be read back, the `unconfigured` ones |

Without flags, the command lists each option with up to three labels: `required` or `optional`, then `sensitive` for an option the manifest declares sensitive, then `set` or `not set`. It prints no saved values. With `--json`, the output includes the saved values of options that aren't sensitive, and never the text of a sensitive one.

To save values, write them to a file as a JSON object that maps option keys to string values, then pass the file on stdin. Replace `formatter@my-marketplace` with your own plugin's id as `claude plugin list` shows it. This example sets one option named `api_url` from a file `values.json` that contains `{"api_url": "https://example.com"}`:

```bash theme={null}
claude plugin configure formatter@my-marketplace --values-stdin < values.json
```

Claude Code validates each value against the option's declared type and prints `Configuration saved. Restart Claude Code to apply it.` If you pass a key the manifest doesn't declare, or a value that fails validation, the command saves nothing, prints `Failed to save configuration:` with the reason, and exits `1`. With `--json`, a refused value also prints an object on stdout whose `refused` field carries the `message` and, when one option is at fault, its `option` key.

Pass the plugin's full `name@marketplace` id, as `claude plugin list` shows it. `configure` doesn't accept a bare `name`. When no loaded plugin has that id, the command prints `No installed plugin has the id "<plugin>".` and exits `1`.

For the settings of a bundled MCP server, see [`plugin install --config`](#plugin-install) or the **Configure** item in `/plugin`.

<!-- section: plugin update -->
### plugin update

Update a plugin to the latest version its marketplace offers. The new version loads in your next session, or after you run `/reload-plugins` in a running one.

```bash theme={null}
claude plugin update <plugin> [options]
```

| Flag | Description |
| :- | :- |
| `-s, --scope <scope>` | Scope to update: `user`, `project`, `local`, or `managed`. Auto-detected when omitted |
| `-y, --yes` | Accept a changed install command from a [command-source](https://code.claude.com/docs/en/plugins/host-marketplace.md) plugin, without the prompt. Required when stdin or stdout isn't a TTY, unless you pass `--accept-command`. Requires Claude Code v2.1.229 or later |
| `--accept-command <sha256>` | Accept the marketplace-declared command whose `sha256` a previous [`--json` run](#plugin-json-result) reported in `shownCommand`, in place of `-y`. Can't be combined with `-y`. Requires Claude Code v2.1.271 or later |
| `--json` | Print the result as one JSON object on the last line of stdout, in the [same format as `plugin install --json`](#plugin-json-result). Requires Claude Code v2.1.268 or later |

Update a plugin:

```bash theme={null}
claude plugin update formatter@my-marketplace
```

Claude Code prints `Checking for updates for plugin "formatter@my-marketplace"…`, then the result. When nothing is newer, it prints `formatter is already at the latest version (1.0.0).` and exits `0`, unless it [retries the plugin's dependency install](#retry-an-unfinished-dependency-install) and that install fails.

#### Which scope the command updates

If you omit `--scope`, the command updates the plugin at the most specific scope it's installed at for your current project, checking local, project, user, then managed.

Before v2.1.281, the command used `user` when you omitted `--scope`, so updating a plugin installed only at project or local scope failed with `Plugin "<name>" is not installed at scope user`. On those versions, pass `--scope`.

`managed` is the one scope you can update but not install to. For admin-installed plugins, see [Manage plugins for your organization](https://code.claude.com/docs/en/plugins/org.md).

#### Update by bare name

You can pass a bare plugin name, which the command matches against your installed plugins. When installed plugins from different marketplaces share the name, the command refuses the update and lists the qualified `plugin-name@marketplace-name` commands to run instead. Updating by bare name requires Claude Code v2.1.246 or later.

#### Retry an unfinished dependency install

When the plugin is already at its latest version, the command can also retry an unfinished dependency install in its cached copy. For the cases where that retry runs or is skipped, see [The packages it lists are not installed](https://code.claude.com/docs/en/plugins/troubleshooting.md#the-packages-it-lists-are-not-installed). If the retry fails, the output is `Failed to update plugin "formatter@my-marketplace"` with the reason and the exit code is `1`. Before v2.1.287, the command reported the plugin at its latest version without retrying the install.

<!-- section: plugin validate -->
### plugin validate

Validate a plugin manifest, a marketplace manifest, or the skills, agents, and commands in a directory, and exit with a code a CI job can act on. For the create, test, and edit workflow, see [Create a plugin](https://code.claude.com/docs/en/plugins/create.md). For what the validator checks in each manifest, see the [plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference.md) and the [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md).

```bash theme={null}
claude plugin validate <path> [options]
```

| Flag | Description |
| :- | :- |
| `--strict` | Treat warnings as errors, so unrecognized fields and missing metadata that the runtime tolerates fail the run |
| `--json` | Output the validation report as one JSON object with the same exit codes. Requires Claude Code v2.1.259 or later |

Validate a plugin before committing it:

```bash theme={null}
claude plugin validate ./my-plugin --strict
```

#### Validate a directory

The `<path>` is a [manifest file](#validate-a-manifest-file) or a directory. Given a directory, Claude Code picks what to validate by what it finds there:

* `.claude-plugin/marketplace.json`, when it exists
* Otherwise `.claude-plugin/plugin.json`
* Otherwise the component files, chosen by the directory's name. Validating component files without a manifest requires Claude Code v2.1.233 or later:
  * A directory named `skills`, `agents`, or `commands`: the files inside it
  * A directory named `.claude`: the `skills`, `agents`, and `commands` directories inside it
  * Any other directory: those three directories under its `.claude`

When the directory holds both a `.claude-plugin/marketplace.json` and a `.claude-plugin/plugin.json`, Claude Code validates the marketplace and also the plugin's manifest and component files. This requires Claude Code v2.1.289 or later.

Claude Code doesn't follow symlinks inside the directory you name. What it does depends on where the link is:

* **A linked `skills`, `agents`, or `commands` directory under the plugin or `.claude` root**: Claude Code warns that nothing in it was read.
* **A linked entry inside a `skills`, `agents`, or `commands` directory**: Claude Code skips it and warns, per directory, how many entries it skipped that a session would load.
* **The `skills`, `agents`, or `commands` directory you name is itself a symlink, or its parent `.claude` directory is**: Claude Code reports an error and checks nothing in it. Name the real directory instead.

A few files are not read by a validation run:

* **A `SKILL.md` at the plugin root**: when you run `claude plugin validate` against a plugin directory, Claude Code doesn't check a `SKILL.md` at the plugin root
* **A `CLAUDE.md` at the plugin root**: in a plugin run, Claude Code also warns about a `CLAUDE.md` at the plugin root
* **Plugin files in a marketplace run**: from a marketplace directory, Claude Code doesn't open the skill, agent, command, or hook files of plugins the marketplace lists in other directories, or the MCP server files they bundle. To find errors in those files, validate each plugin directory

#### Validate a manifest file

When the file isn't named `plugin.json` or `marketplace.json` and isn't in a `.claude-plugin` directory, Claude Code decides what it is by its fields. It validates the file as a marketplace in these cases, and otherwise as a plugin manifest:

* `plugins` is an array
* `plugins` and `owner` are both present
* The file has a field that only `marketplace.json` defines, such as `owner`, and none that only `plugin.json` defines, such as `author`

To choose the checks yourself, name the file `plugin.json` or `marketplace.json`. Claude Code validates any other file in a `.claude-plugin` directory as a plugin manifest.

#### Output and exit codes

Claude Code prints the file it validated, any errors and warnings with their paths, and a verdict line. The exit code follows the verdict:

| Exit code | Verdict line | Meaning |
| :- | :- | :- |
| `0` | `Validation passed` or `Validation passed with warnings` | The manifest loads. With `--strict`, no warnings either |
| `1` | `Validation failed` or `Validation failed (--strict treats warnings as errors)` | An error, or a warning under `--strict`. [Advice](#advice-on-the-readme) doesn't count, with or without `--strict` |
| `2` | `Unexpected error during validation: <reason>` | The validator itself failed, such as on an unreadable path |

With `--json`, Claude Code writes the report to stdout as one JSON object with these top-level fields:

* `success`: the same verdict the exit code gives
* `strict`: whether the run treated warnings as errors
* `target`: the resolved path Claude Code validated
* `manifest`: the manifest's own result, or `null` for a run without a manifest
* `contents`: per-file results, each naming its `file` and carrying `errors`, `warnings`, and `notes` arrays. Files with no error, warning, or note get no entry, so `contents` is empty when there's nothing to report. For a [directory with `marketplace.json` and `plugin.json`](#validate-a-directory), `manifest` is the `marketplace.json` result and `plugin.json` results go in `contents`
  * `gatingHooks`: whether each [mod](https://code.claude.com/docs/en/plugins/mods/overview.md) hook that can refuse an action, such as a `tool.call` hook, has a [`.catch` handler](https://code.claude.com/docs/en/plugins/mods/events#handle-a-hook-that-fails). Each item gives `module`, `pattern`, `hook`, and `hasCatch`. Requires Claude Code v2.1.290 or later
* `advice`: the [advice](#advice-on-the-readme) of the run, each entry naming the README as `file` and carrying a `message` and the `installLine` to paste. Empty when there is none. Requires Claude Code v2.1.295 or later

On exit `2`, the command writes nothing to stdout. The error message goes to stderr.

#### Advice on the README

An `Advice` block in the output of `claude plugin validate` means a plugin's README has no line that installs the plugin from a marketplace, and it gives you a line to add. Advice isn't an error or a warning. It doesn't change the verdict line or the exit code, with or without `--strict`. It requires Claude Code v2.1.295 or later.

For example, validating the `acme-tools` marketplace's directory prints this advice for its `deploy-helper` plugin:

```text theme={null}
Validating marketplace manifest: /path/to/acme-tools/.claude-plugin/marketplace.json

ℹ Advice (does not change the verdict):

  ❯ /path/to/acme-tools/plugins/deploy-helper/README.md: This README has no line that installs "deploy-helper" from a marketplace. Add the install line, which works in one step on Claude Code 2.1.275 or later.
      /plugin install deploy-helper --marketplace acme/tools

✔ Validation passed
```

To clear the advice, paste the suggested line into the README it names, then run `claude plugin validate` again in your shell. The `Advice` block is gone.

If the suggested line holds the placeholder `<owner>/<repo>`, pasting it unchanged doesn't clear the advice. Get the real source first:

* **You validated the plugin's own directory**: when the marketplace lists the plugin from a directory inside its own, validate that directory instead. When it lists the plugin from somewhere else, such as a GitHub repository, fill in `<owner>/<repo>` yourself
* **You validated the marketplace's directory**: Claude Code fills in the source from the `origin` remote of the `.git` directory at the top of that directory. When it can't use that remote, such as when there is none, replace `<owner>/<repo>` with your marketplace's source yourself

An install line you already wrote counts when `plugin install`, or its short form `plugin i`, is followed on the same line by either of these. The `/plugin` and `claude plugin` spellings both count:

* `<plugin>@<marketplace>`, such as `/plugin install deploy-helper@acme-tools`
* The plugin's name and `--marketplace <source>`, such as `/plugin install deploy-helper --marketplace acme/tools`
