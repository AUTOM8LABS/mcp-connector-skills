---
name: navisworks-connector
description: Operating doctrine for driving Autodesk Navisworks through the MCP Connector for Navisworks (AUTOM8LABS). Use whenever the user wants to query aggregated models, run or review clash tests, manage selection and search sets, viewpoints, appearance overrides, TimeLiner, quantification, or NWD/NWF/NWC publishing via MCP tools. Trigger on "in Navisworks", "clash", "NWD", "NWF", "federated model", "search set", "viewpoint", or any coordination-review request. ALWAYS load this skill before the first Navisworks tool call of a session, even for a small query.
---

# Navisworks Connector - operating doctrine

You drive a live Navisworks Manage session through the AUTOM8LABS MCP tools.
Tools act on the open, aggregated document. Free tier is read-only inspection
plus view navigation (26 tools); Pro unlocks selection writes, sets,
viewpoints, clash authoring and review, appearance overrides, exports, and
publishing. Supported hosts: Navisworks 2024–2027.

## Session start

1. Start with `get_model_info` (title, model count, extents). It doubles
   as the connection check; do not spend a separate `ping`. If it fails,
   Navisworks is not running, no model is open, or the connector is off -
   use `ping` then to tell connection trouble from a missing model, and
   the user can check MCP Status on the AUTOM8LABS ribbon.
2. A model must be open for everything except `ping` and `measure_points`.
3. `get_units` next - **all coordinates, tolerances, and bounding boxes
   are in the document's display units**, and there is no conversion
   layer.
4. `list_models` shows the aggregated source files.

## Identifiers

- **Model items** are addressed by session-scoped string ids of the form
  `"{modelIndex}:{pathId}"` (e.g. `"0:1a2b"`), harvested from
  `get_selection_tree`, `get_current_selection`, `find_items`, or
  `get_item_ancestors`. Never invent one, and **never cache ids across a
  file reopen or an `append_model`** - re-query.
- **Sets and viewpoints** are addressed by name or GUID (GUID wins), from
  `list_selection_sets` / `list_saved_viewpoints`.
- **Clash tests** by name; individual results by name or zero-based index.

## Finding things

`find_items` is the workhorse. It matches property values as shown in the
Navisworks **Properties window** - `category` + `property` + `value` (e.g.
category `Element`, property `Name`), with `match` of equals / contains /
wildcard. Multiple criteria go in a `conditions` array and are ANDed. It is
not a query language - mirror what the Properties panel shows.

## Token discipline

- Respect the defaults: `find_items` and `get_current_selection` cap at 200,
  `get_clash_results` at 100, `get_selection_tree` at depth 1 / 500 nodes.
  Narrow the search instead of raising caps; walk the tree one level at a
  time.
- Exports write files and return paths - relay the path, never the content.
- Verify small: a count or the one changed item, not a re-dump.

## Safety

- **`save_document` saves in place over the opened file.** For a model that
  has never been saved, or when in doubt, prefer `export_nwd` /
  `export_nwf` to a new path. Confirm before any in-place save.
- Confirm before: `delete_selection_set`, `delete_saved_viewpoint`,
  `append_model` (permanently aggregates into the scene),
  `run_all_clash_tests` (recomputes every test - can take a long time),
  and any export to a path that already exists (files are overwritten).
- Appearance changes are recoverable: `unhide_all` reverses hide/isolate,
  `reset_appearances` clears overrides - but both are scene-wide bulk
  clears, so warn if the user had their own overrides.

## Fast paths (intent to first tool)

| The user wants to | Start with |
|---|---|
| see what is loaded | get_model_info, list_models, get_units |
| find elements | find_items; get_item_properties to inspect |
| browse the hierarchy | get_selection_tree (shallow, then deepen) |
| work with the UI selection | get_current_selection, set_current_selection (Pro) |
| review clashes | list_clash_tests, get_clash_test_summary, get_clash_results |
| author clash tests | create_search_set ×2, create_clash_test, run_clash_test (Pro) |
| walk a clash visually | focus_on_clash (free), get_clash_result_image (Pro) |
| triage clashes | set_clash_result_status, assign_clash_result, add_clash_comment, group_clash_results (Pro) |
| issue a clash report | export_clash_report (Pro) |
| colour / isolate | override_appearance, isolate_items; reset with reset_appearances / unhide_all (Pro) |
| viewpoints | list_saved_viewpoints, create_saved_viewpoint, apply_saved_viewpoint (Pro) |
| 4D / 5D data | list_timeliner_tasks, get_quantification_summary |
| publish or hand off | export_nwd, export_nwf, publish_nwd, export_nwc (Pro) |
| extract data | export_properties, export_model_tree (Pro, CSV) |
| show the user | zoom_to_items, zoom_to_selection, set_camera, capture_view_image (Pro) |

## Clash workflow (the headline Pro chain)

1. `create_search_set` for each side (or reuse existing sets from
   `list_selection_sets`).
2. `create_clash_test` (tolerance is in model units - check `get_units`;
   default 0.001).
3. `run_clash_test`, then `get_clash_results` (paged).
4. Triage: `group_clash_results`, `assign_clash_result`,
   `set_clash_result_status` (new / active / reviewed / approved /
   resolved), `add_clash_comment` (comment statuses have no "reviewed").
5. `export_clash_report` (CSV/HTML) and report the path.
6. To walk clashes with the user: `focus_on_clash` per result.

## Gotchas

1. **File semantics matter - say them plainly.** NWD is a self-contained
   snapshot; NWF references live source files and stays current; NWC is the
   aggregation cache; `publish_nwd` makes a *locked, read-only* deliverable
   with embedded metadata, distinct from `export_nwd`.
2. **Long operations block.** Everything runs on the Navisworks main
   thread - a big `run_all_clash_tests` or export means latency, not
   failure. Do not re-issue the call.
3. Colours are RGB 0–255; transparency runs 0 (opaque) to 1 (invisible);
   coordinates are right-handed, Z-up.
4. `get_quantification_summary` errors if the model has no quantification
   project - that is a valid "none set up" answer.
5. After a licence change, reconnect the AI client - the tool list is
   served at startup.
6. Free tier is read-only plus navigation. If a Pro tool refuses with a
   licence message, relay it; do not improvise.
7. An empty result is a valid answer, not an error.

## Response style

No play-by-play - do not announce each tool call or narrate steps as you
go. Work, then report the outcome once: clash counts by status,
set/viewpoint names, export paths. Short bullets. Speak mid-task only to
confirm a destructive action or report a failure. If a step failed, show
the error and stop; do not narrate success you did not verify.
