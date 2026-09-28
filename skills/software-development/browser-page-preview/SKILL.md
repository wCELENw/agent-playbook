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

## Project knowledge-base hub (shared nav across pages)

When pages accumulate under one prototypes root plus side services (balance monitor on
another port), the owner wants one hub, not a flat row of links:

- One shared nav script for every page and the side services; group links by meaning
  (Game / Balance ▾ / Research / Architecture / Art & 3D) with native dropdowns
  (`<details>` or `:focus-within`), links to other ports built from `location.hostname`.
- Recurring work streams (balance stages, runs, quick checks, analysis journal) go into a
  dropdown with history — every stage/subtype dated, newest first — never only the latest one.
- Every architecture/infrastructure block starts with a "why do I need this" line: which owner
  decision or problem it helps with (e.g. infra = where each job runs and why: load split
  between hosts, heavy checks offload, RAM limits, ports). A block that answers no question
  gets reframed or proposed for removal.
- Registries with many entries (research) get a new / all / archive filter and date sort;
  superseded entries are marked in the registry, not deleted.
- The served root must render the hub (an `index.html` redirect to the main page), never a
  directory listing: the owner opens the bare `host:port/`, sees a file list without the new
  nav and reports "nothing shipped". Acceptance of a hub change = open the exact root URL the
  owner uses in a real browser (browser tool or headless) and check the nav, not only `curl`
  of subpages; then ask for one Ctrl+F5.
- Every page type needs the shared nav, including generated ones (archify diagrams, variant maps):
  add `<script src="../shared/nav.js" defer></script>` before `</body>` and re-add it after every
  regeneration — `archify deliver` rewrites the HTML and drops it. Grep the served tree for pages
  missing the script (`grep -L nav.js`) when adding a new page family.
- Side-service monitors die silently (502): check every hub port with `curl` when touching
  the hub and record the restart command in the project `CLAUDE.md`.

## Visual standard (all owner-facing pages)

One dark theme everywhere, in the project palette (one shared palette CSS
layered by the page styles); no theme switcher (the owner judged it not worth the cost).
Layout, tables and formatting follow the document/report pages (research docs, reports,
calculator) — the owner likes that structure far more than ad-hoc dark pages.
- Recolour by editing the GENERATORS (`build.cjs`/`build.ts`, page templates, chart theme
  JS), then rebuild; hand-editing generated HTML is undone by the next build.
- Keep body text contrast ≥ 4.5:1 and rarity/school/armor colours distinguishable on the panel.
- Acceptance: open 2–3 pages in a real browser and check computed backgrounds (no light
  panels under tables/cards), plus a screenshot.
- Before a site-wide restyle, ask which pages are the model: an owner saying "make it all
  dark" may still prefer the light pages' structure — confirm with one `clarify`.

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

### Image folders (art review)

When the owner asks "where is everything, let me look on my PC", serve the asset folder itself
with a generated `index.html` gallery: dark background, one section per subfolder (current /
previous attempts / local drafts) with counts, `<img loading=lazy>` thumbnails ~420 px, click
opens full size in a new tab, file name as caption. Own free port + `tailscale serve`, `curl`
200 on the page and one image, then a real-browser check that thumbnails load. Tell the owner
the folder path too.

### Comparing variants (before/after)

Owner standard for any set of image variants (refine methods, attempts, seeds): a web page, not
a contact sheet in Telegram (too small to judge). One image full-screen at a time, buttons +
← → / digit keys to switch (same framing, so differences pop), a **before/after curtain** driven
by mouse move over the image (after-image absolutely positioned on top, `clip-path: inset(0 0 0
X%)`, white divider, "было/стало" labels), Z = 100 % size, Space = hide curtain; groups as
labelled button runs; `#index` in the URL. Data in `items.json` next to a copied static viewer,
so a new comparison is one command (a project-local `tools/assets/compare_page.py`). Acceptance:
real browser, all images `naturalWidth > 0`, a synthetic `mouseMoved` changes the clip-path.
Send only the link to Telegram.

### Art review hub (browse, compare, approve from the page)

When image assets pile up, the owner wants one navigable section, not loose comparison pages:

- Structure: nav group "Art" with a dropdown of subtypes → subtype grid of square thumbs with
  human (localized) titles, split into Approved / Not approved blocks, status badge per card →
  detail page per asset: curtain (original vs refine), a button row with EVERY variant of that
  asset (current, refine, extra refine strengths, old attempts, drafts), ← → neighbours, Z, Space,
  breadcrumbs. One data file built by a script from the asset manifest + folder globs; statuses
  and titles live in the manifest.
- New variants must show up in the same detail page without manual steps: the index script globs
  a per-asset variants folder (label = file name), and the page polls its data JSON every ~15 s
  and reloads when the variant list for this asset changes — skip the reload while the comment
  box has text, or the owner loses the typed text.
- Approval from the page: Approve / Rework / Reject + comment (required except for Approve),
  verdict applies to the variant on screen (curtain shown = refine). A tiny stdlib API on its own
  tailnet port (CORS for the pages origin, validates id/path, 400 on bad input) writes the
  manifest + an append-only review log, rebuilds the index, and notifies the coordinator (who
  acts on rework) and the owner. Worker tests with a dry-notify flag and reverts test verdicts.
- Add an `i` button at the right of the review panel with a short list of what a rework comment
  can ask for (refine strength, lights, add/remove objects, composition, mood, use another
  variant as base) and which asks are minutes vs a new frame — the owner asked for it.
- For a strength sweep the owner asks for (e.g. 0.20…0.45 step 0.05), drop the results into the
  asset's variants folder and send the detail-page link, not a separate comparison page.

The owner may ask for "link + login and password": `tailscale serve` has no auth — access is
limited to devices of the owner's tailnet. Say so plainly; offer the SMB share above if a
Windows share is really wanted, and have the owner set the password (never put one in chat).

## Pitfalls

- A static server started from the main repo serves only merged files: a page committed in a
  worktree branch is 404 until merged — publish after merge or serve the worktree separately.

- Serve pages with caching disabled (`SimpleHTTPRequestHandler` subclass whose `end_headers`
  adds `Cache-Control: no-cache`; e.g. a project-local `tools/serve_nocache.py`). Plain
  `http.server` sends `Last-Modified` without `Cache-Control`, so browsers heuristically reuse
  the old `index.html` after a merge; the owner then sees errors from removed files. When the
  owner reports an error the served HTML no longer contains, `curl` the page first: stale
  cache is the cause — fix the server headers and ask for one Ctrl+F5.
- Start page servers detached from any terminal (WMI `Win32_Process Create`, or a logon scheduled
  task); a server launched from a worker's shell or Orca tab dies when that tab closes and the
  port turns 502. Keep a project-local `tools/serve-pages.ps1` plus a logon task for it.
- Under `pythonw` there is no stderr: `http.server`'s default `log_message` raises on every
  request, so the port listens but every request fails (curl 000 / tailnet 502). Override
  `log_message` to `pass` in any server run with `pythonw`.
- Public internet exposure (owner's VPS with domain): proxy VPS→tailnet host with Caddy +
  tailscale, never Funnel. Static prototypes are safe; a live monitor that shows worker
  screens, spawns processes or serves arbitrary docs must stay behind auth or be exported as
  a static snapshot. One VPS IP serves any number of domains/subdomains (Caddy routes by
  Host/SNI, one Let's Encrypt cert each) — put the hub on a subdomain next to existing sites.
- Give links by tailnet host name, not by IP: `serve` routes on the Host header, so the
  raw `100.x` address returns 404.
- Use `serve` (tailnet only), never `funnel`, and never modify serve/funnel entries on
  other ports — they belong to other projects.
- When the user reports "labels but no 3D", first check whether the library loaded
  (`typeof window.THREE`) before suspecting WebGL; an external dependency failing
  silently is the cheaper, more likely cause.
- Parallel page workers in one worktree commit only their folder
  (`git commit -m ... -- <folder>`), retrying on `index.lock`.
