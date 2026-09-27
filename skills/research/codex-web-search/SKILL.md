---
name: codex-web-search
description: "Use for deep web research via Codex native search."
---

# Codex web search

Codex CLI has OpenAI's native server-side `web_search`. Use it for research that needs several searches plus reasoning. For a single quick lookup, the local `web_search` / `web_extract` tools (backend `web.backend: exa`) are cheaper.

## Command

```bash
cd "$TMPDIR" && timeout 280 codex --search exec -m gpt-6-luna -c model_reasoning_effort=medium --skip-git-repo-check -s read-only "<question>. Answer briefly with source URLs." 2>&1 | tail -30
```

- `--search` is a TOP-LEVEL flag: put it before `exec`. `codex exec --search` fails with `unexpected argument '--search'`.
- Always pin `-m gpt-6-luna -c model_reasoning_effort=medium` (user choice: fast and cheap enough for search). Without it Codex CLI falls back to its default model (gpt-6-astra).
- `-s read-only` stops Codex from editing files; the search itself still runs.
- The last block of output is the final answer. `web search:` lines show the queries it ran.
- Each call spends the Codex limit. Check it with `node C:\Users\user\.codex\usage-status.js`.
- Treat the answer as a self-report. Open the key URL with `web_extract` when the fact matters.

## Do not

- Do not set `web.search_backend: openai-native` while the main model is not on the Codex transport. On Claude every `web_search` call then fails with "openai-native ... requires the Codex Responses transport" and only the keyless rescue saves it.
