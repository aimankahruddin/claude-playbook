---
name: find-rule-clashes
description: Step 2 of the Opus playbook. Find rules in CLAUDE.md, memory, skills and hooks that contradict or repeat each other, as a yes/no page.
disable-model-invocation: true
---

# Step 2 — Find the rules that fight

Read every instruction the session loads and list the places where they pull against each other. **The user decides each clash. Change nothing in this step.**

## What to read

Use the file list in `claude-setup-report.md` (run `/audit-setup` first if it is missing): every rules file and its imports, the memory index and the memory files it points to, each skill's description, each agent's description, and the text that hooks inject.

## What counts

- **Contradiction** — two rules cannot both be followed ("always ask before committing" / "commit without asking").
- **Duplicate** — the same rule in two places. One will drift.
- **Stale** — a rule about a tool, path, person or project that no longer exists. Check that the paths and commands it names are really gone before calling it stale.
- **Wrong place** — a rule for one project sitting in the global file, or a long procedure in a rules file that should be a skill loaded on demand.
- **Shouting** — ALL CAPS, "CRITICAL", "NEVER EVER". Current models over-apply these; say it once, calmly, with the reason.
- **Colliding skills** — two skills whose descriptions claim the same trigger.

Quote both sides exactly, with file and line. Do not report a clash you cannot quote.

## The page

Write `claude-clashes.md`. One numbered entry per clash, worst first, each answerable in a word:

```
### 3. Commit without asking?  [contradiction]
A  ~/.claude/CLAUDE.md:14     "Always ask before committing."
B  ./CLAUDE.md:52             "Commit after each passing test, don't ask."
Recommend: keep B in this project, delete A.  Saves ~20 tokens.
Your answer (yes / no / other):
```

A "yes" means: do what is recommended. Every recommendation must be specific enough to carry out without another question.

Finish with a count per kind and the total tokens a full "yes" would save. Tell the user to fill in the answers and run `/fix-and-prove`.
