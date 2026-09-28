# Codex: where token usage lives and how to cut it

## Source
- Orca-launched Codex uses `CODEX_HOME=C:/Users/user/AppData/Roaming/orca/codex-runtime-home/home`
  (not `~/.codex`). Sessions: `sessions/**/*.jsonl`; images: `generated_images/<session>/exec-*.png`.
- Per session: the last event with `payload.type == "token_count"` -> `payload.info.total_token_usage`
  (`input_tokens`, `cached_input_tokens`, `output_tokens`, `reasoning_output_tokens`, `total_tokens`).
  Per turn: `payload.info.last_token_usage.input_tokens` -> shows context growth turn by turn.
- Model: `turn_context` event -> `payload.model`.
- Headless `codex exec --json`: the `turn.completed` event carries `usage` for that run.

## Reading the numbers
- Output is tiny (~2k per image task); spend is almost all input re-read (~86 % from cache).
- Each attached/generated image adds ~25k to context and stays for every later turn, so an
  agentic image task (generate, send, copy, verify, report = 8-10 turns) lands at ~400k per image.

## Cutting it
- Default route stays an Orca Codex worker, one per image (GLOBAL_RULES §9); keep its spec
  short and the mechanical steps out of it.
- Only when the owner names headless `codex exec`: one image = one `codex exec --ephemeral` in an empty temp dir with
  `-c 'project_doc_fallback_filenames=[]'` (no CLAUDE.md / rules in context) and
  `-c 'model_reasoning_effort="low"'`; prompt says "call image_gen once, do not read files or run
  commands". Measured: ~46k tokens, 1 turn, ~95 s.
- Move every mechanical step (Telegram send, copy, archive, checks) into the calling script.
- Do cheap exploration (drafts, seeds) on a local model first; spend Codex only on the pick.
