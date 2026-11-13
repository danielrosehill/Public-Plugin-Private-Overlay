---
name: audit-plugins
description: Audits every plugin a publisher ships, across one or more marketplaces, against the Public Plugin, Private Overlay standard and Anthropic's plugin guidance, then brings them into line in batches the user approves. It finds personal particulars or secrets in public plugins, writes into the plugin directory or ~/.claude, legacy data locations, skills missing the settings load step, missing setup skills, skill size and naming limits, version drift between plugin.json and the marketplace, plugins listed twice, and parallel private forks. It also finds private plugins that could go public. Use on "audit my plugins", "audit the marketplace", "bring my plugins in line with the standard", "check my public plugins for personal data", "realign plugin storage".
---

# Audit plugins and bring them into line

This is a large job: a publisher can have hundreds of plugins. Work in two phases. **Audit**
is read-only and done in one pass. **Align** runs in batches, each one approved by the user
before anything changes. The source of truth is this repository: `AGENTS.md`,
`docs/checklist.md` and `docs/anthropic-alignment.md`. Read those three before aligning
anything.

## 1. Load your settings

Find the data folder: `$PPO_HOME`, `$CLAUDE_USER_DATA/public-private-overlay/`, then
`~/.claude-user-data/public-private-overlay/`. Read `profile.env` (`PPO_MARKETPLACES`,
`PPO_REPOS_ROOT`, `PPO_PERSONAL_TERMS`) and `audit-plugins.md` if they exist. They win
over the defaults below. With no profile, ask for the marketplace files and the repos root,
and offer `setup` at the end. Without a personal-terms list, the leak check only finds
secrets, so say so.

## 2. Audit (read-only)

Pull the marketplace clones first (`git -C <clone> pull`) so the audit reads what is
published. Then:

```bash
A="${CLAUDE_PLUGIN_ROOT}/scripts/audit-plugins.py"
python3 "$A" $(for m in $PPO_MARKETPLACES; do printf -- '--marketplace %s ' "$m"; done) \
  --repos-root "$PPO_REPOS_ROOT" --personal-terms "$PPO_PERSONAL_TERMS" > "<data folder>/audits/<date>.json"
```

- `--visibility` asks GitHub whether each repo is really public (one API call per plugin, so
  check the rate limit first). Without it, visibility is inferred from the marketplace name
  ("private" in the name means private).
- `--only a,b` audits named plugins. `--plugin <dir> --assume-public` audits a single checkout.
- Small first: run it on three plugins you know, read the findings, then run everything.

Each plugin gets a class:

| Class | Meaning | Priority |
| --- | --- | --- |
| `leak` | public, with a personal term or a secret value | 1. Fix now |
| `fix` | errors or warnings: storage, settings load step, limits, drift | 2 |
| `candidate-public` | private, with no personal terms found | 3. Offer to convert |
| `conforming` | nothing above info level | none |
| `not-found-locally` | listed, but no clone under the repos root | Clone it or skip it, and say which |

The rules, and what each one means:

| Rule | Severity | Fix |
| --- | --- | --- |
| `secret-value` | error | A token or `op://` reference. In a public plugin, treat it as exposed: tell the user to rotate it (their call), replace it with an environment variable name, and check git history ([publishing-private-repo](../../docs/converting-a-private-plugin.md)) |
| `personal-term` | error if public | Move the particular to the overlay (`profile.env` or `<skill>.md`) and write the generic text |
| `author-link` | info | The term appears only inside a URL (author or repo link). Fine |
| `writes-plugin-root` | error | Write to `${CLAUDE_PLUGIN_DATA}` (caches) or the overlay (user content) |
| `touches-dot-claude` | warn | Review it: reads of Claude Code's own files are fine, writes are not |
| `legacy-location` | warn, or info when documented as a migration | Move to the overlay and offer migration |
| `hardcoded-home-path` | warn | Use `~`, `$HOME` or a profile key |
| `user-content-in-plugin-data` | warn | User content belongs in the overlay |
| `no-load-step`, `no-setup-skill`, `resolver-incomplete` | warn | Add the standard load step, a `setup` skill, and the full resolution order |
| `no-data-storage-section` | info | Add `## Data storage` |
| `skill-too-long`, `skill-name-invalid`, `skill-description-*` | warn or error | Anthropic's limits: 500 lines; name of 64 or fewer lowercase-hyphen characters without "claude" or "anthropic"; description of 1,024 or fewer characters |
| `version-drift`, `name-mismatch`, `listed-twice` | warn | Make `plugin.json` and the entry agree. Each plugin is listed in one marketplace |
| `parallel-private-plugin` | info | Fold the private twin's particulars into the public plugin's overlay |

Path rules (`touches-dot-claude`, `legacy-location`, `hardcoded-home-path`,
`user-content-in-plugin-data`) are warnings in code and info in markdown, because prose often
describes a path rather than using it. A plugin can list vendored or quoted material in
`.audit-ignore` at its root, one glob per line (for example `sources/**`).

The script uses heuristics. Before a finding goes into a batch, open the line. A personal
term in an example, or a `~/.claude` path that is only read, is not a bug.

## 3. Report

Write `<data folder>/audits/<date>.md`: the totals by class and by rule, then one row per
plugin that isn't conforming (class, top rules, counts). Show the user the totals, every
`leak` by name, and the proposed batches. Keep personal terms out of anything public: the
report stays in the private data folder.

## 4. Align, one batch at a time

Propose batches of 5 to 10 plugins, in priority order: leaks, then storage errors, then
overlay conformance, then limits and drift, then candidate-public conversions. For each
batch, say what will change in each plugin and **wait for a yes**. Then, per plugin:

1. Pull. Fix by following `AGENTS.md`: particulars to the user's overlay (write them there
   in the same pass, so the user's next run behaves as before), generic text in the plugin,
   the load step, `## Data storage`, `setup`, caches to `${CLAUDE_PLUGIN_DATA}`.
2. Re-run the audit on just this plugin (`--only <name>`) until it is `conforming`, or until
   every remaining finding is reviewed and recorded as acceptable in `audit-plugins.md`.
3. Bump the version in `plugin.json` **and** the marketplace entry. Commit only the paths you
   changed, then push.
4. A leak whose history holds the particular: a public repository keeps serving old commits
   by SHA. Ask whether to recreate the repository (docs/converting-a-private-plugin.md). Never
   rewrite history without a yes.
5. Candidate-public conversions follow docs/converting-a-private-plugin.md in full, including
   the owner's yes before anything is published.

After each batch, push the marketplace changes, refresh whatever indexes the marketplace
(if there is a catalogue, sync it), and report the batch: which plugins went from which class
to which, plus anything skipped and why.

## 5. Close out

Re-run the full audit. Report the before and after totals. Keep both JSON files in
`audits/`. Record any accepted exceptions (rule, plugin, file, reason) in `audit-plugins.md`
so the next audit can skip them.

## Data storage

Reads `profile.env`, `personal-terms.txt` and `audit-plugins.md`. Writes
`audits/<date>.json` and `audits/<date>.md` in the data folder. During alignment, it also
writes to the plugins being fixed and to the user's overlays for those plugins.
