---
name: hermes-tool-backend-setup
description: "Use when fixing Hermes web backends or gateway delivery."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [hermes, web-search, web-extract, backend, config, troubleshooting]
    related_skills: [hermes-agent, agent-harness-config]
---

# Hermes tool backend setup

## When to Use

- User asks to enable search / internet access for Hermes.
- Web tool results carry `backend_error`, `rescued_from`, or a provider error.
- Telegram/messaging replies, `/handoff`, or background notifications stop arriving: follow `references/gateway-delivery.md` (check the gateway process is alive before anything else).

Docs: https://hermes-agent.nousresearch.com/docs/user-guide/features/web-search

## Procedure

1. **Read the evidence first.** Web result with `served_by` + `rescued_from: <name>` + `backend_error` = selected backend failed, keyless tier rescued it. It "works" but every call fails first: fix the selection, don't accept it.
2. **Read stored selection** (never hand-edit config.yaml):
   ```bash
   for k in web.backend web.search_backend web.extract_backend web.keyless_fallback; do echo "$k=$(hermes config get $k)"; done
   ```
3. **Resolve what runtime actually picks.** Empty config does not mean keyless: autodetect walks env keys, then plugin providers' `is_available`, then the keyless ring.
   ```bash
   cd "$HERMES_HOME/hermes-agent" && venv/Scripts/python.exe -c "from tools import web_tools as w; print(w._get_search_backend(), w._get_extract_backend())"
   ```
   Why: `w._ensure_web_plugins_loaded()` then `agent.web_search_registry.list_providers()`, probe `is_available` / `is_keyless_available`.
4. **Pin a backend:** `hermes config set web.backend exa` (keyless-capable, search + extract).
   - Keyless-capable, search + extract: exa, tavily, firecrawl, parallel, keenable (rate-limited without key; throttled calls fail over across the ring).
   - Search-only: searxng, brave-free, ddgs, xai — also set `web.extract_backend`.
5. **Verify both paths:** resolver one-liner shows the pin; real dispatch:
   ```bash
   venv/Scripts/python.exe -c "import model_tools as m; print(m.handle_function_call('web_search',{'query':'test','limit':2})[:300]); print(m.handle_function_call('web_extract',{'urls':['https://example.com']})[:200])"
   ```
   Then call `web_search` in the live session: no `backend_error`. Config is read per call, no restart.
6. **Report:** cause, the one config change, verification, rate-limit caveat plus which `.env` key lifts it (e.g. `EXA_API_KEY`; user adds it, never type secrets).

## Pitfalls

- `openai-native` gets autoselected when `web.backend` is empty and Codex OAuth credentials exist (its `is_available` = has Codex creds). It is only a marker for the Codex Responses transport; on Claude or other transports every `web_search` fails. Pin a client-side backend explicitly.
- Once any `web.*` backend is set, adding an API key to `.env` does not reroute; explicit selection wins. Change the selection too.
