---
name: dynamo-connector
description: Operating doctrine for driving Dynamo through the MCP Connector for Dynamo (AUTOM8LABS). Use whenever the user wants to build, inspect, edit, run, fix, or explain a Dynamo graph via MCP tools - node creation and wiring, sliders, code blocks, Python scripts, package nodes, and Dynamo for Revit workflows. Trigger on "in Dynamo", "Dynamo graph", ".dyn", "wire these nodes", "run the graph", or any request naming Dynamo nodes or packages. ALWAYS load this skill before the first Dynamo tool call of a session, even for a small query.
---

# Dynamo Connector - operating doctrine

You drive a live, already-open Dynamo graph through the AUTOM8LABS MCP tools.
There are 11 tools. The product thesis is the verification loop: not "it ran"
but "it produced the right data, and I read it back to prove it".

## Session start

1. `ping` first. It reports the host (`hostApp`: Revit vs Sandbox), Dynamo
   version, `runMode`, and whether a workspace is open. There is no
   open/new/save in this version - you always operate on the graph the user
   already has open. If no workspace is open, ask them to open one.
2. Recommend **Manual** run mode for the session so every evaluation is an
   explicit, observable `run_graph`. If `ping` reports Periodic, `run_graph`
   will refuse - ask the user to switch mode.
3. Revit and Sandbox share one pipe. If both are open, `ping`'s `hostApp` and
   `processId` tell you who answered - confirm it is the host the user means.

## Build discipline

- **Batch everything.** One `create_nodes` call for all nodes, one
  `connect_nodes` call for all wires. Arrays in, per-item results out. Never
  create or wire one node per call.
- **Resolve names before creating.** `search_nodes` returns the exact
  `creationName` that `create_nodes` needs. Skip the search only for the
  built-in aliases: `number slider`, `integer slider`, `number`, `string`,
  `boolean`, `code block`, `python script`, `watch`. Ambiguous names throw.
- **Introspect ports before wiring.** `get_node_info` (by canvas `id` or by
  library `name` pre-creation) lists every port with name and default. Wire
  by port **name** when you know it - a name beats a guessed index.
- **Never trust a set - read it back.** The known v0 risk is a slider or
  input occasionally reading back its default after `set_values`. After any
  value change that matters, verify via `get_output_values` before building
  on it.
- **Verify runs with data, not adjectives.** After `run_graph`, call
  `get_output_values` on the terminal node(s) and check the actual numbers,
  strings, and geometry summaries. `run_graph` returning
  `evaluationSucceeded` is not the finish line.
- **Code blocks are DesignScript**, statements end with `;`. Setting `code`
  regenerates the node's ports (unbound identifiers become inputs) -
  re-read state after setting code before wiring to it.
- **Python defaults to CPython3.** First run cold-boots the engine (~10–15 s)
  - that is expected, not a hang.
- **Canvas x/y are pixels, not model units.** Omit them and nodes auto-place
  in a clean column to the right of the graph. Finish authored graphs with
  `auto_layout` so the canvas reads like a human made it.

## Identifiers and limits

- Every node, note, group, and wire id is a **GUID string** sourced from
  `create_nodes` responses or `get_graph_state`. Never invent one.
- `get_graph_state` caps at ~200 nodes; `get_output_values` defaults to 25
  items / depth 4. When a response says `truncated: true`, say so - do not
  pretend you read everything. Use `summary: true` or `scope` to narrow.

## Safety

- Every mutation is undoable (Ctrl-Z), and batch deletes are one undo step -
  remind the user of this.
- `delete_nodes` removes nodes and their wires; `set_values` replaces code
  wholesale; `connect_nodes` with `replace: true` drops the existing wire.
  Confirm before deleting or rewriting work the user authored by hand.
- **Revit element binding:** re-running a graph that creates Revit elements
  *replaces* those elements (Dynamo trace binding), it does not duplicate
  them. AIs re-run far more than humans - warn the user, and prefer a
  scratch model for creation experiments, never live project work.
- Inside Revit, evaluation marshals through the Revit idle loop - raise
  `timeoutSeconds` on `run_graph` for big graphs.

## Operating loop

1. `ping` - orient (host, run mode, workspace).
2. `get_graph_state` - ids, ports, values, warnings.
3. `search_nodes` / `get_node_info` - resolve names and ports.
4. `create_nodes` then `connect_nodes` - batched; `set_values` to tune.
5. `run_graph` - explicit evaluation.
6. `get_output_values` - prove the result with real data.
7. On problems: diagnose from `run_graph`'s `problems[]` (per-node state and
   messages), repair with `set_values` / `connect_nodes`, re-run.
8. `auto_layout`, then `delete_nodes` on scaffolding.

## Gotchas

1. Dynamo 3.x only (Revit 2025 → 3.3, Revit 2026 → 3.6.x, Sandbox 3.x).
   Dynamo 2.19 / Revit 2024 is not supported.
2. Package nodes (archilab, Rhythm, Clockwork, …) resolve live if installed -
   `search_nodes` is the truth, not memory.
3. There are no screenshot tools in this version. "Show me" means reading
   values back, and telling the user to look at the canvas.
4. Manual element selection (`Select Model Element`) is unverified - prefer
   category collectors such as `All Elements of Category`.
5. "Cannot reach Dynamo" almost always means Dynamo is not running or the
   package sits under the wrong Dynamo version folder.

## Honesty rules

- No play-by-play - build, run, verify, then report the outcome once with
  the verifying numbers. Speak mid-task only to confirm a destructive
  action or report a failure.
- Report evaluation problems verbatim from `problems[]`; do not narrate
  success you did not verify with `get_output_values`.
- If a capability is missing (open/save graphs, screenshots, node lacing),
  say so and give the user the manual route in Dynamo.
