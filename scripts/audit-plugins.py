#!/usr/bin/env python3
"""Audit a publisher's plugins against the Public Plugin, Private Overlay standard.

  audit-plugins.py --marketplace <marketplace.json> [--marketplace ...]
                   [--repos-root DIR] [--personal-terms FILE] [--visibility] [--only NAME,...]
  audit-plugins.py --plugin <plugin dir> [--plugin ...] [--personal-terms FILE] [--assume-public]

--marketplace   a marketplace.json. Each entry's plugin is found under --repos-root (a
                directory searched for .claude-plugin/plugin.json, matched by name). Entries
                with no local copy are reported as `not-found-locally`
--personal-terms  one term per line (names, usernames, hosts, emails, org names, IDs). Lines
                starting with # are comments. A line starting with ! is an allowed phrase,
                removed before matching (e.g. "!Jane Doe" keeps author credit while "Jane" is
                still caught). Hits in a public plugin are errors; in a private
                one they tell you what would have to move to an overlay
--visibility    ask GitHub (gh api) whether each github-sourced plugin repo is public. One call
                per plugin
Prints JSON: per plugin, its findings (rule, severity, file, line, detail) and a class:
leak, fix, conforming, candidate-public, not-found-locally. Stdlib only. Read-only.
"""
import argparse
import json
import os
import pathlib
import re
import subprocess

TEXT = {".md", ".py", ".sh", ".json", ".js", ".ts", ".mjs", ".toml", ".yaml", ".yml", ".txt", ".env", ""}
SECRET = [
    (r"\bhf_[A-Za-z0-9]{30,}\b", "Hugging Face token"),
    (r"\bsk-(?:ant-)?[A-Za-z0-9_-]{24,}\b", "API key (sk-…)"),
    (r"\bgh[pousr]_[A-Za-z0-9]{30,}\b", "GitHub token"),
    (r"\bgithub_pat_[A-Za-z0-9_]{40,}\b", "GitHub fine-grained token"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key id"),
    (r"\bop://(?![<$]|vault/|Vault/|VAULT/)[^\s\"'`)]+", "1Password secret reference"),
]
WRITE_ROOT = [
    r"(>>?|tee\s+(-a\s+)?|mkdir\s+-p\s+|cp\s+[^\n]*\s|mv\s+[^\n]*\s|touch\s+)\"?\$\{?CLAUDE_PLUGIN_ROOT",
    r"open\([^)]*CLAUDE_PLUGIN_ROOT[^)]*['\"][wa]",
    r"write_text\([^)]*\)\s*#?.*CLAUDE_PLUGIN_ROOT",
]
DOT_CLAUDE = re.compile(r"(~|\$HOME|\$\{HOME\}|home\(\)|expanduser\(['\"]~)[/\"' +]*\.claude/(?!plugins/(cache|data)\b)")
LEGACY = re.compile(r"~/\.claude-plugins/|\.claude/plugins-data|\$HOME/\.claude-plugins")
HOMEPATH = re.compile(r"/home/[a-z_][a-z0-9_-]*/|/Users/[A-Za-z][\w.-]*/")
URL = re.compile(r"https?://\S+")
NAME_OK = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    fm, key = {}, None
    for line in m.group(1).splitlines():
        k = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if k:
            key, fm[k.group(1)] = k.group(1), k.group(2).strip().strip("\"'")
        elif key and line.startswith((" ", "\t")):
            fm[key] += " " + line.strip()
    return fm


def ignored(root):
    """Globs from <plugin>/.audit-ignore (one per line, # comments): vendored or quoted material."""
    f = root / ".audit-ignore"
    pats = [l.strip() for l in f.read_text().splitlines() if l.strip() and not l.startswith("#")] if f.exists() else []
    return lambda rel: any(pathlib.PurePath(rel).match(p) or rel.startswith(p.rstrip("*").rstrip("/") + "/") for p in pats)


def tracked(root):
    """Files git tracks under root (what is actually published), or None if not a git checkout."""
    r = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--", "."], capture_output=True, text=True)
    if r.returncode:
        return None
    return {(root / f).resolve() for f in r.stdout.split("\0") if f}


def files(root):
    skip = ignored(root)
    keep = tracked(root)
    for p in sorted(root.rglob("*")):
        if keep is not None and p.resolve() not in keep:
            continue
        if skip(str(p.relative_to(root))):
            continue
        if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts and \
                (p.suffix in TEXT) and p.stat().st_size < 400_000:
            yield p


def audit_plugin(root, terms, public, allowed=()):
    f = []
    add = lambda rule, sev, file=None, line=None, detail=None: f.append(
        {k: v for k, v in dict(rule=rule, severity=sev, file=file, line=line, detail=detail).items() if v is not None})
    man = root / ".claude-plugin" / "plugin.json"
    manifest = {}
    if not man.exists():
        add("manifest-missing", "error", ".claude-plugin/plugin.json")
    else:
        try:
            manifest = json.loads(man.read_text())
        except ValueError as e:
            add("manifest-invalid", "error", ".claude-plugin/plugin.json", detail=str(e)[:120])
    corpus = {p: p.read_text(errors="replace") for p in files(root)}
    uses_overlay = any(re.search(r"claude-user-data|profile\.env|CLAUDE_USER_DATA", t) for t in corpus.values())
    term_res = [(t, re.compile(r"(?<![\w@.])" + re.escape(t) + r"(?![\w])", re.I)) for t in terms]
    for p, text in corpus.items():
        rel = str(p.relative_to(root))
        is_license = p.name.upper().startswith("LICENSE")
        prose = p.suffix == ".md"  # path rules: prose that describes a path is a note, code is a bug
        psev = lambda sev: "info" if prose else sev
        for i, line in enumerate(text.splitlines(), 1):
            for pat, what in SECRET:
                if re.search(pat, line):
                    add("secret-value", "error", rel, i, what)
            for pat in WRITE_ROOT:
                if re.search(pat, line):
                    add("writes-plugin-root", "error", rel, i, line.strip()[:120])
            if LEGACY.search(line):
                add("legacy-location", "info" if re.search(r"(?i)legacy|migrat|moved?|superseded|up to \d", line)
                    else psev("warn"), rel, i, line.strip()[:120])
            elif DOT_CLAUDE.search(line):
                add("touches-dot-claude", psev("warn"), rel, i, line.strip()[:120])
            if HOMEPATH.search(line):
                add("hardcoded-home-path", psev("warn"), rel, i, line.strip()[:120])
            if "CLAUDE_PLUGIN_DATA" in line and re.search(r"profile\.env|templates/|notes", line):
                add("user-content-in-plugin-data", psev("warn"), rel, i, line.strip()[:120])
            if not is_license and rel != ".claude-plugin/plugin.json":
                for t, rx in term_res:
                    if rx.search(line):
                        clean = URL.sub("", line)
                        for ph in allowed:
                            clean = re.sub(re.escape(ph), "", clean, flags=re.I)
                        bare = rx.search(clean) is not None
                        if bare:
                            add("personal-term", "error" if public else "info", rel, i, t)
                        else:
                            add("author-link", "info", rel, i, t)
    skills = sorted(root.glob("skills/*/SKILL.md"))
    names = {s.parent.name for s in skills}
    for s in skills:
        rel = str(s.relative_to(root))
        text = corpus.get(s, s.read_text(errors="replace"))
        fm = frontmatter(text)
        n = fm.get("name", "")
        if not n:
            add("skill-name-missing", "warn", rel)
        elif len(n) > 64 or not NAME_OK.match(n) or re.search(r"claude|anthropic", n):
            add("skill-name-invalid", "warn", rel, detail=n)
        d = fm.get("description", "")
        if not d:
            add("skill-description-missing", "error", rel)
        elif len(d) > 1024:
            add("skill-description-too-long", "warn", rel, detail=f"{len(d)} chars")
        body = len(text.splitlines())
        if body > 500:
            add("skill-too-long", "warn", rel, detail=f"{body} lines")
        if uses_overlay:
            loads = re.search(r"(?im)^#+\s*(\d+\.\s*)?load (your )?settings", text) or \
                re.search(r"profile\.env|data folder|overlay|paths\.sh", text)
            needs_none = re.search(r"(?i)reads nothing", text)
            if not loads and not needs_none and n not in ("setup", "onboard", "configure"):
                add("no-load-step", "warn", rel)
            if not re.search(r"(?im)^##\s+data storage", text):
                add("no-data-storage-section", "info", rel)
    if uses_overlay:
        if not ({"setup", "onboard", "configure"} & names):
            add("no-setup-skill", "warn")
        if not any("CLAUDE_USER_DATA" in t for t in corpus.values()):
            add("resolver-incomplete", "warn", detail="overlay used but $CLAUDE_USER_DATA is never consulted")
    return manifest, uses_overlay, len(skills), f


def find_local(roots):
    idx = {}
    for root in roots:
        for man in pathlib.Path(root).expanduser().glob("**/.claude-plugin/plugin.json"):
            if any(part in ("node_modules", ".git") for part in man.parts) or len(man.parts) > 14:
                continue
            try:
                idx.setdefault(json.loads(man.read_text()).get("name"), man.parent.parent)
            except ValueError:
                pass
    return idx


def remote_repo(path):
    """owner/name of the GitHub remote of the git repo containing path, or None."""
    r = subprocess.run(["git", "-C", str(path), "remote", "get-url", "origin"], capture_output=True, text=True)
    m = re.search(r"github\.com[:/]([^/]+/[^/\s]+?)(?:\.git)?\s*$", r.stdout)
    return m.group(1) if m else None


def gh_public(repo):
    r = subprocess.run(["gh", "api", f"repos/{repo}", "-q", ".private"], capture_output=True, text=True)
    return None if r.returncode else r.stdout.strip() == "false"


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--marketplace", action="append", default=[])
    a.add_argument("--plugin", action="append", default=[])
    a.add_argument("--repos-root", action="append", default=[])
    a.add_argument("--personal-terms")
    a.add_argument("--visibility", action="store_true")
    a.add_argument("--only")
    a.add_argument("--assume-public", action="store_true", help="treat --plugin targets as public")
    o = a.parse_args()
    terms, allowed = [], []
    if o.personal_terms:
        for l in pathlib.Path(o.personal_terms).expanduser().read_text().splitlines():
            l = l.strip()
            if not l or l.startswith("#"):
                continue
            (allowed.append(l[1:].strip()) if l.startswith("!") else terms.append(l))
    only = set(o.only.split(",")) if o.only else None
    targets, listed = [], {}
    if o.marketplace:
        idx = find_local(o.repos_root or [pathlib.Path(o.marketplace[0]).resolve().parents[2]])
        for mp in o.marketplace:
            m = json.loads(pathlib.Path(mp).expanduser().read_text())
            for e in m.get("plugins", []):
                if only and e["name"] not in only:
                    continue
                listed.setdefault(e["name"], []).append(m.get("name", mp))
                src = e.get("source")
                repo = src.get("repo") if isinstance(src, dict) and src.get("source") == "github" else None
                path = None
                if isinstance(src, str) and src.startswith("./"):
                    path = pathlib.Path(mp).expanduser().resolve().parents[1] / src
                if path and not repo:
                    repo = remote_repo(pathlib.Path(mp).expanduser().resolve().parent)  # in-marketplace plugin
                targets.append({"name": e["name"], "marketplace": m.get("name", mp), "repo": repo,
                                "entry_version": e.get("version"), "path": path or idx.get(e["name"])})
    for p in o.plugin:
        targets.append({"name": pathlib.Path(p).name, "marketplace": None, "repo": None,
                        "entry_version": None, "path": pathlib.Path(p).expanduser(),
                        "public": True if o.assume_public else None})
    results = []
    for t in targets:
        r = {"name": t["name"], "marketplace": t["marketplace"], "repo": t["repo"]}
        public = t.get("public")
        if o.visibility and t["repo"]:
            public = gh_public(t["repo"])
        elif t["marketplace"]:
            public = None if "private" in t["marketplace"].lower() else True
        if t["marketplace"] and "private" in t["marketplace"].lower():
            public = False if public is None else public
        r["public"] = public
        if not t["path"] or not pathlib.Path(t["path"]).exists():
            r["class"] = "not-found-locally"
            results.append(r)
            continue
        manifest, overlay, nskills, f = audit_plugin(pathlib.Path(t["path"]), terms, bool(public), allowed)
        r.update({"path": str(t["path"]), "version": manifest.get("version"), "uses_overlay": overlay, "skills": nskills})
        if t["entry_version"] and manifest.get("version") and t["entry_version"] != manifest.get("version"):
            f.append({"rule": "version-drift", "severity": "warn",
                      "detail": f"plugin.json {manifest.get('version')} vs marketplace {t['entry_version']}"})
        if t["marketplace"] and manifest.get("name") and manifest["name"] != t["name"]:
            f.append({"rule": "name-mismatch", "severity": "warn",
                      "detail": f"plugin.json {manifest['name']} vs entry {t['name']}"})
        if len(listed.get(t["name"], [])) > 1:
            f.append({"rule": "listed-twice", "severity": "warn", "detail": ", ".join(listed[t["name"]])})
        base = re.sub(r"-private$", "", t["name"])
        if t["name"].endswith("-private") and base in listed:
            f.append({"rule": "parallel-private-plugin", "severity": "info",
                      "detail": f"{base} exists; consider moving the particulars to its overlay"})
        sev = {x["severity"] for x in f}
        leak = public and any(x["rule"] in ("personal-term", "secret-value") and x["severity"] == "error" for x in f)
        if leak:
            r["class"] = "leak"
        elif "error" in sev or "warn" in sev:
            r["class"] = "fix"
        elif public is False and terms and not any(x["rule"] == "personal-term" for x in f):
            r["class"] = "candidate-public"
        else:
            r["class"] = "conforming"
        counts = {}
        for x in f:
            counts[x["rule"]] = counts.get(x["rule"], 0) + 1
        r["counts"] = counts
        r["findings"] = f[:200]
        results.append(r)
    summary = {}
    for r in results:
        summary[r["class"]] = summary.get(r["class"], 0) + 1
    rule_totals = {}
    for r in results:
        for k, v in r.get("counts", {}).items():
            rule_totals[k] = rule_totals.get(k, 0) + v
    print(json.dumps({"plugins": len(results), "classes": summary, "rules": rule_totals, "results": results}, indent=1))


if __name__ == "__main__":
    main()
