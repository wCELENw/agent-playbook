---
name: 3d-asset-generation
description: "Use when making 3D game assets from images."
---

# 3D asset generation (image → mesh → texture → rig → client)

Class: turning concept images into game-ready 3D models (characters, creatures, equipment)
for a web client, on the owner's GPU PC first, a paid service (Tripo) only if local quality
fails. Project specifics (paths, style bible, art skill) live in the repo; this is the order
of work and the owner's conventions.

## Owner conventions (always)

- Local free tools first; buy a subscription only after a side-by-side shows local is not
  good enough. The owner runs the free-tier Tripo baseline himself: send him the 4 split
  RGBA views (background removed, cropped) plus the source sheet in Telegram (MEDIA:), note
  which way the figure faces in the side views, then ask for Tripo's result back (GLB or
  front/side/3/4 screenshots) to use as the reference.
- Characters in **T-pose, empty hands**; weapons, shields, equipment are **separate models**.
  A merged character+weapon mesh deforms and intersects when animated.
- Input is **multi-view**: one image with 4 views in a 2x2 grid (front / left / back / right,
  same scale, flat grey background, no shadow, no labels) so the generator does not invent
  hidden sides. Codex `image_gen` makes it via the project art skill.
- First pass of a new image theme: **lenient acceptance** — accept the first attempt if the
  object is whole and pose/view is roughly right; redo only gross defects (wrong object, item
  in hands, cropped). Margins, background tint, small drift go into the report as one line. A
  strict pixel contract with auto-reject burns all attempts per worker.
- The owner judges by eye and harshly: never present a raw untextured shape as progress
  without saying it is raw; show comparisons, not single results.
- Keep **one cumulative comparison sheet** of every run so far (reference on top, one
  labelled row per run: model + setting + seconds + VRAM + faces), regenerate it after each
  batch and send it, not only per-batch sheets. Telegram shrinks tall images to illegible:
  split at row boundaries into ~2500 px parts, and keep the full PNG plus every per-run
  render in the repo (`assets/3d/<pilot>/cmp/`) where the owner opens them over the network
  share. Build it with PIL from the per-run renders and `*.metrics.json`.
- **Every comparison row starts with the source image the model actually received** (same
  scale as the renders) plus its crop at the same zoom as the head/torso close-up, so the
  owner judges fidelity to the input, not just detail. Make it the default of the compare/
  sheet script, not a per-sheet manual step; the Tripo row uses the same front input.
- Judge shape candidates at two levels: raw mesh and after clean-up/decimation to the game
  budget (e.g. 20k tris for a humanoid). The budget level is what ships, so it decides.

## Procedure

1. **Input images** — two-stage concept pipeline (owner's standing choice):
   - **Draft locally** (ComfyUI on the GPU PC, Z-Image Turbo / SDXL): search pose, silhouette,
     composition over several seeds; pick the best draft per asset.
   - **Finish in Codex** `image_gen`: one Codex worker per image, in parallel; input 1 = the
     draft (keep its pose/silhouette/framing), input 2 = style reference. Codex from scratch
     only when told, or when Codex limits are out (then the local draft is the fallback).
     Codex-only concepts without a draft were judged worse by the owner.
   - Before drafting, check the repo for already approved concepts of the same assets
     (`assets/<kind>/concept/`, git log): approved concepts go straight to image-to-3D.
   - Codex refine spec: background tint and side margins are NOT rejection reasons (rembg cuts
     the background before 3D anyway); reject only wrong object, extra body/cloth, wrong pose.
     A strict pixel contract made every worker burn all 3 attempts on background tone.
   - **Rejected for copying an existing asset's shape** (e.g. a new helmet that reads as the
     old one): the draft carries the flaw, so regenerate from scratch in Codex with an explicit
     "must differ from <file>" line, a new silhouette description, and 3 attempts with
     different silhouettes for the owner to choose; format reference only for framing.
   - Deliver for approval as ONE numbered side-by-side sheet (PIL, all finals in a row) plus a
     `clarify` with one Approve/Reject question per item; the owner often answers later as a
     reply to the sheet ("all but N; fix N like …"). Hand approved items to the 3D worker
     immediately; only rejected ones go back to generation.
   - Single front image + 4-view sheet per asset (the single image is the "1 view"
     baseline). Release and close each worker as soon as it reports.
2. **Split sheet** into 4 crops, cut to silhouette, background removed (rembg), aligned by
   height/centre. **Decide left/right by where the face/nose points, not by grid cell** —
   image models often swap the side views.
3. **Pick the shape model on ONE asset before doing the others.** Run every candidate on the
   same views; pause other assets meanwhile. For each: seconds, VRAM peak, faces (write a
   `<out>.metrics.json`), and renders from identical cameras (front, 3/4, side) plus a
   normals/matcap render so detail is visible without texture. One contact sheet
   "model × view" to the owner per candidate, summary at the end.
4. **Texture, then clean-up/decimate in Blender, then rig and animations** — only after the
   owner picks the shape. Humanoids: auto-rig + animation library; creatures: UniRig.
5. **Preview** in the client stack (three.js page in the tailnet, `browser-page-preview`).
6. Write the workflow doc so the next stage reruns a new asset without setup.

When the owner asks how the pipeline looks end to end, frame it around his four review
points — input image, shape (seed variants sheet), textured model in the viewer, model in
the game scene — with machine steps between them (decimate/UV, texture: view projection
vs generator PBR vs ComfyUI touch-up, rig: shared humanoid skeleton vs per-creature,
animation set, gltf-transform meshopt/KTX2, manifest id+licence, client loads by id).
Weapons skip rig/animation (attached to the hand bone); armour pieces must share the body
skeleton and weights. A modular armour kit must cover the body without gaps: list the slots
top to bottom (helmet, pauldrons, cuirass, gauntlets, thigh/cuisses, greaves, boots) and check
that each piece's edge meets the next; the owner spots a bare thigh between a short cuirass skirt
and a knee-high greave immediately. Mark what exists and what is still missing; no decisions in that answer.

Commit pilot scripts and comparison renders to the worktree branch after each batch:
untracked worker output is the only copy and is lost context when a worker dies.

## Shape models on a 12 GB GPU (RTX 5070 class)

- **Reference = Tripo** (owner's free-tier run on the same views). Every local candidate is
  judged against it in the same camera/light contact sheet. Free tier: single image only
  (multiview is paid) and no export, so the reference is the owner's screenshots (clay,
  normals, textured, with face count); compare against local single-view runs.
- **Input image matters more than generator settings**: a separate large single image beat
  a view cropped from the 2x2 sheet; steps, guidance, flash decoder and seeds barely changed
  TripoSG. For production assets make each view its own full-size image.
- **TripoSG (MIT, single view, ~8 GB) is the working local baseline** — good enough for the
  game's on-screen size for now. Improve it by settings before hunting new models: steps
  50→100, guidance 5/7/9, higher mesh-extraction resolution, 3–4 seeds, flash decoder on/off,
  input front vs 3/4 view, clean 1024 RGBA crop. Log time/VRAM/faces per config.
- **Hunyuan3D (2mv / 2.1) is excluded** by the owner: raw shape reads as "plasticine"
  (smoothed plates, lumpy surface). Do not propose it; remove its weights/venv.
- **TRELLIS.2-4B runs on 12 GB** via the visualbruno/ComfyUI-Trellis2 package with its
  prebuilt Windows wheels (cumesh/o_voxel/flex_gemm/nvdiffrast, torch 2.7 cu128) imported
  without ComfyUI (stub `folder_paths`/`comfy.utils`, `ATTN_BACKEND=sdpa`,
  `expandable_segments`): 1024 cascade ~90 s, ~6 GB, ~4M faces — sharper plates and edges
  than TripoSG, needs heavy decimation. Raw output is a double shell (grainy shading); remesh
  with dual contouring before judging.
- **TRELLIS-family meshes break at the game budget**: the raw/remeshed output is thousands of
  disconnected islands, so decimation to ~20k tris either stalls far above budget or opens
  holes. At budget level TripoSG (clean single shell) currently wins even though TRELLIS.2 is
  closest to the input raw. Before judging a TRELLIS-family candidate at budget, merge
  islands / voxel-remesh to one watertight shell, then decimate.
- Other candidates, in order: TRELLIS.2-4B (see above),
  Pixal3D (Tencent ARC, MIT, TRELLIS.2 backbone, low-VRAM mode; needs `natten`; closest to
  the input but same island problem at budget), Hi3DGen (MIT, normal bridging; runs in ~36 s /
  11 GB after pinning an older `diffusers`; clean mesh that decimates to 20k without defects,
  simpler helmet), Direct3D-S2 at 512 (MIT, ~10 GB). Skip Step1X-3D
  (27–29 GB) and TripoSR/SF3D (clearly weaker). Timebox each install to ~40 min; not installed
  or out of VRAM → skip with the reason, do not dig.
- Paid path stays a fallback: switch to Tripo only when the owner says local is not enough.

## Remote GPU PC

- Work over `ssh <host>` (PowerShell on the far side); keep everything in one root
  (`D:\mo3d\{py,venv-*,repos,models,work,blender}`), never inside the owner's ComfyUI.
  ComfyUI stays for texture touch-up.
- Before working around slow downloads, measure the link: `curl.exe -s -L -o NUL -r
  0-104857599 -w "%{speed_download}" <huggingface resolve URL>` — report a slow link to the
  owner, he can fix it faster than hours of workarounds.
- Pull renders back with `scp host:D:/path/file.png <local>` to view or send them.
- The GPU PC also runs other jobs (balance sims in Docker, background `powershell
  -EncodedCommand` runners). A 3D worker stops only its own processes, by PID or by its own
  command line; never a blanket kill of all background PowerShell/Python, which silently ends
  the owner's other queues. State this in every 3D worker spec, and after a worker reports
  "stopped hung jobs", check the other queues on that host.
- When a shape model runs out of 12 GB VRAM on one asset twice, fall back to TripoSG for that
  asset (steps 100, fixed seed) instead of tuning further; note the fallback in the report.
