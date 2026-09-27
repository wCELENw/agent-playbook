---
name: browser-page-preview
description: "Use when publishing a result page (report, demo) to tailnet."
---

# Browser page preview for a remote user

Class: anything the user will open in a browser — clickable prototypes, static mockups,
dev builds. The user works remotely (another PC over Tailscale, or Orca remote), so a
page only counts as delivered when it renders there and the user has a working link.

Standing rule in every project: global rules §14 (`~/.agents/GLOBAL_RULES.md`). Worker roles

build and verify the page in their worktree; the coordinator publishes after merge and sends the link.



## Procedure


1. **Build self-contained.** No build step, opens via `file://` and via HTTP:
   - local scripts as classic `<script src>` by default; switch to ES modules + `importmap`
     only when the library needs it (three.js loaders such as `GLTFLoader`/`SkeletonUtils`
     ship only as modules in current releases) — then the page works over HTTP only, not `file://`;
   - vendor libraries into the repo (e.g. three.js modules under one shared `vendor/`) instead
     of loading from a CDN; write source + license next to it;
   - guard the library: `if (!window.THREE) showMessage('...')` — a failed CDN module
     leaves HTML labels on an empty scene with no visible error, because the fallback code
     lived inside the module that never ran;
   - shared tokens/art in `shared/` that page authors link but never edit.
2. **Verify rendering yourself** before reporting:
   - headless Edge: `msedge --headless=new --disable-gpu --window-size=1600,900
     --screenshot=<png> <url>` and look at the PNG; `--dump-dom` + grep stderr for page errors;
   - inside Orca's browser: `orca tab create --url <url>`, `orca eval --expression "..."`
     (probe `window.THREE`, WebGL renderer via `WEBGL_debug_renderer_info`, app state),
     `orca screenshot --format png --json` (base64 in the JSON; decode to a file, write it
     under a path the vision tool can read);
   - run any bundled self-test (`node <x>.test.js`) and report the exit code.
3. **Publish in the tailnet** (standing user rule):
   ```bash
   cd <dir> && python <no-cache server> <port>      # background process, see pitfall on caching
   tailscale serve --bg --http <port> http://127.0.0.1:<port>
   curl -s -o /dev/null -w "%{http_code}" http://<host>.<tailnet>.ts.net:<port>/<page>
   ```
   Check `tailscale status` / `tailscale serve status` first for the host name and ports
   already taken.
4. **Hand over:** one link per page by host name, how to stop
   (`tailscale serve --http=<port> off` + kill the server), and that it does not survive a
   reboot. Record port and rule in the project `CLAUDE.md` so every role publishes new pages.

## Analytic reports (numbers, balance, comparisons, forks)

User preference: any report with numbers goes out as an analytic web page in the tailnet,
not dry text — charts, sortable tables, decision forks as cards with the recommended option
first. The markdown report stays the source of truth; the page is its view.

- Every computed number shows its formula, the substitution and the result (tooltip or
  expandable row, e.g. `база + очки + предметы → 30 + 12 + 4 → 46`) so the owner can check one
  value; data pages share one format module (number locale, signs, units, rarity/school colours,
  a "data as of · source links" header) instead of per-page styling.
- Build with the `chart-dashboard` skill (MIT, github.com/raghuramsirigiri/claude-chart-dashboard,
  path `plugins/chart-dashboard/skills/chart-dashboard/`): zero-dependency SVG charts,
  its report template for narrative reports, its dashboard template for monitoring. Copy it into
  the project's `.claude/skills/chart-dashboard/` (plus LICENSE and a SOURCE note), skip `tests/`.
- Its `charts.css` pulls Google Fonts — harmless offline (fallback font), but do not add CDNs.
- Numbers only from real runs; gaps stay gaps — the skill's own no-invention rules apply.
- Put the page under the already-served prototypes root (`prototypes/reports/<topic>/`) so no
  new port is needed; the worker verifies render via headless Edge `file://`, the coordinator
  publishes after merge (the server serves the main tree, not worktrees) and sends the link.
- Encode the rule in the reporting role's profile (e.g. `game-designer`) so every future report
  ships with a page.

## Live monitors (progress of long jobs)

When the owner wants to watch a running process (sim runs, generation batches), a static page
is wrong — it goes stale and lives in the wrong tree. A text dump of files and counts is also
wrong: the owner rejects it as dull. Ship charts, KPI tiles and derived analytics computed
automatically from each job's input and output files (domain specifics:
`game-balance-simulation`). Mechanics:

- one stdlib `ThreadingHTTPServer` script in the repo (`tools/<name>/dash.py --root <tree>
  --port <p>`), a JSON endpoint + one HTML page that polls it with `fetch` every 10–15 s
  (meta-refresh flickers and resets scroll); dark "digital" theme, monospaced numbers;
- read-only; point `--root` at the worker's worktree so unmerged results show;
- sections in the owner's order: running now → what the worker does → done items with
  counts → conclusions/forks → raw summaries → inputs/specs;
- cap rendered text (large markdown tables) and cache line counts by mtime so a refresh
  stays under ~1 s;
- own port + `tailscale serve`, `curl` 200, headless Edge screenshot, record the start
  command in the project `CLAUDE.md`.

## Browsing project files remotely

The owner may prefer mapping the project folder as a network drive over links to single
files. Share it read-only over SMB and open the firewall only to the tailnet (run as admin):

```powershell
$u=[Security.Principal.WindowsIdentity]::GetCurrent().Name   # machine\user, not a guess
New-SmbShare -Name <Share> -Path <projects root> -ReadAccess $u
New-NetFirewallRule -DisplayName 'SMB from tailnet (<Share>)' -Direction Inbound -Protocol TCP -LocalPort 445 -RemoteAddress 100.64.0.0/10 -Action Allow
```

Pass `-ReadAccess` the account name from `WindowsIdentity`: a hand-typed `host\user` fails
with system error 1332 when the hostname differs from the tailnet name. Hand over
`\\<tailnet host>\<Share>` (fallback `\\100.x\<Share>`), `net use M: ... /persistent:yes`,
the login account, and where the relevant artefacts sit inside the share.

## Pitfalls

- A static server started from the main repo serves only merged files: a page committed in a
  worktree branch is 404 until merged — publish after merge or serve the worktree separately.

- Serve pages with caching disabled (`SimpleHTTPRequestHandler` subclass whose `end_headers`
  adds `Cache-Control: no-cache`; e.g. a project-local `tools/serve_nocache.py`). Plain
  `http.server` sends `Last-Modified` without `Cache-Control`, so browsers heuristically reuse
  the old `index.html` after a merge; the owner then sees errors from removed files. When the
  owner reports an error the served HTML no longer contains, `curl` the page first: stale
  cache is the cause — fix the server headers and ask for one Ctrl+F5.
- Give links by tailnet host name, not by IP: `serve` routes on the Host header, so the
  raw `100.x` address returns 404.
- Use `serve` (tailnet only), never `funnel`, and never modify serve/funnel entries on
  other ports — they belong to other projects.
- When the user reports "labels but no 3D", first check whether the library loaded
  (`typeof window.THREE`) before suspecting WebGL; an external dependency failing
  silently is the cheaper, more likely cause.
- Parallel page workers in one worktree commit only their folder
  (`git commit -m ... -- <folder>`), retrying on `index.lock`.
