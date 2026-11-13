# Worked examples

## Overlay plugins

**typst-document-generator 0.6.0 (2026-11-02).** The first plugin built on the overlay.
It ships generic document templates. The owner's identity, business, logo and own
formats live in `~/.claude-user-data/typst-document-generator/` (or
`$TYPST_DOCGEN_HOME`). Its `scripts/paths.sh` resolves the folder in the standard order
and lists templates overlay first, the user's copy winning by name. It predates the
`profile.env` convention and keeps its own `profile.yaml`, which the standard allows.
[Repository](https://github.com/danielrosehill/typst-document-generator-plugin).

**hf-ops (private) → hugging-face (public, danielrosehill/Hugging-Face-Plugin),
2026-11-13.** A conversion of a private plugin. Account, organisations, collection
names, export folder and support address became `profile.env` keys with generic
defaults. Secrets are named by variable (`HF_TOKEN` and an S3 key pair). The data
folder is `~/.claude-user-data/hugging-face/`. 18 skills went public in a new
repository. Two backup skills had nothing generic left and moved to a private backup
plugin. The procedure is in
[converting-a-private-plugin.md](converting-a-private-plugin.md).
[Repository](https://github.com/danielrosehill/Hugging-Face-Plugin).

## Workspace plugin: spec-led-certification

A system with all three parts, built August 2026. It predates the overlay and used the
superseded `~/.claude-plugins/` location; the table gives the current equivalent.

| Part | Repo / path | Visibility |
| --- | --- | --- |
| Plugin | [spec-led-certification-plugin](https://github.com/danielrosehill/spec-led-certification-plugin) | Public |
| Template | [Spec-Led-Certification](https://github.com/danielrosehill/Spec-Led-Certification) | Public, marked as a GitHub template |
| Workspace | One private repo per search, instantiated from the template | Private |
| Overlay | `~/.claude-user-data/spec-led-certification/` (originally `~/.claude-plugins/spec-led-certification/`) | Private, local |

### What it does

Chooses a professional certification specification-first: it interviews you, derives a
weighted scorecard from your answers alone, **freezes it before any credential is looked
up**, then surveys the market and scores candidates against it.

That freeze is why the workspace has to be a repo. The claim "the scorecard was fixed
before the research ran" is only worth anything if it can be checked, and a commit
timestamp checks it. A folder cannot.

### How the parts divide

**Plugin** — 14 skills, 3 subagents, one command. Twelve of the skills and all three
agents are vendored from the template; two are plugin-owned:

- `create-workspace` — instantiates the template as a private repo and clones it
- `scaffold-workspace` — copies the structure into a local directory when there is no
  `gh`, or when the search belongs inside an existing repo

Both are plugin-owned for the reason in [sync.md](sync.md): inside an existing
workspace there is nothing left for them to do.

**Template** — the working structure (`profile/`, `scorecard/`, `research/`, `report/`),
the twelve stage skills, the three agents, `AGENTS.md`, and a Typst report template.
Because the skills ship in the template, an instantiated workspace is runnable with the
plugin uninstalled, by a different assistant, on a different machine. That is the
agent-agnostic claim delivered rather than asserted.

**Workspace** — one private repo per search, named for the subject and the month, since
a second search on the same subject two years later is a different repo rather than an
overwrite. Holds the profile, the frozen scorecard, the research with its sources, the
reports, and archived previous runs.

**Overlay** — owner, visibility, workspace parent, naming, and the template
override. Without it `create-workspace` asks four questions; with it, one confirmation.

### Points where the pattern earned itself

**The freeze is evidenced by git.** Three mechanisms enforce it, and the one that
actually settles arguments is the commit ordering. Nothing in a folder-based design
could have provided it.

**The workspace outlives the plugin.** The template carries the skills, so the private
repo is not a data directory for a tool — it is a self-contained record of a decision,
readable by whatever comes next.

**The overlay kept personal defaults out of two public repos.** A GitHub username and a
preference for private repos are unremarkable, and neither belongs in a repository
strangers clone. Without the overlay they would have ended up in the template as
"defaults", and every fork would have inherited them.

**Instantiation is not a fork.** `gh repo create --template` produces a squashed
`Initial commit` with no upstream link, so a workspace cannot receive template changes
later. That sounds like a limitation and is the correct behaviour here: changing the
skills underneath a frozen scorecard is exactly the drift the method exists to prevent.

### Things learned building it

**`gh repo create --template --clone` handles the instantiation race itself.** Template
population is asynchronous and an immediate clone can in principle come back empty. It
does not — `gh` retries internally. Verified against a throwaway repo: seven seconds,
46 files, complete. No wait loop is needed, which is worth knowing because writing a
speculative one is the obvious defensive move.

**Hardcoding one plugin-owned skill name cost a false drift report.** The sync script
originally excluded `scaffold-workspace` by name in two places. Adding a second
plugin-owned skill made `--check` report drift on every run until both were replaced
with a list. Use a list from the start.

**A vendored copy is not a place to make small adjustments.** The byte-identical rule is
what makes `--check` mean anything; one legitimate difference and the check reports
drift forever and everyone stops reading it.

### Reading it

The clearest single file is the plugin's
[`scripts/sync-from-template.sh`](https://github.com/danielrosehill/spec-led-certification-plugin/blob/main/scripts/sync-from-template.sh) —
it states the canonical direction, the ownership split and the empty-data guard in
about a hundred lines. A generalised copy is in
[`reference/sync-from-template.sh`](../reference/sync-from-template.sh).
