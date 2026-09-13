---
name: autocad-connector
description: Operate live AutoCAD drawings through AUTOM8LABS MCP tools with filtered queries, batches and result verification. Use for connector inspection and authorized drawing or folder operations. Do not use for generic drawing advice or another CAD host.
---

# AUTOM8LABS AutoCAD operator

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
| Drawing identity and units | `get_drawing_info`; `ping` for connection/capability diagnosis |
| Totals | `get_entity_count` grouped by type or layer |
| Locate entities | `get_entities` filtered by type/layer |
| Inspect one known entity | `get_entity_by_handle` |
| Related operations in one round trip | `run_batch`, respecting the exclusions returned by `ping` |
| An authorized folder operation | `batch_process_folder`; confirm input/output scope |

Entity handles are identifiers, not array positions. Keep them in the form
returned by the connector. Specify model space or the relevant layout when
the tool supports `space`; don't infer one from the visible tab alone.

`run_batch` takes `calls` containing `tool` and `params`. Its `stopOnError`
option controls continuation, not automatic rollback. Read completed, failed
and skipped entries. Drawing open/save, plotting, undo and folder tools have
batch restrictions; use `ping`'s `batch.excluded` and the current schema.

Folder operations can affect files outside the active drawing. Use supported
previews and a separate output folder when that matches the user's task.
Verify drawing units and coordinate space before numerical edits.

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
