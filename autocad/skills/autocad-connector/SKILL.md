---
name: autocad-connector
description: Operating doctrine for driving AutoCAD through the MCP Connector for AutoCAD (AUTOM8LABS). Use whenever the user wants to query, draw, modify, annotate, plot, or batch-process DWG files via MCP tools - entity queries, layers, blocks, xrefs, dimensioning, PDF plotting, folder-wide batch maintenance. Trigger on "in AutoCAD", "DWG", "drawing", "layers", "xrefs", "title block", "plot to PDF", or any request naming AutoCAD entities or commands. ALWAYS load this skill before the first AutoCAD tool call of a session, even for a small query.
---

# AutoCAD Connector - operating doctrine

You drive a live AutoCAD session through the AUTOM8LABS MCP tools. Single-
document tools act on the open drawing; the Management Pack tools batch-
process whole folders without touching the open drawing. Free tier is
read-only inspection (33 tools); Pro unlocks creation, modification,
annotation, plotting, and the folder-batch pack. A **read-only session**
(user checkbox or administrator policy) withholds the same mutating tools
on a Pro seat. Supported hosts: AutoCAD 2022–2027. Written for connector
v2.1.4.

## Session start

1. Start with `get_drawing_info` - path, units, extents, layer and entity
   counts. It doubles as the connection check; do not spend a separate
   `ping`. If it fails, AutoCAD is not running or the connection is off -
   use `ping` then to diagnose, and the user can check the
   `MCPCONNECTOR_STATUS` command or the AUTOM8LABS ribbon. Both tools
   report `connectorVersion`, `hostVersion` and `readOnlySession`.
   `ping` also returns the edition, how many tools are served, and a
   `capabilities` matrix - check that rather than guessing from a version
   number when you need to know whether a feature exists on this build.
   A tool missing because the seat is unlicensed looks identical to one
   this version never had; `capabilities` tells them apart.
2. **Units before geometry.** Coordinates are in current drawing units per
   INSUNITS, not a fixed unit. On survey or unitless DWGs run
   `detect_units` before creating or measuring anything.

## Token discipline

- **Page, don't dump.** `get_entities` defaults to limit 500. Page with
  `offset` until `hasMore` is false; `matched` is the total the filters
  select, so one call tells you how big the job is.
- **For a bulk geometry read, use `format: "compact"` and one big limit.**
  It returns `columns` + `rows` with geometry as flat number arrays and a
  `geometryFormat` legend - roughly half the bytes of objects-with-geometry,
  and one call instead of nine. A whole 13,000-entity model comes back in
  about a second. Page only when you actually need to.
- **Target, don't scan.** `select_by_filter`, `find_text`,
  `count_text_patterns`, and `get_entity_by_handle` beat unfiltered lists.
  For a spatial window use `boundingBox` on `get_entities` (crossing) or
  `select_by_filter` with `withinExtents` and `mode: "window"` for
  entirely-inside.
- **Say which space.** Reads default to model space. Sheet content
  (title blocks, notes, viewports) needs `space` set to the layout name,
  `current`, or `all`. Every entity comes back with a `space` field.
- **Reports return file paths, not payloads.** The batch reporting tools
  write .xlsx/.csv and return a path - relay the path, do not ask for the
  content inline.
- Verify small: after an action, re-read the one changed entity or a count,
  not the whole drawing.

## Identifiers

Entities are referenced by **handle hex strings** (e.g. `1A3F`), never
invented. Single-entity tools take `handle`; multi-entity tools take
`handles`. Creation tools return the new handles - keep them for follow-up
edits.

- `get_entity_properties` always returns `{success, count, entities: [],
  errors: []}`, including for one handle - read `entities[0]`.
- `trim_entity` returns `newHandles`: the surviving piece gets a **new
  handle** and the old one is gone. Update anything that held it.
- `explode_entity` and boolean operations also replace their inputs.
- `create_leader` returns one `handle` for the MLeader.
- `set_dynamic_block_properties` is atomic: the whole batch is validated
  first and one bad entry writes nothing; read `applied` and `rejected`.
  Names repeat on library blocks (three "Origin" on a door), so address a
  repeated name by index, `"#3"`, using the `index` each property carries
  in `get_dynamic_block_properties`. A repeated name is refused with the
  indexes to use.
- **A failed call is `success: false` with a top-level `error`.** The
  payload stays under `result`. Never treat `success: true` as done
  without reading the counts it reports.

## Safety

- **Checkpoint before a batch of edits.** `create_checkpoint` (add
  `saveCopy: true` for a file backup) before any run of destructive
  changes; `rollback_checkpoint` reverts everything since it in one
  step, `undo` reverts N tool calls (each call is one step), `redo` only
  works as the very next call after `undo` - even a read in between
  clears it. They are queued in AutoCAD (`requested: true`) and the
  connector holds the next call until they have run, so a read straight
  after shows the result - still read back before telling the user. Folder tools work on files on
  disk and sit outside this undo - their safety net is `dryRun` and
  `outputFolder`.
- **Batch tools default to `dryRun: true`.** Keep that default on the first
  pass, review the per-file report with the user, then re-run with
  `dryRun: false`. Prefer `outputFolder` over in-place overwrite.
- **A batch reports `success: false` if any drawing failed.** Read `ok`,
  `failed`, and the per-file detail; a failed file names itself and the
  reason (open in AutoCAD, locked by another user). Relay the names so the
  user can close them and re-run. A dry run confirms which files are in
  scope, not that each one can be plotted or saved.
- **Exception: `purge_drawing` defaults `dryRun` to false** - treat it as
  live unless you set the flag.
- Confirm before: `erase_entities`, `explode_entity` (replaces the
  original), boolean ops (consume input solids), `trim_entity` (erases the
  removed piece), `replace_text`, `detach_xref`, `merge_layers`,
  `audit_drawing` with fix, `delete_layout` (takes the sheet and
  everything on it), `save_drawing` (Save As can overwrite and
  downsave), and any folder-batch write.
- `execute_command` is Pro, hidden unless the machine opts in with
  `MCP_CONNECTOR_ENABLE_COMMAND_EXEC=1`, and hard-blocks code-loading and
  shell verbs (NETLOAD, SCRIPT, SHELL, …). If it refuses, that is by
  design - say so.
- Two refusals look alike; tell them apart by the message. "requires MCP
  Connector for AutoCAD Pro" is a licence. "READ-ONLY session" is a
  deliberate lock: the user turns it off with `MCPCONNECTOR_READONLY`, or
  cannot if an administrator policy set it. Relay either; do not improvise
  around them.

## Fast paths (intent to first tool)

| The user wants to | Start with |
|---|---|
| see the drawing state | get_drawing_info, get_entity_count, list_layers |
| find entities | get_entities (filtered), select_by_filter |
| find or fix text | find_text, replace_text, count_text_patterns |
| draw 2D | create_line, create_polyline, create_circle, create_hatch |
| put content on a sheet | any creation tool with `space: "<layout name>"` |
| read a sheet | get_entities / find_text / get_entity_count with `space` |
| set up sheets | duplicate_layout, set_page_setup, list_viewports, set_viewport, set_viewport_layers |
| existing / proposed sheets from one model | list_layer_states, save_layer_state, restore_layer_state, set_viewport_layers |
| hatch an area by pointing at it | create_hatch with seedX/seedY; create_boundary for the outline |
| floor areas (GIA) | measure_areas, label_areas (with `schedule` for a table) |
| centreline boundary to internal face (GIA) | create_boundary with `inset`, or offset_entity with `direction: "inward"` |
| annotative text, dims and leaders | set_annotative (with `scales`), list_annotation_scales |
| a new text or dimension style | create_text_style, create_dimension_style |
| remember a set of entities by name | save_selection_set, recall_selection_set, list_selection_sets |
| a drawing register from title blocks | export_drawing_register |
| stamp a revision on sheets | add_revision_to_layouts, then update_drawing_register |
| check a clip actually landed | get_clip_boundary |
| resize an opening or room | stretch_entities |
| hatch behind linework, text over a wipeout | set_draw_order, create_wipeout |
| mark a revision | create_revcloud |
| doors and windows from a dynamic library | get_dynamic_block_properties, set_dynamic_block_properties, insert_block with `dynamicProperties` |
| swap every instance of one block for another | replace_block - keeps position, rotation and attributes by tag. Do not erase and re-insert |
| rename a block without breaking its references | rename_block |
| OS extract, aerial, survey PDF under a plan | attach_image, attach_pdf_underlay, clip_underlay, set_image_display |
| red-line boundary width, rounded corners | edit_polyline (setWidth, filletAll) |
| text and dimension standards | set_text_style, set_dimension_style, match_properties |
| title-block QA across sheets | find_text with `includeAttributes: true` and `space: "all"` |
| something went wrong | rollback_checkpoint / undo, then read back |
| model 3D | create_3d_box, create_extrusion, boolean_union |
| edit geometry | move_entities, offset_entity, fillet_entities, trim_entity (with a removal point) |
| dimension and annotate | create_dimension_linear, create_leader, create_table |
| manage layers | list_layers, create_layer, set_layer_properties, merge_layers |
| work with blocks | list_blocks, insert_block, get_block_attributes, set_block_attribute |
| work with xrefs | list_xrefs, attach_xref, reload_xref, repath_xrefs |
| plot one sheet, or a sheet set from one drawing | plot_to_pdf (`layoutNames` in order, or `plotAllLayouts`) |
| plot a folder | dwg_folder_to_pdf |
| copy content between drawings at the same coordinates | copy_to_original_coordinates (lands in the source's space; `targetSpace` to override) |
| extract data / BOM | block_attribute_extract, layer_report_to_excel |
| update title blocks across a project | title_block_update |
| audit a project | drawing_health_report, xref_report, find_proxy_objects |
| clean a folder of DWGs | batch_process_folder (purge/audit/downsave), purge_zero_length |
| return to the same view later | save_view, restore_view |
| see the result | zoom_extents / zoom_object, capture_screenshot |

## Workflows

### Sheet set from a template
1. `duplicate_layout` the template sheet per drawing; `rename_layout` to
   the sheet number.
2. `list_viewports` on the new sheet, then `set_viewport` with the model
   window (`viewCenterX/Y`) and `scale: "1:100"`, `locked: true` last.
3. `set_viewport_layers` to freeze what that sheet must not show; save
   the combination with `save_layer_state` if it will be reused.
4. Title-block text: `find_text` / `replace_text` with
   `includeAttributes: true` and `space` set to the sheet.
5. `get_page_setup` once; `set_page_setup` only if the template is wrong.

### Area takeoff
`measure_areas` with `points` inside each room or `handles` of closed
boundaries; `label_areas` with `names` and a `schedule` when the figures
must appear on the drawing. Point mode subtracts interior loops (islands)
and says so: read `outerArea`, `netArea`, `islandCount` and the islands
beside `area`, and the top-level `note`. A furniture block inside a room
is an island, so for GIA pass `outerLoopOnly: true` and use the outer
figure. Areas come back in m² on a millimetre or metre drawing - do not
convert again.

### Area takeoff to the internal face (GIA)
The traced boundary follows whatever it was drawn along, usually wall
centrelines; GIA is measured to the internal face. `create_boundary` with
`inset` (half the wall thickness) does both in one call and reports the
traced area and the inset area, leaving the inset loop. On a loop you
already have, `offset_entity` with `direction: "inward"` does the same -
never a signed distance, because which side that lands on depends on how
the loop was drawn. Then `measure_areas` with `outerLoopOnly` for the
figure. An inward offset that would collapse the loop is refused, so a
refusal means the distance is too large, not that the tool failed.

### Annotative annotation
Two things must be true or the annotation disappears: the object carries
the annotative flag, AND it holds a scale representation for every scale it
should show at. `set_annotative` does both - pass `scales: ["1:50","1:100"]`
and it adds any the drawing does not have. It refuses the flag with no
scales, because that hides the object everywhere. `list_annotation_scales`
gives the names it accepts. Styles carry the flag too: `create_text_style`
and `create_dimension_style` take `annotative` (set a dimension style's
overall scale to 0 as well).

### Drawing register and revisions
1. `export_drawing_register` builds the register from title-block
   attributes - one row per drawing + layout. Fields are matched to tags
   automatically; check the `columnMapping` it reports and override with
   `columnMapping` if it guessed wrong. Use `blockNameFilter` when the
   sheets carry more than one attributed block, or you get a row per block.
2. `add_revision_to_layouts` stamps revision, date and description. dryRun
   is TRUE by default - read the before/after list first. **Read
   `fieldsNotWritten`**: many title blocks keep the revision letter on a
   separate revision block, so a run can legitimately write only the date.
   Run it again with a different `blockNameFilter` for the rest.
3. `update_drawing_register` patches the existing register in place,
   keeping its formatting, adding an issue column headed with the date.
   dryRun first and read the plan: `matchedBy` says whether rows were keyed
   on drawing number or on file name, and `unmatched` names what missed.

### Folder-batch maintenance (the headline Pro workflow)
1. Confirm folder, file pattern, and recursion with the user.
2. Run with `dryRun: true`; summarise the per-file report.
3. On approval, re-run `dryRun: false` - into `outputFolder` when offered.
4. Check `success`, then report ok / failed counts with the failed file
   names and reasons.

### Trim and extend
`trim_entity` needs `boundaryHandles` plus a point on the piece to remove
(`removeX`, `removeY`); the only case that needs no point is a cut between
two edges where the middle piece goes. If it refuses as ambiguous, supply
the point rather than retrying. `extendBoundaries: true` lets an edge that
stops short still cut. `extend_entity` takes an optional `extendStart`;
omit it to extend whichever end reaches a boundary first.

### Drawing clean-up
audit_drawing (report first), purge_drawing, then verify with
get_drawing_info counts before/after.

### Title block / revision update
title_block_update scans **paper space per layout** - title blocks are not
in model space. dryRun first, then live.

### Plot and read back (sheet verification)
`plot_to_pdf` plots at the layout's SAVED page setup: plot area Layout,
saved scale (1:1 for a sheet), saved paper size. That is the true 1:1 plot,
so do not pass `plotArea` or `scale` to "make sure"; pass them only to
override the setup for one plot (`scale: "fit"`, `plotArea: "extents"` for
a model-space check). `extents` is computed from the entities as they are
now, so a stray entity that has since been erased does not shrink the plot.
Overrides come back in `applied`; each page reports `plotType`, `scale` and
`paperSize`. Several layouts go into one PDF with `layoutNames` (your
order) or `plotAllLayouts` (tab order); layouts on different paper sizes
are written as one PDF per layout with a `note`. The user's tab is
restored afterwards. Read the PDF back with `attach_pdf_underlay` or an
external reader when the sheet must be proven, and check `fileWritten`
and `sizeBytes` before reporting.

### Seeing the drawing
`capture_screenshot` returns with the PNG on disk (`fileWritten`,
`sizeBytes`); read it back to check a result visually. If the reply says
`pending: true` the fallback path ran - wait, then confirm the file exists
before reading it. `plot_to_pdf` also returns `fileWritten` and
`sizeBytes` and is the better check for a sheet.

## Gotchas

1. **Handles, not indices.** Never fabricate a handle; source them from a
   query.
2. **Z defaults to 0** on creation tools; colours are ACI 1–255 (ByLayer if
   omitted); angles are degrees.
3. **Locked layers are skipped, not failed** - batch tools count and report
   them. Layer 0, Defpoints, and xref-dependent layers (`|` in the name)
   cannot be renamed or merged.
4. **Space is explicit.** Reads and creation tools default to model
   space; pass `space` (a layout name, `current`, or `all` for reads) to
   work on a sheet. `select_by_filter` searches every space by default
   and labels each hit. Copies, offsets, arrays, explodes and trims stay
   in the space their source occupies. Unknown layout names are refused
   with the list of layouts that exist - use that list, do not guess.
5. **Modification tools work from any layout.** fillet, chamfer, break,
   lengthen, join, align, and convert_to_polyline switch to the space
   their targets are in and restore the layout afterwards - no need to
   change tab first.
6. **Non-Latin text.** Drawings exported from Revit store text outside
   the code page as `\U+XXXX` escapes; natively drawn ones do not.
   `find_text` and `replace_text` match either form and report
   `encoding` per hit; replacements are written in the form the entity
   already used. Search in the user's own language - no escaping needed.
7. **Hatches.** Pass several `boundaryHandles` for a face with openings:
   the largest is the outer loop, the rest are islands. `boundaryPoints`
   hatches a polygon with no boundary entity. Patterns: predefined, a
   .pat on the support path, or one that exists only inside hatches in
   the drawing (a Revit export's FP_* patterns) - the definition is copied
   from the resident hatch and `patternSource` says `drawing:<handle>`.
   `list_hatch_patterns` lists what resolves, with `hatchCount` and an
   `exampleHandle` per resident pattern. An open boundary or unknown
   pattern is refused by name.
8. **Annotation sizes.** Pass `textHeight` and `arrowSize` to
   `create_leader`, and `height` to `create_mtext`, in drawing units at
   the sheet scale (250 in a millimetre model plotted 1:100 reads as
   2.5 mm). MText `height` reads back as the character height.
9. **Batches run long** (up to 30 minutes server-side). Warn the user; do
   not re-issue a call because it feels slow.
10. **After a licence change, reconnect the MCP client** - the edition is
    read at startup. A read-only toggle shows up when the client refreshes
    its tool list; a tool that has vanished from the list was withheld, not
    broken.
11. **Free tier is strictly read-only.** If a mutating tool is missing or
    refuses with a licence message, the seat is unlicensed - relay it, do
    not improvise.
12. An empty result is a valid answer, not an error.
13. **Zoom tools read the view back.** `zoom_extents`, `zoom_window` and
    `zoom_object` return the centre, height, width and extents AutoCAD
    actually shows and fail if the view did not take; `zoom_object` takes
    `handles` and lists unresolved ones in `notFound`. Trust the read-back,
    not the request.
14. **Transparency and the plot flag round-trip.** `create_layer`,
    `set_layer_properties` and `change_entity_properties` write
    `transparency` (0-90 %; -1 = ByLayer on entities); `list_layers` returns
    `plot` and `transparency`, `get_entity_properties` returns
    `transparency`. Verify with the read, not the success flag.
15. **`detect_units` says what it measured.** `evidenceBasis` is `extents`
    normally and `entitySizes` when the extents are implausible (one entity
    parked far from the rest) - the guess then comes from the sampled
    element sizes and the recommendation says so. `currentSetting` and
    `heuristicGuess` are separate; read the confidence `band` before acting.
16. **`get_entity_properties` on a viewport** returns centre, size, scale
    and view centre, the same figures as `list_viewports`.
17. **Unknown block names come back with `suggestions`** (near misses one
    edit away, shared prefixes); a block that exists with no references is
    `found: true, count: 0`.
18. **Named selection sets are stored in the drawing, not as a GROUP.**
    They survive save and reopen and do not change how picking behaves.
    `recall_selection_set` sets the pickfirst selection, so the next tool
    that reads the selection acts on it; an erased member is reported in
    `missingCount` rather than dropped.
19. **`get_selected_geometry` reads what is selected right now.** Recall a
    set or ask the user to select, then call it. It covers lines, arcs,
    circles, ellipses, polylines, splines, blocks (with attributes), hatches
    (with loop vertices), text, MText, dimensions and wipeouts.
20. **Clips: verify with `get_clip_boundary`.** `clip_underlay` takes a
    `boundaryHandle` to clip to a polyline you already drew. `invert` does
    not apply to images - the response says so rather than echoing it back.
21. **Plot a sheet set from one drawing** with `plot_to_pdf` and
    `layoutNames` (your order) or `plotAllLayouts`. Layouts on different
    paper sizes cannot share one PDF, so those come back as one PDF per
    layout with a `note`.

## Response style

No play-by-play - do not announce each tool call or narrate steps as you
go. Work, then report the outcome once: what changed, with counts,
handles, layer names, output file paths. Short bullets. Speak mid-task
only to confirm a destructive action or report a failure. If a step
failed, show the error and stop.
