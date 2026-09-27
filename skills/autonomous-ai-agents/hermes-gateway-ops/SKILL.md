---
name: hermes-gateway-ops
description: "Use when TG delivery stalls or TUI and TG sessions overlap."
---

# Hermes gateway operations (Telegram + TUI side by side)

The owner runs the main coordinator conversation in Telegram (gateway session
`agent:main:telegram:dm:<chat>`) and opens TUI tabs in Orca on the same machine. This skill covers
"TG is stuck / nothing arrived" diagnosis and keeping a TUI tab from interfering with the TG session.

Paths: `$LOCALAPPDATA/hermes` = HERMES_HOME on Windows. Logs in `logs/` (`gateway.log`, `agent.log`,
`errors.log`, `tui_gateway_crash.log`, `gateway-exit-diag.log`), state in `state.db` and
`gateway_state.json`.

## Procedure: "TG is stuck / nothing arrives"

1. `hermes gateway status`. **Do not trust `gateway_state.json`**: after a hard crash it still says
   `"gateway_state":"running"` with a dead PID. Status line `✗ No gateway process detected` is the truth.
2. `tail -n 60 logs/gateway.log` — last `Sending response` / `inbound message` times show when delivery
   stopped. A silent end (no `exit_clean` in `gateway-exit-diag.log`, no traceback) means the process was
   killed; check `tui_gateway_crash.log` for a sibling `child exit ... exitCode=1` at the same minute.
3. Dead gateway: `hermes gateway start`, wait ~25 s, confirm `✓ telegram connected` in `gateway.log`.
   It redelivers recovered final responses and queued async-delegation / background-process
   notifications by itself — do not resend them by hand.
4. Gateway alive but a specific message missing: grep `gateway.log` for `Sending response` /
   `Delivering ... MEDIA` around that time, and `telegram_network` warnings (transient ConnectError that
   self-recovers is normal).
5. A `/handoff` of a TUI session needs a live gateway: the watcher polls `state.db`
   (`sessions.handoff_state`: pending → running → completed/failed). Check the row before claiming a
   handoff hung — no row means it was never requested.

## Rule: one coordinator mailbox, one consumer

A TUI tab and the Telegram coordinator can share the SAME Orca terminal handle (the TG session's
`watch.py` polls `orca orchestration check --terminal <handle>`; Orca then also shows "You have N
orchestration messages" in the TUI tab bound to that Run).

- Before acking anything in a TUI tab, find who coordinates: `run-current`, the TG session's watcher
  (`Get-CimInstance Win32_Process | ? CommandLine -match 'watch\.py'`), and recent TG turns in
  `state.db` (`messages where session_id=<tg session>`).
- If Telegram coordinates: read with `check --peek` / `check --all --json` only. Never `--ack`, never
  `reply`, never ask the owner via TUI `clarify` — ack consumes the delivery and the TG watcher never
  wakes, so worker results and owner decisions silently bypass the coordinator.
- Stale worker `question` (already superseded by later commits/merges) — verify in `git log master`
  and TG history before surfacing it to the owner.
- A decision the owner gave in the TUI must be relayed to the TG session (it does not see TUI
  history); say so explicitly in the reply.
- To move work to Telegram, prefer closing the TUI tab over `/handoff`: handoff re-binds the TG home
  channel to the TUI session and replaces the long-running TG conversation context.

## Pitfalls

- `tasklist //FO CSV` fails under git-bash; use PowerShell `Get-CimInstance Win32_Process` with
  `CommandLine -match '...'` to find `gateway run`, `tui_gateway.entry`, `watch.py` processes.
- `orca orchestration run-show` takes `--id`, not `--run`; `check --ack` requires the delivery id.
- `worker-release` on a dispatch in `release_unknown` whose tab is already gone keeps returning
  "could not be confirmed stopped" — it is bookkeeping residue, not a live process; confirm with
  `orca terminal list` and move on.
