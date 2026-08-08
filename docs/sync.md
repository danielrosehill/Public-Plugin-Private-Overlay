# Keeping the plugin and the template in step

If the plugin vendors a copy of the template — to scaffold a local workspace, or to
ship the same skills both ways — you now have two copies of the same files and a
standing opportunity to edit the wrong one.

This is the pattern's main maintenance cost. It is manageable, but only if you decide
the direction once and make drift detectable.

## Pick a canonical side and never argue with it

**The template repo is canonical. The plugin's copy is a build artefact.**

The template is the thing users instantiate, fork and read; it has to be right on its
own. Making the plugin canonical would mean the template is generated from a plugin —
which inverts the dependency and means a fork of the template is a fork of nothing in
particular.

So: **a change to a shared file goes to the template first**, then reaches the plugin
through a sync. Doing it the other way round works exactly once, and then the next sync
silently reverts it.

## What is shared and what is not

| Owned by the template | Owned by the plugin |
| --- | --- |
| The working directory structure and its starting files | `.claude-plugin/plugin.json`, `.mcp.json` |
| Skills that operate on the workspace | Commands |
| Subagent definitions | Skills that create or manage a workspace |
| Method documentation, `AGENTS.md` | The sync script itself |

The split is functional, not arbitrary: **skills that operate on a workspace belong to
the template** — they must work in an instance with the plugin uninstalled — while
**skills that create a workspace belong to the plugin**, because inside an instance
there is nothing left for them to do.

Keep the plugin-owned skill names in a list at the top of the sync script rather than
hardcoding one in three places. Two of them appears sooner than you expect, and each
place you missed shows up as permanent phantom drift.

## Make drift detectable

A sync script with a `--check` mode, run before release:

```bash
./scripts/sync-from-template.sh --check    # exit 1 and print a diff on drift
./scripts/sync-from-template.sh            # refresh from upstream
./scripts/sync-from-template.sh --from ../local-checkout
```

The comparison is only meaningful if the vendored copies are **byte-identical**. Resist
"small local adjustments" — the moment a vendored file is legitimately different, the
check reports drift forever and everyone learns to ignore it.

Prefer a local checkout when one exists and fall back to a shallow clone of the
upstream, so the script works both on the author's machine and in CI.

A working implementation is in
[`reference/sync-from-template.sh`](../reference/sync-from-template.sh).

## Guard against shipping live data

A template repo's blank files can quietly acquire real content — someone tries the
workflow in the template checkout instead of an instance, and now the scaffold ships
with their answers in it.

Have the sync refuse rather than warn:

```bash
# Data files must ship empty: header-only CSVs, unfilled forms.
if [[ "$(wc -l < "$f")" -gt 1 ]]; then
  echo "REFUSING: $f carries data rows." >&2
  exit 1
fi
```

Cheap to write, and it fails at the only moment anyone is looking.

## Versioning

Bump the plugin version on any synced change, even one that only touched vendored
files — from a user's side that is a behaviour change, and the plugin version is the
only number they can see.

Record the template version in each workspace's marker file. When a workspace looks
broken because it predates a template change, that field is the difference between a
diagnosis and a guess.

## When not to vendor at all

If the plugin only ever creates workspaces from the template on GitHub and never
scaffolds locally, it does not need a vendored copy — `gh repo create --template` reads
the template directly, and the whole sync problem disappears.

Vendor only for the offline path: scaffolding into an existing repo, or working without
`gh`. That is a real requirement, but check that you have it before paying for it.
