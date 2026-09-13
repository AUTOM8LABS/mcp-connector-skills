---
name: grasshopper-connector
description: Inspect and operate a live Grasshopper definition through AUTOM8LABS MCP tools using scoped reads, batched graph changes and data-tree verification. Use in Rhino or Rhino.Inside.Revit. Do not use for Dynamo or direct Rhino work without Grasshopper.
---

# AUTOM8LABS Grasshopper operator

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
| Definition overview | `get_definition_summary` |
| Canvas IDs | `get_canvas_state` with `summary`, `scope`, and `includeWires` |
| Find a component | `search_components`; use an exact result/GUID to resolve ambiguity |
| Ports for an existing component | `get_component_info` |
| Build a defined set together | `apply_graph` with keyed components and wires |
| Repair known components | `create_components`, `connect_components`, `set_values` |
| Solve and inspect selected outputs | `run_and_verify` with `reads`; cap branches/items |

Component type GUIDs identify library types; instance IDs identify objects on
the canvas. Use the appropriate returned identifier. Preserve branch paths and
list structure when passing data trees; a compact preview can omit branches.

`apply_graph` reports per-item failures and may solve at the end (`runAfter`).
Repair the reported failures rather than recreating successful components.
`run_and_verify` can combine an authorized solve with output reads using
`maxBranches` and `maxItemsPerBranch` to bound the preview.

Solving or changing a definition can affect Rhino, Revit or files through its
components. Check those effects before execution. A successful solve is not
proof of the requested geometry; inspect the selected outputs. Baking and
saving are separate actions that need the user's authorized scope.

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
