---
name: microstation-connector
description: Operating doctrine for driving Bentley MicroStation and MicroStation PowerDraft through the MCP Connector for MicroStation (AUTOM8LABS). Use whenever the user wants to query, draw, model, annotate, print, modify, or maintain DGN files via MCP tools - element queries, levels, references, geometry creation, solid modelling, dimensions and notes, cells, tags, fences, views and camera, printing to PDF, transforms, standards checking, DWG conversion, file cleanup. Trigger on "in MicroStation", "in PowerDraft", "DGN", "levels", "references", "key-in", or any request naming MicroStation elements or models. ALWAYS load this skill before the first MicroStation tool call of a session, even for a small query.
---

# MicroStation Connector - operating doctrine

You drive a live MicroStation session through the AUTOM8LABS MCP tools. Tools
act on the **active model** of the open design file. 116 tools: 31 free
(read-only inspection and view navigation), 85 Pro (levels, references,
properties, geometry creation, solid modelling, transforms, annotation,
printing, cells, tags, fences, cleanup, standards, file lifecycle and DWG
conversion).

## Host

One binary serves every CONNECT-generation host. **Do not gate behaviour on a
version number and do not assume one** - the tool list the client loaded is the
truth about what this session can do.

- MicroStation 2023 to 2026 is the supported range.
- MicroStation PowerDraft shares the engine and the DGN format, and the
  connector is built against it, but it is **not yet verified** - treat a
  PowerDraft session as unproven and report anything that fails. PowerDraft is
  also **2D only**, so the solid modelling tools (`create_smart_solid_*`, the
  boolean and feature tools, `query_solid`) and the camera tools do not apply
  there. Everything else should.

If a tool is missing from the session, it is not licensed or not supported on
that host. Relay the error; never work around it.

## Session start

1. Start with `get_model_info` - **before touching any coordinate**. It
   returns the working (master) units and UOR factors for the active
   model, and doubles as the connection check; do not spend a separate
   `ping`. If it fails, MicroStation is not running, no design file is
   open, or the connector has not started - use `ping` then to diagnose,
   and the user can key-in `MCPCONNECTOR STATUS` (or `MCPCONNECTOR START`).
2. `get_file_info` / `list_models` to orient in multi-model files. Tools act
   on the active model only; ask the user to switch models if needed.

## Units and coordinates

- **All coordinates and lengths on the wire are master units** (working
  units), never UORs. The connector converts internally. Think in the
  model's master unit as reported by `get_model_info`.
- Angles are degrees. Z defaults to 0 (2D-friendly). Rotations are about Z
  unless an orientation is given.

## Identifiers

- Elements are addressed by **`element_id`** (Int64 ElementId) sourced from
  `scan_elements` or `get_selected_geometry`. Never invent one.
- Levels are addressed by **name**; references by **logical_name**; views by
  number 1–8 (most default to view 1).

## Token discipline

- `scan_elements` and `find_elements_in_range` default to limit 500,
  `get_selected_geometry` to 1000. Filter by level or type instead of
  raising limits; use `count_elements` for totals before any list.
- Transforms and property setters are **single-element per call** - plan
  loops deliberately and tell the user when a change spans many elements.
  Bulk exists only where named: `set_all_levels_display`, `array_element`,
  `reload_references`, and the cleanup tools.
- Verify small: re-read the one changed element, not the model.

## Safety

Several tools **save the file as part of the operation**, which defeats
undo. Confirm before running:

- `compress_design`, `data_cleanup`, `purge_unused`,
  `sync_levels_from_dgnlib` - all save by default. `data_cleanup` processes
  duplicates/overlaps per the machine's local settings, so results are
  environment-dependent - treat as potentially lossy.
- `delete_element`, `detach_reference` - destructive. (`delete_level` only
  succeeds on an empty level - a built-in safety.)
- `save_as_dwg` and `batch_save_as_dwg` overwrite an existing file at the
  target path and use the machine's current DWG save options.
- `open_design_file` and `create_design_file` **change which file is active**,
  so every later tool call lands somewhere else. Say which file you switched
  to.
- `send_keyin` runs any MicroStation key-in. It is Pro **and** requires the
  machine opt-in env var `MCP_CONNECTOR_ENABLE_COMMAND_EXEC=1` - refusal is
  deliberate fail-closed behaviour; say so rather than working around it.

## Fast paths (intent to first tool)

| The user wants to | Start with |
|---|---|
| see the file / model state | get_file_info, get_model_info, count_elements |
| find elements | scan_elements (filtered), find_elements_in_range |
| work on their selection | get_selected_geometry |
| inspect an element | get_element_info, get_element_properties |
| manage levels | list_levels, get_level_usage; create/rename/set_element_level (Pro) |
| manage references | list_references, get_reference_info; attach/detach/toggle (Pro) |
| draw geometry | create_line, create_line_string, create_shape, create_arc, create_circle, create_ellipse, create_text (Pro) |
| model 3D solids | create_smart_solid_box / _cylinder / _sphere / _cone / _torus / _wedge (Pro) |
| build solids from profiles | extrude_profile, revolve_profile, sweep_profile_along_path, loft_profiles (Pro) |
| combine or cut solids | solid_union, solid_subtract, solid_intersect (Pro) |
| edit a solid's faces or edges | **query_solid first**, then fillet_solid_edges, fillet_face_edges, chamfer_solid_edge, shell_solid, offset_solid_face, remove_solid_face (Pro) |
| edit geometry | move/copy/rotate/scale/mirror/array_element (Pro) |
| restyle elements | set_element_color / _weight / _style / _transparency (Pro) |
| annotate | dimension_element, place_dimension, place_note, align_notes (Pro) |
| place library content | list_cells; attach_cell_library, place_cell, create_cell (Pro) |
| work in a fence | get_fence_contents; define_fence and undefine_fence (Pro) |
| check standards | check_level_standards, check_text_standards, generate_standards_report (Pro) |
| clean the file | compress_design, purge_unused, data_cleanup (Pro, confirm first) |
| print | list_paper_sizes; then print_to_pdf (Pro) |
| read or write tags | get_element_tags and list_tag_sets; set_element_tag (Pro) |
| hand off as DWG | save_as_dwg, batch_save_as_dwg (Pro) |
| open or save files | open_design_file, create_design_file, save_design_file, save_design_file_as (Pro) |
| show the user | fit_view, zoom_to_element, zoom_view, set_view_rotation, update_views |
| set up a 3D view | set_camera, set_render_mode, set_display_style, set_view_display_flags (Pro) |
| use saved views | list_saved_views, apply_saved_view; save_named_view (Pro) |

## Workflows

### Standards audit
check_level_standards + check_text_standards (or list_non_standard_levels),
then generate_standards_report. To remediate levels from the library, run
sync_levels_from_dgnlib - but only after the check, and with consent (it
saves).

### Draw and place
get_model_info (units) → list_levels (target level) → create_* with an
explicit `level` → zoom_to_element → verify with get_element_info.

### Model and edit a solid
Create or combine (`create_smart_solid_*`, `extrude_profile`, `solid_union`)
→ **`query_solid`** to get real face and edge points → the feature tool with
those coordinates → `query_solid` again to confirm and to re-point before the
next edit. Not available in PowerDraft.

### Print a sheet
`list_paper_sizes` → `print_to_pdf` with an explicit paper size and output
path → report the path. Printing is synchronous, so a success means the PDF
exists.

### File hygiene before issue
check_* first for a record, then purge_unused → compress_design, reporting
counts. Confirm each because they save.

## Gotchas

1. **Units are the #1 error source.** Always read `get_model_info` before
   your first coordinate; never assume mm or metres.
2. **No open design file, no tools.** The connector starts when a file
   opens.
3. **Modal dialogs and in-progress commands stall tool calls** - everything
   marshals to MicroStation's main thread. A hung call usually means
   MicroStation is waiting for the user.
4. **Line styles:** built-in style IDs are 0–7 (0 solid, 1 dotted, 2 medium
   dash, …). Custom DGNLIB styles need the key-in escape hatch, which is
   usually disabled - tell the user rather than guessing a style ID.
5. **References may be DGN or DWG.** Address them by logical name.
6. **`move_to_layer`-style re-homing is `set_element_level`** and the level
   must already exist.
7. Free tier is strictly read-only - a Pro tool may return a licence error;
   relay it honestly.
8. **Solid faces and edges have no persistent IDs.** Every feature tool
   (fillet, chamfer, shell, offset, remove face) targets geometry by a 3D
   pick-point. Run `query_solid` first: it returns face centroids and edge
   midpoints in world coordinates. Never guess a point, and re-run
   `query_solid` after each edit - the previous points are stale.
9. **A few reference tools are key-in backed and report "queued", not
   "done".** `set_reference_nesting`, `set_reference_overrides` and
   `set_reference_visible_edges` hand a key-in to MicroStation and return
   before it runs. Say "queued" to the user; do not claim the change landed,
   and confirm with `get_reference_info` where it matters.
10. An empty result is a valid answer, not an error.

## Response style

No play-by-play - do not announce each tool call or narrate steps as you
go. Work, then report the outcome once: what changed, with element IDs,
level names, counts, output paths. Short bullets. Speak mid-task only to
confirm a destructive action or report a failure. If a step failed, show
the error and stop; remind the user that saved-by-design operations
(compress, cleanup, purge) are not undoable.
