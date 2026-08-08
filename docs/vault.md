# The vault

`~/.claude-plugins/<plugin-name>/` — the user's own data for one plugin.

## Why this location and no other

It is the only place in the layout with both properties user configuration needs:

- **Not replaced by `/plugin update`.** The plugin directory is. Config written there
  works perfectly until the first update and then disappears, with no error and nothing
  in the logs — the failure looks like the user never saved it.
- **Not tracked by any repository.** Neither the plugin repo, the template repo, nor
  any workspace instantiated from it. Nothing can accidentally commit it.

A per-plugin subdirectory keyed on the plugin's own name means no lookup and no
collisions between plugins.

## What goes in it

```
~/.claude-plugins/<name>/
├── config.yaml        preferences, defaults, the template override
├── credentials.yaml   pointers only, never values
├── registry/          user entries that override or extend shipped data
└── logs/              state the plugin must remember between runs
```

**config.yaml** — anything the plugin would otherwise ask every single time. Identity
(`owner`), policy (`visibility`), placement (`workspace_parent`), naming conventions,
and the `template` override that makes the system forkable.

**credentials.yaml** — see below.

**registry/** — where a plugin ships reference data the user can extend. Two layers,
with an explicit merge rule.

**logs/** — anything the plugin needs across sessions that is not project state:
what was sent and when, follow-up dates, revalidation timestamps. Project state belongs
in the workspace; this is for the plugin's own memory of the user.

## Credentials are pointers, never values

```yaml
api_key:
  op: "op://Private/Some Service/credential"
  env: SOME_SERVICE_API_KEY
  note: "Read-only token. Rotate via the vendor console."
```

Resolve at the point of use, pass to the process that needs it, and let it go. The
value must not reach a config file, a log, a draft, a report, or the transcript.

This is not only about disclosure. A pointer stays correct when the underlying secret
is rotated; a copied value silently goes stale and produces an authentication failure
that looks like a bug in the plugin.

## The two-layer merge

When a plugin ships reference data users can extend, be explicit about all three rules,
because ambiguity here produces results nobody can predict:

| Rule | Sensible default |
| --- | --- |
| Conflict on the same key | User entry wins |
| Lists on the same key | Concatenate, user's first |
| Freshness metadata | The **older** verification date governs the merged entry |

That last one is the non-obvious one. If a user override carries today's date and the
shipped entry it merges with was verified two years ago, taking the newer date makes the
whole merged record look fresh when most of it is not.

## Rules for the plugin

**Create nothing unprompted.** Read the vault at the start of any skill with
configurable behaviour, but only write when the user asks. A skill that saves its
guesses as preferences has decided something on the user's behalf.

**Never fail because the vault is missing.** Absent vault means "ask, then offer to
save". A first run must work with no setup at all.

**Ship an example, not a default file.** Document the shape in the plugin's README.
Do not write a populated config on install.

**Say where it is when you write it.** "Saved to
`~/.claude-plugins/<name>/config.yaml`" — one line, so the user can find, edit and
delete it without reading the source.

## Portability

The vault is deliberately local and does not follow the user to a new machine. That is
the right trade — it is the leg most likely to hold sensitive material, and silently
syncing it would be a worse surprise than recreating it.

Make recreation cheap instead: keep `config.yaml` small, human-editable, and documented,
so a user who wants it on two machines can copy it themselves, and one who does not can
answer four questions again.
