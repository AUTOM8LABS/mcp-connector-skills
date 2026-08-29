---
name: unreal-connector
description: Operating doctrine for driving Unreal Engine through the MCP Connector for Unreal Engine (AUTOM8LABS). Use whenever the user wants to light, grade, frame, dress, optimise, render, or make walkable an Unreal archviz scene over MCP - sun and sky, IES, HDRI backdrops, reflection captures, post-process and Lumen quality, cine cameras, Datasmith and BIM intake, foliage and decals, design-option variant sets, collision and walkthrough setup, Movie Render Queue stills and sequences, sun studies, and site context from a postcode. Trigger on "in Unreal", "in UE5", "the level", "Lumen", "Movie Render Queue", "Datasmith", "path tracer", "make it walkable", or any request naming Unreal actors, levels, or materials. ALWAYS load this skill before the first Unreal tool call of a session, even for a small query.
---

# Unreal Engine Connector - operating doctrine

You drive a live Unreal Editor session. Unlike the other connectors in this
family, you are not the only tool provider: **Unreal Engine 5.8 ships its own
in-engine MCP server**, and this connector registers alongside it. You get
Epic's generic editor tools *and* the AUTOM8LABS archviz toolsets in one
registry. Knowing which half to reach for is most of the skill.

## What you are driving

Tools are not listed up front. The registry exposes three entry points and
everything else dispatches through them:

- `list_toolsets` - the toolsets available in this editor.
- `describe_toolset` - the tools in one toolset, with full schemas.
- `call_tool` - invoke one.

Describe before you call. Do not guess a tool name or an argument shape from
memory: the registry is the source of truth and it changes with the engine
version and the enabled plugins.

### The division of labour

| Epic's toolsets (generic editor) | AUTOM8LABS toolsets (archviz) |
|---|---|
| `SceneTools` - find actors, folders, levels, level instances | `ArchvizLightingTools` - sun, sky, point/spot/rect, physical units, IES, HDRI backdrop, reflection captures |
| `ActorTools` - labels, tags, transforms, components | `ArchvizPostProcessTools` - exposure, grading, lens effects, fog, Lumen quality, quality presets |
| `StaticMeshTools` - LODs, Nanite, convex collision, import | `ArchvizCameraTools` - cine cameras, real lenses, framing, orbit sets, piloting |
| `MaterialTools` / `MaterialInstanceTools` - graphs and parameters | `ArchvizLevelTools` - level lifecycle, level digest, heavy meshes, sun studies |
| `BlueprintTools` - Blueprint assets and graph authoring (incl. a text DSL) | `BimIntakeTools` - Datasmith import and re-import, BIM metadata queries, material remapping |
| `SequencerTools`, `UMGToolSet`, `NiagaraToolsets`, `PCGToolset` | `ArchvizDressingTools` - instanced foliage, projected decals |
| `AssetTools` - find, duplicate, move, save, metadata | `ArchvizVariantTools` - design options as variant sets |
| `EditorAppToolset` - `CaptureViewport`, console, cvars, PIE | `ArchvizWalkthroughTools` - spawn point, game mode, collision audit and fixes |
| `ConfigSettingsToolset` - project settings sections | `ArchvizRenderTools` - Movie Render Queue stills and sequences |
| | `SiteContextTools` - postcode to georeferenced OpenStreetMap site context |
| | `MCPConnectorTools` - ping, status, licence, console, connector reload |

**Rule of thumb:** if the task is generic Unreal editing, Epic ships it -
use it. If the task is about how a building looks, reads, or gets delivered
to a client, the AUTOM8LABS toolsets ship it. Chain both: find actors with
`SceneTools.find_actors`, act with an Archviz tool, verify with
`EditorAppToolset.CaptureViewport`.

## Session start

1. `MCPConnectorTools.ping` confirms the connector is alive and reports the
   licence edition. Do it once.
2. `ArchvizLevelTools.get_level_summary` orients you: actor and light counts,
   the post-process setup, whether the level is saved, and warnings that
   predict a wasted render (a manual exposure with a dim sun renders black).
3. For anything visual, look before you act. `EditorAppToolset.CaptureViewport`
   is your eyes; `ArchvizCameraTools.pilot_camera` puts the viewport on a
   specific camera first.

## Conventions

- **Actors are passed as actor references, not labels.** Get them from
  `SceneTools.find_actors` or from an Archviz tool that returns them, and pass
  them straight back in. Do not retype a label into a name field.
- **Distances are centimetres. Rotations are degrees.** Unreal is Z-up. One
  Unreal unit is one centimetre unless the project says otherwise.
- **Light intensity is physical.** Lux for the sun, candelas or lumens for
  local lights. The editor's default sun is about 10 lux, which is nothing -
  a real clear sky is around 100000. Change one and you must change exposure.
- **Every AUTOM8LABS mutation is one undo step.** Epic's generic tools open
  no transaction of their own, so their edits are not undoable as a unit. Say
  so before doing anything large with them.
- **Empty defaults become required parameters.** The registry drops empty
  string and empty list defaults from the schema, so tools that look optional
  are not. Pass `""`, `[]` and `{}` explicitly when a call is rejected for a
  missing argument.
- **Renders need a saved level.** An unsaved level is refused by Movie Render
  Queue. `ArchvizLevelTools.save_level` first.

## Safety

Confirm before running, and be clear about what undo cannot reach:

- **Not recoverable by undo:** `save_level` (writes the map), render output
  files, asset creation and deletion through `AssetTools`, Datasmith re-import
  (replaces the imported branch), and `add_simple_collision` /
  `set_nanite_enabled` (they change the mesh *asset*, so every instance of that
  mesh in every level changes with it).
- **Destructive but undoable:** `delete_lights`, `clear_foliage`,
  `remove_from_scene`, `remap_materials_by_name`, `activate_variant`
  (it overwrites the current state of the bound actors).
- **Long-running:** Movie Render Queue renders and PCG generation block the
  game thread. Start the job, then poll `get_render_status` rather than firing
  other calls into a busy editor.
- Data you send to your AI provider from an open Unreal project is Licensed
  Technology under the Unreal Engine EULA. It is the customer's responsibility
  that their provider does not train on it.

## Fast paths (intent to first tool)

| The user wants to | Start with |
|---|---|
| know what is in the level | `ArchvizLevelTools.get_level_summary`, then `SceneTools.find_actors` |
| bring a building model in | `BimIntakeTools.import_datasmith`; `import_file` for glTF, USD, FBX, IES, HDR |
| update the model after a design change | `BimIntakeTools.reimport_datasmith` |
| query BIM data on what came in | `get_bim_metadata_keys`, `find_actors_by_bim_metadata`, `get_bim_metadata` |
| fix wrong or missing materials | `find_actors_with_missing_materials`, `remap_materials_by_name` |
| light it | `ArchvizLightingTools.create_sun` + `create_sky`, then `set_exposure` |
| light a product or a studio shot | `create_hdri_backdrop` |
| add interior lighting | `create_rect_light`, `create_spot_light`, `set_ies_profile` |
| fix flat or wrong reflections | `create_reflection_capture` per room, then `update_reflection_captures` |
| fix a black or blown-out render | `ArchvizPostProcessTools.set_exposure`, then `get_post_process_summary` |
| grade it | `set_color_grading`, `set_lens_effects`, `set_height_fog` |
| trade quality against frame rate | `apply_quality_preset` (draft / presentation / final) |
| tune Lumen by hand | `set_rendering_features` |
| set up a shot | `ArchvizCameraTools.create_cine_camera`, `set_lens`, `frame_actors` |
| cover a scheme from all sides | `create_orbit_cameras` |
| check a sun angle or a right to light | `ArchvizLevelTools.sun_study`, `set_sun_position` |
| find what is making it slow | `find_heavy_meshes`, then `StaticMeshTools.set_nanite_enabled` |
| plant grass, beds, trees, scattered props | `ArchvizDressingTools.create_foliage_type`, `scatter_foliage` |
| add stains, signage, road markings, wear | `place_decal`, `set_decal_properties` |
| offer the client design options | `ArchvizVariantTools.create_variant_set`, `add_variant`, `capture_variant_state` |
| switch between those options | `activate_variant`; `place_variant_actor` for runtime switching |
| make the level walkable | `ArchvizWalkthroughTools.setup_walkthrough`, `audit_collision`, `add_simple_collision` |
| render a still | `ArchvizRenderTools.render_still`, `get_render_status`, `get_render_image` |
| render a flythrough | `create_walkthrough_sequence`, `render_sequence` |
| grab a quick look | `pilot_camera`, then `EditorAppToolset.CaptureViewport` |
| build the planning context around a site | `SiteContextTools.geocode`, `set_site_origin`, `build_site_massing` |
| see the result | `pilot_camera`, then `EditorAppToolset.CaptureViewport` |

## Operating loop

1. Orient: `get_level_summary`, then `SceneTools.find_actors` for the actors
   the task touches.
2. State the plan for anything destructive, asset-level, or long-running.
3. Act with the smallest number of calls that does the job. Batch tools take
   actor lists - one `scale_light_intensities` call for twelve lights.
4. Verify with numbers *and* a picture. `get_light_inventory` and
   `get_post_process_summary` prove the values; `CaptureViewport` proves the
   look. A setting that reads correctly and looks wrong is still wrong.
5. Report what changed, with counts and actor labels.

## Look development

**Read `references/lighting-and-look.md` before lighting, grading, or
diagnosing an image that looks wrong.** It holds the exposure and physical-unit
contract, the Lumen quality knobs and what each one actually fixes, reflection
strategy, glass and emissive handling, the studio and HDRI setup, and the
diagnostic order for a scene that is black, noisy, blotchy, or flat.

The essentials:

- Exposure and intensity are one decision. Set the sun in real lux, then set
  exposure to match; never chase a dark image by dimming the sun.
- Noise, blotches, and small objects that ignore bounced light are three
  different Lumen settings. Raising all of them together buys nothing and
  costs a lot.
- Reflections are the usual reason a good interior looks cheap. Real-time
  reflections only trace what the screen already shows; a reflection capture
  in each room fills what they miss.
- Verify with `CaptureViewport` at every step. Values lie about appearance.

## Interactive delivery

**Read `references/interactive-delivery.md` before making a level walkable,
building design options, or preparing anything a client will open
themselves.** It covers collision (why a presentation level has none, and what
to give what), spawn points and game modes, variant sets as design options,
dressing with foliage and decals without destroying the frame rate, and the
sequence of checks before a build goes out.

The essentials:

- A level built for stills has no collision anywhere. It looks perfect and is
  unusable the moment anyone walks it. Audit first, always.
- Collision lives on the mesh asset, not the actor: fixing one wall fixes
  every instance of it, in every level.
- Variant sets are the honest way to show options. Bind the actors, set the
  level up the way an option should look, then capture - do not rebuild the
  scene for each option.
- Instanced foliage is cheap; the same meshes placed as individual actors are
  not. Scatter, never place.
