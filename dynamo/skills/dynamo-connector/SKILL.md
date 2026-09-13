---
name: dynamo-connector
description: Inspect and operate a live Dynamo graph through AUTOM8LABS MCP tools using scoped graph reads, batched edits and evaluated-output checks. Use in Revit or Dynamo Sandbox. Do not use for Grasshopper or ordinary Python tasks.
---

# AUTOM8LABS Dynamo operator

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
| Host and run mode | `ping` |
| Graph IDs and structure | `get_graph_state` with `summary`, `scope`, and `includeWires` as needed |
| Locate an installed node | `search_nodes` with a narrow query and `limit` |
| Port definitions | `get_node_info` |
| Repeated edits | `create_nodes`, `connect_nodes`, `set_values`, `delete_nodes` accept batches |
| Evaluate and check data | `run_graph`, then `get_output_values` on the intended output/port |

Start with `summary` for orientation; expand only the nodes whose ports,
wires or errors matter. Use returned IDs and exact `creationName` values from
node search. Inspect ports instead of guessing indices from display names.

An input's stored value is not its evaluated output. In Manual mode, an edit
does not prove that downstream data changed. Verify the intended terminal
outputs after an authorized evaluation; cap previews using `maxItems`.

In Automatic mode, graph edits can recompute immediately and connected nodes
may change the Revit model or files. Establish run mode and effects before
editing. Never run a graph just to satisfy an inspection-only request.

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
