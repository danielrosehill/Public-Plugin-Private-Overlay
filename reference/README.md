# Reference implementations

Files to copy into a plugin and adapt. Each is a working version of one part of the
pattern, generalised from
[spec-led-certification](../docs/worked-example.md).

| File | Drop into | Adapt |
| --- | --- | --- |
| [sync-from-template.sh](sync-from-template.sh) | `scripts/` | Four variables at the top: `UPSTREAM_REPO`, `DEFAULT_LOCAL`, `PLUGIN_OWNED_SKILLS`, `WORKSPACE_PATHS`, plus `EMPTY_ON_SHIP` |
| [create-workspace.SKILL.md](create-workspace.SKILL.md) | `skills/create-workspace/SKILL.md` | `<PLUGIN>`, `<TEMPLATE-REPO>`, `<PROJECT-NOUN>`, config keys |
| [marker-file.md](marker-file.md) | — | Spec for the workspace marker; implement in your creation skill |

## sync-from-template.sh

Keeps the plugin's vendored copy of the template in step, and detects drift.

```bash
./scripts/sync-from-template.sh --check    # exit 1 and diff on drift
./scripts/sync-from-template.sh            # refresh
./scripts/sync-from-template.sh --from ../local-checkout
```

Three things in it are less obvious than they look, and all three were bugs first:

- **`PLUGIN_OWNED_SKILLS` is a list.** Skills that create a workspace belong to the
  plugin and have no upstream counterpart, so they must survive the wipe and be
  excluded from the drift comparison. Hardcoding one name means the second one you add
  is reported as permanent drift.
- **The `EXIT` trap returns 0 explicitly.** A trap's exit status becomes the script's,
  so a bare `[[ -n "$tmp" ]] && rm -rf "$tmp"` makes every clean run exit 1 when the
  temp dir was never created — under `set -e` in CI that is a failing build with a
  successful sync.
- **`EMPTY_ON_SHIP` refuses rather than warns.** A template checkout acquires real data
  the first time someone tries the workflow in it instead of in an instance, and
  without the guard that data ships to every user.

You only need this script if the plugin vendors a copy of the template. If it always
creates workspaces through `gh repo create --template`, there is nothing to sync — see
[docs/sync.md](../docs/sync.md).
