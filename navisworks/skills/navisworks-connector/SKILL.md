---
name: navisworks-connector
description: Operate a live Navisworks coordination model through AUTOM8LABS MCP tools using counts, filtered searches and verified actions. Use for model queries and authorized connector operations. Do not infer Navisworks from a clash request when another host is intended.
---

# AUTOM8LABS Navisworks operator

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
| Document overview | `get_model_info` |
| Appended source files | `list_models` |
| Property totals | `count_items`, with grouping and conditions |
| Find model items | `find_items` with property filters |
| Detail for a known item | `get_item_properties` |
| Existing clash tests | `list_clash_tests` |

Use `count_items` for a property census rather than one search per combination.
Use item IDs returned by this document's queries; do not synthesize hierarchy
paths or reuse IDs after source models change. Request property detail for
the affected items instead of traversing the entire selection tree.

Model units and source-file units may differ. Read the applicable values before
using distances or coordinates. Keep an inspection of existing clash results
separate from running tests, changing statuses, creating viewpoints or
publishing; perform those only within the user's requested scope.

When a result is capped, use the tool's supported filtering or export path for
complete data. Report a disconnected or unsupported capability rather than
substituting a different host.

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
