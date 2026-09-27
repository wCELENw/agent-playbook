---
name: video-transcript-research
description: "Use when asked to watch or analyze a YouTube video."
---

# Video transcript research

Class: the user links a video ("посмотри видео") and wants to know what it shows and what to
adopt. You cannot watch it; the transcript + description + linked repos are the source.

## Procedure

1. **Do not rely on `web_extract` for the video page** — it returns only the opening of the
   transcript (often machine-translated). Use it at most for title/author.
2. **Download subtitles and description**, no video:
   ```bash
   cd "$TMPDIR" && pwd -W   # print the native path: git-bash $TMPDIR may differ from the kernel's
   uvx yt-dlp --skip-download --write-auto-subs --write-subs \
     --sub-langs "ru.*,en.*" --sub-format vtt --write-description -o yt_<id> "<url>"
   ```
   Prefer the `*-orig.vtt` track (original language). A 429 on the second language is fine —
   one track is enough. Read the files from Python by the native path `pwd -W` printed.
3. **Flatten the VTT** in Python: skip header/`-->` lines, strip `<...>` tags, drop
   consecutive duplicate lines (auto-subs repeat every line), keep the last timestamp per line.
4. **Navigate by chapters**: the description usually has `mm:ss` timestamps. Grep the
   flattened text for topic keywords to confirm ranges, then read only the relevant ranges
   in full (plus the cost/summary chapter).
5. **Follow links in the description** (GitHub repos, asset packs) with `web_extract` — they
   hold the real artifacts (sources, file layout, versions) the video only mentions.
6. **Verify claims before adopting**: tools, prices, licenses and hardware needs named in a
   video go stale fast — re-check each with a web search.

## Report shape

- Name the tools/models the author actually used; confirm or correct the user's guess.
- Steps in the author's order, with the author's own mistakes and fixes (the most valuable
  part).
- Cost as stated in the video.
- "What we take" vs "where we differ and why" (the user's budget, hardware, license limits).
  If it feeds a plan, write the analysis to a doc in the project repo and commit; in chat give
  the short version and one decision for the user.
