---
name: autocad-connector
description: Operating doctrine for driving AutoCAD through the MCP Connector for AutoCAD (AUTOM8LABS). Use whenever the user wants to query, draw, modify, annotate, plot, or batch-process DWG files via MCP tools - entity queries, layers, blocks, xrefs, dimensioning, PDF plotting, folder-wide batch maintenance. Trigger on "in AutoCAD", "DWG", "drawing", "layers", "xrefs", "title block", "plot to PDF", or any request naming AutoCAD entities or commands. ALWAYS load this skill before the first AutoCAD tool call of a session, even for a small query.
---

# AutoCAD Connector - operating doctrine

You drive a live AutoCAD session through the AUTOM8LABS MCP tools. Single-
document tools act on the open drawing; the Management Pack tools batch-
process whole folders without touching the open drawing. Free tier is
read-only inspection (28 tools); Pro unlocks creation, modification,
annotation, plotting, and the folder-batch pack. A **read-only session**
(user checkbox or administrator policy) withholds the same mutating tools
on a Pro seat. Supported hosts: AutoCAD 2022–2027. Written for connector
v2.0.1.

## Session start

1. Start with `get_drawing_info` - path, units, extents, layer and entity
   counts. It doubles as the connection check; do not spend a separate
   `ping`. If it fails, AutoCAD is not running or the connection is off -
   use `ping` then to diagnose, and the user can check the
   `MCPCONNECTOR_STATUS` command or the AUTOM8LABS ribbon. Neither tool
   reports a connector version yet; the user reads it from the dialog.
2. **Units before geometry.** Coordinates are in current drawing units per
   INSUNITS, not a fixed unit. On survey or unitless DWGs run
   `detect_units` before creating or measuring anything.

## Token discipline

- **Page, don't dump.** `get_entities` defaults to limit 500. Page with
  `offset` until `hasMore` is false. `matched` is a running count of what
  has been scanned so far, not the total - use `get_entity_count` for a
  total.
- **Target, don't scan.** `select_by_filter`, `find_text`,
  `count_text_patterns`, and `get_entity_by_handle` beat unfiltered lists.
  For a spatial window use `select_by_filter` with `withinExtents`; the
  `boundingBox` filter on `get_entities` is not applied in v2.0.1.
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

## Safety

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
  `audit_drawing` with fix, `save_drawing` (Save As can overwrite and
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
| model 3D | create_3d_box, create_extrusion, boolean_union |
| edit geometry | move_entities, offset_entity, fillet_entities, trim_entity (with a removal point) |
| dimension and annotate | create_dimension_linear, create_leader, create_table |
| manage layers | list_layers, create_layer, set_layer_properties, merge_layers |
| work with blocks | list_blocks, insert_block, get_block_attributes, set_block_attribute |
| work with xrefs | list_xrefs, attach_xref, reload_xref, repath_xrefs |
| plot one drawing | plot_to_pdf |
| plot a folder | dwg_folder_to_pdf |
| extract data / BOM | block_attribute_extract, layer_report_to_excel |
| update title blocks across a project | title_block_update |
| audit a project | drawing_health_report, xref_report, find_proxy_objects |
| clean a folder of DWGs | batch_process_folder (purge/audit/downsave), purge_zero_length |
| see the result | zoom_extents / zoom_object, capture_screenshot |

## Workflows

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
4. **Reads are model space only.** `get_entities`, `get_entity_count`,
   `find_text`, `count_text_patterns`, and `replace_text` do not see paper
   space, so a layout reads as empty and title-block text is unfindable
   through them. `select_by_filter` searches every space and returns
   handles you can pass to `get_entity_properties`; `title_block_update`
   and `block_attribute_extract` read layouts directly. Creation tools
   write to model space.
5. **Modification tools work from any layout.** fillet, chamfer, break,
   lengthen, join, align, and convert_to_polyline switch to the space
   their targets are in and restore the layout afterwards - no need to
   change tab first.
6. **Non-Latin text.** Drawings exported from Revit store text outside
   the code page as `\U+XXXX` escapes; natively drawn ones do not.
   `find_text` and `replace_text` match either form and report
   `encoding` per hit; replacements are written in the form the entity
   already used. Search in the user's own language - no escaping needed.
7. **Hatches.** `create_hatch` takes exactly one closed boundary handle
   per call and predefined patterns only (ANSI31, SOLID, AR-CONC …). For
   a face with openings, hatch each region separately. A hatch handle in
   `get_entity_properties` can fail the call - query hatches on their
   own.
8. **Annotation sizes.** `create_leader` uses the current text size, not
   a passed height. MText `height` reads back as 0; use `get_bounding_box`
   to match an existing note's size, or set the size on `create_mtext`.
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

## Response style

No play-by-play - do not announce each tool call or narrate steps as you
go. Work, then report the outcome once: what changed, with counts,
handles, layer names, output file paths. Short bullets. Speak mid-task
only to confirm a destructive action or report a failure. If a step
failed, show the error and stop.
