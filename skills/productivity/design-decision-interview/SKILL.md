---
name: design-decision-interview
description: "Use when closing open design questions one by one."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [design, decisions, open-questions, clarify, gdd]
    related_skills: [game-design-preproduction]
---

# Design decision interview

## When to Use

- User asks to go through open questions / forks "по одному" or "давай дальше по
  вопросам", or to detail a subsystem (combat, economy) fork by fork.
- Not for writing the initial docs: that is `game-design-preproduction`.

Class: a project has a doc of open questions / forks (`docs/open-questions.md`,
sub-forks like `C1..Cn` inside a design doc), and the user wants to go through them
"по одному". Deliverable: every answered fork written into the docs with its
consequences, downstream docs in sync, one commit per pass.

## User standards (always)

- One fork per `clarify` call. 2–4 choices, recommended first. Question text:
  the trade-off and the recommendation in 3–5 short sentences, in Russian.
  Exception: when one custom answer spawns several INDEPENDENT consequences (new MVP
  boundary, fate of an old mechanic, time target, re-check of an earlier decision),
  batch them as separate questions in ONE `clarify` call — the user answers all at once.
- Large layouts (unlock table per level, per-zone lists): go segment by segment
  (e.g. 1–15, 16–30, 31–50), one question per segment. Build each segment draft from
  already recorded decisions, list it as bullets in the question, first choice "accept
  as is". The user rejected "I draft the whole table, you edit it".
- Plain words for the owner. A question built on jargon or bundled numbers (sim targets,
  p90, TTK, "layers AP → damage") gets the reply "детальнее, понятными словами". Split it:
  one question per target, each opening with what the term means in play terms ("ход" =
  player spends AP and presses end turn), why it matters, the known risk, then 2–3
  concrete number options with a short gloss ("быстрая рутинная охота"). The owner is the
  one who sets targets; the model never picks them.
  Forks copied from a worker's options doc fail the same way: the doc's own entity names
  ("Источник", "Катализатор", "чистый ×1,15 против двойного") are undefined for the owner
  and come back as "не понимаю вопрос". Rewrite every such fork before asking: one sentence
  what the thing is in play, one concrete example with a reference build, then the options.
  An answer to one fork can remove the premise of its neighbours (no per-damage-type boost
  kills the mono/hybrid question); re-read the pending forks after each answer and drop or
  re-word the voided ones.
  The same holds for words from the design doc you work from ("склянка" for any consumable
  buff item): the owner asks "что в твоём понимании X?". Name the thing by its role in the
  owner's own terms ("предмет крафтового каста") or define it in one clause the first time.
- `clarify` timed out (owner away): record the answers that arrived, mark the rest
  "ещё не выбраны — спросить перед <card/wave that needs them>", and keep going with work
  those answers do not block. Re-ask later in the same plain wording. On Telegram a
  re-ask as plain text with numbered options works (owner replies "вопрос 8 ответ 1").
- Keep a live list of pending owner questions and re-ask them as a `clarify` on the owner's
  NEXT message, not as prose buried in a status report: worker notifications and repeats
  arrive in between, and a question mentioned only in a summary gets lost (the owner has to
  scroll back and ask what fell through). "Хочу пройти по одному" as an answer = the very
  next action is a `clarify` with one question per item (up to 5 in one call is fine), each
  with the review's variants re-worded plainly, recommended first.
- An answer given as a reply to an expired `clarify` message counts as that question's
  answer: record it verbatim-plus-gist, then ask the next pending question immediately.
- Forks from a worker-written review doc (damage types, world map): append the owner's
  answers as a protocol section at the end of that doc ("## N. Решения владельца", verbatim
  quote + gist per fork) and commit after each batch. When the answers contradict the doc body
  (zones, stage split, scope), relaunch the same role worker to rework the body against that
  section, keeping the section itself untouched; merge the doc only after the rework. Owner
  follow-ups that arrive while that worker runs go to the worker (`orca terminal send`), not as
  your own commit to the same file.
- The owner answers sub-questions of a design review with remarks outside the options
  ("PvP-локации — исключение, а мирные с межфракционными группами"). Treat such a remark as a
  decision that closes the matching fork and re-check every other section of the doc it breaks.
- Number the questions of a pass ("Вопрос 3 из 9") so a short reply maps to one question.
- The user often answers with an own model instead of an option. Record that model
  as given; never bend it back toward the recommendation.
- Order: P0, then P1, then P2. Small related P2 questions may share one question.
- Before offering options on a contradiction, check whether the doc merged separate
  systems under one word (relic slot vs. Mk tier line vs. top rarity). Options that fuse
  them get rejected wholesale. First ask what each term means, then ask only the gaps
  the user's own model leaves.
- `clarify` takes at most 5 questions per call. A batch of 6+ independent gaps: send 5,
  then the rest together with any follow-up spawned by the first answers.
- The user often turns a small gap into a big own model (new entity, new system). Record
  it, log the design work as "отдельный разбор", and flag in the report every answer that
  grew MVP (new combat entity, real-time map) as scope risk.
- Final report: "question / decision" list (a table only where the channel renders
  tables; on Telegram use bullets), then a short list of decisions that grew MVP scope or
  created risk (perf, legal, content volume, one slot budget overloaded by another
  system), then what is left and one offered next topic. No process replay.
- Pick the offered next topic by grepping the decisions doc first: an "отдельный разбор"
  marker may already be closed by a later block ("закрыт", "Заменяет"), and offering a
  closed topic costs a round-trip and a correction. Best candidate: a gap the decision just
  recorded opened (a property keyed on rarity -> where does rarity come from -> does the
  sibling entity without that property still gain from rarity). When decisions without
  propagation pile up (several R-blocks queued in one doc-keeper card), offer running that
  card instead of a new topic.
- "Короткое \"давай дальше\"" = ask the offered next topic immediately, no recap.

## Procedure

0. Resume ("продолжи где остановились"): `session_search` with no args to find the last
   project session, then read the project handoff file (`docs/STATUS.md`) and the open
   fork's section plus its research doc. Ask the next fork immediately; no recap first.
   Status questions ("что в каком статусе", "получилось что-то?"): run `git log` and
   `ls tasks/open` first; another session may have closed cards and queued new ones since
   `STATUS.md` was written, so STATUS alone is stale.
   Post-prototype gap pass: harvest forks from the prototypes' "Открыто" / "Заглушки" /
   "Не показано" panels (strip HTML, grep those words) plus `заглушк` comments in their JS;
   keep only rules missing from the design docs, drop pure `[Б]` numbers. Record answers in
   a new decisions-doc section ("Пробелы после прототипов", ids R1..Rn).
   Planning question ("что открыто / что всплыло / что решить до / что в фон"): answer in
   exactly those four groups, each item with `file:line`; mark which open items block the
   balance simulator (decide now) versus MVP-irrelevant tails (16+ levels, premium).
   Proposal doc with per-section "Вопросы владельцу" (variants A1/A2/A3, B1/B2/B3): ask
   the section's framework question ALONE first, because the owner often answers it
   with an own model that reshapes the rest. Then re-word the remaining questions of
   that section against that model and batch them (max 5) in one `clarify`. Record the
   section as a new `Rk-разбор` block, and set the proposal's status line to "разобран;
   решения — Rk, они приоритетнее текста ниже", so doc-keeper treats it as reference only.
   Separate reviews ("отдельный разбор") spawned by gap answers or deferred by an earlier
   decision ("механика — глубже отдельно"): when the user says "по порядку", run them in
   the listed order. Before asking, grep the topic's current GDD/design text AND every
   recorded decision that already constrains it (e.g. "each upgrade step adds a socket"
   fixes the socket count), and state those givens in the first question so it asks only
   the real gap. Ask the topic's framework question ALONE first (the owner often answers
   with an own model), then batch 3–5 independent sub-questions re-worded against that
   model, then one batch of follow-ups for ambiguous answers.
   A mechanic ported from a sibling project (e.g. an equipment-slot system): `git pull`
   and grep that repo's architecture doc for the real parameters (free limit, hard cap,
   soft-limit penalty, theme sets) and offer them as concrete options, not a vague "as in
   the mod". Record each as a `- **Rk-разбор. Title.**` block above one footer line
   that lists what is still open; the final pass rewrites the footer to "закрыты".
1. Re-read the fork's current text before asking, so options reflect earlier
   decisions (a decided timer removes that half of a later question). Forks from a
   review doc (P0/P1/P2) were written before the owner answered the earlier tiers:
   recompute the review's estimates on the new base (e.g. content density from a changed
   hours target) and name the earlier decision it touches in the question text.
   - An option that conflicts with a recorded cap or budget (per-threshold bonus against a
     total cap) gets ONE follow-up: keep the cap or raise it.
   - Review-sourced decisions go into the review section of the decisions doc as
     `- **Pn-k. Title.** Решение: X (date). …`; keep one trailing line "Pn-k — Pn-m не
     разобраны" and shrink it each pass, final pass replaces it with "Ревью закрыто".
2. Ask. On a custom or partial answer ask ONE follow-up that pins the ambiguous part
   (range of what, with or without premium, who loses what) or the direct consequence
   ("no compensation for the attacker" requires HP/mana to persist between fights).
   - Answers in one batch can contradict each other (own model "unique monster cores"
     in one question, "keep the 4 old currencies as cores" in another), and one free-text
     answer can hold two readings ("skills on top of the slots" vs "skills inserted into
     the slots"). Ask a follow-up that reconciles them — offer a split into two kinds
     that satisfies both readings as the first choice; do not pick one reading silently.
   - An own model that reopens a P0 decision (items as the main skill source vs.
     "skills live in the Codex, independent of items"): name the P0 in the follow-up and
     offer "keep P0, new thing layers on top" first; record the result as "уточняет Qn".
   - An answer that leaves a sub-part unstated (sources named, trade not): ask the
     unstated part in the follow-up batch, citing the existing rule it would inherit
     (reputation items always bound).
   - An answer that touches monetization (a reagent sold in the battle pass or premium):
     grep the recorded monetization principles first, record compatibility, and flag
     pay-to-win risk in the question and the final report. Ask ONE follow-up if the answer
     contradicts a recorded principle ("premium without combat power"). If the owner then
     drops the principle or declares the content "a separate track, anything I decide",
     edit the principle line in place ("снято/изменено <id>"), record the separate track,
     flag the risk once in the report, and stop pressing.
   - Two decisions that multiply each other (set bonus only at the lowest part's rarity
     × per-item upgrade chance) are a grind risk: state the multiplied count (5 parts × 4
     steps = 20 rolls) in the next related question and in the report.
3. Stop follow-ups when the user calls it a separate big topic: log it as "отдельный
   разбор" in the doc and move on.
   - Deferred topics the owner names "в тудушку" go into the project's root `TODO.md`: one
     checkbox per topic with a "после <condition>" gate and the aspects the owner named, plus
     a pointer to the decision line. Create the file if missing, link it from `CLAUDE.md` next
     to the task queue, commit right away.
   - A decision that moves work between stages changes the roadmap: say so in the report and
     offer the roadmap edit. Hand it to the next design worker with the rule "dependencies on
     the later stage → question with options, not a silent move".
   - The user may reverse an already recorded decision mid-flow. Edit that decision line
     in place and commit before the next topic; do not append a second rule.
   - The user may defer a segment but slip in one concrete change ("later, but move X
     to level 7"). Record the change, store the unaccepted draft as "черновик,
     отложено", and ask one follow-up if the move crosses the MVP/`[POST]` boundary
     (scope of X inside MVP).
   - An answer that changes a SCALE (level cap, currency, time curve) invalidates every
     number tied to the old scale. Grep all docs for those numbers (`\d+ уровн`,
     `до N уровня`, old caps), re-anchor each bound decision by play time rather than by
     number (old level 3 at 2–3 h becomes the new level reached at 2–3 h), ask the
     re-anchoring as a follow-up, then fix every hit.
   - A newer fork superseding an older question's decision: keep the old text, add one
     line "Заменено Qn (date): …" under it, and update derived docs to the new value.
   - The user may step aside to research a reference game. Commit pending decisions
     first, then follow `references/reference-game-research.md`; keep decided forks
     untouched and bring the conflicts back as new forks.
4. Write the decision right after the answer: replace `Решение: —` with decision,
   date and consequences. Do this between questions in the same turn (the patch call
   can run in parallel with the next `clarify`).
5. Propagate consequences in the same pass: roadmap "Готово, когда" / "Нужны
   решения", GDD MVP scope, CLAUDE.md title/pointers, numbers mirrored in sibling
   design docs. Mark stale GDD sections with a pointer to the authoritative docs
   instead of silently leaving contradictions.
6. Commit after each decided fork or sub-fork (small commits survive interruption).
   If an Orca worker or another session is editing the same repo (`git status` shows
   foreign changes, `orca orchestration worker-list` shows `working`), write ONLY the
   decisions doc and commit with `git commit -- <path>`: a plain `git add -A`/`commit -a`
   sweeps in the worker's half-done edits, and also your own temporary edits (specs renamed
   to move them off a running sim). Check `git show --stat HEAD` after every commit. The running worker never sees decisions made
   after its start; propagation to design docs becomes the next doc-keeper card, queued
   after the current one is accepted. Say this to the user before starting.
   If a doc-keeper card is already queued but not started, extend it instead of adding a
   card: append "Дополнение координатора (date)" naming the new decisions section and
   what to propagate vs leave as "отдельный разбор" link, and state that this is not
   "входы новее" (cards carry a stop-if-inputs-newer rule that would otherwise halt it).
   Commit the card together with the decisions doc.
   Owner questions listed inside a stage plan (architect's `docs/plans/stage-N.md` §"Вопросы
   владельцу"): run the same interview, then insert a "Решения владельца (date) —
   приоритетнее вариантов ниже" block at the top of that section, above the architect's
   original options, so card workers read the decision first. Questions left after a doc
   sync (doc-keeper/architect reports) go into the decisions doc as a new section with
   ids T1..Tn and one shrinking footer line.
7. Finish: count `Решение: —` left, update the doc status line and the handoff file
   (`docs/STATUS.md`: document table status, next steps), commit docs (no push unless
   asked). A multi-part layout gets its own design doc (e.g. `docs/design/progression.md`)
   plus a row in the STATUS table.

## Spec before code

This owner wants an exact written spec before any engine work: concept forks closed, then a
design-doc revision with its own engine section (data schema, formulas, tests that fail
first, acceptance, sim sets), then the owner answers the revision's "Вопросы владельцу", they go
into the decisions doc, and only then the engine worker starts with a spec citing that doc
section plus the new answers. Never start code in parallel with an unfinished spec.
- Placeholder numbers in that spec are implemented as written; the owner's power target
  (e.g. "N packs at level L") goes into the data file header as a balancer target. The engine
  worker never tunes numbers.
- Technical questions from the engine worker that follow from recorded decisions: answer them
  yourself, then tell the owner in one message (question, answer, why, "say so and I'll
  change it"). Escalate only design forks. Conditions needed only to pick sim sets must not
  restrict the player in the game; say so in the answer.
- Owner targets like "holds N packs" are soft: record what success rate N means and how it
  grows with level, not a hard cap.

## Layout and map forks

- Spatial forks (world map, location graph, zone layout) are chosen by picture, not by text:
  the owner asks "сделай визуализации" instead of picking from prose. Deliver one diagram per
  variant (dark theme) plus screenshots sent as MEDIA, then ask the pick. Offer the pictures
  with the first question to skip a round-trip.
- The owner usually picks a variant and modifies it ("A, but the east arc all PvP"). Relaunch
  the design worker on that variant; its spec lists the earlier recorded rules the change
  breaks (level gates, zone counts, stage switches, level bands of moved nodes) and requires
  them as "Вопросы владельцу" with options, never silently resolved.
- Location content rule of this owner: at least 2–3 monster species per location, overlaps
  only between neighbours, shown as a species × location matrix.
- Once the map is final, location key art may start as a parallel track: 16:9 painterly
  backdrop per location, open readable middle band with flat spots for later markers. New art
  family = one target location first, owner approval, then the rest in parallel (project art
  skill). Each location prompt carries, from the map doc:
  - its map neighbours and what of them is visible — a backdrop not tied to its neighbours
    gets rejected;
  - the location's own monsters from the species × location matrix, calm, small-to-medium
    scale — an empty backdrop reads as dead;
  - the function of the place: a safe outpost reads as a real fortification, a spot with an
    NPC gets a mini-outpost, an industrial zone is ruined and unlit;
  - "matte, dry painted surfaces, no wet/glossy sheen, soft painterly edges" plus explicit
    bans on unwanted motifs from the reference images — image_gen otherwise renders surfaces
    wet and copies reference architecture.
- Art review: ONE image per message with its own approve/reject `clarify` ("N/M · name,
  attempt K, neighbours, worker note"), not contact sheets or 5-question batches. The answer
  is usually a free-text Other remark = correction for the next attempt. After the pass,
  launch all second attempts in parallel; a partly liked image goes back as an edit of the
  same image with the kept objects named, not a fresh generation. Keep attempt 1 under
  `assets/<family>/_attempts/<slug>-1.png`.

## Numbers

Balance values are placeholders (`[Б]`). Ask for a base set (base value, cap, carry
limit, cost table) and say that a simulation tunes them later; the user prefers a
base stack for MVP and balancing afterwards.

Balance targets for the simulator:
- Frame difficulty as a curve over **level × gear rarity × number of enemy groups**, not as
  one fixed encounter ("pack of 6: 5–8 turns"). The owner rejects single-encounter targets
  as crude; ask per curve point (early levels any gear; mid level blue gear 1/2/3 packs;
  3+ packs need gold).
- Present every sim/sandbox result as a matrix: rows level + gear rarity, columns
  encounters, cell = win rate, median turns, HP lost, out-of-target cells marked. Put this
  format into the sim, report and sandbox cards.
- Targets are stated **without consumables**; consumables only push odds toward a win.
  Every run goes in two branches, "without / with consumables"; ask a separate target for
  the "with" branch at the key curve points. In this owner's design consumables are a
  must-have: fights without them are meant to be hard, because potions feed crafting
  professions and drain currency. Do not propose "almost safe without potions" targets past
  the early levels. If the owner names a consumable from a later stage, ask which kinds and
  how many per fight, and add them as a bot action now.
- Scenario ladder, always: single pack → elite pack → 2, 3 and more packs in one fight, at
  every curve level. Sim, report and sandbox cards list encounters in this order. Elite pack =
  a standard pack plus ONE elite monster whose aura buffs the plain monsters while it lives;
  affixes never go on every squad.
- A higher-level buff source (commander/boss aura on every pack in the fight) next to a lower
  one (elite aura on its own pack): record the scope of each. When the owner does not yet know
  whether they stack, do not pick: add a `[Б]` switch constant (`sum` | `max`) and have the
  simulator run both variants.
- The owner revises target numbers freely: replace the table row in place, keep one line
  with the previous values, and re-check any temporary floor you set against the new rows
  (a floor above the new mid-level target contradicts the curve).
- Translating words ("почти безопасно", "легко") into numbers is the owner's call: offer
  2–3 numeric sets, record the owner's numbers, mark any gap filled by you as a temporary
  floor until the owner confirms.
- Owner ideas about tooling (a sandbox to tweak numbers/scenarios and run hypotheses
  himself) go into an `idea-` card plus a requirement on the card that builds the base tool
  (everything changes through a spec file, no code edits; README for a non-coder).

## Editing pitfalls

- Docs may be CRLF or LF, even in one repo. Detect per file (`'\r\n' in s`) before
  splicing. Edit in `execute_code` with `newline=''` I/O, `s.count(old)==1`
  asserts, and inserted text converted to `\r\n`; splicing a `\n` block into a CRLF
  file leaves mixed endings. Verify `s.count('\r\n') == s.count('\n')`.
- The `patch` tool can garble neighbouring headings in long Russian markdown. Read the
  section back after a multi-line patch and repair via exact-string replace.
- Locate a fork's decision line by regex over its `### Qn.` section rather than by
  the shared `Решение: —` string, which occurs in every open section.
