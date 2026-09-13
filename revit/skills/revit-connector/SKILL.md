---
name: revit-connector
description: Operate a live Revit model through AUTOM8LABS MCP tools with scoped reads, bulk operations and result verification. Use for connector queries and authorized edits. Do not use for general Revit API programming or another host.
---

# AUTOM8LABS Revit operator

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
| Identify session/model | `get_session_info`, `get_document_info` |
| Category totals | `get_element_count` |
| Find affected elements | `get_elements` with category/family/type/level filters, or `search_elements` for text |
| Inspect parameter data | `get_parameter_values_by_category`; inspect only relevant parameters |
| Set repeated values | `batch_set_parameters` with returned element IDs; inspect `dryRun` and per-item results |

`get_elements` supports `limit` and `includeParameters`; leave parameter
expansion off unless needed. Linked-document results need their `linkId`
context. Do not treat a linked element ID as an element in the host document.

Respect explicit unit fields. Bare `get_elements` lengths use Revit internal
feet; labelled `Mm`, `SqM` and `CuM` fields are metric. For measurable values
in `batch_set_parameters`, use explicit text such as `400 mm` where supported.
Do not apply one conversion rule to every tool.

`batch_set_parameters` accepts a shared value or a `values` array for different
values per element. It can partially succeed. Check failed IDs and read back
the requested values; do not retry successful items. Saving, synchronizing
and relinquishing require the appropriate user-authorized scope.

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
