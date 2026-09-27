# AI 3D asset pipeline for web games

Tool landscape changes fast: re-check versions, pricing and licenses with a web search
before recommending.

## Pipeline

1. Style bible (palettes, faction silhouettes, materials, bans) from the source project.
2. GPT concept sheet per asset: front/side/back, neutral T/A pose, flat light with no baked
   shadows, clean background. Save the prompt next to the result for regeneration.
3. Image → 3D: cloud service or open model on a GPU machine.
4. Cleanup (auto or Blender): scale and pivot, retopo/decimate to budget, UV, remove baked
   light from albedo, rig to a shared humanoid skeleton.
5. Animations: one shared humanoid clip set; monsters 4–6 clips (service autorig,
   Mixamo for humanoids, or Blender).
6. Optimize with `gltf-transform`: meshopt geometry, KTX2 textures, budget check.
7. Register in object storage + asset manifest (id, version, path, budget, source,
   license); content references assets by id.

## Generator options (verify current state)

| Tool | Type | Strength | Watch out |
|---|---|---|---|
| Tripo | cloud API | quad topology, autorig, animations, FBX | commercial use needs paid plan |
| Meshy | cloud API | full image→3D→remesh→rig→animate, PBR | free-tier models published CC BY |
| Rodin (Hyper3D) | cloud | detailed hard-surface, quad mode | heavy meshes |
| Hunyuan3D Studio | cloud | clean geometry, PBR, retopo/UV/rig | newest versions closed |
| Hunyuan3D 2.x | open weights | PBR, self-host | license excludes EU/UK/KR; 16–24+ GB VRAM |
| TRELLIS.2 | open, MIT | best open model, GLB PBR | NVIDIA GPU; triangle mesh, retopo separately |

Practice: cheap draft shape (open model) → final via paid service or Blender; input is a
clean image, not text; animated characters need quad topology + rig.

Recommend a pilot (≈5 assets: humanoid, weapon, monster, boss, pet) through 2–3 paths
before choosing; compare quality, hours, cost, license.

## Blender worker on a second PC

Headless `blender -b -P job.py` pulls jobs from a queue (HTTP endpoint or Redis),
downloads source from S3/MinIO, runs normalize/decimate/rig/export glTF, uploads result.
Keep job scripts in the game repo (`tools/assets/blender/`). Ask the user for OS, GPU and
network reachability of that PC.

## Starting budgets

Humanoid ≤20k tris 2K; weapon ≤3k 1K; monster ≤10k; boss ≤30k; prop ≤5k atlased.
Target: 42 animated models in a battle scene at 60 fps on integrated GPU via instancing,
LOD, shared materials, baked diorama lighting. Fallback if too slow: pre-rendered sprites
(2.5D).
