# Converting a private plugin

How to turn an existing private plugin into one public, generic plugin plus a private
overlay, without losing anything the owner relies on and without leaking the old
history.

## 0. Get the owner's yes

This publishes existing work. Ask first, and say what will become public: the skills, in
generic form. The particulars stay private.

## 1. Sort the particulars

Go through every skill, script, template and README. List each thing that is specific
to the owner and give it a home:

| Particular | Home |
| --- | --- |
| Values: hosts, IDs, emails, paths, account names, org names | `profile.env` in the overlay |
| Secrets, or where they are kept | Neither. Name the environment variable only |
| Formats: templates, presets, voices, layouts | Overlay `templates/`, named like the built-ins |
| Procedure: "in my setup, always do X first" | Overlay `<skill-name>.md` |
| Records: logs, history, state | A private workspace repository |

Then apply the tests to each skill. A skill stays private only if:

- nothing useful is left once its particulars are gone,
- its existence is itself sensitive, or it belongs to a client or employer, or
- the owner has a standing rule that covers it.

## 2. Rewrite generically

- Replace every particular with a `profile.env` key and a default that works for a
  stranger. Prefix keys with the plugin name.
- Add a `setup` skill that writes `profile.env`, asking only for what it cannot detect.
- Add the load step to the top of each skill and a `## Data storage` section to each.
- Add overlay-first lookup for any formats.
- Replace secret locations with variable names. Remove any mention of the owner's
  secrets manager or wrapper.
- Rewrite `plugin.json`'s description and the README in generic terms.

## 3. Write the owner's particulars to the overlay

In the same pass, write everything sorted in step 1 into the owner's overlay folder:
`profile.env`, the per-skill notes, their templates. The owner's next run must behave
as it did before the conversion. If the user-data root is a git repository, stage only
this plugin's folder.

## 4. Search the public diff

Grep the whole public tree, not only the files you touched, for the owner's names,
usernames, hostnames, IPs, domains, emails, account and project IDs, org names and home
paths:

```bash
git grep -n -i -E '<name>|<username>|<host>|<domain>|<email>|<org>|/home/<user>'
```

Anything found goes to the overlay, and the public text gets a key or a placeholder.
An author credit (name in `plugin.json` and the README) is fine.

## 5. Publish without the old history

If the old history holds anything private, and it usually does:

1. **Keep a git bundle of the old history** somewhere private:
   `git bundle create <plugin>-private-history.bundle --all`.
2. **Create a new repository** from one clean commit of the converted tree. Do not reuse
   the old repository.
3. **Confirm an old SHA returns 404** on the new repository:
   `https://github.com/<owner>/<new-repo>/commit/<old-sha>`.
4. Only then make it public.

Never flip the old repository from private to public, and never trust a squash or a
force-push to clean it. GitHub keeps old commits and serves them by SHA, so anyone with
a SHA, a fork or a cached link can still read them.

## 6. Move what has nothing generic left

Skills that fail the tests in step 1 go into a fitting private plugin that already
covers that subject, or a new one if none does. Do not leave them in the public plugin
behind a flag, and do not keep a private fork of the whole plugin to hold them.

## 7. Move the marketplace entry

In the same change, remove the plugin from the private marketplace and add it to the
public one. A plugin is listed in one marketplace only. Confirm it shows up under the
new marketplace at the new commit.

## 8. Delete the old repository

Once the new one is live, installed from the public marketplace, and the owner's run
works from the overlay, delete the old private repository. The bundle from step 5 is the
record. Archiving keeps a second, drifting copy around for no gain.

## Worked examples

**typst-document-generator 0.6.0 (2026-11-02).** The first plugin converted to this
shape. The owner's identity, business, logo and their own document formats moved into
the overlay (`~/.claude-user-data/typst-document-generator/`, or `$TYPST_DOCGEN_HOME`).
The plugin ships generic built-in templates; `scripts/paths.sh` resolves the overlay and
lists templates overlay first, the user's copy winning by name. Its setup skill is
called `onboard`, and it predates the `profile.env` convention, so it keeps its own
`profile.yaml`. Its older location, `~/.claude/plugins-data/typst-document-generator`,
is reported and never read; `onboard` offers to move it. Repository:
[typst-document-generator-plugin](https://github.com/danielrosehill/typst-document-generator-plugin).

**hf-ops (private) → hugging-face (public, danielrosehill/Hugging-Face-Plugin), 2026-11-13.**
A private Hugging Face Hub plugin whose skills named the owner's account,
organisations, collection names, export folder and support email. The conversion moved
those into `profile.env` keys (default owner, owners list, default visibility, naming
style, export folder, collection names), each with a default that works for a stranger,
and named the secrets by variable only (`HF_TOKEN`, `HF_S3_ACCESS_KEY_ID`,
`HF_S3_SECRET_ACCESS_KEY`). 18 skills were published under a new repository,
[Hugging-Face-Plugin](https://github.com/danielrosehill/Hugging-Face-Plugin), with the
data folder at `~/.claude-user-data/hugging-face/`. Two backup skills checked one
person's backup arrangement end to end and had nothing generic left; they moved to a
private backup plugin.
