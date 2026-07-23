---
name: 3dsmax-connector
description: Operating doctrine for driving Autodesk 3ds Max through the MCP Connector for 3ds Max (AUTOM8LABS). Use whenever the user wants to inspect, model, transform, group, layer, texture, animate, render, or convert scenes via MCP tools. Trigger on "in 3ds Max", "in Max", ".max scene", "viewport", "modifier stack", "render the scene", or any request naming 3ds Max objects, materials, or modifiers. ALWAYS load this skill before the first 3ds Max tool call of a session, even for a small query.
---

# 3ds Max Connector - operating doctrine

You drive a live 3ds Max session through the AUTOM8LABS MCP tools. Every call
runs against the real open scene on the Max main thread. There are 63 tools:
26 Free (query, transforms, screenshots) and 37 Pro (creation beyond
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

## Gotchas

1. **Only Physical Material can be created.** Texture slots are limited to
   base_color, roughness, metalness, bump, cutout.
2. **`move_to_layer` needs the layer to exist** - `create_layer` first.
   Layer 0 can never be deleted; `delete_empty_layers` only removes empty
   ones.
3. **Re-frame before every screenshot** - a stale viewport angle makes a
   correct edit look wrong.
4. **An empty result is a valid answer**, not an error.
5. **Supported host: 3ds Max 2026.** If the connector does not
   respond, Max is not running or the plugin has not loaded; the user can
   verify via the AUTOM8LABS menu (MCP Connector Status).
6. Licence-gated tools return a purchase message on the Free tier - relay
   it honestly instead of improvising with free tools that cannot do the
   job.

## Response style

No play-by-play - do not announce each tool call or narrate steps as you
go. Work, then report the outcome once: what you did and the result
(object names, counts, file paths for renders/conversions). Short
bullets. Speak mid-task only to confirm a destructive action or report a
failure. If a step failed, show the error and stop; do not narrate
success you did not verify.
