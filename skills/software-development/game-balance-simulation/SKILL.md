---
name: game-balance-simulation
description: "Use when planning or running game balance sims."
---

# Game balance simulation

Class: a game project (turn-based combat, deterministic engine) has numbers marked `[Б]`
(pending balance) and a plan with a simulator, experiment specs and a number-entry step.
Project specifics (roles, zones, card numbers) live in the repo `CLAUDE.md` and
`docs/studio/BALANCE.md`; this skill is the order of work and the owner's conventions.

## Owner conventions (always)

- Walk through **all rule and simulation forks with the owner before building or running
  simulations**. Do not start the simulator card just because its dependencies merged.
- Targets are set by the owner and stated **without potions**; every scenario runs both
  with and without potions.
- Escalation order in every sweep: normal pack → elite pack → more packs.
- Undecided rule variants (e.g. elite aura + commander aura: sum vs strongest-only) stay as
  switchable sim options; never pick one silently, report both.
- Forks are closed one question at a time via `clarify`, recommended option first
  (`design-decision-interview`).
- **No number fitting on placeholder builds.** Before fitting to target win rates, the
  character frame must exist and be shown to the owner: stat model (attribute → derived stat
  formulas, non-linearity, thresholds, stat sources by level), skill directions (schools,
  which attributes feed them, board growth), potion/elixir/buff directions, reference builds
  per archetype. Without it, smoke and sensitivity runs are fine (they rank knobs, find engine
  bugs and archetype skews), but fitting and number entry stop. Deliver the frame as a design
  doc + interactive tailnet page (attribute/level sliders with live derived stats vs the
  archetype reference, stat curves with thresholds, skill map, potion matrix, a note under
  every chart); then close its forks one by one and fit on it. Every reference build on the
  page gets a description card, not just a name: role and row, gear, attribute spread per
  level point with why that feed order, board sigils with one line each, belt, strengths/
  weaknesses and matchups, design reason (niche vs neighbours). Page and doc texts in plain
  Russian: no → arrows in prose, no bare attribute abbreviations or internal fork ids («R3»,
  «Ф8»), sigil names taken from the game i18n. Gaps the card writer finds (a strength with
  no sigil behind it, missing row/belt) go to the owner as a fork, never invented. When
  asked "what are the sims
  running on", answer plainly which parts are placeholders (files marked `balance:
  placeholder`, hand-made test builds, gear colour as a multiplier, stand-in potions/buffs).
- **Long buffs (DWAR "обкаст") are part of the baseline build**, not an extra: a character
  without them is noticeably weaker. Every sim build carries at least the minimal crafted buff
  set; at the top level of the stage also the reputation buff. Reports show a separate
  "without buffs" row next to the baseline.

## Procedure

1. **Readiness review first.** Launch the game-designer role (Opus high, docs only, no
   code/YAML) on the MVP docs + what is actually implemented. Deliverable:
   `docs/design/sim-readiness-<date>.md`, first line = owner questions P0–P2, containing:
   - map of mechanics affecting outcome: implemented / placeholder / designed-only / not
     designed, stage it lands, `file:line`; flag what the owner's targets depend on
     (gear tiers, potions, levels, faction resists);
   - per `[Б]` number: which mechanics it depends on, which later stages will force a
     re-balance;
   - separate verdicts for harness / experiments / number entry;
   - every fork with 2–4 options, recommendation first, cost: player-bot model, potion
     modelling, gear-tier stand-ins before items exist, faction resists, horde placement,
     aura stacking, success metrics, fights per point, seeds;
   - 2–3 plan variants with cost/risk.
   It can run in parallel with QA of the previous wave (disjoint zones).
2. **Split the pipeline** — three independent decisions:
   - **Harness** (CLI: spec → JSONL metrics, same engine as the server, all cores). Nearly
     independent of unfinished mechanics — picks up new systems automatically. Worth
     building early: smoke runs catch "no build can win this encounter" and measure
     turns-to-outcome and AI turn time.
   - **Experiment spec + report.** Depends on which mechanics exist.
   - **Final numbers into content.** Premature while the owner's targets reference systems
     not yet built (items/gear colours, belt/potions, progression sigils, faction resist
     numbers, bosses/pets) — numbers fitted now get re-tuned. Propose moving it after the
     stage that brings those systems, or a design block before it.
3. **Close forks with the owner**, then adjust the stage plan, then launch the harness.
4. **Size the package before generating specs** (owner picks, clarify with options):
   - A **cell** = one line of the report: build × level × encounter × buff kit × potions ×
     (weapon, armor…). Budgets are always **fights per cell**, never "N per run split across
     cells": the owner reads "80k per run" as a big number per variant, and splitting it over
     180 cells silently gives ~450 fights each. When the owner quotes a total, restate it as
     per-cell and total fights before relaying to a worker.
   - Precision of a win rate (95 %): 330 fights ±5 pp, 1000 ±3 pp, 2000 ±2 pp, 60k ±0.4 pp.
     Offer 1000–2000 per cell; cut the number of variant axes (e.g. 3 buff kits in the big
     weapon track, the rest in a separate buff track) instead of fights per cell.
   - Estimate time as total fights ÷ measured fights/s (stage-2 reference: 200–490/s on 12
     threads, slower at higher levels; extreme cases 1×5–20 packs with turn_limit 100 far
     slower — measure in the smoke run). Give the owner a table per track and per budget.
     Put a 1.5–2× margin on the smoke estimate: 10-fight smoke cells miss long high-level
     fights and thread contention, so a full weapon spec ran 34–43 min against a 22 min
     estimate. Re-estimate after the first full spec finishes and tell the owner the new ETA.
   - Every track runs on **every** reference build (all archetypes + hybrid), not a sample;
     weapon tracks cover every level point from the first weapon level up, with all other
     branches (buff kits, potions, armor/offhand) crossed.
   - Make fights-per-cell a generator parameter (one command regenerates the package), write
     measured speed and per-track time into the package README, order the most important
     track first in the run script.
5. **Before the package starts**, bring it in line with the latest content, or the night's
   numbers are stale on arrival:
   - merge every content/engine branch the package tests (new techniques, modifiers), then
     regenerate boards → builds → specs with the generators and run the full check;
   - the player bot (`ai/policy.ts`) must value every new effect kind (ally heal, barrier,
     ward status, mana/stamina restore, new target/reach fields). A bot that ignores them
     under-rates support/caster archetypes; if it is not done, flag those archetypes'
     numbers as understated in the report.
6. **Runs**: scripts only (no LLM watcher), coarse grid → narrow around target, exit code
   catches crashes; morning summary one line to Telegram; anomalies flagged by script. Heavy
   packages go to the stronger machine the owner allowed (see memory for hosts); keep the
   coordinator host for checks — its RAM is small, one docker compose at a time.
   - **Prepare the remote host while the owner is awake**: copy the repo (`git bundle
     create <native scratch path> master`, `scp`, `git clone -b master <bundle>`, copy
     `.env.example` to `.env`) and confirm `docker info` answers there. Commands that delete
     folders need owner approval and a dead Docker Desktop may need a manual start in the
     owner's desktop session, so an overnight offload set up after the owner sleeps stalls.
     Pass the bundle a native Windows path, not `$TMPDIR`: MSYS maps it to `/tmp`, which
     `scp` cannot find.
   - **Thread cap = 80 % rule (global rule 13), stated per host in threads, never derived from
     the logical count alone**: minipc 12, powerpc-1 12 (12 physical cores, 8 of 20 threads are
     E-cores; more only heats the owner's desk machine). Sum over all runs on a host stays in
     the cap. Quote the host's core/thread numbers from a fresh `Win32_Processor` check when
     the owner asks.
   - **One runner per host.** Background runs started over SSH (`remote.sh bg`) survive a
     stop of the parent shell. Before any (re)launch list `docker ps` AND processes whose
     command line contains `run-stage`/`--threads`; kill both the `sh`/`docker` processes and
     the containers, then confirm zero before starting. Stacked runners silently push the
     host to 100 % and throttle every run.
   - Docker over SSH on a Windows host fails `error getting credentials ... logon session does
     not exist` (wincred/desktop helper needs the desktop session). Fix once: a no-op
     credential helper `docker-credential-anon.cmd` (`list` prints `{}`, `get` exits 1) in a
     PATH dir and `"credsStore": "anon"` in `~/.docker/config.json` (back it up first); write
     the .cmd locally and `scp` it — backticks/newlines inside `ssh "..."` get mangled by
     bash. Verify with `docker pull hello-world` over SSH.
   - Never claim one host is N× faster until the same spec finished on both; give measured
     per-spec minutes, otherwise say "not measured yet" and when it will be. Reference at 12
     threads, 1000 fights/cell weapon spec: minipc 34–49 min, powerpc-1 21–24 min.
   - Before relaunching a spec that "may have been killed", read the host's runner log and
     the `balance/runs` listing: it may already have finished. A duplicate run wastes an hour
     of the owner's machine.
   - Copy finished `balance/runs/*` out of a worktree before `git worktree remove/prune`;
     gitignored run output is deleted with the folder.
   - Host CPU: before a long package check the active power plan (`powercfg /getactivescheme`,
     `PROCTHROTTLEMAX`, `PERFBOOSTMODE`) and the live `ProcessorFrequency` under load — a
     quiet plan with max state <100 % silently disables boost. Do not change the owner's plan
     on your own: audit (where the plan came from), report the measured frequency and a
     realistic gain, and switch only on explicit request. For that keep a separate "max
     performance" plan (`powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61`, min/max
     state 100, boost Aggressive, EPP 0) and verify by frequency + a short CPU benchmark A/B.
     A mini-PC stays near base clock on all cores anyway (power/thermal limit): expect ~10–30 %,
     not multiples; further gain needs PPT limits (RyzenAdj) — owner decision (noise/heat).
   - While a package runs on the small coordinator host, worker specs say "no Docker
     checks; list what is not run" (local `tsc`/`vitest` of one package is fine): a worker's
     full `pnpm test` in Docker next to a 12-thread sim runs RAM to <1 GB and gets killed.
     The coordinator runs the full check of each worker branch sequentially after the
     package, and merges only after it is green.
   - To move queued specs off a running sequential runner, rename their YAML files (e.g.
     suffix `.pc`); the loop then fails to find them and skips them. This only works for specs
     that have not started — check which spec is running first (`docker ps`, newest log).
     Run the moved specs on the other host, or rename them back and rerun them locally if
     that host is not ready.
   - Rerun leftover specs on the SAME engine commit as the finished part (detached worktree
     `git worktree add --detach <path> <commit>`, copy `.env`), so tracks stay comparable
     while master moves on. A fresh worktree needs, before the runner: `mkdir -p
     balance/runs` (gitignored, the log redirect fails without it) and one `docker compose
     run --rm --no-deps tools sh -c "pnpm install --frozen-lockfile && pnpm content:build"`
     (otherwise every spec exits 1 in 2 s with `ERR_MODULE_NOT_FOUND @<project>/content`).
     A spec that exits in seconds is a setup failure: read its log before reporting ETA.
   - Report finished tracks without waiting for the rest: a `delegate_task` aggregator reads
     JSONL (streamed in Python), writes `balance/reports/<stage>-partial.md` + `.json` with
     class × weapon, level curve, potion delta, buff sensitivity (p.p. per +10 % power), top 5
     problems with file + numbers + first test, and a caveats section (missing tracks, old bot,
     rejected kits). Commit it and send the file to the owner.
   - Merge gate for a worker branch when the full check shows Biome errors: run Biome on the
     branch's changed files and on master; equal counts on master = pre-existing, not a
     blocker — say so to the owner and merge on green tests/typecheck/content build.
7. **Calculator sync.** After a content wave that adds techniques or sigils, check that every
   board id in `character-frame.json` has an i18n name and a board note, and that the
   school × role table matches the new content. Do this in the same wave; the page lags
   content otherwise and the owner sees raw ids. Offer an interactive skill-board page
   (drag sigils, live link-rule check, damage/mana/cooldown totals, load reference boards)
   next to the calculator, sharing `calc.cjs`.

## Pitfalls

- Smoke results on placeholder numbers (0% win on some pack) are data for the review, not
  a bug to fix in content before the forks are closed.
- Every engine/AI card that can change monster output (action count, AP spending, special
  choice) must report win rate on the anchor encounter before/after (same seeds, ~1000 fights,
  each bot profile). A literal card reading ("monsters spend all remaining AP") can multiply
  baseline attacks and drop wins to 0% — resolve such forks so the baseline is unchanged and
  only the modifier (e.g. bonus AP of "fast") adds actions; tell the owner with the numbers.
- A new mechanic that shifts resources over a fight (in-battle regen, buffs, new modifiers)
  gets the same before/after report on the anchor encounter; ask the worker for variants that
  isolate each part (e.g. HP-only vs mana/stamina-only regen, monsters on/off) so the owner
  sees which part moves win rate and duration.
- Simulator/harness tests must not depend on content balance: a test asserting "aborted by
  turn limit" breaks as soon as monster damage grows, and a fixture that appends a content
  section (e.g. `pack_tiers`) breaks once content ships that section itself (duplicate YAML key).
  Use a limit no side can finish in (turn_limit 1), read the real content section, and build the
  "section missing" case by stripping it from a temp copy. When a content card turns such a test
  red, fix the test, never weaken the numbers.
- Owner watches long runs live on a tailnet page (own port, e.g. 8766). A text-only page
  (tables of files, line counts, raw summaries) is rejected as dull and uninformative: build
  it as a visual analytics UI from the start. Everything is computed automatically from the
  run's input (spec YAML) and output (JSONL), no hand-written conclusions:
  - home: KPI cards per run (type run/sweep, fights, win rate, aborted/crash, duration),
    live run with progress bar + ETA from file growth, the balance worker's terminal panel;
  - run page: spec in plain words (what varied, points, seeds, turn limit, bot); win-rate
    heatmap build × encounter (with/without potions, coloured by the spec target band);
    turns and HP-loss distributions; potion contribution; monster turn time p90;
  - sweep page: dependencies — main effect per knob as a tornado (low vs high, per potion
    branch and per build), line per knob value when >2 values, 2-knob interaction heatmap,
    sortable point table;
  - dynamics: rolling win rate / convergence of a live run; same cells compared across runs.
  - "what was run" in plain words, generated from spec + content (no YAML reading needed):
    player level(s), builds (archetype, key stats/weapon/skills), encounters with monster
    names, counts, tier, level and pack modifiers, bot profile, potions, turn limit, runs per
    cell; for sweeps what each knob means in-game and its low/high values;
  - **every chart gets 1–2 lines under its title**: what it shows, why look at it, how to
    read it and what counts as bad;
  - **automatic post-run analysis by a cheap model**: when a run finishes (summary `.md`
    exists, JSONL stopped growing) the server builds a compact digest (description + the
    same aggregates + target bands; never raw JSONL) and runs headless `claude -p --model
    opus` read-only as the game designer: what was tested, key numbers, target bands hit/
    missed, anomalies/suspected sim bugs, hypotheses, what to run next — numbers only from
    the digest. Output per run to `balance/analysis/<stem>.md` and a newest-first journal
    `balance/analysis/README.md`; shown on the run page (top block), one line on the home
    card, journal link. One analysis at a time, `.err` on failure without retry loops,
    `--no-analyze` flag. Spot-check a few analyses for invented numbers before trusting them.
  Style: "digital" dark theme from the project tokens, monospaced numbers, neon accent,
  hover tooltips; refresh via fetch JSON every 10–15 s, not meta-refresh (no flicker).
  Server: stdlib Python, read-only on the worktree, aggregates cached by (path, mtime, size)
  and a live JSONL read incrementally from a saved offset (files are 40–60 MB). Charts from
  the project dashboard skill's offline lib, no CDN. Build it with a UI worker on a separate
  port and switch `tailscale serve` only after screenshots check out. After restarting the
  server on the live port, confirm the NEW build is served (grep the page for a new asset,
  e.g. `charts.js`): on Windows an orphaned old process can keep the port and answer 200
  with the old page — find it by port owner (`Get-NetTCPConnection -LocalPort`) and stop it. Manual runs from the
  page come later; add only when asked. Markdown reports stay the source of truth.
- Balance worker sends one-line interim numbers to Telegram after the smoke run and after
  sensitivity; forks go into the report with the recommendation first and the worker
  continues on the recommendation instead of waiting.
- When the owner calls a mechanic weak or too narrow (e.g. long buffs), do not retune it in
  the canon doc: a game-designer worker writes an options file — diagnosis with numbers per
  reference build and level vs other power sources and the reference game, 2–3 complete
  models, recommendation, forks list (recommended first). Put each model as a switchable kit
  into the next sim package, so the owner decides with win rates in hand.
  The recommended model is only a recommendation: close its forks before the night package
  if you can. When the owner's answers diverge from the kit already running, say that those
  cells become reference-only, let the other tracks finish, have a worker rebuild the model
  (doc, content, engine, kits), then regenerate and rerun only the buff track.
- Reference-game research for a model (e.g. buffs in sibling browser MMOs) goes to an Orca
  worker `--agent claude --model opus --effort medium` with the project `researcher` profile,
  one worker per reference game, all with the SAME spec shape (owner requirement for a market
  comparison), not to a background `delegate_task`: an hours-long dig outlives the Hermes
  process that owns a delegate child, and the child then dies without writing its file.
  Pre-download owner-named pages and linked item cards yourself into scratch and point the
  worker at them. The spec always covers: reputations by rank, **production professions and
  the effects they craft** (tiers, numeric growth, level gates, resources), every buff line,
  stacking groups, an effect taxonomy (kind, layer, flat/%), a candidates table in the MVP
  table's columns and a completeness section. Depth rules for FULL dig: every line of the
  system from player summary guides first, then card numbers, a full mid-level combo table, a
  "not found" list; put the owner's named items and known guide URLs in the goal. Map the
  result onto the owner's recorded decisions (decisions win over reference numbers).
  Spot-checking two cited cards proves numbers, not completeness: before forwarding, compare
  the report's lines with a summary guide's list. The research ends in ONE proposal table of
  the target MVP effect system (rows = effect families; layer, what it gives flat/%, tiers,
  duration, conflict, source, reference, empty "owner decision" column; rows outside recorded
  decisions marked as proposals) that the owner approves line by line.
  Buff research alone is not enough for sizing: pair it with an **items/sets uplift study**
  per reference game (item stats by level and rarity, set bonuses per piece count,
  upgrades/runes, typical vs top doll per reference level, one table "power source × level ×
  gain" with an explicit common metric) so buff strength is judged against gear. Rare items
  (reputation, valor/heroism, quests, events, arenas, clan, donate, rare jewellery, "red"
  boosts) get their own section and a "beyond baseline" column: shown as the ceiling, never
  balanced for. Every finished study goes into the project's research registry and page.
- Aura/affix modifiers with a multiplicative op on stats that are 0 for monsters do nothing
  — check op type (`add` vs `inc`) when an aura shows no effect in sims.
