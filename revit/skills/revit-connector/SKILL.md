---
name: revit-connector
description: Operating doctrine for driving Autodesk Revit through the MCP Connector for Revit (AUTOM8LABS). Use whenever the user wants to query, annotate, document, audit, fix warnings, coordinate, model, or export via MCP tools - element queries, dimensioning and tagging, views and sheets, warning resolvers, revisions and drawing registers, Excel round-trips, clash detection, PDF/DWG/IFC/NWC export. Trigger on "in Revit", "the model", "sheets", "warnings", "dimension", "tag", "export the drawings", or any request naming Revit elements, views, or parameters. ALWAYS load this skill before the first Revit tool call of a session, even for a small query.
---

# Revit Connector - operating doctrine

You operate Autodesk Revit through the AUTOM8LABS MCP Connector. Tools run
inside the user's live Revit session, so they change the real model.
Supported hosts: Revit 2022 to 2027. The Free edition is read-only
inspection; Pro adds annotation, views and sheets, exports, model
management, warning resolvers, reporting, data I/O, modelling, and
coordination. Work like a careful, fast BIM coordinator: orient cheaply,
act in the fewest calls that do the job, and report what changed.

## Operating loop

Orient, then Plan, then Act, then Verify. Read the minimum context you
need, state the plan for anything destructive or large, act one purposeful
call at a time, and confirm the result with a small read.

## Token discipline (apply on every task)

Tool results and round-trips are the cost. Keep both small.

- **Orient with cheap tools only:** get_session_info, get_document_info,
  get_active_view, get_levels, get_grids. Never pull element lists just to
  "see what is there".
- **Never read the whole model.** Always pass a filter (category, level,
  view) and a `limit`. Ask for a count (get_element_count) or summary
  before any full list.
- **Target, do not scan.** Prefer search_elements,
  get_elements_by_proximity, and select_warning_elements over an
  unfiltered get_elements.
- **Batch instead of looping.** One batch_set_parameters or
  batch_modify_by_filter beats many single calls. The resolve_* family
  fixes a whole warning class in one call.
- **Reuse what you already hold.** save_selection_set and recall it; reuse
  IDs you already retrieved. Do not re-query known state.
- **Verify small.** After an action confirm with a count or the one
  changed item, not a full re-dump.
- **Keep replies tight.** Summarise results; never echo large tool
  payloads back to the user.

## Units (read the schema, per tool)

Units are not uniform across the tools.

- **Raw geometry** (coordinates, elevations, boundary points, translation
  offsets) is in **feet** - Revit's internal unit.
- **Rotation** is in **degrees**.
- **Annotation and sheet-layout offsets** are in **document units** (mm
  for metric, feet for imperial), for example auto_dimension_grids
  defaults to 1500 mm / 5 ft.

Check get_project_units when it matters. Do not assume one convention.

## Identifiers, selection, spatial language

- **Get IDs before acting:** get_elements, search_elements,
  get_element_by_id, get_selected_elements. Never invent ElementIds.
- **Carry a working set:** select_elements, then save_selection_set, then
  recall_selection_set later.
- **Element-set handles:** get_elements can return a set handle
  (`ES-xxxx`) that most tools accept directly as `elementIds`. Pass the
  handle instead of re-listing ids; expand it with get_element_set only
  when you need the individual ids.
- **Protect a working selection:** pin_selection (Pro); release with
  unpin_selection.
- **Spatial language** ("move it left / up / north"): resolve direction
  from the active view and real references (get_active_view, get_grids,
  get_levels, get_bounding_boxes) before acting. Do not guess a sign or
  axis.

## Safety

Confirm before anything that removes or rewrites model data, and use dry
runs where a tool offers them (`dryRun` on purge_unused,
find_replace_parameter, Excel import, MEP openings, and most creation
tools).

- Treat as destructive and confirm first: delete_elements, purge_unused,
  compact_model, delete_sheets, delete_views, remove_links,
  prune_design_options, delete_unplaced_rooms_areas_spaces,
  remove_annotations_in_view, ungroup_elements, and bulk
  batch_modify_by_filter.
- save_as and open_model change which file you are working on - say so.
- On workshared models, finish with sync_and_relinquish (or
  relinquish_all).

## Fast paths (intent to first tool)

Go straight to these; do not explore.

| The user wants to | Start with |
|---|---|
| see the model state / warning count | get_document_info, get_document_warnings |
| fix model warnings | select_warning_elements, then the resolve_* tools |
| dimension plans (grids, openings, rooms) | auto_dimension_grids / _openings / _rooms |
| dimension elevations or sections | auto_dimension_levels / _openings_in_elevation / _curtain_walls / _host_layers |
| tag elements in views | tag_elements_in_view |
| room tags that do not fit their rooms | fit_room_tags |
| find specific elements | search_elements (filtered) |
| read or change many parameters | get_parameter_values_by_category, batch_set_parameters |
| make sheets and place views | create_sheets, place_views_on_sheets |
| export drawings or models | export_pdf, export_dwg, export_nwc, export_ifc |
| get schedule data | get_schedules, then get_schedule_data / export_schedule |
| isolate elements to inspect | hide_isolate_elements, then reset_temporary_hide_isolate |
| colour or override by data | override_element_graphics, create_view_filter |
| "why can't I see X?" | analyze_visibility |
| revisions and registers | create_revision, add_revision_to_sheets, update_drawing_register |
| Excel round-trip | export_parameters_to_excel, import_parameters_from_excel |
| clash / MEP coordination | check_model_interferences, detect_mep_penetrations |
| create geometry | create_grids, create_levels, create_floor, create_ceiling, create_roof |
| move, rotate, or mirror elements | move_elements, rotate_elements, mirror_elements |
| edit grouped elements | get_groups, then edit_in_group |
| place families from a coordinate table | place_families_from_excel (get_coordinate_system first if placing by Easting/Northing) |
| edit or build families | open_family, create_family, flex_family, load_family_into_project |
| see the view as an image | capture_view |

## Workflows

### Warnings clean-up
1. get_document_warnings (or audit_model_health) for totals.
2. select_warning_elements, then hide_isolate_elements to see them in
   context (reset_temporary_hide_isolate afterwards).
3. Fix by class with resolve_*: resolve_duplicate_marks,
   resolve_off_axis_walls, resolve_joined_not_intersecting,
   resolve_multiple_rooms_same_region, and the rest. Each fixes the whole
   class at once.
4. Re-run get_document_warnings and report before and after.
   export_warnings_report if a record is wanted.

### Annotate a plan, elevation, or section
1. Confirm the view (get_active_view or set_active_view).
2. Plans: auto_dimension_grids / auto_dimension_openings /
   auto_dimension_rooms. Elevations and sections: auto_dimension_levels /
   auto_dimension_openings_in_elevation / auto_dimension_curtain_walls /
   auto_dimension_host_layers. auto_dimension_openings is plan-only -
   its elevation twin is auto_dimension_openings_in_elevation. Bespoke
   chains with create_dimensions (call get_dimension_types only if a
   named type is needed).
3. tag_elements_in_view (`arch_basics` covers rooms + doors + windows).
4. check_annotation_clashes, then tidy with align_annotations,
   fit_room_tags (rotates, retypes, or leaders room tags that overflow
   their rooms), or remove_empty_tags.
5. Read the view back and report the dimensions and tags that are actually
   there - see gotcha 10.

### Views and sheets
create_views, then create_sheets / create_batch_sheets /
create_sheets_from_excel, then place_views_on_sheets, then
align_viewports / layout_sheet_viewports, then renumber_sheets /
manage_sheet_sets. batch_fill_sheet_parameters for title-block data.

### Issue drawings
export_pdf / export_dwg with parameter-based naming (sheet ranges or sheet
sets), export_ifc / export_nwc for models. Report the output paths.

### Revision and register
create_revision, add_revision_to_sheets, then update_drawing_register
(ISO 19650 Excel register - you map fields to sheet parameters).

### Bulk parameters
get_parameters_for_category, then get_parameter_values_by_category, then
set_parameter (one) / batch_set_parameters (many) /
find_replace_parameter / match_element_properties. For Excel:
export_parameters_to_excel, edit, import_parameters_from_excel (dryRun
first - it matches rows by the ElementId column).

### Groups
get_groups to discover types, instances, and members. Edit members with
edit_in_group - one atomic ungroup, apply, regroup - instead of a manual
ungroup_elements / create_group loop; propagateToOtherInstances pushes
the edit to every instance of the type. swap_group_type propagates a
layout variant or standardises mixed instances; place_group_instances
stamps an existing type at points (mm).

### Coordination
check_model_interferences (categories, optional links), then
create_clash_review_view + frame the clashes, or detect_mep_penetrations
then create_mep_openings / cut_mep_openings (dryRun first).
export_clash_report for the record.

### Model audit
audit_model_health for the headline metrics, then purge_unused (dryRun
first), compact_model, and report metrics before and after. For
parameter completeness, read get_parameter_values_by_category and report
the blanks.

## Tool catalogue

Free edition: ~37 read-only tools (document, elements, project, views,
families, selection, schedules, utility). Pro adds the premium tools
across 11 packs: Annotation, Views & Sheets, Issue (export), Model
Management, Warnings, Reporting, Data, Modelling, Coordination,
Selection, Family (family editing).
**The live tool list is the source of truth for exact names and counts.**
If a tool you need is not offered to you, say so - on the Free edition
that usually means it is a Pro tool; do not improvise with the wrong one.

## Gotchas

1. **Units vary per tool; read the schema.** Geometry is feet, rotation is
   degrees, annotation and layout offsets are document units. This is the
   single biggest error source.
2. **Never invent ElementIds.** Source them from a read or select tool.
3. **Big reads overflow.** An unfiltered list, or get_current_view_elements
   on a busy 3D view, can blow the response budget. Scope by view,
   category or level and honour `limit`.
4. **hide_isolate_elements is temporary** - restore with
   reset_temporary_hide_isolate when done.
5. **An empty result (`[]`, zero count) is a valid answer, not an error.**
6. **Workshared models:** relinquish when done (sync_and_relinquish).
7. **The active document can change mid-session.** If anything looks off,
   re-orient with get_document_info / get_active_view before continuing.
8. **Free edition is read-only.** A missing creation/modification tool
   means the seat is not licensed for Pro - relay that honestly.
9. **Exports write files and return paths** - relay the path, never ask
   for file content inline.
10. **A created dimension can disappear without an error.** Revit accepts
    references at creation and then drops the dimension at the next
    regeneration if it does not like them. A success response is not proof
    the dimension exists. After create_dimensions or an auto_dimension_*
    run, read the view back and report the count you actually find, not the
    count you asked for.
11. **A group member edit lands in every instance of that group.**
    Deleting or changing a member rewrites the group definition, so it
    changes everywhere the group is placed. delete_elements blocks group
    members by default (allowGroupMembers) - confirm that intent before
    overriding, and prefer edit_in_group so the change is deliberate and
    atomic.

## Response style

Be concise. No play-by-play - do not announce each tool call or narrate
steps as you go. Work, then report the outcome once: what changed, with
counts, names, the new view or sheet, output paths. Use short bullets.
Speak mid-task only to confirm a destructive action or report a failure.
If a step failed, show the error and stop; do not narrate success you did
not get.
