---
name: grasshopper-connector
description: Operating doctrine for driving Grasshopper through the MCP Connector Grasshopper (AUTOM8LABS). Use whenever the user wants to build, inspect, run, fix, or explain Grasshopper definitions via MCP tools - parametric modelling, attractor patterns, script components, data trees, Kangaroo/physics, facades, towers, stairs, baking to Rhino, or Grasshopper running inside Revit via Rhino.Inside. Trigger on "in Grasshopper", "GH definition", "parametric", ".gh file", "bake to Rhino", or any request naming Grasshopper components or plugins (Kangaroo, Ladybug, LunchBox). ALWAYS load this skill before the first Grasshopper tool call of a session, even for a small query.
---

# Grasshopper Connector - operating doctrine

You drive a live Grasshopper canvas through the AUTOM8LABS MCP tools. These
habits are the difference between one clean build and six debug loops. They
were all learned in real sessions; skip one and you repeat the same mistake.

## Session start

1. `ping` first. It tells you the host (standalone Rhino, or Revit via
   Rhino.Inside - see `references/rhino-inside-revit.md` when it reports
   Revit), whether a document is open, and the object count.
2. If several CAD connectors are available and the user's ask is generic,
   confirm Grasshopper is the intended host before building anywhere.
3. Before pattern work (stars, attractors, membranes, towers, facades,
   stairs, math surfaces), call `get_recipe` - no topic lists the index.
   A recipe replaces hours of parameter and data-tree discovery. If
   `get_recipe` is not in your toolset, proceed without it.

## Build discipline

- **Introspect before wiring.** `get_component_info` on any component whose
  ports you have not seen this session. Same-name components exist in
  different categories (Maths "Square" vs Grid "Square") - pass `category`.
- **Never trust "it solved" - read it back.** After every tree-shaping or
  batch operation, `get_output_values` and check branch × item counts
  against what the geometry implies (10×10 grid → 10 branches of 10).
  Trees fail silently; a wrong shape caught late is an archaeology dig.
- **Numbers prove claims.** Radius set to 7.5 → read 7.5 back. Rounded
  corners → perimeter arithmetic. Twist eased → per-frame angle deltas
  small at ends, peaking mid-span. Report the numbers, not adjectives.
- **Sliders: size ranges deliberately** to the intended use (an attractor
  slider must span the whole grid plus margin). Centre panels/plates with
  a ±half domain - a bare number casts to a corner-anchored 0..N domain.
- **Angles are radians at every component input.** Degrees only on slider
  labels. All numeric string parsing is InvariantCulture.
- **Script components write IronPython 2** (no f-strings). Geometry inputs
  may arrive as Guids - coerce before use. Edit the existing component
  (`edit_script_component`) rather than recreating it.
- **Destructive actions need consent.** Clearing a canvas with someone's
  work on it: say what is there and ask first. Every mutation you make is
  one named undo step - remind the user Ctrl-Z always works.

## When things go wrong

- Solve first, then diagnose from data: `run_solution` pins red components
  by id; `get_component_info` on the culprit; repair with
  `connect_components` replace - not a rebuild.
- Physics/Kangaroo results that look wrong: check for NaN in the raw
  points BEFORE trusting any derived metric (NaN comparisons read as a
  lying zero). Then check goal-strength ratios. Full rules:
  `get_recipe kangaroo-membrane`.
- A definition someone else made: `open_definition` +
  `get_definition_summary` before touching anything.
- Every tool except `ping` returning a purchase message means the trial
  or licence has lapsed - relay that plainly and stop; do not retry or
  improvise around it.

## Showing results

- Capture the viewport after geometry changes; capture the canvas after
  layout changes. Tell the user the image is inside the tool-result
  expander if their client hides it.
- For presentation shots see `references/capture-and-demo.md`.
- Before a demo capture: `auto_layout`, then group and NAME the stages
  (`manage_groups`) - a tidy labelled canvas reads as craftsmanship.

## Honesty rules

- No play-by-play - build, solve, verify, then report the outcome once
  with its numbers. Speak mid-task only to confirm a destructive action
  or report a failure.
- Report limitations plainly: an open loft is not a solid; a deformation
  rig is not mesh reconstruction; corner-anchored panels are not centred.
  Offer the fix, do not paper over it.
- If a capability is missing (camera framing, preview control), say so and
  give the user the manual route in Rhino/Grasshopper.
