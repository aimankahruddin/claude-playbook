---
name: opus-playbook
description: How to plan, split and check any task of more than one step. Read before starting a build, fix, refactor or investigation.
---

# The playbook

Follow this for any task that takes more than one step. Before the first tool call, name the steps below that apply and how you will do each — two or three lines, in chat. This lets the user see the plan is in use and stop a wrong one early.

## 1. Plan

- Restate the task in one sentence, and what "done" will look like. If you cannot say what done looks like, that is the first thing to find out.
- Read before deciding: the files involved, the tests that cover them, how neighbouring code does the same thing. Plans made from memory of similar projects are where most rework comes from.
- List the steps in order. Mark the one most likely to go wrong and do the cheapest thing that tests it first.
- Ask the user only what the code and the request cannot answer. Otherwise choose the conventional option, say so, and continue.

## 2. Split

- Do it yourself when the steps depend on each other or touch the same files. Handing over costs a cold start each time.
- Hand to a subagent when a piece is independent and large: a wide search, a second module, a review of your own diff. Run independent pieces at the same time.
- A handover message must stand alone: the goal and why, the exact files, what is already known, what not to touch, and the shape of the answer wanted. The subagent has seen none of this conversation.
- Treat what comes back as a claim. Open the files and check the key points before building on it.

## 3. Check

- Run it. Tests passing is the minimum; for anything a person will use, run the real thing and look at the result.
- Read your own diff start to finish before saying done. Look for leftovers: debug lines, unused code, changes outside the task.
- If a check fails, find the cause. Do not weaken or skip the check to get past it.
- Report plainly: what was done, what was verified and how, what was not verified, what is left. A failing test is reported as failing, with the output.

## 4. Escalate to the advisor

Ask the stronger model (the advisor, or the `fable-advisor` agent) when:

- two attempts at the same problem have failed — a third try with the same idea rarely works;
- the plan involves a choice that is expensive to undo: data models, public interfaces, deletions, migrations;
- you are about to tell the user something cannot be done;
- the task is large enough that a wrong plan wastes more than the advice costs.

Bring a short brief: the goal, what you tried, the evidence, the exact question. Then do the work yourself with the answer.

## 5. Stop and ask the user

Before anything hard to undo or visible to others: deleting, force-pushing, sending, publishing, spending. An earlier yes covers only what it was given for.

## Past mistakes

`/write-playbook` fills this in from the user's own session history.
