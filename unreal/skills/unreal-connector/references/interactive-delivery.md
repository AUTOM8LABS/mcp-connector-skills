# Interactive delivery

Operator reference for turning an Unreal archviz level into something a
client can walk, choose options in, and open on their own machine. Read it
before making a level walkable, building design options, dressing a scene, or
preparing anything that leaves the studio. Verified in AUTOM8LABS field
sessions on Unreal Engine 5.8.

---

## 1. Three ways to hand a scheme over

Decide which one you are building before touching anything, because they need
different work:

| Deliverable | What it needs | What it does not need |
|---|---|---|
| **Stills** | Cameras, lighting, quality preset, Movie Render Queue | Collision, game mode, packaging |
| **Flythrough** | The above plus a Level Sequence and camera cuts | Collision, game mode, packaging |
| **Walkable build** | All of the above plus collision everywhere, a spawn point, a game mode, and a packaged build | - |

A level built for the first two is perfectly usable and completely unwalkable.
That is not a defect; it is a different job. The moment the brief changes from
"send us the images" to "let us walk it", collision becomes the work.

---

## 2. Collision: why a presentation level has none

An architectural model imported for rendering has no collision on anything.
The camera does not collide, so nothing reveals it. Press play and the visitor
falls through the floor, then walks through the walls.

**Audit first, always.** `ArchvizWalkthroughTools.audit_collision` lists the
mesh assets a visitor would pass through, heaviest first, each with its fix.
Use `min_triangle_count` to concentrate on the walls, slabs and stairs before
worrying about props.

**Then fix in bulk** with `add_simple_collision`:

| Element | Shape |
|---|---|
| Walls, floors, slabs, worktops, furniture blocks, doors | `box` |
| Columns, posts, balustrade uprights, bottles | `capsule` |
| Round props, lamps, bowls | `sphere` |

Simple shapes are what a walking visitor collides against and they cost
almost nothing. Complex per-polygon collision is for things that need
precision, and it is expensive; simple shapes are almost always the right
answer in a walkthrough.

**Two rules that catch people out:**

- **Collision lives on the mesh asset, not the actor.** Give one wall
  collision and every instance of that wall, in every level, gets it. That is
  usually what you want, and it means the fix is far cheaper than the actor
  count suggests. It also means it is *not* undoable in the usual sense - the
  asset changed.
- **Not everything should block.** Glass a visitor should not bump into,
  foliage cards, ceiling clouds, decorative hangings: use
  `set_collision_response(blocks_visitor=False)` on those actors. It sets the
  actor's components without touching the shared mesh.

Re-run `audit_collision` after fixing. It is the acceptance test.

---

## 3. Spawn point and game mode

`ArchvizWalkthroughTools.setup_walkthrough` does the level-side setup in one
call:

1. Frame the entrance in the viewport first - with no arguments the spawn
   point lands at the viewport camera, facing the same way.
2. It places or moves the `PlayerStart` at eye height (160 cm by default).
3. `game_mode_path` sets the level's game mode, which is what supplies the
   walking pawn and the controls. Without one, the visitor spawns in whatever
   the project default is.
4. It reports how many meshes still have no collision, and the ordered next
   steps.

The one thing it cannot persist is the project's default map. Setting
`GameDefaultMap` in the `/Script/EngineSettings.GameMapsSettings` config
section is what points a packaged build at the right level, and Epic's config
settings toolset writes it. Do that before packaging or the build opens an
empty map.

Sub-levels loaded alongside the main level must be set to load automatically,
or they will be missing from the build even though they are visible in the
editor.

---

## 4. Design options as variant sets

`ArchvizVariantTools` is the honest way to present alternatives: one level,
several captured states, switchable in the editor and at runtime. It maps
directly onto the way a practice already thinks - design options, material
options, phasing.

The model is two levels deep:

- A **variant set** is the question: "Kitchen finish", "Furniture layout",
  "Facade treatment", "Phase".
- The **variants** inside it are the answers: "Oak", "Walnut", "Painted".

Sets are independent, so a client can pick oak *and* the open-plan layout.

**The sequence:**

1. `create_variant_set("Kitchen finish")` - creates or reuses the
   LevelVariantSets asset.
2. `add_variant(..., "Oak", actors=[...])` - binds the actors this option has
   an opinion about. Binding says nothing about *what* the opinion is.
3. Set the level up in the editor the way this option should look.
4. `capture_variant_state(..., property_paths=["Static Mesh Component / Material[0]"])`
   - records the current state of every bound actor.
5. Repeat 2-4 for each option.
6. `activate_variant` switches between them.

**Property paths carry the component they live on**, spelled exactly as the
editor spells them. A guessed bare path such as `Visible` is silently skipped -
it comes back in the capture result's `skipped` list and the option quietly
does nothing. Always read the real paths first with
`get_capturable_properties` on one of the bound actors. The common ones on a
mesh actor:

| Intent | Property path |
|---|---|
| Show or hide an option | `Static Mesh Component / Visible` |
| Swap a finish | `Static Mesh Component / Material[0]` (index is the slot) |
| Move or rotate furniture | `Static Mesh Component / Relative Location`, `... / Relative Rotation` |
| Change a light | the light component's `Intensity`, `Light Color` |

**`place_variant_actor` is the step people forget.** Without it the options
only switch in the editor. With it, a packaged walkthrough can drive them -
a client changing the kitchen finish from an on-screen menu is switching
variants on that actor.

`activate_variant` overwrites the current state of the bound actors. Capture
before you switch, or the state you were about to record is gone.

---

## 5. Dressing without killing the frame rate

### Foliage

Grass, planting beds, gravel, scattered props: **scatter as instanced
foliage, never place as individual actors.** Instances of one type share a
draw call; two thousand grass actors do not.

1. `create_foliage_type(static_mesh_path=...)` wraps a mesh in a recipe -
   scale range, random yaw, alignment to the surface normal, the steepest
   slope it may sit on, and whether it casts shadows.
2. `scatter_foliage(foliage_type_paths=[...], surface_actors=[...])` samples
   the surface actors' footprint and traces each sample down onto them.
3. `get_foliage_inventory` reports what is actually in the level and how much
   of it.

**The trace reads render geometry, not collision**, so it works on an
imported model before any collision exists - which is the normal state of a
level that has only ever been rendered. If `placed` comes back 0, the surface
actors are wrong or the area does not overlap them. For a flat ground plane,
`use_ground_plane=True, ground_z_cm=...` skips the tracing entirely.

Turn `cast_shadow` off on grass. It is the single biggest cost in a planted
scene and almost invisible at grass scale. Set a `cull_distance_cm` so
instances stop drawing before they stop mattering.

Foliage is also where `lumen_scene_detail` earns its keep - see
`lighting-and-look.md`. Planting with default Lumen settings sits on the
ground without belonging to it.

### Decals

`place_decal` projects an image onto whatever geometry falls inside its box:
stains, patches of damp, kerb and road markings, signage, wear at door
handles, tyre marks. They follow corners and curves, so they add the
imperfection that reads as real without any new geometry.

- Default rotation projects along the actor's **+X** axis. Use `pitch=-90` to
  project down onto a floor or a road.
- `projection_depth_cm` should be just deep enough to reach the surface.
  Leave it long and the decal bleeds through onto whatever is behind the
  wall.
- `sort_order` decides which wins when decals overlap.
- `fade_screen_size` stops small decals drawing when they are far away.

Two or three well-placed decals do more for realism than another thousand
polygons.

---

## 6. Optimisation, in the order that pays

Frame rate falls as a project grows. Work the list top down; each step is
cheaper than the one after it.

1. **Nanite on heavy meshes.** `ArchvizLevelTools.find_heavy_meshes` ranks
   what is actually costing triangles, weighted by how many times each mesh is
   placed. `StaticMeshTools.set_nanite_enabled` handles it. Nanite is for
   dense opaque geometry - not for foliage cards, not for translucent
   materials.
2. **LODs on what Nanite cannot take.** `StaticMeshTools.generate_lods` and
   `set_lod_thresholds`.
3. **Textures.** Resolutions that are powers of two (1024, 2048, 4096) get
   automatic mip mapping; anything else does not, and pays full resolution at
   every distance. A texture at 10000 x 3300 is a bug, not a detail.
4. **Shadows.** Dynamic shadows on decorative fittings are pure cost. Turn
   them off where the fitting only needs to glow.
5. **Foliage cull distance and shadow casting** - see above.
6. **Quality preset and screen percentage** last, as the deliberate trade
   rather than the first reach.

`get_level_summary` and `find_heavy_meshes` tell you where you actually are.
Measure before optimising; the intuition about what is heavy is usually wrong.

---

## 7. Pre-flight before a build goes out

Run through this before packaging or sending anything:

- [ ] `audit_collision` returns nothing above the triangle threshold that
      matters.
- [ ] A `PlayerStart` exists, at eye height, somewhere sensible - and inside
      the building rather than in a wall.
- [ ] A game mode with a walking pawn is set on the level.
- [ ] `GameDefaultMap` points at this level, and any sub-levels load
      automatically.
- [ ] `update_reflection_captures` has been run since the last lighting
      change.
- [ ] `apply_quality_preset` matches the target machine, not yours.
- [ ] Variant sets have a `place_variant_actor` in the level if the client is
      meant to switch options.
- [ ] The level is saved (`save_level`), and so are the assets that changed.
- [ ] Someone has actually pressed play and walked from the front door to the
      furthest room.

The last one catches more than the other eight combined.
