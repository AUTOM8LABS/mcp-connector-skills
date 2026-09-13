---
name: 3dsmax-connector
description: Operate a live 3ds Max scene through AUTOM8LABS MCP tools with filtered reads, typed operations and bounded verification. Use for connector queries and authorized scene changes. Do not use for general image generation or visual-design instruction.
---

# AUTOM8LABS 3ds Max operator

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
| Scene identity | `get_scene_info` |
| Units and available host features | `get_host_capabilities` |
| Scene totals and heavy objects | `get_scene_statistics` with `top_count` |
| Find target objects | `list_objects` with `name_pattern`, `category`, `layer`, and `limit` |
| Read several objects | `get_object_properties` with exact `names` |
| Dimensions | `measure_objects` for the named set |
| Related compatible operations | `run_batch` with `calls` and `stop_on_error` |

Object tools commonly take an array of exact names. Reuse names returned by
the scene query; do not invent nodes, material names or modifier indices.
Use `list_modifiers` only for a stack involved in the requested change.

System units and display units are distinct. Read both before numerical work;
changing `set_units` is a scene mutation, not a harmless query. Verify requested
dimensions using `measure_objects` rather than relying on appearance.

`run_batch` has exclusions, including file operations, rendering and undo.
Inspect its live schema, then inspect each returned result. Never assume a
stopped batch rolled back earlier successes. Renderer-specific tools require
the corresponding renderer capability; retain the renderer the user selected.

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
