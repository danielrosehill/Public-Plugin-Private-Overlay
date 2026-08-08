---
name: create-workspace
description: Create a private GitHub repository from the <PLUGIN> template and clone it, as the durable home for one <PROJECT-NOUN>. Use when the user wants the work backed by a repo rather than a local folder. For a plain local directory with no remote, use scaffold-workspace instead.
---

<!--
  Reference skill for the Plugin-Workspace-Vault pattern:
  https://github.com/danielrosehill/Claude-Plugin-Workspace-Vault

  Replace <PLUGIN>, <TEMPLATE-REPO>, <PROJECT-NOUN> and the config keys.
  Everything else is the pattern and should survive adaptation.
-->

# Create a workspace repository

Stand up a private GitHub repo from the `<TEMPLATE-REPO>` template and clone it. That
repo is the definitive store for one <PROJECT-NOUN>.

## Why a repo rather than a folder

The premise is that this state outlives the conversation, and a folder on one machine
is a weak form of that. A repo survives the laptop, its history shows the order in
which things happened, a diff shows what changed between runs, and it can be opened by
a different assistant on a different machine months later.

Instantiating the template also copies the skills and docs into the new repo, so it
explains its own process with this plugin uninstalled.

Use `scaffold-workspace` instead when the work belongs inside an existing repo, when
`gh` is unavailable, or when the user wants no remote.

## Check prerequisites

```bash
gh auth status
```

If `gh` is missing or unauthenticated, say so and offer the local path. Do not work
around it — a half-created repo is worse than a folder.

## Read the vault first

`~/.claude-plugins/<PLUGIN>/config.yaml`:

```yaml
owner: <github-user-or-org>
visibility: private
workspace_parent: ~/repos
naming: "{subject}-{mmyy}"
template: <owner>/<TEMPLATE-REPO>    # a fork wins over the author's default
```

If it exists, use it and stop asking what it answers. If not, ask, and **offer to
write it at the end** so the second run is one confirmation. Never write it unprompted.

Honour `template` — that key is what makes the system forkable rather than locked to
the plugin author.

## Choose the name

Propose one from the subject plus a month stamp. The month matters: a second
<PROJECT-NOUN> on the same subject later is a new repo, not an overwrite.

```bash
gh repo view <owner>/<name> >/dev/null 2>&1 && echo taken
```

## Confirm before creating

**Creating a repository is outward-facing. Show the exact command and get an explicit
yes.**

```bash
gh repo create <name> --template <owner>/<TEMPLATE-REPO> \
  --private --clone --description "<subject>"
```

State in the confirmation: that it will be **private**, what it will end up holding,
and that it lands under their GitHub account rather than on this machine only.

If they ask for `--public`, say once — without lecturing — what the repo will contain,
then do as they asked. The point is that the choice is made knowingly rather than by a
default nobody read.

## Create

`gh` handles the template-instantiation race internally; the clone arrives complete, so
no wait loop is needed.

The new repo starts with a squashed `Initial commit` and **no upstream link**. That is
correct: an instance is not a fork and should not receive template changes underneath
work in progress.

## Settle the workspace in

1. **Write the marker** `.<PLUGIN>` at the repo root:

   ```yaml
   created: <YYYY-MM-DD>
   subject: <one line>
   template: <owner>/<TEMPLATE-REPO>
   template_version: <plugin version>
   backing: github
   repo: <owner>/<name>
   workspace_root: .
   ```

2. **Replace `README.md`** with a status page for *this* <PROJECT-NOUN>. The template's
   README describes the template and is the wrong front page for an instance. Keep it
   short — subject, date opened, current state, where the output lands — not a second
   copy of the docs.

3. **Commit and push.**

## Then

Say where the repo is — local path and URL — and confirm it is private. Offer to save
anything they answered that the vault could have.

Hand off to the first working skill as a **separate step**. Creating a repo is
infrastructure; give them a chance to look at it before starting the real work.
