# Task 4 — Git Challenges

All three challenges completed on `git-assessment`.

Starting state after cloning:

```
main            fdd0878 update readme
git-assessment  91b1bdc fix typo error 4
                5e6147e fix typo error 3
                687f604 fix typo error 2
                1eaedc3 fix typo error 1
                1443488 typo error
                6bc6d5c Add payment feature      ← wrong branch
                fdd0878 update readme
feature/payment fdd0878 update readme            ← no payment commit
```

Note `fix typo error 5` is missing from the branch tip — that is Challenge 1.

> **In plain terms:** The repo has three problems baked in. A commit was
> "deleted" (Challenge 1), the history is cluttered with junk commits
> (Challenge 2), and a payment feature landed on the wrong branch (Challenge 3).
> Each requires a different Git technique to fix.

---

## Challenge 1 — Lost commit

`git reset --hard HEAD~1` moved the branch pointer back one commit. The commit
object itself was never deleted: nothing in Git removes objects until `gc` runs,
and `gc` will not collect anything still referenced by the reflog. The reflog is
the record of where `HEAD` has been, so the "lost" commit is one lookup away.

```bash
git checkout git-assessment
git reflog
```

```
91b1bdc HEAD@{1}: reset: moving to HEAD~1
100f978 HEAD@{2}: checkout: moving from feature/payment to git-assessment
```

`HEAD@{2}` is the value `HEAD` held immediately before the reset — `100f978`,
`fix typo error 5`.

> **In plain terms:** Git's reflog is like a browser history for your branch
> pointer — even after "deleting" a commit with `reset --hard`, Git still
> remembers where HEAD used to point. The commit is not gone, just unreferenced.
> We look it up in the history and point the branch back at it.

Confirmed before touching anything:

```bash
git show -s --format="%h %s" 100f978
# 100f978 fix typo error 5
```

Recovered by moving the branch pointer back to it:

```bash
git reset --hard 100f978
```

```
100f978 fix typo error 5      ← recovered
91b1bdc fix typo error 4
5e6147e fix typo error 3
...
```

**Why `reset --hard` here:** the working tree was clean and the goal was to
restore the branch to exactly that commit. `git cherry-pick 100f978` would also
work and is the safer reflex when the branch has moved on since — it replays the
change as a new commit rather than repointing the branch. With uncommitted work
present, `reset --hard` would discard it, so `git stash` first (which is exactly
what I did before running this on a tree that held the Task 2 work).

If the reflog had also been unavailable — a fresh clone, or after `gc` — the
fallback is `git fsck --lost-found`, which lists unreachable objects.

---

## Challenge 3 — Wrong branch commit

Done before Challenge 2, because `6bc6d5c` sits at the *base* of the noisy
stack. Removing it first means the history cleanup operates on a run of commits
that all belong on the branch.

The commit needs to move, not be copied: land on `feature/payment`, disappear
from `git-assessment`.

> **In plain terms:** A letter ended up in the wrong mailbox. We photocopy it
> into the right mailbox (`cherry-pick`), then remove the original from the
> wrong one (`rebase --onto`). The result: the payment feature exists only on
> `feature/payment`, where it belongs.

**Step 1 — copy it onto the correct branch:**

```bash
git checkout feature/payment
git cherry-pick 6bc6d5c
```

```
a8a65e1 Add payment feature
fdd0878 update readme
```

`payment.txt` is now present on `feature/payment`. The hash changes because a
cherry-pick creates a new commit with a new parent — same tree change, different
identity.

**Step 2 — remove it from the wrong branch:**

```bash
git checkout git-assessment
git rebase --onto fdd0878 6bc6d5c git-assessment
```

Read as: take the commits after `6bc6d5c` up to `git-assessment`, and replay
them onto `fdd0878`. The payment commit is the excluded base, so it is dropped;
everything above it is preserved.

```
e0e6e1d fix typo error 5
543dd03 fix typo error 4
73e1885 fix typo error 3
5c82159 fix typo error 2
173bcac fix typo error 1
1fa3e01 typo error
fdd0878 update readme
```

`payment.txt` is gone from `git-assessment` and present on `feature/payment`.
The typo commits were rewritten (new hashes) because their parent changed — the
unavoidable cost of removing a commit from the middle of a branch.

**Alternative:** `git revert 6bc6d5c` on `git-assessment` leaves history intact
and adds an undo commit. That is the correct choice on a shared branch where
others have already pulled. Here the branch is an assessment branch and the task
asks to *move* the commit, so rewriting is appropriate — the payment commit
should not appear in this branch's history at all.

---

## Challenge 2 — Messy commit history

The six remaining commits:

```
1fa3e01 typo error          — adds 5 junk lines to README.md
173bcac fix typo error 1    — removes line 1
5c82159 fix typo error 2    — removes line 2
73e1885 fix typo error 3    — removes line 3
543dd03 fix typo error 4    — removes line 4
e0e6e1d fix typo error 5    — removes line 5
```

> **In plain terms:** Six commits look like work — "typo error" then five
> "fix typo error" commits. But reading the actual diffs reveals they cancel
> each other out completely: one adds junk, five remove it. The file ends up
> identical to where it started. The honest cleanup is to drop them all, not
> to squash them into a tidy lie.

Inspecting the diffs first rather than squashing blind is the whole job here.
`1fa3e01` appends five lines to the end of `README.md`; the five "fix" commits
remove them one at a time. The stack is a closed loop — `README.md` at
`e0e6e1d` is byte-identical to `README.md` at `fdd0878` (blob `18fa38f` both
times).

That determines the right cleanup. These commits do not describe work that
happened badly; they describe work that did not happen at all. Squashing them
into one well-named commit would produce a commit with an empty diff, and a
commit that changes nothing does not belong in history regardless of how good
its message is.

**The rebase:**

```bash
git rebase -i --empty=drop fdd0878
```

Todo list, keeping the first commit of the run and folding the five undo commits
into it (`fixup` rather than `squash`, since none of the messages are worth
keeping):

```
pick  1fa3e01 typo error
fixup 173bcac fix typo error 1
fixup 5c82159 fix typo error 2
fixup 73e1885 fix typo error 3
fixup 543dd03 fix typo error 4
fixup e0e6e1d fix typo error 5
```

The combined result was, as expected, an empty commit, which was then dropped:

```bash
git reset --hard fdd0878
```

**Result:**

```bash
git diff --stat main git-assessment
# (no output — branches identical)
```

`git-assessment` is back to a clean base with the noise gone, and the real work
sits on top of it as the commits listed below.

**Why not squash into one "fix README typos" commit:** it would be a lie. The
message would describe a change the commit does not contain, and the next person
to run `git log --stat` would find an empty commit and have to work out why.
Empty history is more honest than decorated history.

**Why `fixup` over `squash`:** `squash` concatenates all six messages into an
editor buffer for combining. There was nothing in `fix typo error 1..5` worth
carrying forward, so `fixup` discards them.

**On a shared branch** none of this rewriting would be acceptable without
coordination — rewritten history forces every collaborator to reset, and
`--force-with-lease` (never bare `--force`) is the minimum safety on push.

---

## Final state

```
git-assessment
  <commits>  Investment Strategy agent, tests, docs   ← Tasks 1-3
  fdd0878    update readme                            ← clean base, noise removed

feature/payment
  a8a65e1    Add payment feature                      ← relocated
  fdd0878    update readme
```

Verification:

```bash
git log --oneline feature/payment -2      # payment commit present
git show 100f978                          # recovered commit reachable
git log --oneline git-assessment          # no "fix typo error N" commits
git diff --stat fdd0878 git-assessment    # only the assessment work
```

---

## Commit conventions used for the assessment work

Conventional Commits (`feat`, `test`, `docs`) with a scope, one logical change
per commit, ordered so each builds on the last: schemas and context before the
agent that uses them, the agent before the endpoint that exposes it, tests
before the docs that reference them. Each commit leaves the test suite passing.
