# Rendering playbook for the 3ds Max connector

Read this before any task whose output is a picture: a clay study, a client
render, a turntable, a batch of cameras. It tells you what a good result needs and
how to get there with the tools you have. Grounded in AUTOM8LABS field sessions
(August 2026, 3ds Max 2027 + V-Ray 7), checked against current Chaos documentation.

## 0. Decide the job before touching the scene

Ask, or infer from the request, three things:

1. **Study or photograph?** A clay/white-card study wants one white material, a dome
   and no sun. A photograph wants textures, a physical camera, real sky, context.
2. **Interior or exterior?** They are lit differently; using one recipe for the
   other wastes the engine.
3. **Still or animation?** Stills can use every noisy-but-beautiful feature.
   Animation needs stable GI and no flicker, and effects (DOF, motion blur, glare)
   move to post.

Then check `get_render_settings` for the active renderer and decide the path:

- **Arnold** (Max default): everything below is reachable with typed tools.
- **V-Ray**: the photographic recipe is typed (connector 1.3.0): `set_renderer`,
  `create_physical_camera`, `set_camera_exposure`, `setup_hdri_environment`,
  `set_render_quality`, `set_output_exr`, `setup_clay_render`, `create_vray_material`,
  `apply_vray_texture`, `apply_dirt`, `randomize_materials`, `place_cosmos_asset`,
  `create_grass`, `create_tree_belt`, `sweep_profile`, `apply_displacement`. Each
  reports `unapplied` for anything the host refused. If V-Ray classes are absent the
  tools say so; deliver the Arnold path and never claim V-Ray features you cannot reach.

## 1. Prepare the model for the camera

- **Detail belongs where the camera looks.** Model to the viewpoint: high detail
  in the foreground, silhouettes further back. Ask what the shot is before adding
  polygons.
- **No perfect edges exist.** Chamfer what is close to camera; everywhere else use a
  round-edges shader (`VRayEdgesTex` in the bump slot, 3-5 mm on metal frames,
  10-20 mm on concrete).
- **Fine relief is displacement, not geometry.** Bump and normal maps are shading
  tricks; when the relief must break the silhouette (stone joints, lattice, grass
  mats) use a displacement modifier in 2D mode with box mapping, and collapse
  objects that share the same map into one before final render.
- **Repetition is instancing.** Trees, people, furniture, glazing units: one source,
  instanced (`clone_objects mode:instance`, `array_objects`), so an edit propagates
  and memory stays flat. Heavy meshes become V-Ray proxies.
- **Reality is chaotic.** Rows of identical objects scream CG. Jitter position,
  rotation and scale by tiny random amounts (books, chairs, glazing panes,
  boards) and vary materials across clones (4-5 variants). This is usually the last
  pass before rendering, and it is cheap.
- **Buy the library, model the architecture.** Furniture, cars, vegetation and
  people come from asset libraries (Chaos Cosmos here); spend the time on the
  building, materials and light.

## 2. Materials

Principles first, values second:

- **Observe, then photograph.** Surfaces are chaos at molecular scale; a solid colour
  carries almost none of it. Textures come from photographs. Solid colours are for
  placeholders and clay.
- **Nothing is fully matte.** Almost every architectural surface has been coated,
  polished or eroded and has a specular component. Every material gets some
  reflection at the right glossiness: plaster at the matte end, chrome at the mirror
  end, everything else between. Never 255 white; paint is 210-225.
- **One VRayMtl is enough** for nearly everything. Blend materials are for a
  genuine second layer (lacquer over wood), not the default.
- **Glass:** white reflection + white refraction + IOR 1.52-1.56 + Fresnel is a
  correct pane. Tint lives in the fog (absorption) colour, never the surface, and
  never at 255 (250 max). Turn on reflect-on-back-side for panes. Frosted glass is
  lower refraction glossiness, not SSS.
- **Translucency** in architecture is three cases: frosted glass (VRayMtl), thin
  curtains and paper (VRay2SidedMtl), and true subsurface (VRayMtl SSS or
  VRayAlSurfaceMtl) almost never.
- **Mapping:** UVW box mapping covers 95% of architecture (`add_uvw_map`). Unwrap
  only organic forms. Give the mapping real-world sizes so tiles and boards are the
  right scale.
- **Detail is dirt and wear.** Dirt collects in interior corners, wear on exterior
  edges. `VRayDirt` (ambient occlusion) with a masked radius gives both; bias it
  along Z for water streaks; combine with the base texture through a composite map.
  Paint where dirt goes with vertex paint when the automatic result is wrong.
- **Metals** are diffuse plus a large glossy specular; the glossiness alone moves
  them from brushed to mirror.
- **Randomise across clones:** hue, saturation and mapping offset per group.

Tool mapping today: Physical Material tools (`create_physical_material`,
`apply_bitmap_texture`, `add_uvw_map`) for Arnold; `VRayMtl` via script for V-Ray.
Never put a Physical Material on an object that already carries a V-Ray or Multi
material; `apply_bitmap_texture` throws on non-Physical materials.

## 3. Lighting

- **Exterior daylight:** one HDR sky photograph in a dome light (`VRayHDRI`,
  spherical mapping = `mapType 2`, in a `VRayLight type:1`, the same map as the
  environment background). It carries the sun's intensity and colour, so no extra
  lights are needed. Rotate it to put the sun where the facade wants it (raking
  across the main elevation, not flat behind the camera). Alternative: `VRaySun` +
  `VRaySky`; a scripted sun **must** get a target node or it points below the
  horizon. Arnold: `setup_sun` does sun, sky and exposure in one call.
- **Sky is never a flat colour.** An LDR sky picture gives colour but only 256
  levels of intensity and needs a separate sun; HDR/EXR is the realistic route.
- **Interior daylight:** let GI bring the outside in through the openings; do not
  put a coloured area light in the window. Model the exterior context (ground,
  neighbouring volumes, trees as low-poly stand-ins) because it bounces colour in.
  Skylight portals are legacy since the adaptive dome light; only for extreme
  occlusion.
- **Artificial light** only to reproduce a real fixture (IES profile) or a real
  studio set. Do not add invisible fill lights to fix exposure; fix it at the camera
  and in colour mapping. Texture big soft sources with a photo so their reflections
  are not flat.
- **Overcast HDRI** with no visible sun can take a modest spherical light for
  direction and shadow shape.
- **Clay study:** white material on everything, dome only, no sun; an invisible plane
  key (V-Ray: 25 m, normalised, multiplier ~18 against a dome at 1.0) gives a soft
  ground shadow so the form does not flatten into the backdrop.

## 4. Camera and composition

- **Always a physical camera** for photographic output: `VRayPhysicalCamera`
  (or Max Physical Camera for Arnold) with f-number, shutter, ISO. Sunny exterior
  starts at f/8, 1/200-1/320, ISO 100; interiors f/5.6-8, 1/30-1/60, ISO 200-400.
  The scene exposure control does not act on a plain target camera under V-Ray,
  and a physical sun/sky is ~13 stops brighter than a dome: without the physical
  camera the frame is blown or black.
- **Lens:** 24-35 mm for exteriors and rooms, 50-85 mm for details and furniture.
  Wide lenses add depth and drama; long lenses flatten and compress.
- **Height:** eye level (1.6-1.8 m) unless the shot is a deliberate aerial or
  worm's-eye. Keep verticals vertical for architecture (shift, or tilt the camera
  back to level); a slight residual convergence reads more natural than a
  perfectly corrected one.
- **Compose like a photographer, not a drawing.** Three primitives (triangle,
  rectangle, circle), diagonals from perspective lines, natural elements in the
  foreground as frame and contrast, contrast pairs (light/dark, straight/curved,
  solid/transparent, organic/synthetic), and one or two tonal ranges with one
  saturated accent rather than many colours.
- **Random shots:** the virtual camera's real advantage is free movement. Fire a
  batch of low-resolution candidates from different positions (square 1:1, 24 mm),
  pick, then reframe the winner (1.85, 2.35, portrait) at the output resolution.
  Vertical formats suit architecture; for wide-screen output, use a wide lens and
  frame the structure with dark, quiet edges.
- **Depth of field** from aperture, focal length and focus distance; motion blur
  only for a moving subject, 180-degree shutter. Both are also available in post
  from depth and velocity elements when render time matters.

## 5. Render settings and output (V-Ray 7)

- **GI:** Brute Force primary + Light Cache secondary (default). The Irradiance
  Map is deprecated; do not reach for it. Path guiding, adaptivity clamp and
  firefly removal handle the corners that used to need manual tweaks.
- **Sampler:** progressive for iteration, bucket for the final if needed. **Noise
  threshold is the quality control**: 0.02 preview, 0.008-0.01 final, lower only
  for large prints. Add the `VRayDenoiser` render element. Max render time is the
  test-vs-final lever, not quality settings.
- **Colour mapping:** render **linear** (Reinhard with burn 1.0 or linear
  multiply, gamma 2.2, "colour mapping only" mode), sub-pixel mapping OFF, clamp
  OFF, and tone-map non-destructively in the VFB (Filmic or ACES layers, or the
  OCIO/ACEScg management Max 2027 defaults to). Burning Reinhard 0.5-0.6 into the
  render is the fallback when the VFB cannot be driven; it costs highlight range.
- **Output:** 32-bit float EXR (raw, with render elements) for anything that will
  be graded; 16-bit for delivery straight from the frame buffer. Reflections,
  refractions, GI, direct light, self-illumination, Z-depth and velocity as
  elements when compositing is planned.
- **Lens effects** (bloom, glare) are a VFB layer, not a render pass; they read
  the HDR data so apply them after tone mapping, small first, build up in soft
  layers. Vignetting via the physical camera is fine; in post, a radial neutral-grey
  gradient in overlay, never a black multiply.
- **Animation:** keep GI stable (light cache with camera path, no per-frame GI for
  gently moving vegetation), move DOF/MB/glare to post, and never let settings
  change mid-sequence.
- **Cutoff / light reach** limits are speed tools; keep them off for high dynamic
  range output to avoid banding.

## 6. Context: vegetation, people, ground

- **Chaos Cosmos** is the library: `chaosCosmosAssetImportByName "Maple Tree 001"`
  (display name with spaces) downloads the textures, builds the multi-material and
  scales the proxy. Placing `.vrmesh` files by path yourself gives black, untextured
  models. Imported materials appear in the scene material list; assign by name.
  `showCosmosBrowser()` opens the library for the user when something is not yet
  downloaded. Never size a proxy from its bounding box; judge by render.
- **Trees:** trunk to penultimate branch is one body, last branches with leaves
  another (most of the polygons). Leaves are small meshes, never a single
  opacity-mapped quad: the transparent area costs the raytracer and the flat plane
  kills the specular. Use 4-5 leaf/tree variants and vary scale and rotation.
- **Scatter** with Chaos Scatter (ships with V-Ray 7; no separate licence since
  update 1): random surface distribution or a greyscale density map, scale and
  rotation variation, a seed per patch. Vary the seed rather than hand placing.
- **Lawn:** scattered grass clumps for hero ground, V-Ray fur for a quick lawn,
  a good tiling grass texture with displacement at distance.
- **Horizon:** a belt of instanced trees at 50-75 m in two staggered rows hides it;
  a subtle atmospheric haze or the HDRI's own horizon finishes it.
- **Wind** for animation: a slight random rotation on leaves and a gentle bend on
  branches with a noise controller, cycle 100-150 frames, first and last frames
  matching.
- **People** at 1.8 m, few, placed where a photographer would put them for scale.

## 6b. Tool sequence for a photographic still (typed, 1.3.0)

1. `snapshot_session` (or rely on the automatic one) so everything can be undone.
2. `set_renderer vray` if needed; `set_render_quality preview`.
3. `place_cosmos_asset` for trees, people, ground materials; `create_tree_belt` for the
   horizon; `create_grass mode fur` on the lawn; `randomize_transforms` on repeated
   elements; `randomize_materials` across clones.
4. `create_vray_material` with `round_edges_radius` for frames and steel; `apply_dirt`
   on concrete, stone and paint; `apply_vray_texture` for photographic surfaces.
5. `setup_hdri_environment` (a Cosmos sky via `place_cosmos_asset` returns the file
   path) rotated so the sun rakes the facade.
6. `random_shots` (viewport mode) on the subject; pick; `reframe_camera` to the output
   format; `create_physical_camera` at that position or `set_camera_exposure` on it.
7. `render_frame` at quarter size to judge; `set_render_quality final`;
   `set_output_exr` when grading follows; render.

## 7. Final-frame checklist

Before calling a render "final", verify each line with a screenshot or a re-read:

1. Units are real-world and every texture has a real-world mapping size.
2. Physical camera, exposure set, verticals level, lens chosen on purpose.
3. One HDR sky (or sun+sky with target), no stray default lights, no fill hacks.
4. Every material has reflection; nothing pure white; glass has Fresnel and fog.
5. Edges rounded (geometry or shader), dirt in corners, wear on edges.
6. Clones jittered and material-varied; instanced, not copied.
7. Context present: ground, horizon cover, vegetation, a person or two.
8. Colour mapping linear, sub-pixel off, clamp off; tone map in the VFB.
9. Noise threshold for the purpose; denoiser on; output EXR if grading follows.
10. Test frame at quarter size first; look at it; only then the full frame.

## 8. Gotchas seen live

- `VRayHDRI mapType` 1 is cubic; 2 is spherical. A half-grey sky means the wrong
  projection.
- A scripted `VRaySun` created with `targeted:true` still has no target node.
- Under V-Ray the scene exposure control on a plain camera does nothing visible;
  use a physical camera.
- `boolean_objects` union of a box and a rotated cylinder silently dropped the
  cylinder; a closed spline profile + extrude + one subtract was reliable.
- Chaos Scatter accepted model nodes by script but produced zero instances until
  the model nodes were renderable and added through the interface; verify by render.
- Cosmos assets placed by file path render black (textures arrive only via the
  importer).
- `setup_sun` and `create_light type:directional` replace the environment and
  exposure; on a pre-lit scene ask before running them.

## 9. What has moved on in V-Ray

Much published V-Ray guidance is V-Ray 2-era. Checked against current Chaos
documentation (August 2026): Irradiance Map deprecated in favour of Brute Force + Light Cache;
skylight portals superseded by the adaptive dome light; tone mapping moved from the
render to the VFB / OCIO; VRayFastSSS2 replaced by VRayMtl SSS and
VRayAlSurfaceMtl; third-party scatter plugins replaced by Chaos Scatter in the
installer; bloom/glare moved to the VFB Lens Effects layer. The principles of
observation, materials, light, composition and imperfection are unchanged.
