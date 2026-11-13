# The workspace marker file

A dotfile at the workspace root that identifies the directory as a workspace and
records what it was made from.

```
.<plugin-name>
```

```yaml
created: 2026-08-08
subject: "One line describing this instance"
template: <owner>/<template-repo>
template_version: 0.3.0
backing: github          # github | local
repo: <owner>/<name>     # omit when backing is local
workspace_root: .
```

## Finding it

Search the **current directory, then upward**. Two reasons, and the second is the one
that bites:

1. A user invokes a skill from a subdirectory and every relative path would otherwise
   break.
2. A workspace may be a subdirectory of a larger, unrelated repo. Using the enclosing
   git repo as the root is wrong in exactly that case, and wrong quietly — paths
   resolve to plausible-looking locations one level too high.

If no marker is found, offer to create a workspace. Never assume the current directory
is one.

If a marker for a *different* plugin is found, say so rather than adopting it. Two
plugins' workspaces can legitimately sit side by side.

## Why each field

**`created`** — absolute date. Relative dates in stored state are worthless the moment
the session ends.

**`template` and `template_version`** — the first time a workspace looks broken and
turns out to predate a template change, these are the difference between a diagnosis
and a guess. Record the plugin version that created it, since that is the number the
user can see.

**`backing`** — `github` or `local`. Skills behave differently: whether to commit and
push, whether history is available for a diff, whether the work survives the machine.

**`repo`** — so a skill can report the URL without asking git, and so a workspace moved
or copied still knows where it came from.

**`workspace_root`** — always `.` in practice, but stating it makes the file
self-describing rather than a marker whose meaning lives only in the plugin.

## Do not

**Do not put user configuration in it.** That is the overlay's job. The marker describes
the *workspace*; the overlay describes the *user*. Mixing them means a workspace commits
someone's preferences into a repo they may later share.

**Do not put state in it.** Progress, stage completion and status belong in the working
files where they can be read and corrected. A marker that mutates constantly produces
noise in every diff, which is the one thing a repo-backed workspace was for.
