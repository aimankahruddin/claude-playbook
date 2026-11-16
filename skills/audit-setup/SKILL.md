---
name: audit-setup
description: Step 1 of the Opus playbook. Measure what every Claude Code session loads before the first word. Read-only report.
disable-model-invocation: true
---

# Step 1 — Measure what loads

Produce a report of what every session carries before the user types. **Change nothing.** No edits, no deletes, no settings changes in this step.

## Do this

1. Run the script in this skill's folder from the user's project folder:
   `python3 <this skill's folder>/scripts/measure.py --days 30`
   Add `--json` if you want the raw numbers.
2. Ask the user to paste the output of `/context` from a **fresh** session if they have it. Those numbers are exact; where they disagree with the script's file estimates, use `/context` and say so.
3. Write the report to `claude-setup-report.md` in the current folder, then show the headline in chat.

## The report

Lead with four numbers, each labelled exact or estimate:

- tokens loaded before the first word
- skills listed by name only, out of how many
- tokens carried on a typical call (median, with the call count)
- share of calls above 150,000 tokens

Then, in this order:

1. **The start-up load** — one breakdown: rules files, memory index, connectors, skill list, Claude Code itself. Biggest first.
2. **The skill list** — which entries show a name only, and the ten longest descriptions. A skill with only a name is hard to pick at the right time.
3. **Hooks that add text** — every `SessionStart` and `UserPromptSubmit` hook, what it injects, and whether it fires on messages it has nothing to do with.
4. **Three biggest savings** — each with the tokens it would save. Suggestions only.

## Rules for the numbers

- Anything you could not measure is written **NOT MEASURED**, with how to measure it. Never fill a gap with a guess.
- File figures are estimates (characters ÷ 4). Session-log figures are exact.
- The skill list budget in the script is an assumption (`--skill-budget`). If `/context` shows the real one, rerun with it.

End by telling the user the next step: `/find-rule-clashes`.
