# Opus playbook

Audit your Claude Code setup, trim it, then hand the daily work to Opus with a playbook written by the stronger model. Six steps, about ten minutes.

The idea: the strongest model is the most expensive one to run all day. Use it once to clean up what every session carries and to write down how it works; then let Opus do the work from that playbook, with the stronger model on call for the hard moments.

## Install

```bash
git clone https://github.com/aimankahruddin/claude-playbook
cd claude-playbook && ./install.sh
```

This copies six skills into `~/.claude/skills/` and one agent into `~/.claude/agents/`. Anything already there with the same name is moved to `~/.claude/backups/opus-playbook-<time>/` first. To try it without installing: `claude --plugin-dir /path/to/claude-playbook`.

## The six steps

Run steps 1–4 on your strongest model, in a fresh session.

| # | Step | Run | You get |
|---|---|---|---|
| 1 | Measure what loads | `/audit-setup` | `claude-setup-report.md` — read-only, changes nothing |
| 2 | Find the rules that fight | `/find-rule-clashes` | `claude-clashes.md` — a yes/no page; you decide each clash |
| 3 | Fix it, then prove it | `/fix-and-prove` | a leaner setup, a backup, and before/after numbers |
| 4 | The strong model writes the playbook | `/write-playbook` | the `opus-playbook` skill, tailored to your work |
| 5 | Switch to Opus, keep the strong model on call | `/model`, `/advisor` | see below |
| 6 | Prove Opus uses it | `/prove-playbook <task>` | `playbook-proof.md` — named steps, checks, cost |

### Step 5 — switching models

- `/model` → pick Opus as the working model.
- `/advisor` → pick the stronger model as advisor, if your Claude Code version has that command.
- If it does not, the `fable-advisor` agent installed here does the same job: the playbook tells Opus when to ask it. It is read-only and only advises.

## What is in the repo

```
skills/
  audit-setup/         step 1, with scripts/measure.py
  find-rule-clashes/   step 2
  fix-and-prove/       step 3
  write-playbook/      step 4
  opus-playbook/       the playbook itself: plan, split, check, escalate
  prove-playbook/      step 6
agents/fable-advisor.md
install.sh
```

Only `opus-playbook` is visible to the model in every session, and its description is one line. The five step skills are started by hand and stay out of the skill list, so the kit adds almost nothing to the load it measures.

## The measuring script

```bash
python3 skills/audit-setup/scripts/measure.py            # report for the current folder
python3 skills/audit-setup/scripts/measure.py --json     # raw numbers
python3 skills/audit-setup/scripts/measure.py --days 7 --skill-budget 16000
```

It only reads. It needs Python 3 and nothing else.

How far to trust each number:

- **Exact** — anything from session logs: tokens on the first call of a session, tokens carried per call, share of calls over 150,000. These are the usage figures the API reported.
- **Estimate** — anything sized from files (rules, memory index, skill list), counted as characters ÷ 4.
- **Assumption** — the skill list budget (default 16,000 characters). It decides how many skills are reported as "name only". Check against `/context` and pass `--skill-budget` if yours differs.
- **Not measured** — the token cost of each connector and the text hooks inject. `/context` in a fresh session gives the connector numbers.

## Undo

Step 3 puts a copy of every file it touches in `~/.claude/backups/setup-<date-time>/` with a `RESTORE.md`. To remove the kit, delete the six skill folders and `agents/fable-advisor.md` from `~/.claude/`.
