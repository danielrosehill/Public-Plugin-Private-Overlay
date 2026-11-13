---
name: setup
description: Saves the settings the audit needs in a private profile — which marketplaces you publish, where your plugin repositories are cloned, and a private list of personal terms (names, hosts, emails, org names) that must never appear in a public plugin. Use on "set up the plugin audit", "add a marketplace to the audit", "update my personal terms list".
---

# Set up the audit

## 1. Find the data folder

Stop at the first match: `$PPO_HOME`, `$CLAUDE_USER_DATA/public-private-overlay/`,
`~/.claude-user-data/public-private-overlay/` (if `~/.claude-user-data` exists),
`${XDG_DATA_HOME:-~/.local/share}/claude-plugins/public-private-overlay/` (if that root exists),
else `~/.claude-user-data/public-private-overlay/`. Read `profile.env` if it is there; this
run updates it.

## 2. Ask for what can't be detected

- **Marketplaces:** paths to each `marketplace.json` you publish. Look for clones first
  (`find ~ -maxdepth 6 -path '*/.claude-plugin/marketplace.json'`) and confirm the list.
- **Repos root:** the directory your plugin repositories are cloned under.
- **Personal terms:** your names as they appear in prose, usernames, hostnames, home
  network names, email addresses, private org names, the names of your secret tools and
  vaults, family members' names. Leave out the public handle you publish under: author
  links and marketplace names use it legitimately.

## 3. Write

`profile.env`:

```
PPO_MARKETPLACES="/path/a/marketplace.json /path/b/marketplace.json"
PPO_REPOS_ROOT=~/repos
PPO_PERSONAL_TERMS=<data folder>/personal-terms.txt
```

`personal-terms.txt`: one term per line, `#` for comments. It is private: never copy it
into a plugin or a public repository. If the data folder is in a git repository, commit
only this plugin's folder.

## Data storage

Writes `profile.env` and `personal-terms.txt` in the data folder.
