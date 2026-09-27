---
name: game-ui-prototyping
description: "Use when building clickable game-screen HTML prototypes."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [game-design, prototype, html, threejs, ui]
    related_skills: [game-design-preproduction, agent-delegation-and-verification, orca-worker-routing]
---

# Game screen prototypes (throwaway HTML)

## When to Use

- The design is on paper and the owner wants "something to look at and touch".
- Typical screens: battle, character or paper doll, main world screen.
- Not for real engine code: once stage plans exist, follow the repo rulebook.

The prototypes show accepted design decisions. They are not stage-1 code.

## Procedure

1. **Shared assets first (coordinator does this).** Create `prototypes/shared/`:
   - `tokens.css`: palette and fonts from the GDD UI section.
   - `ref/`: reference art from the lore project. Downscale it with PIL to 1400 px JPEG
     q82, because the source PNGs are about 2.5 MB each. Add `SOURCE.md` with the origin
     commit and a table of files.
   - `vendor/`: third-party libraries as local files, plus a README line with the source
     URL and the license.
   Commit this together with the cards.
2. **One card and one worker per screen**, in parallel in the same worktree. Each worker
   owns only its own `prototypes/<screen>/` folder. Roles that worked: battle scene with
   three.js = 3d-developer on Opus high; UI screens = ui-developer on Opus low.
3. **Spec: one shared block pasted into every worker spec.** It carries the rules below.
4. **Acceptance.**
   - Look at each `screenshot.png` with vision.
   - Run any self-test the worker shipped (`node <x>.test.js`).
   - Open the page in the browser the owner actually uses (in Orca: `orca tab create
     --url file:///...`, then `orca eval`, then `orca reload`), not only in headless Edge.
5. **Report** the absolute path to each `index.html` and what each page lets the owner do.

## Spec rules (always)

- No build step and no npm. Pages are served to the owner over the tailnet static server
  (project rulebook port), so local ES modules and an import map pointing at **local**
  vendor files are fine (needed for GLTFLoader/SkeletonUtils). Never a CDN. Pages that must
  also open by double-click over `file://` keep classic `<script src>` only.
- Every page has a collapsible "About this prototype" panel. It lists what the screen shows,
  the design decision behind each element with `docs/...:line`, and what is a stub.
- Show numbers that still wait for balance with their pending-balance label. Mark anything
  not in the docs as a stub. Never invent mechanics.
- The latest owner decisions (the dated review section of the open-questions doc) override
  older design docs and the GDD. Say so in the spec.
- Visual direction comes from the owner's lore project art, not invented. Painterly dark
  art is used as backgrounds, portraits and item crops. Fancy graphics are not needed; clarity is.
- The worker checks its page with a headless Edge screenshot and commits it as
  `screenshot.png`:
  `msedge.exe --headless=new --disable-gpu --window-size=1600,900 --screenshot=<png> file:///.../index.html`
- Commit only the worker's own folder: `git commit -m ... -- prototypes/<screen>`.

## Pitfalls

- **Serve prototypes with caching off.** Plain `python -m http.server` lets the browser
  reuse a stale `index.html` after a merge; when a merge removes or renames an asset (e.g.
  `three.min.js` replaced by modules) the owner sees the old page's error while curl shows
  the new one. Use a tiny `SimpleHTTPRequestHandler` subclass adding
  `Cache-Control: no-cache` (e.g. a project-local `tools/serve_nocache.py`), and after such a
  merge tell the owner Ctrl+F5 once. Verify in a real browser tab, not only curl.
- **Real 3D models in a prototype scene** (glb from the asset pipeline): load each glb once,
  clone per unit with `SkeletonUtils.clone` + per-unit materials, one `MODELS` table
  "unit type → glb, scale, weapon", keep the old primitive until load and as fallback,
  borrow missing clips from another rig on the same skeleton, fake hit/death (tint +
  knockback, fall + fade) when clips are absent, one shadow-casting light, pixelRatio ≤ 2,
  instanced grass/rocks/trees. Reference glb files by relative path, never copy them. Ask
  the worker for a list of model defects it noticed — it seeds the 3D fix backlog.
- **Shared top menu + cross-links.** One `prototypes/shared/nav.js` (self-injecting, sticky,
  highlights the current page) included by every page, including build-script outputs (edit
  the template, not only the built `index.html`). A new page is not done until it is in the
  menu. Research documents get a registry (`docs/research-index.yaml`) and a generated
  reader page so studies do not get lost.
- **Bundle 3D libraries locally.** Keep three.js under `prototypes/**/vendor/` (UMD r159 for
  classic-script pages, ES modules for model-loading scenes). Why: with an
  import map to a CDN, a failed download kills the whole module silently. The HTML
  overlays still render, so the owner sees labels with no 3D and no error.
- **Put the fallback message outside the code that can fail.** Check `if (!window.THREE)`
  in a plain script and show a message on the field. A try/catch inside the same module
  never runs when the module import itself fails.
- **Headless Edge proves little about the owner's browser.** Both headless Edge and the
  Orca tab can render fine while the owner's window does not. When the owner reports a
  blank scene, ask for the on-field message text. Remove the network dependency before
  you investigate GPU or WebGL.
- `orca screenshot` saves nothing without `--json`. With `--json` the image arrives as a
  base64 string: decode it to PNG. In git-bash `$TMPDIR` is `%LOCALAPPDATA%\Temp`, not the
  Hermes scratch dir. Pass that path to vision.
