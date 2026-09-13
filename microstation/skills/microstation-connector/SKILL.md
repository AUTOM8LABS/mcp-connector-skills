---
name: microstation-connector
description: Operate a live MicroStation DGN through AUTOM8LABS MCP tools with counts, bounded scans and verified changes. Use for model inspection and authorized connector operations. Do not use for generic references, levels or another host.
---

# AUTOM8LABS MicroStation operator

## Use the connected tools

Use this skill only with the matching AUTOM8LABS connector. Tool names below
are logical names; use the names and schemas exposed by the current client.
Discover deferred tools when needed. The live schema and capability response
take precedence over examples. Missing tools can reflect connection, build,
edition, or session policy; identify the reported cause.

Establish the target host and document once. Reuse that context until a
document switch, reconnect, or unexpected result. The user's instructions
take precedence over this guide; operate within their authorized scope.

## Spend context on the requested result

- Start with a count or summary when it can answer the question. Otherwise
  filter the query before requesting individual records.
- Request only needed fields, bounded previews, and supported result limits.
  Reuse returned identifiers instead of rediscovering the same objects.
- Use a purpose-built bulk operation for repeated work. A generic batch is
  appropriate only when its schema permits the chosen calls and dependencies.
- Load only the tool schemas needed now. Avoid whole-catalogue dumps, repeated
  screenshots, or full model/graph reads after every small edit.
- A capped preview is not a complete inventory. If completeness is requested,
  use supported continuation, narrower disjoint queries, or an export and
  report the total and any omissions. Do not invent pagination parameters.

## Connector operations

| Need | Tools and scope |
|---|---|
| Active model and units | `get_model_info` |
| File and model inventory | `get_file_info`, `list_models` |
| Element totals | `count_elements` filtered by level/type |
| Element identifiers | `scan_elements` with level/type filters and `limit` |
| Detail for a known element | `get_element_info` or `get_element_properties` |
| Spatial query | `find_elements_in_range` with a bounded range and `limit` |

Queries operate on the active model. Keep DGN file, model and element identity
together; a model switch invalidates assumptions about the target set.

Use the master units and conversion factors returned by `get_model_info`.
`find_elements_in_range` coordinates are master units. Follow each tool's
schema for other inputs; do not assume millimetres across DGN files.

Keep ElementIds in the representation required by the exposed schema. Avoid
rounding large IDs during client-side conversion. Query only needed property
groups, and use bulk tools only when the installed connector exposes them.
File conversion and reference-path changes need explicit input/output scope.

## Verify and finish

Sequence dependent calls on the live host. Read per-item failures and skipped
results; a batch response is not proof that every item changed. After a timeout,
inspect the affected state or job status before repeating a write.

Use a targeted read to check the requested outcome. An inspection request does
not authorize cleanup or saving. Establish scope before destructive or shared
changes and ask only when that scope is unresolved or not already authorized.
Prefer typed connector tools; any scripting fallback must be available and
authorized for the same task.

Report the result, affected count, verification and unresolved failures briefly.
Paths returned by tools belong to the host machine. Claim a local file or image
was inspected only when it was accessible and actually read.
