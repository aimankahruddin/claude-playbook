---
name: prove-playbook
description: Step 6 of the Opus playbook. Test that the working model actually follows the opus-playbook skill, on a real task.
disable-model-invocation: true
---

# Step 6 — Prove the playbook is used

A playbook that is installed but not followed costs tokens and buys nothing. Test it on real work.

## The test

Take a real task from the user (ask for one if none was given). Then:

1. Read the `opus-playbook` skill.
2. **Before any other tool call**, name the playbook steps that apply to this task and how you will carry each out. Quote the step headings so it is clear they came from the playbook and not from habit.
3. Do the task.
4. At the end, go back through the steps you named and mark each: followed, skipped (why), or did not apply.

## What to record

Append one row per run to `playbook-proof.md`:

| date | model | task | named steps first? | steps followed | escalated? | check that proved it | cost |
|---|---|---|---|---|---|---|---|

Take the cost from `/cost` or `/usage` — ask the user to paste it; do not estimate it.

## Reading the results

- Steps not named first: the skill is not being picked. Check it shows with its description in `/context`; if it shows a name only, the skill list is still too full — go back to `/fix-and-prove`.
- Named but not followed: the step is vague or its reason is missing. Rewrite that step.
- Followed, but the result was still wrong: the playbook is missing something. Add one line to "Past mistakes", with the reason.

To compare models, run the same few tasks on each setup — the working model alone, the working model with the advisor, the strongest model alone — and compare cost against whether the work passed its check.
