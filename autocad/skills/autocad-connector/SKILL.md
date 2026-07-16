---
name: autocad-connector
description: Operating doctrine for driving AutoCAD through the MCP Connector for AutoCAD (AUTOM8LABS). Use whenever the user wants to query, draw, modify, annotate, plot, or batch-process DWG files via MCP tools - entity queries, layers, blocks, xrefs, dimensioning, PDF plotting, folder-wide batch maintenance. Trigger on "in AutoCAD", "DWG", "drawing", "layers", "xrefs", "title block", "plot to PDF", or any request naming AutoCAD entities or commands. ALWAYS load this skill before the first AutoCAD tool call of a session, even for a small query.
---

# AutoCAD Connector - operating doctrine

You drive a live AutoCAD session through the AUTOM8LABS MCP tools. Single-
document tools act on the open drawing; the Management Pack tools batch-
process whole folders through a side database without touching the open
drawing. Free tier is read-only inspection (28 tools); Pro unlocks creation,
modification, annotation, plotting, and the folder-batch pack. Supported
hosts: AutoCAD 2022–2027.

## Session start

1. Start with `get_drawing_info` - path, units, extents, layer and entity
   counts. It doubles as the connection check; do not spend a separate
   `ping`. If it fails, AutoCAD is not running or the connection is off -
   use `ping` then to diagnose, and the user can check the
   `MCPCONNECTOR_STATUS` command or the AUTOM8LABS ribbon.
2. **Units before geometry.** Coordinates are in current drawing units per
   INSUNITS, not a fixed unit. On survey or unitless DWGs run
   `detect_units` before creating or measuring anything.

## Token discipline

- **Page, don't dump.** `get_entities` defaults to limit 500 with an
  offset - filter by type, layer, or bounding box, and never assume one
  page was everything.
- **Target, don't scan.** `select_by_filter`, `find_text`,
  `count_text_patterns`, and `get_entity_by_handle` beat unfiltered lists.
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

## Safety

- **Batch tools default to `dryRun: true`.** Keep that default on the first
  pass, review the per-file report with the user, then re-run with
  `dryRun: false`. Prefer `outputFolder` over in-place overwrite.
- **Exception: `purge_drawing` defaults `dryRun` to false** - treat it as
  live unless you set the flag.
- Confirm before: `erase_entities`, `explode_entity` (replaces the
  original), boolean ops (consume input solids), `replace_text`,
  `detach_xref`, `merge_layers`, `audit_drawing` with fix, `save_drawing`
  (Save As can overwrite and downsave), and any folder-batch write.
- `execute_command` is Pro, hidden unless the machine opts in with
  `MCP_CONNECTOR_ENABLE_COMMAND_EXEC=1`, and hard-blocks code-loading and
  shell verbs (NETLOAD, SCRIPT, SHELL, …). If it refuses, that is by
  design - say so.

## Fast paths (intent to first tool)

| The user wants to | Start with |
|---|---|
| see the drawing state | get_drawing_info, get_entity_count, list_layers |
| find entities | get_entities (filtered), select_by_filter |
| find or fix text | find_text, replace_text, count_text_patterns |
| draw 2D | create_line, create_polyline, create_circle, create_hatch |
| model 3D | create_3d_box, create_extrusion, boolean_union |
| edit geometry | move_entities, offset_entity, trim_entity, fillet_entities |
| dimension and annotate | create_dimension_linear, create_leader, create_table |
| manage layers | list_layers, create_layer, set_layer_properties, merge_layers |
| work with blocks | list_blocks, insert_block, get_block_attributes, set_block_attribute |
| work with xrefs | list_xrefs, attach_xref, reload_xref, repath_xrefs |
| plot one drawing | plot_to_pdf (prefer dwg_folder_to_pdf for reliability at scale) |
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
4. Report processed / skipped / failed counts. Files open in AutoCAD are
   skipped by design - list them so the user can close and re-run.

### Drawing clean-up
audit_drawing (report first), purge_drawing, then verify with
get_drawing_info counts before/after.

### Title block / revision update
title_block_update scans **paper space per layout** - title blocks are not
in model space. dryRun first, then live.

## Gotchas

1. **Handles, not indices.** Never fabricate a handle; source them from a
   query.
2. **Z defaults to 0** on creation tools; colours are ACI 1–255 (ByLayer if
   omitted); angles are degrees.
3. **Locked layers are skipped, not failed** - batch tools count and report
   them. Layer 0, Defpoints, and xref-dependent layers (`|` in the name)
   cannot be renamed or merged.
4. **The single-doc `plot_to_pdf` is a command macro** and can ignore parts
   of its own schema; `dwg_folder_to_pdf` uses the real plot engine - point
   it at one file if you need reliability, and name `Model` in `layouts` to
   plot the Model tab.
5. **Batches run long** (up to 30 minutes server-side). Warn the user; do
   not re-issue a call because it feels slow.
6. **After a licence change, reconnect the MCP client** - the tool list is
   served at startup.
7. **Free tier is strictly read-only.** If a mutating tool is missing or
   refuses with a licence message, the seat is unlicensed - relay it, do
   not improvise.
8. An empty result is a valid answer, not an error.

## Response style

No play-by-play - do not announce each tool call or narrate steps as you
go. Work, then report the outcome once: what changed, with counts,
handles, layer names, output file paths. Short bullets. Speak mid-task
only to confirm a destructive action or report a failure. If a step
failed, show the error and stop.
