# Captures, presentation shots, and demo assets

Read this when the user wants screenshots, close-ups, poster/LinkedIn
material, or complains an image is not visible.

## What the capture tools do today

- `capture_canvas` = the Grasshopper canvas as PNG. `capture_viewport` = a
  Rhino viewport, zoom-extents on visible geometry. Neither can frame a
  close-up region yet - do not pretend otherwise. For a tight shot, give
  the user the manual route: orbit in Rhino, pick a clean display mode
  (Arctic reads like a clay render), and use Rhino's ViewCaptureToFile at
  full resolution for final assets. Chat captures are for verification;
  poster assets deserve full res.
- Some clients render tool-result images only inside the collapsed
  tool-call chip. If the user says "where is the screenshot", point them at
  the expander before re-capturing.

## Making a shot read well

1. **Declutter previews.** Grasshopper previews every component - planes
   render as gridded squares and drown the geometry. There is no preview
   tool yet: tell the user to Ctrl+A on the canvas → right-click → untick
   Preview, then re-enable it on just the final components. (Or bake and
   use pure Rhino geometry.)
2. **Bake finals to named layers** so the user can screenshot without
   Grasshopper running, and so layers can be toggled per shot.
3. **Tidy the canvas before canvas shots**: `auto_layout`, then
   `manage_groups` with NAMED stages (Input, Attractor, Twist, Output…).
4. Two-variant comparisons (before/after, low/high slider): capture both
   states and report the changed parameter values alongside.

## Demo narrative beats that land

- Build → verify with read-back numbers → iterate via set_values (not a
  rebuild) → show. The verification IS the demo: read values, prove the
  claim, then show the picture.
- A deliberate break + diagnose + one-wire repair is the strongest single
  sequence this product demos. Keep it in the tape.
