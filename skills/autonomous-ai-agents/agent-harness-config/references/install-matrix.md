# Install matrix: skills and plugins per harness

## Commands

| Harness | Install | Always-on mechanism | Verify |
|---|---|---|---|
| Hermes (skill) | `hermes skills install <hub-id> --yes` (hub-id from `hermes skills search`, e.g. `skills-sh/<owner>/<repo>/<skill>`) | `hermes config set skills.auto_load '[...]'` | `cd $HERMES_HOME/hermes-agent && ./venv/Scripts/python.exe -c "from agent.skill_commands import build_auto_load_prompt; t,l,m=build_auto_load_prompt(); print(l,m)"` → all loaded, `missing` empty |
| Hermes (plugin) | `hermes plugins install <owner/repo> --enable` | plugin `pre_llm_call` hook | `hermes plugins list`; may be BLOCKED by scan — fall back to skill |
| Claude Code | `claude plugin marketplace add <owner/repo>` then `claude plugin install <name>@<marketplace>` (works from a shell in one call) | plugin SessionStart hook | `enabledPlugins` in `~/.claude/settings.json`; run the hook (below) |
| Codex (plugin) | `codex plugin marketplace add <owner/repo>` then `codex plugin add <name>@<marketplace>` | plugin hooks, **only after trust**: user runs `codex`, opens `/hooks`, trusts them | `[plugins."name@mp"] enabled = true` in `$CODEX_HOME/config.toml`; files under `$CODEX_HOME/plugins/cache/` |
| Codex (skill only) | `npx -y skills add <owner/repo> -a codex -g -s <skill> -y` → `~/.agents/skills/<skill>` | none native → rule in `GLOBAL_RULES.md` | directory exists |

## Hook smoke test (Claude Code / Codex plugins)

Feed a SessionStart payload on stdin; isolate state in a scratch config dir so the real session store is untouched:

```bash
P='C:/Users/user/.claude/plugins/cache/<mp>/<name>/<ver>'
F="C:/Users/user/AppData/Local/hermes/cache/scratch/fakeclaude"; mkdir -p "$F"
echo '{"session_id":"t1","source":"startup","hook_event_name":"SessionStart"}' \
  | CLAUDE_CONFIG_DIR="$F" CLAUDE_PLUGIN_ROOT="$P" node "$P/<hook>.js" | head -3
```
Expect the banner with the configured level (e.g. `... MODE ACTIVE — level: full`).

## Known skills

| Skill | Repo | Hermes | Claude Code | Codex | Default level |
|---|---|---|---|---|---|
| caveman (terse prose) | `JuliusBrussee/caveman` | hub skill `skills-sh/juliusbrussee/caveman/caveman` + auto_load | plugin `caveman@caveman` (hook: `src/hooks/caveman-activate.js`) | no plugin → `npx skills add ... -a codex` + GLOBAL_RULES rule | `%APPDATA%\caveman\config.json` `{"defaultMode":"full"}` or env `CAVEMAN_DEFAULT_MODE` |
| ponytail (minimal code) | `DietrichGebert/ponytail` | hub skill `skills-sh/dietrichgebert/ponytail/ponytail` + auto_load (plugin gets scan-blocked) | plugin `ponytail@ponytail` (hook: `hooks/ponytail-activate.js`) | plugin `ponytail@ponytail` + trust hooks | `%APPDATA%\ponytail\config.json` `{"defaultMode":"full"}` or env `PONYTAIL_DEFAULT_MODE` |

On Windows both config resolvers use `%APPDATA%\<name>\config.json` unless `XDG_CONFIG_HOME` is set.
