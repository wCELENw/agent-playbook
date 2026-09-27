---
name: game-design-preproduction
description: "Use when planning a new game: refs, GDD, roadmap, docs."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [game-design, gdd, roadmap, preproduction, mmorpg]
    related_skills: [spike, grounded-citations]
---

# Game design preproduction

## When to Use

- User starts a game project and asks for a plan, design doc, open questions or roadmap.
- User gives reference games and/or a lore source project to base the design on.
- Not for implementing game code: once stage docs exist, follow the repo `CLAUDE.md`.

Class: user describes a game idea (often "like game X, lore from my project Y") and wants
a plan, open questions for big forks, and a design doc to follow later. Deliverable is a
set of committed markdown docs, not code. Output: references, GDD, open questions,
roadmap, tech design, CLAUDE.md in the repo.

## User standards (always)

- Docs and chat in Russian; ids in code/content in English.
- All tech runs in Docker (`docker compose`); docs must say so and plan for it from stage 1.
- Art: promo/2D via GPT image generation; 3D via GPT concept sheet then an image-to-3D
  generator and/or Blender on a second PC. See `references/ai-3d-asset-pipeline.md`.
- Visual style and lore come from the user's linked project, not invented.
- Plan split into big stages; each stage is detailed later in `docs/plans/stage-N.md`.
- Never silently decide a fork: put it in open questions with a recommendation.
- Final chat report: short, per-document summary, then the P0 questions with a
  recommendation each, then one offered next step. No process replay.

## Procedure

1. **Locate the repo.** Look under `~/orca/projects/<Name>` (desktop shortcuts may point
   there). Check `git status`/`git log` before writing.
2. **Read the source lore project fresh.** `git clone --depth 1 <github url>` into the
   scratch dir. Do not trust an older local checkout: it may lag GitHub and miss the lore
   files. Read lore bible, art reference, readme styles (extract CSS tokens), view 2–3
   reference images with vision for palette/materials.
3. **Research reference games.** Browser MMOs keep public "library"/"about" sections
   (e.g. `/info/library/index.php?category_id=N`, `library.php?c=N`, `info/?obj=cat&id=N`).
   - Open the index with `browser_exec`, list category links, pick mechanics categories
     (stats, equipment, sockets/runes, reputations, PvP, pets, instances, UI, lore).
   - Loop categories in one call, save `innerText` per category to a workspace JSON
     (one file per site), then trim menus and read in `execute_code`.
   - If `web_extract` returns a stub (< 1–2k chars) on an old site, switch to
     `browser_exec` + `document.body.innerText`.
   - Look at 2–3 official screenshots with vision for UI layout (battle screen,
     character doll).
   - The user may add more reference sites mid-task: keep per-site files so earlier
     research survives the interruption.
4. **Check environment facts** for the tech doc: `docker compose version`, daemon
   state, `nvidia-smi` (self-hosted 3D generators need an NVIDIA GPU). Record them as a
   dated "environment state" note, not as design constraints.
5. **Write docs** (skeletons in `templates/doc-skeletons.md`):
   - `docs/references.md` — per game a table "mechanic / how it works / what we take";
     lore canon summary; 3D tool comparison.
   - `docs/design/gdd.md` — labels `[MVP]`, `[POST]`, `[Qn]` (open question),
     `[Б]` (number pending balance sim). Design pillars first; every system section
     states MVP scope.
   - `docs/open-questions.md` — Qn numbered to match GDD labels; options A/B/C,
     recommendation, what it blocks, priority P0/P1/P2, `Решение: —` line; end with the
     list of P0 needed before stage 1.
   - `docs/roadmap.md` — stages with Цель / tasks / «Готово, когда» / «Нужны решения»;
     ASCII dependency graph; run logic and 3D pilot in parallel; post-MVP table.
   - `docs/tech.md` — architecture, monorepo, deterministic rules package, content as
     YAML + schema, Docker services, asset pipeline, security, tests.
   - `CLAUDE.md` in repo root — short rulebook pointing at the docs (no AGENTS.md copy).
6. **Verify, then commit.** Check sizes (`wc -c`) and grep every written doc for
   `HERMES-CONTEXT-COMPRESSION`: a long `write_file` replayed after context compaction
   can land a truncated stub with that marker instead of the full text. Rewrite any hit.
   Cross-check that every `[Qn]` in the GDD exists in open-questions. Check that paths
   cited in docs exist. Commit docs only; do not push unless asked.

## Design heuristics that worked

- Turn the source lore's alternative endings or ideologies into the playable factions:
  instant conflict with lore justification.
- Map lore locations/tiers (posts, Mk tiers, materials) onto instances, item tiers and
  crafting currencies so every mechanic has a lore reason.
- For "1 vs many" turn-based combat recommend simultaneous rounds on a row grid with
  area patterns; sequential initiative queues stall at 10×10+.
- Classless (PoE-like) = modifier aggregator + skill gems in a character panel +
  reputation perks ("pick 1 of 3"); a big passive tree is post-MVP content cost.
- Flag naming collisions with reference games in the naming question.
