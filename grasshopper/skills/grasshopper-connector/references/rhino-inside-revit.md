# Grasshopper inside Revit (Rhino.Inside.Revit)

Read this when `ping` reports the host as Revit, or the user mentions
Rhino.Inside / RiR / driving Revit through Grasshopper.

## What is true in this mode

- Same plugin, same 24 tools, same pipe - the canvas just lives inside
  Revit's process. `ping` reporting Revit + a PID is the proof of mode.
- RiR components (Revit element queries, category pickers, bake-to-Revit)
  appear in `search_components` like any installed plugin. Introspect their
  ports before wiring - their param types are exotic.

## Hard rules

1. **One host at a time.** Standalone Rhino and Revit-hosted Grasshopper
   listen on the SAME pipe name. If both are open, requests route to
   whichever grabbed the pipe - close standalone Rhino before an RiR
   session and tell the user why.
2. **Definitions full of RiR components only load correctly inside Revit.**
   Opened in standalone Rhino they show missing-component placeholders -
   do not diagnose that as file corruption.
3. **Transactions and long solves.** RiR operations that create/modify
   Revit elements run inside Revit's transaction machinery - solves can be
   much slower than pure-GH ones, and a failed solve may leave warnings on
   the RiR components. Read component runtime messages before retrying.

## Known rough edges (harvest new ones into this file)

- `set_values` may not reach RiR's custom pickers (element/category
  selectors expect human interaction). Work around by wiring from value
  lists / panels where the component accepts text or ids, and say when a
  step genuinely needs a human click in Revit.
- Element binding: re-running a definition can duplicate or rebind Revit
  elements depending on the RiR component's binding mode. Prefer a small
  test run (one element) before a batch, and tell the user what re-solving
  will do to already-created elements.
