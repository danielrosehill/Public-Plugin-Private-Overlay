# Extract: https://code.claude.com/docs/en/plugins/loading

Verbatim sections from Anthropic's documentation, fetched 2026-11-13 by `scripts/anthropic-guidance.py`. Copyright Anthropic; quoted for reference. Don't edit by hand: run `update`.

<!-- section: Find plugins on disk -->
## Find plugins on disk

Claude Code keeps plugin files and state records under one plugins root, which is `~/.claude/plugins` unless you set [`CLAUDE_CODE_PLUGIN_CACHE_DIR`](https://code.claude.com/docs/en/env-vars). Every path in the table is relative to that root.

| Path | What it holds |
| :- | :- |
| `cache/<marketplace>/<plugin>/<version>/` | One directory per installed version of a marketplace plugin. `<plugin>` is the marketplace entry name and `<version>` is the [resolved version](#versions-and-updates). `${CLAUDE_PLUGIN_ROOT}` points at this directory |
| `data/<plugin-id>/` | The plugin's persistent directory, exposed as `${CLAUDE_PLUGIN_DATA}`. For how `<plugin-id>` is formed, see [Path variables and persistent data](https://code.claude.com/docs/en/plugins/components.md#path-variables-and-persistent-data). Claude Code creates it when a plugin component first uses it and keeps it across updates. By default, Claude Code deletes it when you uninstall the plugin from its last scope. For `--keep-data` and the other cases where it stays, see [plugin uninstall](https://code.claude.com/docs/en/plugins/cli-reference.md#plugin-uninstall) |
| `marketplaces/<name>/` | The clone or download of a marketplace added from GitHub, another Git host, or a URL. A marketplace added from a local `file` or `directory` source has no copy here, and its `installLocation` in `known_marketplaces.json` is the path you gave |
| `synced/` | The plugins Claude Code [synced from your claude.ai account](#synced-plugins) |
| `.trash/` | Plugins that the claude.ai sync removed, such as after you turn one off on claude.ai or stop syncing |
| `installed_plugins.json` and `known_marketplaces.json` | The records of what Claude Code has installed and which marketplaces it has fetched, described under [Check which stage a plugin reached](#check-which-stage-a-plugin-reached). A [marketplace hosted on claude.ai](https://code.claude.com/docs/en/plugins/install.md#add-from-claude-ai) is recorded in `known_marketplaces_claudeai.json` instead |
| `flagged-plugins.json` | Plugins Claude Code uninstalled because their marketplace delisted them. They appear in the **Flagged** section of `/plugin`; see [Host a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace.md) |
| `installed_plugins.set-aside.<date>.<hash>.json` and `installed_plugins.unreadable.<date>.<hash>.kept` | Dated copies Claude Code keeps before it drops install records that no version of Claude Code can use or rebuilds an unreadable `installed_plugins.json`. See [the recovery notes](https://code.claude.com/docs/en/plugins/troubleshooting.md#installed-plugins-json-could-not-be-read-and-was-rebuilt). They age out on the [`cleanupPeriodDays`](https://code.claude.com/docs/en/settings-reference#cleanupperioddays) schedule |

Because `${CLAUDE_PLUGIN_ROOT}` points at a version directory, a plugin's root path changes with every version. Keep a plugin's durable files in `${CLAUDE_PLUGIN_DATA}` instead.

### In-place and copied plugins

Claude Code loads some plugins in place from where you keep them and copies the rest into the cache, according to their origin:

* **`--plugin-dir` and skills-directory plugins**: the directory loads in place and is never copied. A `--plugin-url` archive or a `--plugin-dir` `.zip` is extracted into a session temp directory first
* **Relative-path plugins in a marketplace you added from a local path**: the plugin loads in place from its path inside the marketplace folder. Your edits to the source directory take effect at the next session start or `/reload-plugins`, and you don't need to increase the version. The plugin's hook processes and MCP and LSP servers receive a `CLAUDE_PLUGIN_ROOT` that points at the source directory. For its Node.js package dependencies, see [When the dependency install runs](#when-the-dependency-install-runs)
* **`command`-source plugins in [link mode](https://code.claude.com/docs/en/plugins/marketplace-reference.md#command-plugin-source)**: the directory the command printed loads in place, through links in the cache entry
* **Every other marketplace plugin**: Claude Code copies the plugin into `cache/<marketplace>/<plugin>/<version>/` at install and loads that copy. Files outside the plugin directory aren't copied, so when a script inside a copied plugin reads a path above the plugin root, such as `../shared`, it doesn't find them

### Paths that escape the plugin directory

Whether a plugin loads in place or from a cached copy, Claude Code doesn't let it declare components outside its own directory. It rejects a component path that resolves outside the plugin root, whether the path is declared in `plugin.json` or in a marketplace entry:

* **A path that points outside the plugin as written**, such as `../shared-utils`
* **A symlink that leads outside the plugin**, other than [links between plugins within one marketplace](https://code.claude.com/docs/en/plugins/host-marketplace.md#share-files-within-a-marketplace-with-symlinks)
* **On macOS and Linux, a path that contains a backslash anywhere in it**, even when the path stays inside the plugin. Components declared with backslash paths therefore load on Windows only, so write component paths with forward slashes, such as `./commands/deploy.md`

A rejected path appears as a [`path escapes plugin directory`](https://code.claude.com/docs/en/errors#path-escapes-plugin-directory) error, and the plugin loads without that component.

### Cleanup of previous versions

When you update or uninstall a plugin, Claude Code writes an `.orphaned_at` marker into the previous version directory. It removes that directory in a background cleanup 14 days later, so a session that already loaded the old version keeps running.

The sweep runs only while `installed_plugins.json` records at least one install. After you uninstall your last plugin, orphaned directories stay until you install another.

### Node.js package dependencies

When Claude Code copies a plugin into the cache, it also installs the plugin's Node.js package dependencies there, so the plugin's hooks and MCP servers can load them.

This section covers the npm and Bun packages a plugin declares in its own `package.json`. For plugins that depend on other plugins, see [plugin dependency versions](https://code.claude.com/docs/en/plugins/dependencies.md).

#### When the dependency install runs

Claude Code installs the dependencies into the copied version directory each time it creates one:

* When you install a plugin
* When Claude Code updates a plugin to a new version
* At session start when an enabled plugin isn't cached yet, such as on a new machine

For a relative-path plugin [loaded in place](#in-place-and-copied-plugins) from a marketplace you added from a local path, Claude Code doesn't install the dependencies into the source directory. Install them there yourself, or from a hook into [`${CLAUDE_PLUGIN_DATA}`](https://code.claude.com/docs/en/plugins/components#path-variables-and-persistent-data).

The install runs only when the plugin's root directory contains both a `package.json` and a supported lockfile.

The lockfile decides which package manager Claude Code runs:

| Lockfile | Package manager |
| :- | :- |
| `bun.lock` | Bun |
| `npm-shrinkwrap.json` or `package-lock.json` | npm |

If a plugin contains more than one of these lockfiles, Claude Code uses the first match, checking in order: `bun.lock`, `npm-shrinkwrap.json`, `package-lock.json`.

Claude Code skips the install in these lockfile cases:

* **`bun.lockb`**: Bun's binary lockfile can't be checked. Ship a text `bun.lock` or an npm lockfile instead
* **`yarn.lock` or `pnpm-lock.yaml`**: replace it with an npm lockfile
* **A lockfile in a format Claude Code doesn't read**: an npm lockfile needs a `lockfileVersion` of `2` or `3`, which npm 7 or later writes, and a `bun.lock` needs a `lockfileVersion` no higher than `2`

Include an npm lockfile to reach the most users. Claude Code runs the matched lockfile's package manager from the user's PATH and doesn't try the other lockfile instead if that package manager is missing.

For a plugin distributed through an npm source, use `npm-shrinkwrap.json`, because npm excludes `package-lock.json` from published packages.

#### Limits on the dependency install

Claude Code constrains this dependency install so that no code from the plugin or its packages executes during it, and bounds how long it can run:

* **Registry packages only**: every dependency must be a registry package pinned in the lockfile to an exact version. A plugin with a git, GitHub, folder, workspace, or linked dependency gets no install.
* **`https` downloads**: a download link in the lockfile must use `https`, unless it points at the installing user's own default npm registry.
* **A separate install folder**: the package manager runs in a folder of its own that holds only a copy of the checked dependency list, so npm and Bun don't read the plugin's `.npmrc`, `.env`, or `bunfig.toml`. When the install succeeds, Claude Code moves the resulting `node_modules` into the plugin.
* **Frozen resolution**: the install uses exactly the versions the lockfile pins, and Claude Code skips it when `package.json` and the lockfile don't list the same dependencies
* **No lifecycle scripts**: `--ignore-scripts` keeps `preinstall`, `install`, and `postinstall` scripts from running, so dependencies that build native modules in those scripts download but don't compile during this install
* **No overrides or patches**: a plugin whose `package.json` sets npm `overrides` gets no install from an npm lockfile, and a plugin that sets Bun `patchedDependencies` gets no install from `bun.lock`
* **60-second timeout**: Claude Code stops an install that runs longer and treats it as failed

Claude Code fetches an npm-source plugin before this dependency install, and none of the package's own install scripts run during the fetch. See [npm plugin source](https://code.claude.com/docs/en/plugins/marketplace-reference.md#npm-plugin-source).

You can't turn the automatic install off. No setting or environment variable disables it.

In restricted networks, see the [network access requirements](https://code.claude.com/docs/en/network-config.md#network-access-requirements) for the hosts to allow.

#### When the dependency install fails or is skipped

If the install fails or is skipped, the plugin still loads, but the parts of it that need the missing packages may not work.

`/plugin` and `claude plugin list` show a note on an enabled plugin whose cached copy has a lockfile and a `package.json` that lists runtime dependencies, but no `node_modules` directory. The note says whether the install didn't finish or can't run for this plugin. See [the troubleshooting entry](https://code.claude.com/docs/en/plugins/troubleshooting.md#the-packages-it-lists-are-not-installed) for what to do about each.

When the automatic install can't provide a dependency, install it from a hook into the [persistent data directory](https://code.claude.com/docs/en/plugins/components.md#path-variables-and-persistent-data). That includes packages that need their lifecycle scripts to build, Python dependencies, plugins locked with Yarn or pnpm, and dependencies that aren't registry packages, such as git dependencies.

<!-- section: Versions and updates -->
## Versions and updates

If a plugin's author pushed new commits and `claude plugin update` prints `<name> is already at the latest version (<version>).`, the version Claude Code computes for the plugin is unchanged, so the plugin's files on disk don't change.

Claude Code computes a version for every plugin it installs, and that version is how it detects an update. `claude plugin update` and background auto-update compute the version again and don't replace the cached copy when it matches what `installed_plugins.json` records. An update that you start can still [retry an unfinished dependency install](https://code.claude.com/docs/en/plugins/troubleshooting.md#the-packages-it-lists-are-not-installed) in that copy.

The version also names the plugin's cache directory.

A manifest that pins `"version"` is one way the computed version stays the same across commits. See [How Claude Code computes the version](#how-claude-code-computes-the-version) for the resolution order.

A plugin [loaded in place](#in-place-and-copied-plugins) from a marketplace you added from a local path loads its current source files at every session start, whatever its version string says. For a plugin from a [marketplace hosted on claude.ai](https://code.claude.com/docs/en/plugins/install.md#add-from-claude-ai), the version claude.ai records for the plugin is its version, and the manifest's `version` isn't read.

### How Claude Code computes the version

For a marketplace you added by source, Claude Code picks the rule by the `source` type of the plugin's marketplace entry. The [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md#plugin-sources) lists the source types. For every source type in that list except `command`:

1. The `version` field in the plugin's manifest comes first
2. Then the `version` field in the plugin's marketplace entry
3. When neither is set, the version comes from the source type:

| Source type | Version when no `version` field is set |
| :- | :- |
| `github`, `url`, or `git-subdir` | The commit SHA of the source, shortened to 12 characters. A `git-subdir` version also carries a hash of the subdirectory path |
| `archive` | The SHA-256 digest, shortened to 12 characters: the `sha256` pin in the marketplace entry, or the digest of the downloaded file when there is no pin |
| Relative path inside a Git-hosted marketplace | The commit SHA of the installed directory |
| Local directory, when neither the plugin directory nor its marketplace is a git repository | `unknown` |
| `npm` | `unknown` |

Claude Code doesn't take the version from a repository that encloses the install path, such as a git-managed `~/.claude`.

For a `command` source, Claude Code always derives the version from what the command produced: a 12-character hash on its own, or `<manifest version>-<hash>` when the manifest sets one. The marketplace entry's `version` is ignored for command sources. For what the hash covers, see [Copy mode and link mode](https://code.claude.com/docs/en/plugins/marketplace-reference.md#copy-mode-and-link-mode).

Because the manifest comes first, a manifest that pins `"version": "1.0.0"` keeps every user on the cached copy until its author changes the string, however many commits they push. To let users track commits instead, leave `version` out of both the manifest and the entry. [Host a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace.md) covers which choice fits which release setup.

### When Claude Code refreshes a marketplace before an install

When you install a plugin, Claude Code looks it up in its local copy of the marketplace catalog. You can run `/plugin install` in a session or `claude plugin install` in your shell, and name the plugin with or without its marketplace. The table shows which of those combinations refresh the local copy.

| Plugin name | Command | What Claude Code refreshes |
| :- | :- | :- |
| `name@marketplace` | `/plugin install` or `claude plugin install` | The named marketplace, before the lookup |
| `name` alone | `/plugin install` | Only marketplaces that have auto-update on, and only after the lookup misses |
| `name` alone | `claude plugin install` | Nothing. It reads the cached catalogs without refreshing |

The refresh before a `name@marketplace` install doesn't depend on the marketplace's auto-update setting or on `DISABLE_AUTOUPDATER`.

When the refresh fails, the install proceeds from the cached catalog and `claude plugin install` reports `marketplace not refreshed`.

Claude Code skips the refresh before a `name@marketplace` install when:

* The marketplace was added from a local `file` or `directory` source, or is defined inline in settings with a [`settings` source](https://code.claude.com/docs/en/settings-reference#extraknownmarketplaces)
* A [seed directory](https://code.claude.com/docs/en/env-vars.md) supplies the marketplace
* Claude Code refreshed the marketplace within the last 30 seconds
* You set `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`
* [Managed settings](https://code.claude.com/docs/en/plugins/org.md#restrict-what-users-can-install) block the marketplace, in which case Claude Code also refuses the install

### When auto-update runs

In an interactive session, after you send your first message, Claude Code waits a random delay of up to ten minutes. It then refreshes every marketplace with auto-update on and updates the plugins installed from them on disk.

The running session keeps the versions it loaded, and you see `Plugin updated: <name> · Run /reload-plugins to apply`. Whether or not you reload, the new versions load on your next launch.

#### Which marketplaces and plugins auto-update

Whether a marketplace auto-updates follows the first of these that is set:

1. **`autoUpdate` on its `extraKnownMarketplaces` entry** in a settings file
2. **`autoUpdate` on its `known_marketplaces.json` entry**, which the **Enable auto-update** toggle under `/plugin` **Marketplaces** writes. When a settings file also declares the marketplace under `extraKnownMarketplaces`, the toggle writes `autoUpdate` to that settings entry as well
3. **The default**: on for Anthropic's official marketplaces such as `claude-plugins-official`, off for `knowledge-work-plugins` and `first-party-plugins`, on for [marketplaces added from claude.ai](https://code.claude.com/docs/en/plugins/install.md#add-from-claude-ai), and off for every other marketplace

If you set `DISABLE_UPDATES=1`, `DISABLE_AUTOUPDATER=1`, or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`, the whole pass is off and the **Enable auto-update** toggle is hidden, unless you also set `FORCE_AUTOUPDATE_PLUGINS=1`. The [environment variables reference](https://code.claude.com/docs/en/env-vars.md) covers each variable's wider effect.

Auto-update also skips a plugin whose marketplace entry declares a `headersHelper`. [Installs and updates that refuse a command instead of asking](https://code.claude.com/docs/en/plugins/host-marketplace.md#installs-and-updates-that-refuse-the-command-instead-of-asking) explains when such a plugin appears in the `/plugin` **Errors** tab and how you update it from there.

When a copied plugin updates mid-session, hook commands, monitors, MCP servers, and LSP servers keep using the previous version's path. Run `/reload-plugins` to switch hooks, MCP servers, and LSP servers to the new path. Monitors require a session restart.

### When a command source re-runs

Plugins with a `command` source don't wait for the [auto-update pass](#when-auto-update-runs). The printed directory reflects the tool's state at the time the command ran, so Claude Code runs the [command you accepted](https://code.claude.com/docs/en/plugins/host-marketplace.md#change-the-command-of-a-command-source) again at these times:

* Every time you install or update the plugin
* Once per session for each enabled command-sourced plugin, in the background, shortly after the session starts. This run doesn't depend on the marketplace's auto-update setting or on `DISABLE_AUTOUPDATER`
* At startup or on `/reload-plugins`, when an enabled plugin's installed version is missing from the plugin cache

Claude Code skips the two background runs when you set [`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`](https://code.claude.com/docs/en/env-vars). Explicit installs and updates still run the command with that variable set.

When the command's hashed output has changed, Claude Code installs the result as a new version and reloads it in the running interactive session, switching [the same components that `/reload-plugins` switches](https://code.claude.com/docs/en/plugins/cli-reference#reload-plugins). You see a notification that the plugin was reloaded.

If reloading in place would invalidate the session's prompt cache, Claude Code instead prompts you to run `/reload-plugins`, which [warns about the cache cost and applies when rerun with `--force`](https://code.claude.com/docs/en/prompt-caching#enabling-or-disabling-a-plugin).
