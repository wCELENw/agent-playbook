---
name: agent-harness-config
description: "Global rules/skills across Hermes, Claude Code, Codex."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, claude-code, codex, global-rules, soul-md, skills, plugins, always-on, symlink]
    related_skills: [hermes-agent, claude-code, codex]
---

# Agent Harness Config (Hermes + Claude Code + Codex)

The user runs three harnesses (Hermes, Claude Code, Codex, often launched via Orca); behavior rules and always-on skills must be identical in all three.

## When to Use

- Installing or changing global agent behavior rules (`GLOBAL_RULES.md`, SOUL.md, CLAUDE.md, AGENTS.md).
- Installing a skill or plugin "for the agent", making it always-on, or setting its default level.
- Checking why a harness does not follow the global rules or an always-on skill.

## Standing preferences (always apply)

- **Single source of truth.** Global rules live ONLY in `~/.agents/GLOBAL_RULES.md`. Every harness file is a **symlink** to it, never a copy: edits must propagate without syncing. Treat any other copy (e.g. a dropped file in a project `.orca/drops/`) as stale once installed.
- **Changes cover all harnesses.** A request to install/enable something "for the agent" means Hermes, Claude Code AND Codex unless the user narrows it. If one harness can't auto-activate it natively, add a rule to `GLOBAL_RULES.md` so it still applies there.
- **Ask before dropping content.** When replacing an existing harness file with the symlink, diff it against the global file first; blocks that exist only in the old file (e.g. reference data like chat IDs) → ask the user: merge into global / drop / leave file alone.
- **Back up before replacing** into the harness's own `backups/` dir with a dated suffix.

## Harness file map

| Harness | Rules file (symlink → `~/.agents/GLOBAL_RULES.md`) |
|---|---|
| Hermes | `$HERMES_HOME/SOUL.md` (here `C:\Users\user\AppData\Local\hermes\SOUL.md`) — always loaded, identity slot |
| Claude Code | `~/.claude/CLAUDE.md` |
| Codex | `~/.codex/AGENTS.md`; **check `$CODEX_HOME` first** — Orca points it at `%APPDATA%\orca\codex-runtime-home\home`, whose `AGENTS.md` links to `~/.codex/AGENTS.md`, and `codex plugin` commands write to `$CODEX_HOME/config.toml` |

Not for global rules: Hermes `AGENTS.md`/`.hermes.md` are cwd/project-scoped.

## Procedure: install global rules

1. Read the source file; `ls -la` every target; diff existing harness files against it (see preferences).
2. Copy the source to `~/.agents/GLOBAL_RULES.md` (create dir if needed).
3. Back up + remove each target, then create the symlink with Python — Git Bash `ln -s` makes a plain copy by default (unless `MSYS=winsymlinks:nativestrict`), which breaks single-source:
   ```bash
   PY="$HERMES_HOME/hermes-agent/venv/Scripts/python.exe"
   "$PY" -c "import os; os.symlink(r'C:\Users\user\.agents\GLOBAL_RULES.md', r'<target>')"
   ```
4. Verify: `os.path.islink(p)` true and bytes equal the source for every target.
5. Verify Hermes actually ingests it (length, not blocked by the injection scanner):
   ```bash
   cd "$HERMES_HOME/hermes-agent" && ./venv/Scripts/python.exe -c "from agent.prompt_builder import load_soul_md; s=load_soul_md(); print(len(s), 'BLOCKED' in s)"
   ```
6. Apply config the rules demand via `hermes config set` (e.g. notification sound → `display.bell_on_prompt true`).
7. Report: takes effect in NEW sessions only. SOUL.md replaces Hermes's default identity line — mention it.

## Procedure: always-on skills / plugins in every harness

1. Find sources: `hermes skills search <name>` (gives hub identifiers); read the upstream install docs from a shallow clone (`git clone --depth 1 <repo> "$TMPDIR/x"`, then README/INSTALL.md, plugin manifests, installer `bin/install.js`) — it lists the native path per harness and the default-mode config.
2. Install per harness — commands in `references/install-matrix.md`.
3. Make it always-on:
   - Hermes: `hermes config set skills.auto_load '["a","b"]'` (loads into every new CLI/TUI/gateway/cron session).
   - Claude Code / Codex: plugin SessionStart hooks do it; Codex needs hook trust (user step, see matrix).
   - Harness without native auto-activation → add a numbered rule to `GLOBAL_RULES.md`.
4. Default level: set via the plugin's config file / env var (matrix), not by editing plugin code.
5. Verify each harness (matrix "Verify" column). Run hook scripts with native `C:/...` paths — node is a native binary and does not translate `/c/...` MSYS paths.
6. Check the new always-on skills against the user's tone rules in `GLOBAL_RULES.md` (e.g. a terse-prose skill vs a butler tone); report the conflict and the softer level that resolves it.

## Procedure: sync to the public playbook repo

`agent-playbook` on GitHub is **public**. The canon stays on the machine (`~/.agents`,
`$HERMES_HOME/skills`); machine copies keep real values, the repo gets placeholders.

1. Copy the changed rules/skills into the clone.
2. Replace private data with placeholders: owner chat_id → `<OWNER_CHAT_ID>`, tailnet name →
   `<tailnet>`, e-mails → remove; project names in examples → neutral wording
   ("a project-local `tools/x.py`", `<project>`), never the real project name.
3. Run `bash scripts/check-public.sh`. It reads private terms from
   `~/.agents/public-scrub.txt` (one per line, kept **outside** the repo: chat ids, e-mails, tailnet,
   project names). It checks tracked files, unpushed diffs and commit authors. Install it once per
   clone as `.git/hooks/pre-push` so a push with a leak is refused.
4. Commit as `wCELENw <148003103+wCELENw@users.noreply.github.com>` (`git -c user.email=...`), not a
   personal e-mail: author e-mails are public.
5. If a private value was already pushed: replace it, squash history and force-push; GitHub still
   serves old commits by hash, so recreate the repo (rename the old one, keep it private) when the
   leak matters.

## Pitfalls

- `hermes skills install` in TUI needs `--yes`, otherwise it waits for a confirmation prompt.
- `hermes plugins install <community repo>` scans the whole repo; tests/benchmarks/examples can trip a CAUTION verdict → BLOCKED. Do not `--force` without the user's consent; the hub skill + `skills.auto_load` covers the behavior.
- Hub skills installed via `hermes skills install` are hub-owned: do not edit their SKILL.md; change behavior via config (`defaultMode`) or `GLOBAL_RULES.md`.
- Don't claim a harness picked up a change unless it was exercised; say which harness was only file-verified.
