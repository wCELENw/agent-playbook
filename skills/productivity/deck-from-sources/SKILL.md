---
name: deck-from-sources
description: "Use when building a short deck from source files."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [pptx, presentation, slides, workflow, orca]
    related_skills: [powerpoint, orca-worker-routing]
---

# Deck from sources (2–5 slides)

Tools: skill `powerpoint` (python-pptx scripts, render via LibreOffice + pdftoppm). Workers: skill
`orca-worker-routing`. This skill is the order of work and the traps that cost time.

## Layout

```
<work>/requirements.md   brief (slide structure, numbers, colours)
<work>/sources/          every input file
<work>/specs/            one spec per worker
<work>/out/facts.md      claim | OK/MISMATCH/NOT FOUND/ESTIMATE | file, page | quote
<work>/out/style.md      size, fonts, hex colours, card patterns, ref PNGs in out/ref/
<work>/out/deck/         build.py (re-runnable), deck.pptx, render/slide-N.png, report.md
```

## Order

1. **Inventory before anything.** For every source the brief cites, check the file is in `sources/`
   and holds that content (`pdfinfo` pages, `pdftotext | grep -c .`). A cited file that is missing or
   is a different document is the first question to the owner, not a finding after 20 minutes.
2. **In parallel:** fact-check + style extraction (one worker, Opus medium) and web lookup split by
   topic (3–4 Codex Luna workers, one output file each). Web data is optional garnish — the build
   does not wait for it.
3. **Owner decisions before the build:** what to do with NOT FOUND numbers (mark "estimate/draft",
   use as internal inputs, or drop). Ask once, all questions in one `clarify`.
4. **Build once with every input known.** One worker, Opus **medium**, spec says: one render +
   one fix pass, then `worker_done`. Adding inputs mid-build (new source, corrections) restarts its
   render loop — each loop is build → soffice → pdftoppm → look, several minutes.
5. Coordinator looks at the PNGs itself (vision) before handing over.

Measured: high effort + "at least 2 review passes" + a mid-build correction = 25+ min for 3 slides;
the owner found it too slow. Medium + one pass + inputs frozen is the default.

## Traps

- **Image-only PDFs:** `pdftotext` returns empty. Worker must render pages (`pdftoppm -r 70`) and
  read them visually; say so in the spec.
- **Fonts:** brand fonts (Montserrat, corporate faces) are often not installed; LibreOffice renders
  with a wider substitute. Keep the font name in the pptx, note the substitution, check with
  `pdffonts`. The real font usually has more room, not less.
- **LibreOffice headless may write the PDF and never exit** when other soffice instances hang.
  Use a private profile (`-env:UserInstallation=file:///<tmp>/lo-profile`), wait for the PDF, then
  kill the process.
- **Brand colour:** take hex from the official logo SVG, not from the brief or an old deck; they
  drift (brief vs deck vs logo differ by a few units). Report the difference, don't silently pick.
- **Titles:** 36–40 pt titles next to a logo wrap to 3 lines on long headlines — shorten the title
  or drop to 32 pt; let the builder shorten text and move detail to speaker notes.
- **Confidential inputs:** internal figures go to the model provider; keep the work folder outside
  public repos and never copy deck content into skills or playbooks.

## Spec checklist for the builder

Inputs (brief, facts, style, refs) · number rules (source footnote per number, which ones are
"estimate") · design (16:9, fonts, hex, min 14 pt body, footer plate, slide numbers, logo) · outputs
(`build.py`, pptx, PNGs, notes, short report.md) · **iteration limit: one render + one fix pass** ·
acceptance: `pptx_read.py --outline` shows N slides; PNGs without overlaps.
