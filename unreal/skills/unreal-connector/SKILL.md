---
name: unreal-connector
description: Operate a live Unreal Editor through AUTOM8LABS MCP toolsets with targeted registry discovery, scoped reads and verified actions. Use for the connector and its editor integration. Do not use for general rendering advice or Unreal code-only work.
---

# AUTOM8LABS Unreal Engine operator

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

| Need | Toolset and operation |
|---|---|
| Connector state | `MCPConnectorTools`: `ping`, `get_status` |
| Level summary | `ArchvizLevelTools`: `get_level_summary` |
| Light inventory | `ArchvizLightingTools`: `get_light_inventory` |
| Camera inventory | `ArchvizCameraTools`: `get_cameras` |
| BIM identifiers/properties | `BimIntakeTools`: `get_bim_metadata_keys`, `find_actors_by_bim_metadata`, `get_bim_metadata` |
| Render progress/output | `ArchvizRenderTools`: `get_render_status`, `get_render_image` |

The editor registry can contain AUTOM8LABS and other editor toolsets. Identify
the provider and discover only the relevant toolset's schema; do not request
the entire registry for each action. Use the identifiers returned by the
editor and preserve actor-path context rather than guessing from labels.

Inspect numeric units in each operation's schema; coordinates, light values
and camera settings are not interchangeable. Limit BIM metadata queries to
the keys and actors needed. Prefer a summary over an actor-by-actor inventory.

A render submission may return before the job finishes. Reuse its job identity
and poll status at the indicated interval; do not submit another render to
check progress. Verify the completed output when accessible. Saving a level,
importing assets, activating variants and changing collision require the
user's authorized scope; this skill does not prescribe visual settings.

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
