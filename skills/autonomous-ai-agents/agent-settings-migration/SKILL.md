---
name: agent-settings-migration
description: "Use when copying Hermes settings to another machine."
version: 1.0.0
metadata:
  hermes:
    tags: [hermes, migration, ssh, config, skills, memories, windows]
    related_skills: [agent-harness-config, hermes-agent]
---

# Agent settings migration (machine to machine)

Remote hosts are Windows over `ssh <host>` (PowerShell). Hermes home on both: `%LOCALAPPDATA%\hermes`. Global-rules conventions: skill `agent-harness-config`.

## Procedure

1. Recon both sides in one call: list local home; on remote `Test-Path` home, list it, `hermes --version`, first lines of `config.yaml` (template header = fresh install), `ls ~/.agents`, `where.exe claude codex tar`.
2. Ask the user in ONE clarify call:
   - scope: config.yaml + SOUL.md + memories + own skills + GLOBAL_RULES (no secrets) / same + `.env` + `auth.json` / only config + SOUL;
   - Telegram: disable on target (recommended) / copy as is. One bot token polled by two gateways conflicts.
3. Pick own skills only: walk `skills/` for dirs with `SKILL.md` whose name is not in `skills/.bundled_manifest` (lines `name:hash`). Bundled skills stay the target's version.
4. Stage into `$TMPDIR/hx/{h,a}` keeping category paths, `tar -czf`, `scp` to remote home. Windows has `tar.exe`.
5. Apply with a PowerShell script: `scp` it, run `powershell -ExecutionPolicy Bypass -File` (inline quoting through ssh breaks). Script steps:
   - back up config.yaml, SOUL.md, .env, auth.json, memories to `hermes\backups\pre-import-<stamp>`;
   - extract, `Copy-Item -Recurse -Force` over Hermes home; copy `.env` explicitly (dotfile);
   - GLOBAL_RULES into `~\.agents`, `~\.claude\CLAUDE.md`, `~\.codex\AGENTS.md`: try symlink first (single source); if refused (no Developer Mode/admin) copy and tell the user copies miss later edits;
   - Telegram off: comment `^TELEGRAM_` lines via `[IO.File]::WriteAllLines(...)` (PS 5 `Set-Content -Encoding utf8` writes a BOM) and `hermes config set platforms.telegram.enabled false`;
   - delete archive and script.
6. Verify on remote: `TELEGRAM_` lines commented, `hermes config get model.provider`, SKILL.md count, memories listed, then real call `hermes chat -q "Reply with OK only"` (session summary = provider auth works).
7. Report: backup path, version gap (run `hermes update` on older target; source `_config_version` may be newer), `skills.trusted_project_dirs` keep source paths (harmless). Remove local staging.

## Pitfalls

- Writing another machine's secrets/config is gated: state exactly what the script changes, get an explicit go. Timed-out approval = nothing ran; do not retry, ask.
- Never print `.env`/`auth.json` contents; list key names only (`grep -o '^[A-Z_]*'`, JSON top-level keys).
