---
name: write-playbook
description: Step 4 of the Opus playbook. Run on the strongest model to write the opus-playbook skill, tailored to how this user actually works.
disable-model-invocation: true
---

# Step 4 — Write the playbook

Tomorrow a cheaper model does this user's work. Write down how you would do it, so that model can follow it. The output is the `opus-playbook` skill at `~/.claude/skills/opus-playbook/SKILL.md`. A general version ships with this repo; your job is to replace the general parts with this user's specifics.

## Find out how the work really goes

Read the last 30 days of session logs in `~/.claude/projects/` (sample the longest twenty sessions if there are many), plus the rules files. Look for:

- The five or six kinds of task that come up most, in the user's own words.
- Where things went wrong: the user correcting course, redoing work, saying "no", "that's not what I asked", "you didn't test it".
- What a finished task looks like here: which test command, which build, which review.
- Which work was handed to subagents, and whether that paid off.

## Write it

Keep the shipped structure — plan, split, check, escalate — and make each part specific:

- **Plan**: for each common task kind, the steps in order and the files or commands involved.
- **Split**: what to do directly, what to hand to a subagent, and what a handover message must contain.
- **Check**: the real commands that prove work is done in this user's projects.
- **Escalate**: the situations, taken from the logs, where the cheaper model should stop and ask the advisor.
- **Past mistakes**: at most ten, each one line, each with the reason.

Rules for the writing:

- Every instruction carries its reason. A model that knows why can handle the case you did not foresee.
- Plain, calm sentences. No capitals for emphasis.
- Under 150 lines. Anything longer goes in a separate file beside SKILL.md, named in the playbook with one line on when to read it.
- Leave out what any capable model does anyway. Each line should change behaviour.
- The description stays one line, so it is never cut from the skill list.

Show the user the draft and the evidence behind each specific rule before saving. Then: switch models (step 5 in the README) and run `/prove-playbook`.
