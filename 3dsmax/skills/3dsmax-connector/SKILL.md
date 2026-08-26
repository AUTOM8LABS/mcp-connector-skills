---
name: 3dsmax-connector
description: Operating doctrine for driving Autodesk 3ds Max through the MCP Connector for 3ds Max (AUTOM8LABS). Use whenever the user wants to inspect, model, transform, group, layer, texture, animate, render, or convert scenes via MCP tools. Trigger on "in 3ds Max", "in Max", ".max scene", "viewport", "modifier stack", "render the scene", or any request naming 3ds Max objects, materials, or modifiers. ALWAYS load this skill before the first 3ds Max tool call of a session, even for a small query.
---

# 3ds Max Connector - operating doctrine

You drive a live 3ds Max session through the AUTOM8LABS MCP tools. Every call
runs against the real open scene on the Max main thread. There are 101 tools:
23 Free (query, transforms, screenshots) and 78 Pro (creation beyond
primitives, modifiers, materials, layers, animation, rendering, file I/O,
scripting). If a tool refuses with a licence message, relay it
honestly - do not improvise with tools that cannot do the job.

## Session start

1. Start with `get_scene_info` - it orients you and doubles as the
   connection check; do not spend a separate `ping`. If it fails, use
   `ping` to confirm whether Max and the connector are running at all.
2. Then `list_objects` with a `name_pattern` or category filter. `list_objects` caps at 500 and
   `find_objects_by_property` at 200 - honour the limits and filter rather
   than paging a huge scene.
3. For anything visual, frame first: `set_viewport` + `zoom_extents`, then
   `create_viewport_screenshot`. The screenshot is your eyes - use it to
   verify, not just to decorate.

## Conventions

- **Objects are referenced by exact name**, not handles. Get names from
  `list_objects` / `get_selection`; never invent one. Unknown names throw.
- **Batch by default.** Mutators take `names` arrays - one `move_objects`
  call for ten objects, not ten calls. Single-target exceptions:
  `set_modifier_property`, `animate_transform`, and the per-material tools.
- **Units are the scene's native system units** - no conversion layer.
  Positions are `[x, y, z]` (Z-up). Rotations are Euler `[x, y, z]` in
  **degrees**. Colours are `[r, g, b]` in **0–255**.
- **Modifier indices are 1-based** (`list_modifiers` first). Material editor
  slots are 1–24. `add_modifier` takes friendly names (bend, twist, taper,
  shell, turbosmooth, edit_poly, uvw_map, noise, symmetry, lattice, smooth,
  relax, push, skew).
- **In-scene edits are undoable** - each tool is one named undo step in Max.
  Disk writes are not (see Safety).

## Safety

Confirm before running, and say clearly which effects Ctrl-Z cannot recover:

- **Not recoverable by undo:** `save_scene` (overwrites the .max file),
  `convert_scene_to_format` (writes FBX/OBJ/STL/3DS/glTF/DWG to disk, can
  overwrite), `render_frame` output files, and `collapse_stack` (flattens
  the modifier stack - parametric history is gone).
- **Destructive but undoable:** `delete_objects`, `delete_animation` (strips
  all keys), `delete_empty_layers`, `ungroup_objects`.
- `execute_maxscript` is Pro **and** requires the machine opt-in env var
  `MCP_CONNECTOR_ENABLE_SCRIPT_EXEC=1`. If it refuses, that is deliberate
  fail-closed behaviour - tell the user how to opt in; never try to smuggle
  script effects through other tools.

## Fast paths (intent to first tool)

| The user wants to | Start with |
|---|---|
| see what is in the scene | get_scene_info, list_objects, get_scene_statistics |
| inspect specific objects | get_object_properties, list_modifiers |
| find objects by data | find_objects_by_property (Pro) |
| make base geometry | create_primitive; splines/text/cameras/lights are Pro |
| move / rotate / scale / rename | move_objects, rotate_objects, scale_objects, rename_objects |
| organise the scene | list_layers, create_layer, move_to_layer, group_objects |
| shape geometry non-destructively | add_modifier, set_modifier_property |
| look development | create_physical_material, assign_material, apply_bitmap_texture, add_uvw_map |
| animate | get_animation_info, set_time_range, animate_transform |
| render | get_render_settings, set_render_settings, render_frame |
| hand the model to another app | convert_scene_to_format |
| see the result | set_viewport, zoom_extents, create_viewport_screenshot |

## Operating loop

1. `get_scene_info` / `list_objects` - orient.
2. State the plan for anything destructive or large.
3. Act with batch tools, fewest calls that do the job.
4. Verify: re-read the changed objects (`get_object_properties`) or take a
   framed screenshot. Numbers prove transforms; screenshots prove looks.
5. Report what changed with counts and names.

## Look development and rendering

The connector's typed render surface is renderer-agnostic (`get_render_settings`,
`set_render_settings`, `render_frame`, `batch_render_cameras`, `setup_sun`,
`create_light`, `create_camera`, `frame_camera_to_objects`, the Physical Material
tools). `get_render_settings` tells you the active renderer. Use these rules:

**Choose the path by renderer and licence**
- Arnold (the Max default): everything below is reachable with typed tools.
  `setup_sun` creates the Sun Positioner, the Physical Sun and Sky environment and
  the exposure control together, so daylight renders come out exposed.
- V-Ray present: the good results need V-Ray classes (physical camera, HDRI dome,
  VRayMtl, Cosmos import). Those are `execute_maxscript` today, which is Pro and
  needs the machine opt-in. If script execution refuses, say so and render with the
  Arnold path; do not pretend V-Ray features are available.
- Never create a Physical Material for an object that already carries a V-Ray or
  Multi material: `apply_bitmap_texture` throws on non-Physical materials and
  `get_material_properties` returns only name and class for them.

**Clay / white-card study (any renderer)**
One white material on everything, no textures, a soft dome as the only light, no
sun: the shading is occlusion alone. Arnold: white Physical Material + skydome
light + an invisible plane light for a soft ground shadow. V-Ray: global override
material (VRayMtl with VRayDirt in diffuse: occluded grey, unoccluded white) +
white dome light visible as backdrop + invisible plane key. Keep the dome/key ratio
around 1.0 : 18 (V-Ray, key normalised, 25 m plane) so the form does not flatten
into the background.

**Photographic exterior (V-Ray recipe, proven on Max 2027 / V-Ray 7)**
1. Sky and sun from one HDR photograph: `VRayHDRI` (spherical mapping, `mapType 2`)
   in a dome `VRayLight` (type 1) and the same map as the environment background.
   Rotate the map to put the sun where the facade wants it. `VRaySun` + `VRaySky` is
   the alternative; the sun must have a target or it points below the horizon.
2. Exposure through a `VRayPhysicalCamera`: f/8, 1/200-1/320, ISO 100, 24-35 mm,
   slight vignetting. The scene exposure control does not act on a plain camera and
   physical sun/sky is ~13 stops brighter than a dome, so without the physical camera
   the frame is blown or black.
3. GI: Brute Force + Light Cache (the V-Ray 7 default; the Irradiance Map is
   deprecated). Colour mapping: render linear (Reinhard burn 1.0, gamma 2.2, "colour
   mapping only" mode, sub-pixel mapping and clamp off) and tone-map in the VFB
   (Filmic/ACES) or via the OCIO colour management, so the EXR keeps its range. If
   the VFB cannot be driven, Reinhard burn 0.5-0.6 in the render is the fallback.
   Progressive sampler, noise threshold 0.008-0.01, denoiser render element. Max
   render time is the test-vs-final lever, not quality settings.
4. Every material gets some reflection at the right glossiness; nothing is fully
   matte. Off-white (220) never 255. Round edges via `VRayEdgesTex` in the bump slot
   (radius 3-5 mm on frames, 10-20 mm on concrete). Glass: white reflection + white
   refraction + IOR 1.52-1.56 + Fresnel, tint in fog, reflect on back side on.
5. Dirt and wear are the detail: `VRayDirt` in crevices, wear on exterior edges,
   bias along Z for streaks. Randomise materials across clones (4-5 variants).
6. Context sells the shot: a belt of instanced trees at 50-75 m hides the horizon;
   a lawn is fur or scattered clumps, not a flat green; people at 1.8 m give scale.

**Chaos Cosmos assets (trees, people, materials, HDRIs)**
- Import with `chaosCosmosAssetImportByName "Maple Tree 001"` (the display name,
  with spaces). The importer downloads the texture package, builds the Multi
  material and scales the proxy. Placing a `.vrmesh` by file path yourself gives a
  black, untextured model because textures only arrive with the importer.
- Imported materials land in the scene material list; find them by name and assign.
- Never size a `VRayProxy` from its bounding box - it lies; judge scale by render.
- `showCosmosBrowser()` opens the library for the user when an asset is not yet
  downloaded; only downloaded assets can be imported by name.

**Composition, before the final frame**
Eye level (1.6-1.8 m) and 24-35 mm for exteriors; verticals kept vertical; a
foreground element for depth; the sun raking across the main facade rather than
flat behind the camera. Frame like a photographer, not like an elevation.

Grounding for this section: AUTOM8LABS field sessions (August 2026).

## Gotchas

1. **Only Physical Material can be created.** Texture slots are limited to
   base_color, roughness, metalness, bump, cutout.
2. **`move_to_layer` needs the layer to exist** - `create_layer` first.
   Layer 0 can never be deleted; `delete_empty_layers` only removes empty
   ones.
3. **Re-frame before every screenshot** - a stale viewport angle makes a
   correct edit look wrong.
4. **An empty result is a valid answer**, not an error.
5. **Supported hosts: 3ds Max 2024-2027.** If the connector does not
   respond, Max is not running or the plugin has not loaded; the user can
   verify via the AUTOM8LABS menu (MCP Connector Status).
6. **VRayHDRI `mapType` 1 is cubic, 2 is spherical** - a half-grey sky means
   the wrong projection. **A scripted `VRaySun` needs an explicit target node.**
7. Licence-gated tools return a purchase message on the Free tier - relay
   it honestly instead of improvising with free tools that cannot do the
   job.

## Response style

No play-by-play - do not announce each tool call or narrate steps as you
go. Work, then report the outcome once: what you did and the result
(object names, counts, file paths for renders/conversions). Short
bullets. Speak mid-task only to confirm a destructive action or report a
failure. If a step failed, show the error and stop; do not narrate
success you did not verify.
