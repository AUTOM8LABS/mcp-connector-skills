# Modelling playbook for the 3ds Max connector

Read this before any task that builds or repairs geometry: blocking a building from a
plan, joinery and fixtures, frames from profiles, cleaning an imported mesh, mapping
before texturing. It tells you how a working archviz modeller builds in 3ds Max and how
to do the same through the tools you have. Grounded in AUTOM8LABS field sessions on a
house-and-interiors project (real-time target, centimetre scene), checked against the
3ds Max 2024-2027 documentation and a live Max 2027 session (August 2026).

## 0. Decide the approach before touching the scene

Ask, or infer from the request, four things:

1. **Units.** `get_scene_info` reports system units. Set them with `set_units` BEFORE
   importing or building; a real-time target usually wants centimetres, a BIM-fed
   scene millimetres or metres. Every number below is scene units.
2. **Reference or freehand?** A plan, elevation or photo goes in first as a
   `create_reference_image` plane at a known width, frozen. Model against it; never
   guess a dimension you could read off a reference.
3. **Which construction family?**
   - **Primitives + Edit Poly** for walls, carcasses, boxes, fixtures: a box, then
     connect, inset, extrude, chamfer. This is 80% of architectural modelling.
   - **Splines to solids** for anything with a profile or an outline: floor slabs
     (`extrude_spline`), frames and rails (`sweep_profile`, `sweep_spline`), turned
     objects (`lathe_spline`), thin skins (Shell).
   - **Booleans** only for clean cuts through clean, closed solids (section 4).
   - **Deformers** (FFD, Noise, Bend) only on meshes that have segments to deform.
4. **Detail budget.** Model to the camera and the target. Smoothing groups and a
   1-segment chamfer read as rounded; do not add subdivisions for roundness. "We are
   doing the whole house, not showing a product."

Then `snapshot_session` (or rely on the automatic one), `list_objects`, and frame a
screenshot so you know what is there.

## 1. Reference and blocking

- **Reference planes:** `create_reference_image` with the real width (a door is about
  90 cm, an internal wall 10-12 cm if no drawing exists). Cross-check two more
  dimensions with `measure_objects` before trusting the scale. The tool freezes the
  plane and leaves it in colour; keep it renderable off. Elevations are the same tool
  with `orientation front/left`.
- **Block walls as boxes.** One box per wall run at the true height, converted to
  Editable Poly, grown by extruding faces (`execute_maxscript` with
  `polyop.extrudeFaces`). Keep the extra cuts at door and window positions; they
  align later openings.
- **Round every value.** 37.8 becomes 40; wall thickness is one standard (12 cm
  internal, 40-45 cm external) for the whole project unless the drawing says
  otherwise. 1-2 cm does not matter for visualisation.
- **Openings:** delete the face, cap the border. Doors and glazing are separate
  objects, never cut into the wall with a Boolean.
- **Floor slab:** trace the wall footprint as a closed spline (`create_spline`,
  `closed: true`) offset by the cladding allowance, then `extrude_spline` 10 cm.
  Use an outline offset for even distance on angled walls; moving lines by hand
  does not give equal depth.
- **Verify with numbers, not eyes:** `measure_objects` with two names returns the
  centre distance and the bounding-box gap; use it the way a modeller uses the tape.

## 2. The modifier stack discipline

- **Keep the base parametric** and test edits in an Edit Poly modifier on top
  (`add_modifier edit_poly`). Collapse (`collapse_stack`) only when the result is
  right; parametric history is gone after that and it is not undoable by Ctrl-Z.
- **Order matters.** Deformers need segments beneath them; mapping sits above
  geometry edits; Shell and Chamfer go before creasing; Symmetry after the half is
  finished. A finishing chamfer goes on last, then the object is collapsed.
- **Give deformers something to deform.** FFD, Noise, Spherify, Bend do nothing on a
  1-segment box. Set `segments` on `create_primitive` or add a Subdivide.
- **Instance modifiers across siblings** (one edit propagates); make unique only where
  a piece must differ. Copy a proven modifier from one object to the next rather than
  re-typing values.
- **Naming and layers as you go:** `rename_objects` with a pattern
  (`Wall_Living_01`), `create_layer` + `move_to_layer` per assembly (WALLS, FRAMES,
  JOINERY, FLOOR, REF, STAIRS, POOL), `set_object_properties wirecolor` by class.
  `move_to_layer` needs the layer to exist first.
- **Reset XForm** whenever an object has been rotated, mirrored or scaled and BEFORE
  it is attached to anything: scale back to 100%, rotation to 0, transform baked into
  the mesh. Only the base object needs it; objects attached to it inherit. Then put
  the pivot where the next operation needs it (`set_pivot bottom` for anything that
  sits on a floor, `center` before mirroring or rotating in place). The typed route
  is `prepare_for_mapping` with `clear_mapping: false, collapse: false`; the script
  route is `ResetXForm n; collapseStack n`.
- **Typed modifier surface today:** `add_modifier` takes bend, twist, taper, shell,
  turbosmooth, edit_poly, uvw_map, noise, symmetry, lattice, smooth, relax, push,
  skew, with a `properties` map applied per property; `set_modifier_property` edits
  by 1-based stack index (`list_modifiers` first). Everything else (Chamfer, Slice,
  FFD, Normal, Normalize Spline, Quadify Mesh, Retopology, Mesh Cleaner, Sweep custom
  sections, UVW XForm, Boolean modifier, Array modifier) is `execute_maxscript`
  `addModifier n (Class())` with the property names in section 9.

## 3. Primitives and Edit Poly: the daily verbs

Through `execute_maxscript` on an Editable Poly (`convertToPoly n` first):

- **Connect** loops at typed offsets to place cuts; **inset** per polygon group for
  equal gaps (a chamfer on the dividing edge gives unequal gaps; inset does not);
  **extrude** faces along local normals (`polyop.extrudeFaces n faces amount`);
  **bridge** facing borders to join walls; **cap** open borders; **split** edges
  to separate door slabs; **detach as clone** (`polyop.detachFaces n faces
  delete:false asNode:true`) to derive a new part from an existing face so it
  inherits the exact size.
- **Derive, do not draw.** Every panel of a cabinet comes from the carcass base;
  every door leaf from the frame; the second wardrobe from the first (copy, rotate 90,
  pull the end vertices). The wall footprint is the seed for the floor and for
  built-in joinery ("edit the furniture, never the house").
- **Boxes over cuts.** A sink, a drawer, a recess: build it from boxes and detached
  faces, not from Boolean cuts into the carcass. Fewer cuts now means easier edits
  later.
- **Topology hygiene:** remove an edge WITH its vertices (Ctrl+Backspace in the UI,
  `polyop.deleteEdges` after `collapseVerts` by script), never leave a vertex on a
  straight edge; weld coincident vertices after every connect that lands on an
  existing edge (`weld_vertices` threshold 0.1 in cm scenes, 0.025 on thin rails);
  no coincident edges; triangles are fine on static meshes; quads where a smoother
  will run.
- **Coplanar faces are forbidden.** Offset copies by 2-4 mm; 2 mm clearance between
  glass and bead; 1 mm between water and pool floor. Z-fighting is a modelling bug.
- **Auto Smooth** (`smooth_mesh threshold 30-45`) after any cut or removal to clear
  shading artefacts; lower the threshold (20) when a corner still shows. When it
  merges groups you wanted separate, assign smoothing groups per element by script
  (`polyop.setFaceSmoothGroup`).
- **Material IDs before attaching**, on the base object before duplication: 1
  structure/wood, 2 finishing/metal, 3 glass, 4 mirror (any consistent scheme). A
  multi-material later recognises them; attaching after IDs is free, re-ID-ing 40
  doors later is not. Script: `polyop.setFaceMatID n faces id`.
- **Attach at the end** (`attach_objects`, first name survives) with the finishing
  done; a chamfer applied to a half-built assembly has to be redone.

## 4. Booleans done safely

- Booleans work when the operands are clean: closed, no open edges, no stray
  vertices, no self-intersections, Reset XForm done. "People complain it errors; it
  errors on dirty meshes." `audit_mesh` first; `weld_vertices` and `fix_normals` if
  it flags anything.
- `boolean_objects` (union, subtract, intersect) is the typed route; operands are
  consumed and the result is collapsed to Editable Poly so operations chain. A closed
  spline profile + `extrude_spline` + one subtract has proven more reliable than a
  union of a box and a rotated cylinder (the union silently dropped the cylinder in a
  field session).
- Since 3ds Max 2024 the **Boolean modifier** (`BooleanMod`) supersedes the ProBoolean
  and Boolean compound objects: it lives in the stack, chains operands, and has an
  OpenVDB voxel method (`method`) that copes with mesh errors the mesh method cannot;
  2027 adds recursive welding for cleaner output. Use it by script when the typed
  tool's result is dirty. ProBoolean still exists for old scenes; do not teach it as
  the current tool.
- Alternatives to a Boolean that give cleaner topology: a Slice modifier (planar or
  radial, with cap) for a straight cut; ShapeMerge to project a closed spline onto a
  surface and delete the inside; connect + delete + cap for a rectangular opening.
- Verify by re-reading `faces_before/after` and a screenshot; a Boolean that "worked"
  but left the operand in place has not worked.

## 5. Splines to solids

- **Extrude** (`extrude_spline amount, segments, cap`): closed spline gives a solid,
  open spline a surface. The spline stays editable underneath; `closed_spline: false`
  in the reply is the warning that you extruded a surface.
- **Lathe** (`lathe_spline degrees, segments, axis, align min/center/max, weld_core`):
  an XZ profile revolved about Z is a standing vase, column, tap body. Align the axis
  to the profile edge (`align: min`) or the object doubles through itself.
- **Sweep** (`sweep_profile section bar/angle/channel/tee/wide_flange/tube/pipe/
  cylinder/half_round/quarter_round`) for frames, glazing beads, skirtings, rails: the
  section rides the spline and the spline stays editable. A custom section (any closed
  spline) needs `execute_maxscript`: `sw.CustomShape = 1; sw.Shapes[1] = sectionNode`.
  Rotate the section with `angle` rather than the object when it faces the wrong way.
  `sweep_spline` (renderable-spline round/rectangular) is the lightweight cousin for
  handrails and pipes.
- **Shell** (`add_modifier shell` with `outerAmount` / `innerAmount`,
  `straightenCorners: true`, `autosmooth`): thickness for glass, panels, slabs,
  boxes built from one face. Use `innerAmount` when the outer face must stay put.
  Straighten corners on for any non-90 corner. Shell output is polygons; keep it as
  Editable Poly, never leave an Editable Mesh in the scene.
- **Spline hygiene** before any of these: all knots Corner (Bezier knots bulge a
  straight run), coincident knots welded, no open segment on a "closed" outline
  (an unwelded outline is why a Shell or Extrude comes out broken), Reset XForm on
  the shape before converting. Normalize Spline (`Normalize_Spline2`) re-spaces
  knots at a fixed length when a line was drawn with irregular clicks.
- **Spline from a mesh**: `polyop.createShape n edges smooth:false` gives a Linear
  shape from an edge loop (floor outline from wall bases, frame path from a box
  edge); set knots to Corner and drop the pivot to Z 0.

## 6. Mesh health: imported and finished geometry

Run `audit_mesh` on anything imported and on anything about to be delivered. Then:

- **Normals:** `fix_normals mode auto` measures first and only touches inverted
  objects. For a partly-flipped mesh the Normal modifier sequence is Unify then Flip,
  and a second pass if the first leaves a patch; dark or see-through faces with
  backface cull on are the tell.
- **Weld:** `weld_vertices threshold` reports before/after counts; a count that did
  not drop means the threshold was too small or nothing was coincident.
- **Cleaner:** the Mesh Cleaner modifier (`MeshCleaner`, 2021+, improved 2026)
  detects and optionally repairs holes, non-manifold edges, self-intersections,
  isolated vertices, zero-area UVs and non-planar faces. Detection is reliable; check
  a repair, and when most faces are flipped fix the normals yourself.
- **Optimise:** `optimize_mesh percent` (ProOptimizer; `percent` is the share of
  vertices to KEEP, `keep_uvs: true` by default or the mapping is destroyed). 50% is
  invisible on a dense scan, 10% is fine for a distant object, 5% shows.
- **Retopology** (`RetopologyComponent`, bundled since 2026, ReForm engine): halve a
  symmetric object with a Slice, retopologise the half with `numFacesTarget`, then
  Symmetry. Defaults work; face count is the only dial; keep UVs when mapped.
- **Quadify Mesh** (`Quadify_Mesh quadsize`) before a TurboSmooth on an n-gon mesh;
  smaller quad size means more polygons and can lock the host, start large.
- **Finishing edges (the recipe that stops renders reading as CG):** Chamfer
  modifier, amount 0.2 cm (2 mm) on furniture and metal, 0.1 on small parts, 1
  segment, minimum angle 55 so only real corners chamfer (the default 20 chamfers
  edges you did not want; drop it towards 0 only when every edge must round),
  smoothing threshold 180 with "chamfers only" smoothing, then collapse, select the
  chamfered edges and crease them to 1 so a later TurboSmooth keeps them. Test with a
  TurboSmooth, look, remove the TurboSmooth. `chamfer_edges amount, segments,
  angle_threshold` applies the chamfer with the minimum-angle pick; the smoothing
  threshold, chamfers-only smoothing and the crease are `execute_maxscript` today
  (`obj.EditablePoly.setEdgeData 1 1.0` on the edge selection).
- **Smoothing over subdivisions:** a 1-segment chamfer plus smoothing groups looks
  rounded; adding chamfer segments is polygon bloat with no visual gain.
- **Open borders:** close them even when hidden (`polyop.getOpenEdges` to find
  them). An open border is what makes Shell, Boolean and the cleaner misbehave.
- **Before hand-off:** `audit_scene` (duplicate names, missing assets, empty layers),
  `cleanup_scene`, `list_missing_assets` + `relink_assets` when textures went black,
  and `optimize_mesh` on anything a downstream app does not need dense.

## 7. Mapping and UVs

- `prepare_for_mapping` first (clear old mapping, Reset XForm, collapse) unless the
  stack must survive; a gizmo in a scaled or rotated object projects skewed no matter
  what size it is, and old mapping modifiers override anything applied beneath.
- **Box mapping covers most of architecture** (`add_uvw_map map_type box`), with
  `real_world_scale` or `set_texel_density` so boards and tiles are the right size
  across the set. `audit_uv` judges density (tiled layout) and, for baked or unique
  layouts, overlap and 0-1 fit.
- **Unwrap only organic or unique surfaces**: `auto_unwrap` (flatten by angle, relax,
  pack) or the staged `add_unwrap` > `flatten_uv` > `relax_uv` > `pack_uv`. A
  one-click flatten + pack for walls is exactly `auto_unwrap`.
- **Re-tile a region without touching the material**: UVW XForm (`UVW_Xform U_Tile,
  V_Tile, U_Offset, Rotation_Angle`) above an Edit Poly polygon selection, by script.
- **Strip junk UVs from imports** with `UVW_Mapping_Clear` (or `prepare_for_mapping`)
  before re-mapping.
- Mapping goes on AFTER the geometry is final and collapsed; Shell, Chamfer and
  Symmetry after a UVW Map will move the seams.

## 8. Symmetry, instancing, arrays

- **Symmetry** (`add_modifier symmetry` with `PlanarX/PlanarY/PlanarZ`, `PlanarFlipX`
  ..., `weld`, `threshold`): model one half, mirror the rest; since 2022 one modifier
  does several planes and a radial count, so "Symmetry X then a second Symmetry Z" is
  one modifier with two planes on. Turn `weld` OFF while the gizmo is being placed and
  weld manually after collapsing (0.1) - the automatic weld glues vertices you did not
  intend at the seam. A rotated Symmetry gizmo is also a bending tool: a straight
  cylinder becomes an elbow at 45 degrees.
- **Mirror** (`mirror_objects axis, clone`) for the opposite-hand door or wardrobe;
  the pivot must be at the object centre first or the result lands elsewhere; Reset
  XForm after any mirror. Check door swing in a top view before moving on.
- **Instances, not copies** (`clone_objects mode instance`): windows, doors, handles,
  balusters. Edit one, all follow; memory stays flat. Copies only where a piece must
  diverge.
- **Arrays:** `array_objects` (linear, radial, grid, instanced; the original counts as
  element 1) for paving, treads, fence posts; `distribute_along_spline` (even,
  end_to_end, at_knots) is the Spacing Tool: shelves along a run, panels butted end to
  end, posts at corners. In the host, the Array modifier (2023.2+, extended through
  2027 with spline, surface and phyllotaxis distribution) supersedes the old Array
  dialog; script it when the array must stay parametric.
- **Break the clone look** on anything visible in numbers: `randomize_transforms`
  and `randomize_materials` (see the rendering playbook).
- **Link, do not group,** assemblies that move together (tap to counter, floors and
  water to the pool base) so moving the parent carries the children; groups are for
  finished units that are copied whole.

## 9. Class and property names (verified on Max 2027.2)

| Task | Class / call | Properties that matter |
|---|---|---|
| Chamfer edges | `Chamfer` | `amount`, `segments`, `useminangle`, `minangle` (default 20), `smooth`, `SmoothType`, `smooththreshold`, `chamfertype`, `openchamfer` |
| Shell | `Shell` | `outerAmount`, `innerAmount`, `straightenCorners`, `autosmooth`, `autoSmoothAngle`, `segments` |
| Symmetry | `symmetry` | `PlanarX/Y/Z`, `PlanarFlipX/Y/Z`, `weld`, `threshold`, `RadialCount`, `RadialAxis` |
| Slice | `SliceModifier` | `Slice_Type` (0 refine, 1 split, 2 remove top, 3 remove bottom), `PlanarX/Y/Z`, `cap`, `Radial_Type`, `Angle1/2` |
| Normal | `Normalmodifier` | `unify`, `flip` |
| Weld | `Vertex_Weld` | `threshold` |
| Smooth | `smooth` | `autosmooth`, `threshold` |
| Optimise | `ProOptimizer` | `VertexPercent`, `KeepUV`, `KeepNormals`, `Calculate` (set last) |
| Retopology | `RetopologyComponent` | `numFacesTarget`, `useSymmetry`, `x/y/zSymmetry`, `engineType` |
| Quadify | `Quadify_Mesh` | `quadsize` |
| Mesh Cleaner | `MeshCleaner` | `repairHoles`, `repairNonManifold`, `repairSelfIntersections`, `repairIsolatedVertices`, `repairNonPlanarFaces` |
| Normalize spline | `Normalize_Spline2` | `length`, `NormalizeType`, `numKnots`, `MaxKnots` |
| Sweep | `sweep` | `CurrentBuiltInShape`, `CustomShape`, `Shapes[1]`, `angle`, `XOffset`, `yOffset`, `MirrorXZPlane`, `SmoothPath` |
| Extrude / Lathe | `Extrude`, `Lathe` | `amount`, `segs`, `capStart/End`; `degrees`, `segs`, `weldCore`, `axis` (assign the whole Matrix3) |
| Mapping | `Uvwmap`, `UVW_Xform`, `UVW_Mapping_Clear`, `Unwrap_UVW` | `maptype` (4 box), `realWorldMapSize`, `length/width/height`; `U_Tile`, `V_Tile`, `U_Offset`, `Rotation_Angle` |
| Boolean | `BooleanMod` | `Operands`, `method` (mesh or voxel), `voxelSize`; compound `ProBoolean` still present |
| Array | `Arraymodifier` | `type`, `countX/Y/Z`, `offsetX/Y/Z`, `useInstances`, `referenceSpline` |
| Noise | `Noisemodifier` (`Noise_Plus` in 2027) | `strength` (Point3), `scale`, `fractal`, `seed` |
| FFD | `FFD_2x2x2`, `FFD_3x3x3`, `FFD_4x4x4`, `FFDBox`, `FFDCyl` | control points via the sub-object |

Editable Poly by script (all verified live): `polyop.extrudeFaces`, `polyop.chamferEdges`,
`polyop.weldVertsByThreshold`, `polyop.setFaceMatID`, `polyop.setFaceSmoothGroup`,
`polyop.makeFacesPlanar`, `polyop.splitEdges`, `polyop.detachFaces ... asNode:true`,
`polyop.createShape`, `polyop.getOpenEdges`, `polyop.deleteFaces`; inset is
`n.insetType = 1; n.inset = 0.1; n.EditablePoly.buttonOp #Inset`; crease is
`n.EditablePoly.SetSelection #Edge sel; n.EditablePoly.setEdgeData 1 1.0`; auto smooth
is `n.autoSmoothThreshold = 45; n.EditablePoly.buttonOp #Autosmooth`; Reset XForm is
`ResetXForm n; collapseStack n`.

## 10. Recipes (values in cm, mapped to tools)

- **Cabinet carcass:** footprint box (depth 55-60, height 240), panels 1.5 thick by
  Shell inward, back panel kept (glass doors show it), plinth 10 high recessed 2,
  shelves as copies at 60 / 80 / up to 180, drawer side clearance 1.5, top and front
  clearance 0.2, door gaps 0.2 all round (inset 0.1 by polygon twice, delete the rim,
  bridge the borders), door edge chamfer 0.1, edge banding 0.2 by Shell outward,
  handles at door bottom + 110 or 5 in from the corner, IDs before attach, pivot at
  base, Reset XForm, layer.
- **Glazed frame:** frame members from a box edge loop turned into a Linear shape and
  `sweep_profile bar` (width 1, length 1.4 for a 1 cm glass slot), members split 0.2
  apart so light catches the joints, glass 0.6 thick with 0.2 clearance in the bead,
  patch fittings 1 thick overhanging 1 each side, chamfer 0.2 / crease 1 on all metal,
  IDs 1 frame, 2 fittings, 3 glass, pivot at the hinge for a swing door.
- **Sliding door and rail:** rail as a box, ring + connect 3 to make channels of
  equal width by inset per group, channel recess by extrude, wheels as 16-side
  cylinders 1 cm, door raised 0.5 over the rail, 1 between overlapping leaves.
- **Tap:** 16-side cylinder radius 1.2, Symmetry Y with the gizmo at 45 degrees and
  flip for each elbow (weld off, weld 0.1 after collapse), grooves as a connected loop
  extruded -0.1 with a support loop each side and a crease, base column 32 sides,
  ID metal, linked to the counter.
- **Stairs:** the parametric Stairs object (Straight, L, U, Spiral) with rail path on,
  handrail from welded cylinder sections (chamfer 0.2, crease), treads as instanced
  boards arrayed by run and rise; guide box 450 x 260 as the size reference.
- **Terrain and water:** terrain plane with about 10 cm cells and Noise in Z only
  (strength 5, scale 100), a flat plane beneath for scatter; pool water as a SOLID
  volume 1 mm above the floor, 50 x 50 connects on the top face, Noise on the top
  polygons only, normals flipped outward, linked to the pool base. A single noisy
  plane does not read as water.
- **Cladding and decking:** boards as instanced boxes along the wall via
  `array_objects` (board 8 wide, 7 thick, joint 0.5, 3 off the floor, direction per
  wall; overlap -0.5 for shiplap), or a board-generator plugin if the customer has
  one (third party, no connector equivalent): splines over planes, pattern origin at
  the creation point, close the underside, chamfer later.

## 11. Checklist before calling a model done

1. Units right (`get_scene_info`) and the reference planes frozen or on a REF layer.
2. Every object named by pattern and on a layer; wire colour by class.
3. No Editable Mesh objects; Shell and Chamfer outputs converted to poly.
4. `audit_mesh`: no inverted normals, no degenerate faces; open borders only where
   intended; welds done (counts dropped).
5. Reset XForm on everything mirrored, rotated or scaled; pivots at base or hinge.
6. No coplanar faces: 2-4 mm offsets, 1 mm water gap, 0.2 door gaps.
7. Material IDs consistent across the assembly; attached only after finishing.
8. Chamfer 0.2 / crease 1 on visible edges; TurboSmooth test passed and removed.
9. Instances where things repeat; jitter applied where the repeat is visible.
10. Mapping: `prepare_for_mapping`, box map with real-world size, `audit_uv` clean.
11. `audit_scene` clean: no duplicate names, no missing assets, no empty layers.
12. Screenshot from two angles; numbers checked with `measure_objects`.

## 12. Gotchas

- `add_modifier` friendly names are a fixed list; anything else throws. Use the
  class names in section 9 by script.
- `prepare_for_mapping` defaults to clearing mapping AND collapsing; pass
  `clear_mapping: false, collapse: false` when you only want the Reset XForm.
- `chamfer_edges angle_threshold` is the Chamfer modifier's MINIMUM ANGLE (which
  edges get chamfered), not the smoothing threshold.
- `optimize_mesh percent` is the share of vertices to keep, not to remove.
- `boolean_objects` consumes its operands and collapses the result; keep a copy
  (`clone_objects`) if the operand is needed again.
- `collapse_stack` and `save_scene` are not undoable; `snapshot_session` first.
- Symmetry's automatic weld and Shell's default outward direction are the two
  modifier defaults that most often produce a "wrong" result; set `weld: 0` and
  `innerAmount` explicitly.
- Editable Poly sub-object selection passes up the stack: a Chamfer above an Edit Poly
  with an element selected chamfers only that element; clear the selection and it
  chamfers everything.
- Creating on a hidden current layer fails in the host UI; by script use
  `LayerManager.current` on a visible layer before creating.
- Objects are created at Z 0 with the pivot at the creation point; Box parameters
  grow from that pivot, so set width and length before moving the pivot.
- A Noise, FFD or Push on a mesh without segments looks like the tool is broken; it
  is the mesh.

## 13. What has moved on across 3ds Max 2023-2027

Much published 3ds Max modelling guidance predates 2024. Checked against the Autodesk
2024-2027 documentation and a live 2027.2 session:

- **Booleans:** the Boolean modifier (2024) replaces ProBoolean and the Boolean
  compound object as the default route; OpenVDB voxel method for dirty meshes; 2027
  recursive welding. The compound objects remain for old scenes.
- **Arrays:** the Array modifier (2023.2, extended 2024, 2025, 2027) replaces the
  Array dialog; the Spacing Tool remains in the Tools menu.
- **Retopology and Mesh Cleaner:** no longer a separate download; bundled, ReForm
  engine updated in 2026 with cloud Flow Retopology; 2027 moves it to the Tools menu.
  Mesh Cleaner now repairs holes, non-manifold and self-intersecting geometry, not
  only flipped faces.
- **Slice and Symmetry** (2022): planar X/Y/Z and radial modes in one modifier, with
  capping; stacked Symmetry modifiers are one modifier now.
- **Smart Extrude** (2021.1, cut-through 2022, multi-body 2022.3, auto-smooth of
  extruded faces within 30 degrees in 2025) is present on every supported host
  (2024-2027); older "this version cannot" caveats no longer apply.
- **2027:** Smart Bevel for post-Boolean edges (follows surface shape, not topology),
  Noise Plus modifier, Extrude modifier with a chosen direction, Spline Chamfer with
  fixed radius and auto weld, Field helper for selections.
- **Chamfer modifier** defaults are unchanged (minimum angle 20, smoothing 30); its
  option names moved across 2020-2024 and are listed in section 9 as they are today.
- The third-party helper scripts a modeller typically installs (relink, scene checker,
  batch modifier edit, pivot-to-base, split elements, detach by ID, batch rename, board
  generator) map to connector tools (`relink_assets`, `audit_scene` + `cleanup_scene`,
  `find_objects_by_property` + `set_modifier_property`, `set_pivot`, `rename_objects`)
  or to the v1.4 backlog; none are needed to follow this playbook.
- The principles (derive from the base, round the numbers, finish before attaching,
  IDs before duplication, Reset XForm before attach, smoothing over subdivisions,
  no coplanar faces) are unchanged.
