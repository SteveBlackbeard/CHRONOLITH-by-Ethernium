# NODE ASSET PIPELINE

## Current Reality

The dashboard is a tactical top-down 2D map with 3D assets projected into it.

That changes the asset rules completely:

- loading correctly is not enough
- the asset must read clearly from above
- the pivot must match the node anchor
- the silhouette must survive a top-down view

Right now, `sentinel` works because it has a strong top silhouette.
Most other assets do not read well because they are spherical or nearly spherical from above.

## What We Verified

These canonical assets are present and loadable:

- `public/assets/nodes/core/Core0.glb`
- `public/assets/nodes/edition/lite/Core1.glb`
- `public/assets/nodes/edition/pro/Core2.glb`
- `public/assets/nodes/edition/omega/Core3.glb`
- `public/assets/nodes/engine/crystallizer/Coreconnection.glb`
- `public/assets/nodes/engine/auditor/Coreconnection.glb`
- `public/assets/nodes/engine/guardian/Coreconnection.glb`
- `public/assets/nodes/linked-root/Corerealconnection.glb`
- `public/assets/nodes/sentinel/sentinels.glb`

And this is the practical diagnosis:

- `sentinel`: readable from above, directional, works well
- `core`: richer and potentially usable, but still needs family tuning
- `lite/pro/omega`: almost spherical, visually too similar from above
- `crystallizer/auditor/guardian`: tiny spheres, too generic for tactical reading
- `linked-root`: another sphere-like form, too weak from above

## Correct Production Direction

Do not design these assets as generic 3D objects.
Design them as sovereign top-view glyph-objects.

Each asset should be readable in this order:

1. top silhouette
2. anchor position
3. scale relative to orbit
4. color/material identity
5. side-view beauty

If the top silhouette is weak, the asset will look like "it is not there" even when it is loaded correctly.

## Blender Rules

### 1. Pivot / Origin

This is critical.

- Place the object origin at the logical connection center of the node
- The origin must be the exact tactical anchor
- Do not leave the origin off to one side
- Apply location, rotation, and scale before export

Recommended Blender flow:

1. place the model where you want it
2. set 3D cursor to the intended node anchor
3. `Object > Set Origin > Origin to 3D Cursor`
4. `Ctrl+A > All Transforms`

### 2. Top Silhouette

The dashboard is top-down first.

Good:

- crosses
- forks
- tridents
- rings with asymmetry
- blades
- anchors
- multi-lobed systems
- directional hulls
- crown-like shapes

Bad:

- perfect spheres
- near-spheres
- smooth blobs with no top signature
- tiny compact meshes with no edge logic

### 3. Scale

Aim for a normalized footprint that reads well from above.

- the object should occupy a clear tactical footprint
- avoid huge empty bounding boxes
- avoid microscopic detail that only works in close 3D inspection

### 4. Height

Vertical detail is secondary.

- keep some height for richness
- but do not rely on vertical drama for identity
- the asset must still work as a symbol when flattened by the camera

### 5. Materials

Prefer strong form over heavy material tricks.

- matte-metal + sharp highlights works well
- restrained emissive accents are fine
- avoid materials that need dramatic lighting to be legible
- avoid relying on transparency for the main silhouette

## Family Design Guidance

### `core`

- sovereign central object
- radial or crown logic is good
- should feel like the root intelligence of the system
- top view must be unmistakable

### `lite`

- lighter, cleaner, simpler than `pro`
- should not be a plain orb
- think compact shard-core, split ring, or light trident

### `pro`

- denser and more engineered than `lite`
- should feel operational and premium
- from above it should have a stronger signature than `lite`

### `omega`

- most advanced edition
- can be more complex and aggressive
- top silhouette should imply power, not just scale

### `crystallizer`

- should feel like synthesis / convergence / lattice formation
- good motifs: radial forks, crystal arms, comb-like structures

### `auditor`

- should feel precise, scanning, forensic
- good motifs: apertures, rings, segmented blades, measuring geometry

### `guardian`

- should feel defensive and containment-oriented
- good motifs: shields, braces, lock-rings, tri-barriers

### `linked-root`

- should read as gateway/system ingress
- not a sphere
- better as dock, hub, gate, or connection crown

### `sentinel`

- current best reference
- directional ship-like silhouette
- keep using this as the standard for readability

## Export Rules

- format: `glb`
- up axis: `Y`
- one clean root object preferred
- transforms applied
- no giant hidden helper geometry
- no external texture dependency assumptions
- animation optional, but the static silhouette must already work

## Runtime Reality

Current runtime behavior lives in:

- `src/lib/nodeAssets.ts`
- `src/components/NodeAssetRig.tsx`

Important current runtime assumptions:

- canonical assets are mostly forced to `normalizationMode: 'planar'`
- canonical assets are mostly using `anchorMode: 'origin'`
- the top-down renderer applies a base `-90°` X rotation to read the asset from above

That means:

- a bad pivot in Blender will stay bad in runtime
- a weak top silhouette will stay weak in runtime
- a sphere will still read like a sphere

## Immediate Fix Plan

Rework families in this order:

1. `lite`
2. `pro`
3. `omega`
4. `crystallizer`
5. `auditor`
6. `guardian`
7. `linked-root`
8. `core` fine-tuning

Use `sentinel` as the visual benchmark.

## Asset Checklist

### `core/Core0.glb`

- keep the richer multi-mesh structure
- verify origin is exactly at the tactical connection center
- strengthen the top silhouette so it reads as a sovereign hub, not just a glowing orb
- preserve readable asymmetry from above

### `edition/lite/Core1.glb`

- current issue: almost spherical from above
- replace with a lighter directional silhouette
- recommended shapes: split ring, forked shard, open trident
- recenter origin before export

### `edition/pro/Core2.glb`

- current issue: reads almost the same as `lite`
- redesign with a denser, more engineered top profile
- recommended shapes: segmented cross-core, four-arm dock, radial brace
- ensure it is visually stronger than `lite`

### `edition/omega/Core3.glb`

- current issue: also spherical from above
- redesign as the most advanced and forceful edition
- recommended shapes: crown, blade wheel, sovereign star, shielded reactor
- make its top silhouette the most distinctive of the three editions

### `engine/crystallizer/Coreconnection.glb`

- current issue: tiny sphere, no functional read
- redesign around convergence/synthesis
- recommended shapes: crystal lattice, converging prongs, radial assembler
- avoid round closed blobs

### `engine/auditor/Coreconnection.glb`

- current issue: tiny sphere, no audit identity
- redesign around scanning/inspection
- recommended shapes: segmented ring, aperture scanner, measuring array
- top silhouette should imply analysis, not mass

### `engine/guardian/Coreconnection.glb`

- current issue: tiny sphere, no defense identity
- redesign around defense/containment
- recommended shapes: shield triad, brace-lock, defensive arc cluster
- top silhouette should feel protective and stable

### `linked-root/Corerealconnection.glb`

- current issue: spherical gateway with weak ingress identity
- redesign as a gate, hub, dock or ingress crown
- recommended shapes: portal fork, docking crown, anchor gate
- it must read as "entry point" from above

### `sentinel/sentinels.glb`

- current status: best current reference
- keep directional hull language
- keep top readability
- optional refinements: cleaner origin, slightly stronger nose/read from above

## Production Table

| Asset | Current Problem | Blender Action | Priority |
|---|---|---|---|
| `core/Core0.glb` | Better than the others, but still not yet a fully sovereign top-view icon | Keep structure, recenter origin exactly, exaggerate top silhouette and asymmetry | Medium |
| `edition/lite/Core1.glb` | Reads as a sphere from above | Replace with a lighter directional silhouette, open shape, split ring or shard fork | Critical |
| `edition/pro/Core2.glb` | Reads too close to `lite`, almost spherical | Redesign as denser engineered top-view object, stronger than `lite` | Critical |
| `edition/omega/Core3.glb` | Also spherical, no “omega” identity from above | Redesign as strongest edition silhouette, crown/blade/reactor language | Critical |
| `engine/crystallizer/Coreconnection.glb` | Tiny sphere, no synthesis identity | Rebuild as lattice / convergence / radial assembly object | Critical |
| `engine/auditor/Coreconnection.glb` | Tiny sphere, no forensic/scanner identity | Rebuild as scanner aperture / segmented audit ring / measuring array | Critical |
| `engine/guardian/Coreconnection.glb` | Tiny sphere, no defense identity | Rebuild as shielded brace / lock barrier / containment triad | Critical |
| `linked-root/Corerealconnection.glb` | Gateway reads like another orb | Redesign as ingress gate / dock / anchor crown | High |
| `sentinel/sentinels.glb` | Works already | Keep as benchmark, only refine pivot or nose if desired | Low |

## Fast Blender Checklist

For every asset before export:

1. Apply transforms with `Ctrl+A`
2. Move origin to the real tactical connection center
3. Check top view only and ask: "does this still read if flattened?"
4. Remove hidden helper geometry or giant empty bounding boxes
5. Export as `glb`
6. Reopen the exported file and verify the origin did not drift

## Definition Of Done

An asset is ready only if:

- it is clearly readable from top view
- it anchors correctly to the node center
- it does not need placeholder help to be understood
- it is visually distinct from sibling families
- it still reads when zoomed out in the tactical map
