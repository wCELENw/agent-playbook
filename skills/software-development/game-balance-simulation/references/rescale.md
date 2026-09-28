# Global stat rescale ("апнуть показатели")

Use when the owner wants base numbers bigger (e.g. ×2) for a wider balancing window.

## Steps

1. **History first.** `git log --oneline --all -- '*scale*'` and grep commits for `scale`/`×2`.
   A previous rescale may exist (e.g. a one-shot `tools/sim/src/scale-x2.ts` transform).
   `git show --stat <commit>` tells which content files it touched; diff `attributes.yaml`
   to see which stats doubled.
2. **Classify every stat**: flat pools (HP, barrier, flat armor, stamina, mana), flat damage
   (weapon min/max, monster damage, technique flat parts), resource costs (technique stamina/
   mana cost), flat regen, flat gear/buff/cast adds — scale. Shares and chances (resists,
   evasion %, crit, regen as share of max, stance cuts) — do not touch.
   A rescale that doubles HP/damage but not stamina/mana leaves resource pools on the old
   scale: one potion or attribute point then weighs 3–5 % and costs stay coarse.
3. **Show numbers, then fork.** Dump derived stats of reference dolls at the key levels
   (L1 grey, L15 blue) with the engine's own formula, plus monster base/per-level, and give
   the owner options:
   - neutral ×2 of everything flat (both sides, costs included) — fight unchanged, scale wider;
   - player base only (HP/armor/pools) — player much tougher, monsters refit in the balance run;
   - finish the skipped pools only (stamina/mana + costs).
   Recommendation first; never pick silently.
4. Record the owner's choice in the decisions file and commit it, then hand the transform to
   an engine worker (Opus high) in its own worktree: extend the script, run it ONCE (a second
   run doubles again), commit script + result, regenerate calculator data (`gear.json`, page),
   update fixed-number test expectations only (×2, logic untouched), full tests on the strong
   host, smoke A/B on the same seeds before/after (±10 pp = noise), doll table before/after.
5. **Sources checklist — every flat source scales, not only the base.** Attribute base and
   per point; gear per level, armor types, shield/offhand, set piece stats; cast/buff flat
   `add` (crafted, auras, red/seasonal, sign) including `per_level`; elite affixes;
   technique/modulator damage, heal, barrier, `restore` amounts; status ticks; monster stats
   and per level; the monster proposal JSON and the design model JSON. Regen stored as a
   share of max per turn stays — it doubles in absolute terms with the max. Verify on the
   branch diff: grep every `op: add` on a flat stat and every `restore`/`cost` in `content/`
   and confirm each line appears among the diff's `+` lines; the owner asks explicitly
   whether flat bonus sources were doubled — answer with diff examples per source.

6. **Report caveats honestly.** `sim:quick` hashes the run name into the seed, so "before" and
   "after" runs are not paired: compare as two samples against the noise band. Integer rounding
   (regen `round(max × share)`, costs after a `mul` modulator) gets finer on the bigger scale — a
   small shift, mention it. List pools the decision did not name (e.g. grace) and ask instead of
   scaling them.

## Why neutral scaling is neutral

Armor mitigation `armor / (armor + armor_k × hit)` is scale-invariant: doubling armor and hit
together keeps the cut. Doubling armor alone (without damage) raises the cut — that is a
balance change, not a rescale. Integer rounding (`round(max × share)` regen) drifts slightly
in the player's favour on long fights.

## Dumping derived doll stats

Temporary script next to the simulator (e.g. `tools/sim/src/dump-*.ts`): load the default
content the way the sim does, call the engine's own derive-stats function per reference build
with buffs empty, print JSON. Run it inside the project's tool container, e.g.

```
docker compose run --rm --no-deps tools sh -c "pnpm install --frozen-lockfile >/dev/null 2>&1; cd tools/sim && pnpm exec tsx src/dump-stats.ts" > "$TMPDIR/dump.json"
```

Use the default compose project (its node_modules volume is populated) or run
`pnpm install` first in a fresh one; `npx tsx` pulls tsx from the npm cache and cannot
resolve workspace packages (`ERR_MODULE_NOT_FOUND`). Parse the JSON with `execute_code`,
delete the script afterwards.
