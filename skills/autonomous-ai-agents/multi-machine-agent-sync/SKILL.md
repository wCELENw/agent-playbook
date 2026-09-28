---
name: multi-machine-agent-sync
description: "Use when syncing agent rules/skills between machines or handling CONFLICT/LOCAL lines of the playbook sync log."
---

# Sync agent setup between machines (agent-playbook)

The owner runs a Hermes coordinator on several Windows machines (e.g. `minipc`, `powerpc-1`,
a laptop). Each learns lessons into its own `$HERMES_HOME/skills` and `~/.agents/GLOBAL_RULES.md`;
the public repo `wCELENw/agent-playbook` is the source of truth and the exchange point
(GLOBAL_RULES §16). Scrubbing rules for the public repo: `agent-project-setup`
`references/playbook-sync.md`. This skill is the machine-to-machine part.

## Automatic pull (already running)

- Scheduled task `agent-playbook-sync` (daily and at logon) runs `scripts/sync_playbook.py`
  from the machine's clone: `git pull --ff-only`, then per file of `skills/**` and
  `global/GLOBAL_RULES.md` compares the local copy with the repo (CRLF ignored) and with the
  hash recorded at the last sync. New machine: install the task with `scripts/install-sync-task.ps1`.
- State: `~/.agents/agent-playbook.sync.json` (repo hash per file at last sync); log:
  `~/.agents/agent-playbook.sync.log`, one summary line per run
  (`OK / INSTALL / UPDATE / ADOPT / LOCAL / CONFLICT` counts) plus one line per non-OK file.
- It only overwrites copies untouched since the last sync (`UPDATE`) and installs missing ones.
  - `LOCAL` — the copy was edited on this machine, the repo did not change: a machine lesson
    not yet in the repo.
  - `CONFLICT` — the copy differs and the repo changed too (or the file has no state yet).
  Both are left alone and reported; nothing is pushed automatically (public repo, scrub first).
- First run on a machine whose copies already drifted: `py scripts/sync_playbook.py --adopt`
  takes the repo version everywhere and backs up every replaced copy to
  `~/.agents/playbook-backup-<timestamp>/`. Before `--adopt`, move the machine lessons into the
  repo (procedure below) or mine the backup afterwards. `--dry-run` shows the plan.

## Manual part: CONFLICT / LOCAL and machine lessons

Do this at the next work with skills after the log shows `LOCAL` or `CONFLICT` lines.

1. `grep -E "LOCAL|CONFLICT" ~/.agents/agent-playbook.sync.log | tail` — the file list.
2. **Read the hunks** per file: `diff --strip-trailing-cr <repo file> <local copy>`. A differing
   machine copy often holds lessons the repo lacks — copy them INTO the repo, do not overwrite
   them. Machine copies keep real values (chat id, private project names) where the repo has
   placeholders; that difference is expected and stays out of the repo.
3. **Carry over only what is current:** lessons written against an older routing (`delegate_task`
   as a route, Sonnet, Luna doing analysis) are dropped — GLOBAL_RULES §9 wins. Generalize private
   examples ("in a game mod", `<project>`), no real chat ids, IPs or tokens.
4. Other machines: pull their copies read-only and compare the same way (full set, both
   directions — files missing in the repo too: `references/*`, `scripts/*`, whole skills).
5. `bash scripts/check-public.sh` → `clean`, commit explicit paths, push. The next scheduled run
   on each machine turns its `LOCAL` lines into `OK` (copy now equals repo); for `CONFLICT` lines
   whose lesson is merged, run `--adopt` on that machine (backup kept) or copy the repo file over.
6. Report per machine: what moved in which direction, commit hash, what still needs the owner.

## Rules files and config

- Check `SOUL.md`, `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` are symlinks to
  `~/.agents/GLOBAL_RULES.md` (`pwsh Get-Item <f> | Select LinkType,Target`); plain copies drift.
  A machine-only line in them is an owner decision (machine override vs repo value) — ask,
  recommended option first.
- **Rules text is not config.** A model-routing change in §9 changes nothing by itself: update
  on each machine the config it names (`hermes config set ...`), every rules copy, the
  `orca-worker-routing` table and the repo together, then grep for the old slug.

## Other machine over SSH

- Use Windows OpenSSH (`C:/Windows/System32/OpenSSH/ssh.exe` / `scp.exe`), not git-bash ssh.
  SSH user = the Windows login, not the owner's name; on "Permission denied" try the login name
  and fix `User` in `~/.ssh/config`. Print a public key in full — never truncate it when the
  owner must paste it. The remote shell may be cmd or PowerShell; output may be cp866 (`grep -a`).
- Run Python there by `scp`-ing a script file, not by quoting one-liners through cmd.
- `scp` a whole skills tree is slow (venvs, assets): list files first, or pack a zip on the
  remote side and copy one file. Local destination paths: relative or native Windows; a
  `C:/...` destination inside a bash loop fed from a CRLF list fails on the trailing `\r`.
- **Fallback when the machine has no GitHub access** (the scheduled pull then logs
  `ERROR git pull`): deliver commits by bundle. If the source clone is shallow, `git fetch
  --unshallow` first (a shallow bundle fails: "remote did not send all necessary objects").
  `git bundle create x.bundle main` (in the repo dir, not an MSYS `/tmp` path) → `scp` → on the
  target clone (clean tree): `git fetch ../x.bundle main && git reset --hard FETCH_HEAD &&
  git update-ref refs/remotes/origin/main HEAD`, then `py scripts/sync_playbook.py --no-pull`.

## Pitfalls

- **Test a script that edits app state only on a copy, and prove the real store is
  untouched** (hash or revision before and after). Point the script at the copy through the
  env var it actually reads (`HERMES_HOME`, `AGENTS_HOME` for `sync_playbook.py`); after
  renaming an override variable re-check — a stale name silently falls back to the real path.
- **Never open a maybe-absent SQLite file with plain `sqlite3.connect`**: it creates an empty
  file the app may then misread. Use `file:<path>?mode=ro` (read) or `mode=rw` (edit).
- **App settings storage differs by app version across machines** (e.g. Orca: SQLite
  `profile-state.db` in newer builds, `orca-data.json` in older). Detect the store per machine
  before editing.
- **Editing a running app's settings**: close the app first (it holds settings in memory and
  overwrites the edit); closing it on a busy server kills live workers — ask the owner when.
