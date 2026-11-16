#!/usr/bin/env python3
"""Measure what a Claude Code session carries before you type. Read-only.

Usage: measure.py [--project DIR] [--days 30] [--skill-budget CHARS] [--json]

Token figures for files are estimates (characters / 4). Figures from session
logs are exact: they are the usage numbers the API reported for each call.
"""
import argparse, glob, json, os, re, statistics, sys, time

HOME = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
MEMORY_INDEX_LINES = 200  # only the top of MEMORY.md is loaded


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def tok(text):
    return round(len(text) / 4)


def with_imports(path, seen=None, depth=0):
    """Return [(path, text)] for a rules file and the files it @imports."""
    seen = seen if seen is not None else set()
    real = os.path.realpath(path)
    text = read(path)
    if text is None or real in seen or depth > 5:
        return []
    seen.add(real)
    out = [(path, text)]
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    for ref in re.findall(r"(?:^|\s)@([~./\w-][\w./~-]*)", prose):
        target = os.path.expanduser(ref)
        if not os.path.isabs(target):
            target = os.path.join(os.path.dirname(path), target)
        if os.path.isfile(target):
            out += with_imports(target, seen, depth + 1)
    return out


def rules_files(project):
    paths = [os.path.join(HOME, "CLAUDE.md")]
    paths += sorted(glob.glob(os.path.join(HOME, "rules", "**", "*.md"), recursive=True))
    d, chain = os.path.abspath(project), []
    while True:
        chain.append(d)
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    for d in reversed(chain):
        paths += [os.path.join(d, n) for n in ("CLAUDE.md", "CLAUDE.local.md", ".claude/CLAUDE.md")]
    paths += sorted(glob.glob(os.path.join(project, ".claude", "rules", "**", "*.md"), recursive=True))
    seen, out = set(), []
    for p in paths:
        for path, text in with_imports(p, seen):
            out.append({"path": path, "chars": len(text), "tokens": tok(text),
                        "lines": text.count("\n") + 1})
    return out


def slug(project):
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(project))


def memory_index(project):
    path = os.path.join(HOME, "projects", slug(project), "memory", "MEMORY.md")
    text = read(path)
    if text is None:
        return None
    lines = text.splitlines()
    loaded = "\n".join(lines[:MEMORY_INDEX_LINES])
    return {"path": path, "lines": len(lines), "tokens": tok(loaded),
            "truncated": len(lines) > MEMORY_INDEX_LINES}


def frontmatter(text):
    m = re.match(r"\s*---\n(.*?)\n---", text, flags=re.S)
    meta, key = {}, None
    if not m:
        return meta
    for line in m.group(1).splitlines():
        kv = re.match(r"([A-Za-z_-]+):\s*(.*)$", line)
        if kv:
            key = kv.group(1)
            meta[key] = kv.group(2).strip().strip("\"'")
            if meta[key] in (">", "|", ">-", "|-"):
                meta[key] = ""
        elif key and line.startswith((" ", "\t")):
            meta[key] = (meta[key] + " " + line.strip()).strip()
    return meta


def listed_items(project):
    """Skills, commands and agents whose name + description sit in every session."""
    patterns = [
        ("skill", os.path.join(HOME, "skills", "*", "SKILL.md")),
        ("skill", os.path.join(project, ".claude", "skills", "*", "SKILL.md")),
        ("skill", os.path.join(HOME, "plugins", "**", "skills", "*", "SKILL.md")),
        ("command", os.path.join(HOME, "commands", "**", "*.md")),
        ("command", os.path.join(project, ".claude", "commands", "**", "*.md")),
        ("agent", os.path.join(HOME, "agents", "*.md")),
        ("agent", os.path.join(project, ".claude", "agents", "*.md")),
    ]
    seen, out = set(), []
    for kind, pattern in patterns:
        for path in sorted(glob.glob(pattern, recursive=True)):
            real = os.path.realpath(path)
            text = read(path)
            if real in seen or text is None:
                continue
            seen.add(real)
            meta = frontmatter(text)
            default = os.path.basename(os.path.dirname(path)) if kind == "skill" \
                else os.path.splitext(os.path.basename(path))[0]
            name = meta.get("name") or default
            desc = (meta.get("description", "") + " " + meta.get("when_to_use", "")).strip()
            hidden = meta.get("disable-model-invocation", "").lower() == "true"
            out.append({"kind": kind, "name": name, "path": path, "desc_chars": len(desc),
                        "listed": not hidden, "body_tokens": tok(text)})
    return out


def settings_files(project):
    return [p for p in (os.path.join(HOME, "settings.json"),
                        os.path.join(HOME, "settings.local.json"),
                        os.path.join(project, ".claude", "settings.json"),
                        os.path.join(project, ".claude", "settings.local.json"))
            if os.path.isfile(p)]


def load_json(path):
    try:
        return json.loads(read(path) or "")
    except ValueError:
        return {}


def hooks(project):
    out = []
    for path in settings_files(project):
        for event, groups in (load_json(path).get("hooks") or {}).items():
            for group in groups or []:
                for h in group.get("hooks", []):
                    out.append({"event": event, "matcher": group.get("matcher", ""),
                                "command": h.get("command") or h.get("prompt") or h.get("type"),
                                "file": path,
                                "adds_context": event in ("SessionStart", "UserPromptSubmit")})
    return out


def connectors(project):
    names = {}
    home_cfg = load_json(os.path.join(os.path.dirname(HOME), ".claude.json"))
    for name in (home_cfg.get("mcpServers") or {}):
        names[name] = "~/.claude.json"
    proj = (home_cfg.get("projects") or {}).get(os.path.abspath(project)) or {}
    for name in (proj.get("mcpServers") or {}):
        names[name] = "~/.claude.json (this project)"
    for name in (load_json(os.path.join(project, ".mcp.json")).get("mcpServers") or {}):
        names[name] = ".mcp.json"
    return [{"name": n, "source": s} for n, s in sorted(names.items())]


def session_calls(days):
    """Tokens carried into each API call, from session logs. Exact, deduplicated."""
    cutoff = time.time() - days * 86400
    carried, first_calls, seen = [], [], set()
    for path in glob.glob(os.path.join(HOME, "projects", "*", "*.jsonl")):
        try:
            if os.path.getmtime(path) < cutoff:
                continue
            first = True
            with open(path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if '"usage"' not in line:
                        continue
                    try:
                        row = json.loads(line)
                    except ValueError:
                        continue
                    msg = row.get("message") or {}
                    usage = msg.get("usage")
                    if row.get("type") != "assistant" or not usage or row.get("isSidechain"):
                        continue
                    key = msg.get("id") or row.get("uuid")
                    if key in seen:
                        continue
                    seen.add(key)
                    n = (usage.get("input_tokens") or 0) \
                        + (usage.get("cache_creation_input_tokens") or 0) \
                        + (usage.get("cache_read_input_tokens") or 0)
                    if n <= 0:
                        continue
                    carried.append(n)
                    if first:
                        first_calls.append(n)
                        first = False
        except OSError:
            continue
    if not carried:
        return None
    return {"days": days, "calls": len(carried), "sessions": len(first_calls),
            "median_carried": round(statistics.median(carried)),
            "pct_over_150k": round(100 * sum(c > 150000 for c in carried) / len(carried)),
            "median_first_call": round(statistics.median(first_calls))}


def measure(project, days, skill_budget):
    rules = rules_files(project)
    mem = memory_index(project)
    items = listed_items(project)
    listed = [i for i in items if i["listed"]]
    # Fill the list in order until the budget runs out; the rest show a name only.
    used, name_only = 0, 0
    for i in listed:
        cost = len(i["name"]) + i["desc_chars"] + 4
        if used + cost <= skill_budget:
            used += cost
            i["shown_with_description"] = True
        else:
            used += len(i["name"]) + 4
            i["shown_with_description"] = False
            name_only += 1
    report = {
        "measured_at": time.strftime("%Y-%m-%d %H:%M"),
        "config_dir": HOME, "project": os.path.abspath(project),
        "rules": rules, "rules_tokens": sum(r["tokens"] for r in rules),
        "memory_index": mem,
        "listed": items,
        "list_total": len(listed), "list_name_only": name_only,
        "list_tokens": tok("x" * sum(len(i["name"]) + i["desc_chars"] + 4 for i in listed)),
        "skill_budget_chars": skill_budget,
        "hooks": hooks(project), "connectors": connectors(project),
        "sessions": session_calls(days),
    }
    report["file_estimate_tokens"] = report["rules_tokens"] \
        + (mem["tokens"] if mem else 0) + report["list_tokens"]
    return report


def render(r):
    n = lambda x: f"{x:,}"
    L = [f"# What every session carries before you type",
         f"Measured {r['measured_at']} from `{r['config_dir']}` and `{r['project']}`. Nothing was changed.", ""]
    s = r["sessions"]
    L += ["## Headline", f"- ~{n(r['file_estimate_tokens'])} tokens from your own files "
          "(rules + memory index + skill list; estimate, chars/4)"]
    L.append(f"- {r['list_name_only']} of {r['list_total']} listed skills/commands/agents likely show a name only "
             f"(budget {n(r['skill_budget_chars'])} chars; estimate)")
    if s:
        L += [f"- {n(s['median_first_call'])} tokens on the first call of a session "
              f"(median of {n(s['sessions'])} sessions; exact, includes Claude Code itself and connectors)",
              f"- {n(s['median_carried'])} tokens carried on a typical call (median, {n(s['calls'])} calls, {s['days']} days)",
              f"- {s['pct_over_150k']}% of calls carry more than 150,000 tokens"]
    else:
        L.append("- Session logs: NOT MEASURED (none found in the period)")
    L += ["", "## 1. Rules files", "| tokens | lines | file |", "|--:|--:|---|"]
    L += [f"| {n(x['tokens'])} | {x['lines']} | `{x['path']}` |" for x in r["rules"]] or ["| 0 | 0 | none found |"]
    m = r["memory_index"]
    L += ["", "## 2. Memory index"]
    L.append(f"- `{m['path']}`: {m['lines']} lines, ~{n(m['tokens'])} tokens loaded"
             + (" — over the 200-line limit, the rest is cut off" if m["truncated"] else "")
             if m else "- none for this project")
    L += ["", "## 3. Skill list", f"~{n(r['list_tokens'])} tokens if every description were shown.",
          "", "| kind | name | description chars | shown with description | file size (tokens) |", "|---|---|--:|---|--:|"]
    for i in sorted(r["listed"], key=lambda i: -i["desc_chars"]):
        shown = "hidden from model" if not i["listed"] else ("yes" if i["shown_with_description"] else "NAME ONLY")
        L.append(f"| {i['kind']} | {i['name']} | {i['desc_chars']} | {shown} | {n(i['body_tokens'])} |")
    L += ["", "## 4. Connectors (MCP servers)"]
    L += [f"- {c['name']} ({c['source']})" for c in r["connectors"]] or ["- none configured in files"]
    L.append("- Token cost per connector: NOT MEASURED from files. Run `/context` in a fresh session for exact numbers.")
    L += ["", "## 5. Hooks"]
    for h in r["hooks"]:
        flag = " — ADDS TEXT TO CONTEXT (size not measured)" if h["adds_context"] else ""
        L.append(f"- {h['event']} {h['matcher']}: `{h['command']}`{flag}")
    if not r["hooks"]:
        L.append("- none")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", default=os.getcwd())
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--skill-budget", type=int,
                    default=int(os.environ.get("SLASH_COMMAND_TOOL_CHAR_BUDGET", 16000)),
                    help="characters the skill list may use (default 16000; an assumption — check /context)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rep = measure(a.project, a.days, a.skill_budget)
    sys.stdout.write(json.dumps(rep, indent=2) if a.json else render(rep))
