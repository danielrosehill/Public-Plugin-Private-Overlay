#!/usr/bin/env python3
"""Keep verbatim extracts of the Anthropic docs this standard relies on, and detect changes.

  anthropic-guidance.py check    fetch every page in sources/anthropic/sources.json, compare each
                                 tracked section with the stored extract; print JSON: changed,
                                 missing (section heading gone), new_headings (untracked sections
                                 on tracked pages, to consider adding) and a short diff per change.
                                 Writes nothing.
  anthropic-guidance.py update   same, then rewrite sources/anthropic/<slug>.md and index.json.

Stdlib only. Pages are fetched as markdown (<doc url>.md). Headings inside fenced code blocks
are ignored. A section runs to the next heading of the same or a higher level.
"""
import datetime
import difflib
import hashlib
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "sources" / "anthropic"
CONF = SRC / "sources.json"
INDEX = SRC / "index.json"
HEAD = re.compile(r"^(#{1,6})\s+(.*?)\s*$")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "public-plugin-private-overlay/guidance-check"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def sections(md):
    """Return {heading: (level, text)} for every heading outside code fences."""
    lines, out, fence = md.splitlines(), {}, None
    heads = []
    for i, line in enumerate(lines):
        f = re.match(r"^\s*(```|~~~)", line)
        if f:
            fence = None if fence == f.group(1) else (fence or f.group(1))
            continue
        if fence:
            continue
        m = HEAD.match(line)
        if m:
            heads.append((i, len(m.group(1)), m.group(2)))
    for n, (i, lvl, title) in enumerate(heads):
        end = len(lines)
        for j, l2, _ in heads[n + 1:]:
            if l2 <= lvl:
                end = j
                break
        out.setdefault(title, (lvl, "\n".join(lines[i:end]).strip() + "\n"))
    return out


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def stored(slug):
    f = SRC / f"{slug}.md"
    if not f.exists():
        return {}
    text = f.read_text()
    parts = re.split(r"^<!-- section: (.*?) -->\n", text, flags=re.M)
    return {parts[k]: parts[k + 1].rstrip("\n") + "\n" for k in range(1, len(parts), 2)}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode not in ("check", "update"):
        sys.exit(__doc__)
    conf = json.loads(CONF.read_text())
    today = datetime.date.today().isoformat()
    report = {"checked": today, "pages": []}
    index = {"fetched": today, "pages": {}}
    for page in conf["pages"]:
        entry = {"slug": page["slug"], "url": page["url"]}
        try:
            secs = sections(fetch(page["url"]))
        except Exception as e:
            entry["error"] = str(e)[:200]
            report["pages"].append(entry)
            continue
        old = stored(page["slug"])
        changed, missing, diffs, keep = [], [], {}, []
        for title in page["sections"]:
            if title not in secs:
                missing.append(title)
                continue
            text = secs[title][1]
            keep.append((title, text))
            if any(title != o and text in otx for o, otx in
                   [(t2, secs[t2][1]) for t2 in page["sections"] if t2 in secs]):
                keep.append((title, text))
                continue
            if title in old and old[title] != text:
                changed.append(title)
                d = list(difflib.unified_diff(old[title].splitlines(), text.splitlines(), "stored", "live", n=1, lineterm=""))
                diffs[title] = d[:60] + (["… (diff truncated)"] if len(d) > 60 else [])
            elif title not in old:
                changed.append(title + " (new extract)")
        # a tracked section nested inside another tracked one is kept once, inside its parent
        keep = [(t, tx) for t, tx in keep if not any(t != o and tx in otx for o, otx in keep)]
        tracked = set(page["sections"])
        entry["new_headings"] = [t for t, (lvl, _) in secs.items() if lvl <= 3 and t not in tracked
                                 and not any(t in tx for _, tx in keep)][:40]
        entry.update({"changed": changed, "missing": missing, "diffs": diffs})
        report["pages"].append(entry)
        index["pages"][page["slug"]] = {"url": page["url"], "sections": {t: sha(tx) for t, tx in keep}}
        if mode == "update":
            body = [f"# Extract: {page['url'].removesuffix('.md')}",
                    "",
                    f"Verbatim sections from Anthropic's documentation, fetched {today} by "
                    "`scripts/anthropic-guidance.py`. Copyright Anthropic; quoted for reference. "
                    "Don't edit by hand: run `update`.",
                    ""]
            for title, text in keep:
                body += [f"<!-- section: {title} -->", text.rstrip("\n"), ""]
            (SRC / f"{page['slug']}.md").write_text("\n".join(body))
    if mode == "update":
        INDEX.write_text(json.dumps(index, indent=1) + "\n")
    report["summary"] = {
        "changed": sum(len(p.get("changed", [])) for p in report["pages"]),
        "missing": sum(len(p.get("missing", [])) for p in report["pages"]),
        "errors": [p["slug"] for p in report["pages"] if "error" in p],
        "written": mode == "update",
    }
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
