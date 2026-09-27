# Gateway / Telegram delivery stalls

Symptom: Telegram (or other platform) stops getting replies, a CLI/TUI `/handoff` "hangs", background-process or async-delegation notifications never arrive.

## Procedure

1. **Is the gateway process alive?** `hermes gateway status`.
   - `✗ No gateway process detected` = dead gateway; go to step 4.
   - Do not trust `$HERMES_HOME/gateway_state.json`: it keeps `gateway_state: running` and the old PID after a hard crash. Its `updated_at` is roughly the last heartbeat, so it dates the death.
2. **Find when it stopped.** Tail `$HERMES_HOME/logs/gateway.log` (last `Sending response` / `inbound message`) and `logs/agent.log` for the gap. A hard kill leaves no `gateway.exit_clean` entry in `logs/gateway-exit-diag.log` and no traceback. Check `logs/tui_gateway_crash.log` (TUI child exit codes, thread exceptions such as `WinError 1450` resource exhaustion) and `logs/gateway-stdio.log`.
3. **Handoff specifically:** the queue is `state.db` → `sessions.handoff_state` (`pending` → `running` → `completed`/`failed`, plus `handoff_platform`, `handoff_error`). Query with the venv python:
   ```bash
   cd "$HERMES_HOME" && hermes-agent/venv/Scripts/python.exe -c "import sqlite3;c=sqlite3.connect('state.db');print(list(c.execute(\"select id,title,handoff_state,handoff_error from sessions where handoff_state is not null order by started_at desc limit 5\")))"
   ```
   No `pending`/`running` row = the handoff was never queued, so there is nothing to unstick: re-issue `/handoff` after the gateway is up. Only the gateway's watcher claims rows, so a dead gateway leaves them `pending` forever.
4. **Restart:** `hermes gateway start`, wait ~25 s, then `hermes gateway status` and look for `✓ telegram connected` in `gateway.log`.
5. **Verify delivery in the log, not by assumption.** On startup the gateway redelivers queued finals (`Redelivered recovered final response`) and injects finished background work (`ASYNC DELEGATION BATCH COMPLETE`, watch-pattern notifications). Wait for `response ready` + `Sending response` to the chat id before reporting success.

## Report

Cause (dead process + death time), restart evidence, what was redelivered, and whether the user must re-run `/handoff`. A guessed root cause for the crash (e.g. resource exhaustion) is a hypothesis; say so.
