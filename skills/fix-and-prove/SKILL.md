---
name: fix-and-prove
description: Step 3 of the Opus playbook. Back up the Claude setup, apply the user's answers to the clash page, then re-measure to prove the saving.
disable-model-invocation: true
---

# Step 3 — Fix it, then prove it

Apply the user's answers from `claude-clashes.md` and show the before and after.

## Order of work

1. **Back up first.** Copy every file you are about to touch into `~/.claude/backups/setup-<date-time>/`, keeping the folder structure, and write a `RESTORE.md` there with the exact copy commands to put everything back. Confirm the backup exists before any edit.
2. **Apply only what was answered.** A "yes" gets the recommendation. A "no" is left alone. "Other" gets what the user wrote. Unanswered entries are left alone and listed at the end. Do not make improvements nobody approved.
3. **Trim the start-up load**, if the user said yes to the savings in the report:
   - Move long procedures out of rules files into skills, so they load only when used.
   - Shorten skill descriptions to one line: what it does, when to use it.
   - Add `disable-model-invocation: true` to skills the user only ever starts by hand, so they leave the list.
   - Keep the memory index under 200 lines; move detail into the files it points to.
   - Narrow hooks that inject text on every message so they fire only where they apply.
   - Connectors nobody uses: tell the user which to turn off. Do not turn them off yourself.
4. **Never delete outright.** Removed text stays in the backup; whole skills move to `~/.claude/backups/setup-<date-time>/removed/`.
5. **Prove it.** Rerun the `audit-setup` script and compare with the earlier report.

## The result

Append to `claude-setup-report.md`:

| | before | after |
|---|--:|--:|
| tokens before the first word | | |
| skills showing a name only | | |
| rules file lines | | |

Followed by: what changed (file by file), what was left alone and why, and where the backup is.

File estimates move immediately. The exact start-up number only shows in a **new** session — tell the user to open one, run `/context`, and compare. Do not claim a saving you have not measured.

Next step: `/write-playbook`.
