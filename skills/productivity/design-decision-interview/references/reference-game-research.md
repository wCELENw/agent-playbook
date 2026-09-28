# Reference-game mechanic research

Use when a fork needs evidence from a reference game ("как устроены уровни в Y,
сравни с Z"). Deliverable: `docs/research/<game>-<topic>.md`, committed, plus a chat
summary that ends with forks against current decisions. Research public sources; never
describe the mechanic from memory.

## Depth (owner standard)

The owner played these games and rejects sample-based reports at once ("где Сила радуги? где
бафы от репутаций?"). Default is a FULL dig of the system, not a few item cards.

- No depth given in the request: ask one question (overview vs full dig) before collecting;
  no answer = full dig.
- Full dig = every line of the mechanic the community knows, listed first from player
  summary guides (forum topics "максимальный обкаст", "связки", free-server guides, fan
  wikis), THEN each line filled from item cards: effect (stat, flat or %), numbers per tier,
  duration, consumable or reusable, conflict group, source (craft/shop/reputation/clan/premium).
  Summary guide gives completeness, card gives the exact number; starting from cards misses
  whole lines.
- A system that combines into a kit (buffs, build): show one full mid-level combo as a table
  with the total gain.
- Before handing in: list the lines the guides mention, mark covered ones; uncovered go to a
  "Не нашёл" section with where searched.
- Effects are graded per card, not per line: a report that names a line («благословения
  Братства») without every card's stat numbers, tier chain growth, duration, cooldown
  («1 раз за бой», «раз в N дней»), effect group and rank gate is still "поверхностно".
  When the owner points at library pages (e.g. a reputation page), scrape EVERY item card
  linked from them (regex `artikul_id=(\d+)`, fetch each card, 0.3 s throttle, save
  `{id: {source, text}}` JSON in scratch) and hand that dump to the researcher as the start.
  Then iterate the whole category (`page=1..N`) for sibling pages of the same kind.
- Buff/effect research always includes production professions (what each profession
  crafts, recipe tiers and numeric growth, profession level gates, resources, who uses it)
  — the owner treats crafting as the main buff source.
- "Комплексно смотреть на рынок" = the same spec for every reference game (DWAR,
  Троецарствие, Джаггернаут), one file per game, identical candidate-table columns, so the
  coordinator merges them into one table. Write the first spec to a scratch file and derive
  the others by string replacement; steer already-running researchers with any added
  mandatory section.
- Research ends in a proposal table for the owner, not prose: rows = effect families/slots,
  columns № | Семья/слот | Слой | Что даёт (плоско/%) | Ступени и рост ([Б]) | Срок/расход |
  Конфликт | Источник | Референс | Решение владельца (empty). Rows outside recorded owner
  decisions are marked "предложение, вне решений". 12–25 rows.
- Research runner: an Orca Claude worker (`--agent claude --model opus --effort medium`, or the
  model the owner names) with the role profile path in the spec; `delegate_task` is not a route.
- Research worker spec: put the owner's named items, the known
  summary-guide URLs and "aim for 40+ distinct entries" in the goal; a bare "research X in
  games A, B" returns a thin card sample. Spot-check 2–3 numbers against the cards yourself
  (curl + `iconv -f cp1251` works when `web_extract` times out) before forwarding.
- A project can keep this as a role, e.g. `.claude/agents/researcher.md`.

## Procedure

1. Grep `docs/references.md` for the game first: earlier research may list the portal URL
   and category ids.
2. Open the info portal index with `browser_exec`, dump `a` texts + hrefs filtered by the
   portal path. Pick every category that feeds the topic, not only the obvious one. For
   progression: ranks/titles, talents, reputations/seals, professions, item upgrades
   (sharpening, runes, epicness), counters (executions, bestiary), premium, newbie FAQ.
3. Loop the ids in one call and save `document.body.innerText` per page into a workspace
   JSON. Read it in `execute_code`; cut the nav menu by slicing between the last menu item
   and the footer.
4. Icon tables (talents, runes) carry no text. Collect item links per row
   (`a[href*=artifact_info]`) and fetch tooltips for tier I and tier V only: that gives
   effect and range at a fraction of the requests.
5. The newbie FAQ often states the core rule in one line ("stats come only from level and
   items"). Quote such lines: they decide the model.
6. Name the data that is login-only (e.g. XP-per-level table) as not seen.

## Document shape

1. Sources line: portal sections read, date, what is behind login.
2. Core idea in 2–3 sentences: what the level (or system) actually gives.
3. Table of parallel scales: scale / fed by / gives / level gate.
4. Detail of the richest subsystem (e.g. talents: blocks, pick-one, block upgrade, reset).
5. "Why deeper than <other game>" as numbered mechanisms, plus weak spots.
6. "Collisions with our decisions" by Qn: state the conflict, change no decision.

Chat report: same skeleton compressed, then offer to walk the collision forks one by one.

## Portal notes

- No search backend (web_search without key; Google/DDG captcha, Bing returns junk, fandom
  and Reddit behind Cloudflare): open Steam community guides for the app
  (`steamcommunity.com/app/<id>/guides/?searchText=...`, click «Показать центр сообщества»
  on the content gate). Top guides link the official game guide portal; read that.
- Undecember: official guide `guide.floor.line.games/UD/en_US/detail/<id>` (runes: About
  1166916549917300337, Types 1166916574409800978, Cast 1166916576948300323); screenshots on
  `static.pcs.line.games` load in vision_analyze.

- jugger.ru: `https://s1.jugger.ru/info/info/index.php?obj=cat&id=N` (talents 419,
  heroism/ranks 285, FAQ 15, execution 336, rage 273); tooltips
  `/artifact_info.php?artikul_id=N`.
- dwar-b.com / 3kingdoms.ru: library pages `library.php?c=N` / `category_id=N`.
- w2.dwar.ru library category 241 = reputations, one per page
  (`/info/library/?category_id=241&page=N`: 13 Вершители зла, 14 Братство Добродетели,
  34 Орден Триады); served as UTF-8 now — read the charset from the page before decoding.
- DWAR / 3kingdoms / jugger item cards are often cp1251 (check `charset=`): `curl -s -A Mozilla/5.0 <url> | iconv -f
  cp1251 -t utf-8`. DWAR buff summary guides: forum topic `w2.dwar.ru/info/forum/topic.php?id=308323`
  ("благи/обкаст"), `dwar.ru.tilda.ws` (max buff 3–10 lvl with sources). Free server
  Некрономикон: `necronomikon.com/forum.php?c=19&t=N`, `library.php?c=N`.
