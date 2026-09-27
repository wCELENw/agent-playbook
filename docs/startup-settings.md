# Startup settings: machine checklist for Hermes + Orca

Run this once on every machine after installing the playbook, and again after a harness update.
Each item: **Do** — the change; **Check** — the command whose output proves it. An item is done
only when its check passes. Report a table "item → done / skipped (why) / failed (output)".

Rules: back up every file before editing it (`<file>.bak-<date>`); edit JSON/TOML with a script
(load, set, dump), never by hand; do not touch other tools' hooks or settings. Paths are for
Windows + git-bash; on macOS/Linux use `~/.hermes` for `$LOCALAPPDATA/hermes` and `~/.config` for
`%APPDATA%`.

## 1. Rules and skills

1. **Global rules in one file, harness files are symlinks.**
   Do: `~/.agents/GLOBAL_RULES.md` from `global/GLOBAL_RULES.md`; symlinks
   `$LOCALAPPDATA/hermes/SOUL.md`, `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` → it (Developer
   Mode; `pwsh New-Item -ItemType SymbolicLink`, see `agent-project-setup` §4).
   Check: `pwsh -c "Get-Item <each file> | Select Name,LinkType,Target"` shows `SymbolicLink`;
   if a harness file must stay a copy, `diff --strip-trailing-cr` with the canon is empty.
2. **Placeholders replaced** in the installed copies only (never in the clone): `<OWNER_CHAT_ID>`,
   `<tailnet>`, machine names, paths, CPU limits (§13: at most 80 % of logical threads).
   Check: `grep -n "<OWNER_CHAT_ID>\|<tailnet>" ~/.agents/GLOBAL_RULES.md` is empty.
3. **Global skills installed**: `skills/*` → `$LOCALAPPDATA/hermes/skills/`.
   Check: `hermes chat -q "list skills whose name starts with agent-" -Q` names them.
4. **Third-party packs** `caveman`, `ponytail` (auto-load, level full) and Orca `orchestration`:
   `skills/autonomous-ai-agents/agent-project-setup/references/third-party-skill-packs.md`.
   Check: a fresh Hermes, Claude Code and Codex session answers tersely without being asked.
5. **Version file**: `git -C ~/agent-playbook rev-parse HEAD > ~/.agents/agent-playbook.version`.
   Check: the file holds the clone's HEAD.

## 2. Hermes (coordinator)

6. **Delegation model** (§9): `hermes config set delegation.provider anthropic`,
   `delegation.model claude-opus-5-5`, `delegation.reasoning_effort medium` (the warning
   "not a recognized config key" for `reasoning_effort` is harmless).
   Check: `grep -A5 '^delegation' $LOCALAPPDATA/hermes/config.yaml`.
7. **Sound on questions** (§5): `hermes config set display.bell_on_prompt true`.
   Check: grep the key in `config.yaml`.
8. **Telegram delivery** (if used): the owner has sent `/start` to the bot.
   Check: `hermes send -t telegram:<OWNER_CHAT_ID> "setup check"` returns a `message_id`.

## 3. Claude Code (workers)

9. **Sound on questions** (§5): `hooks.Notification` in `~/.claude/settings.json` running
   `powershell -NoProfile -Command "[System.Media.SystemSounds]::Asterisk.Play()"`; keep existing
   hooks (Orca, claude-mem).
   Check: `python -c "import json,pathlib;print(json.load(open(pathlib.Path.home()/'.claude/settings.json'))['hooks']['Notification'])"`.
10. **Early auto-compaction** (§15): `env.CLAUDE_CODE_AUTO_COMPACT_WINDOW = "300000"` in
    `~/.claude/settings.json` (script in README "Install manually").
    Check: the same one-liner prints `['env']`.
11. **Trusted project folders**: for every repo and worktree root workers open,
    `projects["C:/path/with/forward/slashes"].hasTrustDialogAccepted = true` in `~/.claude.json`.
    Otherwise an Orca worker hangs on "Do you trust this folder?".
    Check: the key is `true` for each project path; a test worker starts without the dialog.

## 4. Codex (image worker)

12. **Model and project rules in both homes** — `~/.codex/config.toml` and the Orca copy
    `%APPDATA%/orca/codex-runtime-home/home/config.toml`: top-level
    `project_doc_fallback_filenames = ["CLAUDE.md"]`, `model = "gpt-6-luna"`,
    `model_reasoning_effort = "xhigh"`, and `[projects.'<path>'] trust_level = "trusted"` per repo.
    Codex and Orca rewrite these files, so re-check after updates.
    Check: from a repo, `codex debug prompt-input hi | grep "<a phrase from CLAUDE.md>"`, once per home.

## 5. Orca

13. **Where Orca keeps settings depends on its version.** Newer Orca (seen in 1.4.215): SQLite
    `%APPDATA%/orca/profiles/local-default/profile-state.db`, table `profile_state_documents`,
    row `domain='settings'`, JSON in `payload`, `content_hash = sha256(payload)` hex;
    `orca-data.json` is then only an export. Older Orca (seen in 1.4.210): no such table, settings
    are in `orca-data.json` → `settings`. Edit only with Orca fully closed (every `Orca.exe`
    except `daemon-host`): Orca keeps settings in memory and overwrites a live edit. Use
    `scripts/orca_agent_env.py`: it finds the store, backs it up, and for SQLite bumps `revision`
    and recomputes the hash. Do not open `profile-state.db` with a plain `sqlite3.connect` where
    it does not exist: that creates an empty file.
14. **claude-mem off for Orca workers** — only if the Claude Code plugin claude-mem
    (thedotmack) is installed (`~/.claude-mem/` exists).
    Why: it hooks SessionStart / UserPromptSubmit / PostToolUse / PreToolUse(Read) / Stop /
    SessionEnd and calls Haiku (`CLAUDE_MEM_MODEL` in `~/.claude-mem/settings.json`) on each event.
    With Hermes as coordinator this is pure spend: Hermes keeps the memory, workers are short.
    Measured over 5 days: ~4300 Haiku calls on one machine, ~$45 at API prices, 60 % of it
    1-hour cache writes. claude-mem 13.28 skips all hooks when `CLAUDE_MEM_INTERNAL=1`
    (`scripts/worker-service.cjs`, `shouldTrackProject`, first check).
    Do: close Orca, `python scripts/orca_agent_env.py --set claude CLAUDE_MEM_INTERNAL 1`, start Orca.
    Orca adds `agentDefaultEnv.claude` to every Claude launch it makes, including
    `orchestration worker-start`. Scope: this covers all Claude tabs Orca starts (also manual ones
    from its UI); `claude` typed in a plain shell or an Orca shell tab keeps claude-mem.
    Check: `python scripts/orca_agent_env.py` shows the key; run a test Claude worker in an empty
    folder, then `sqlite3 ~/.claude-mem/claude-mem.db "select count(*) from sdk_sessions where project='<folder name>'"` is `0`.

## 6. Machine

15. **CPU cap** (§13): the machine's thread limit is written in `GLOBAL_RULES.md` §13.
    Check: the machine's host name appears there with a number.
16. **Pages in the tailnet** (§14): `tailscale status` lists this machine; `tailscale serve status`
    shows no foreign port you would reuse.
    Check: serve a test dir on a free port, `curl -s -o /dev/null -w "%{http_code}"
    http://<host>.<tailnet>.ts.net:<port>/` returns `200`, then `tailscale serve --http=<port> off`.
17. **Maintainers only**: deny-list `~/.agents/public-scrub.txt` (private terms, one per line) and
    `cp scripts/check-public.sh .git/hooks/pre-push`.
    Check: `bash scripts/check-public.sh` prints `check-public: clean`.
