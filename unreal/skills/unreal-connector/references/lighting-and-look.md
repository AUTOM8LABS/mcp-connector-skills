# Lighting and look development

Operator reference for the AUTOM8LABS archviz toolsets in Unreal Engine.
Read it before lighting, grading, or diagnosing an image that looks wrong.
Everything here is verified in AUTOM8LABS field sessions on Unreal Engine 5.8
and against Epic's published documentation.

---

## 1. Exposure and intensity are one decision

The single most common way to waste an hour: the image is dark, so the sun
gets brighter, so the highlights blow out, so exposure comes down, and the
scene ends up lit by numbers that mean nothing.

Unreal lights are physical. Treat them that way:

| Light | Unit | Realistic range |
|---|---|---|
| Sun (directional) | lux | 100000 clear midday, 20000 overcast, 1000 dusk |
| Sky light | unitless scale | 1.0 is physical |
| Point / spot | candelas or lumens | 200-1500 lm for a domestic fitting |
| Rect light | candelas, lumens or nits | nits for a lit panel or a window |

The editor's default sun is about **10 lux**. That is roughly moonlight. A
level lit at 10 lux and rendered with manual exposure comes out black, and
`ArchvizLevelTools.get_level_summary` warns about exactly that combination.

**The order that works:**

1. `create_sun` with a real lux value and a colour temperature (5500 K
   midday, 3000 K late afternoon).
2. `create_sky` with `real_time_capture` on, so the sky light picks up the
   atmosphere instead of a stale cubemap.
3. `set_exposure` to match. `method="manual"` gives a fixed, comparable image
   across shots - use it for anything a client will compare side by side.
   `method="auto"` (histogram) is for walkthroughs, where the eye should
   adapt walking from a dark hall into a bright room.
4. Verify with `CaptureViewport`, not with the numbers.

`set_exposure` with `exposure_compensation_ev` is how you brighten a
correctly lit scene. Changing the sun is how you change the *time of day*.
They are not interchangeable.

### Sun position for a real site

`ArchvizLevelTools.set_sun_position` takes latitude, longitude, time zone and
a date and time, and puts the sun where it actually was. `sun_study` sweeps a
day and reports the angles. This is the tool for right-to-light questions,
shadow studies and planning submissions - not for making a picture prettier.

---

## 2. Lumen: four knobs, four different problems

Lumen is real-time global illumination. It builds a simplified,
lower-resolution version of the scene so it can bounce light every frame.
Everything that looks wrong with it traces back to that simplification.

`ArchvizPostProcessTools.set_rendering_features` exposes the knobs. Each one
fixes a different symptom - raising all of them together is how frame rates
die for no visible gain.

| Symptom | Knob | What it does |
|---|---|---|
| Blotchy, splotchy indirect light in dark areas | `lumen_final_gather_quality` | The noise control. 1 is default, 4 is a real improvement, past 8 it stops paying |
| Bounced light looks weak or wrong in colour | `lumen_scene_lighting_quality` | Fidelity of the bounce itself |
| Foliage, blinds, railings and small props ignore GI | `lumen_scene_detail` | How small an object still participates. The setting that makes planting read properly |
| Glossy floors and worktops reflect a smear | `lumen_reflection_quality` | Sharpness of the reflection trace |
| Light does not reach across a large space | `lumen_max_trace_distance_cm` | How far bounces and reflections travel. Raise for exteriors, lower to reclaim frame rate indoors |

**Diagnosing with the Lumen scene view.** Switch the viewport to the Lumen
Scene view mode (via `EditorAppToolset` console: `r.Lumen.Visualize.CardPlacement`
and the view-mode menu). Surfaces that appear black in that view *receive*
bounced light but do not *emit* it - almost always inverted normals on the
imported mesh. No amount of Lumen tuning fixes that; fix the geometry, or
re-export and `reimport_datasmith`.

### The three-way trade

Quality, frame rate and resolution fight each other. `apply_quality_preset`
sets all three together for one purpose:

- **`draft`** - modelling and lighting. Navigable, visibly noisy.
- **`presentation`** - a live client walkthrough. The best look that still
  holds a usable frame rate.
- **`final`** - stills and sequences. Quality regardless of frame rate;
  offline rendering does not care that the viewport crawls.

`screen_percentage` above 100 renders above display resolution and
downsamples. It sharpens edges and hides Lumen noise better than almost any
other setting, and it costs more than almost any other setting. Reach for it
last, and only for stills.

---

## 3. Reflections: the usual reason a good interior looks cheap

Real-time reflections trace what is already on screen. Anything behind the
camera, or off the edge of the frame, has nothing to reflect - so polished
floors, worktops, glass and chrome go blurry or dark exactly where a client
looks first.

**Fill the gaps with reflection captures.** `create_reflection_capture` bakes
the surroundings from one point:

- One **sphere** capture per room, at head height, in the middle. Set
  `influence_radius_cm` to cover the room and no further.
- A **box** capture for corridors and rectangular spaces, where the shape
  matches the walls.
- Overlapping captures blend; a room with none falls back to the sky light.

Captures hold a snapshot. Move a light, change a material or open a wall and
they keep reflecting the old room. **Call `update_reflection_captures` after
any lighting or geometry change**, and always before a final render. This is
a quiet, common source of renders that look subtly wrong and nobody can say
why.

### When reflections have to be exact

For mirror-accurate reflections and physically correct refraction through
glass, switch to path tracing: `render_still(path_tracer=True)` with 64-256
`spatial_samples`. It is not real-time and it is not for the viewport - it is
for the two or three hero stills that carry a pitch.

---

## 4. Glass, emissives and the materials that mislead

- **Glass under real-time GI is approximate.** Reflections and refraction
  through a translucent material are the weakest part of the real-time
  pipeline. Accept it for walkthroughs; path-trace the stills where glass is
  the subject.
- **Emissive materials are not lights.** They tint nearby surfaces and they
  read beautifully in the frame - a lit sign, a screen, a strip in a soffit -
  but the bounce they contribute is approximate and cannot be shaped. Light
  the room with an actual light and use the emissive for the *look* of the
  source. Chasing illumination with emissive intensity produces exactly the
  flat, colour-washed image people mean by "it looks like a game".
- **Materials are Epic's territory.** `MaterialTools` and
  `MaterialInstanceTools` author graphs and set parameters. Our
  `BimIntakeTools.remap_materials_by_name` exists for the one archviz job
  Epic does not cover: an imported model arriving with material names
  from the authoring application that need mapping onto a real library in bulk.

---

## 5. Local lighting and IES

`create_point_light`, `create_spot_light` and `create_rect_light` take
physical units and colour temperature. Beyond that:

- **IES profiles are what make interior lighting look designed.** A spot
  light with `set_ies_profile` throws the real distribution of a real
  fitting - the scallops on a wall, the tight pool under a downlight -
  instead of a generic cone. Import `.ies` files with
  `BimIntakeTools.import_file`. Manufacturer IES files are usually free to
  download and turn a specification into an image.
- **Rect lights are the studio tool.** Large source, soft shadow. Two or
  three rect lights, warm one side and cool the other, is a complete product
  setup. `source_width_cm` and `source_height_cm` control shadow softness far
  more than intensity does.
- **Shadows are the expensive part.** Turning off dynamic shadows on
  decorative fittings that only need to *glow* buys frame rate with no
  visible loss. `set_light_properties(cast_shadows=False)`.
- **Sun softness** is `source_angle_deg` on the sun, not a shadow setting.
  0.5 degrees is the real sun; larger values give the diffuse look of an
  overcast day.

`get_light_inventory` is the audit: every light, its units, temperature,
mobility and IES profile in one call. `scale_light_intensities` rebalances a
whole level by a factor when the exposure changes.

---

## 6. HDRI backdrop for studio and product work

`create_hdri_backdrop` places one actor that supplies the environment light,
the reflections and the background image, with a ground plane that catches
shadows so the subject sits on something. For a car, a component, a piece of
furniture or a facade study, this beats building a rig of rect lights:

1. Import an `.hdr` with `BimIntakeTools.import_file`.
2. `create_hdri_backdrop(cubemap_path=..., size_cm=...)` - make the dome
   comfortably larger than the subject.
3. `angle_deg` rotates the environment: it moves the sun and everything the
   subject reflects in one parameter. This is the fastest way to find a
   flattering key direction.
4. Add one or two rect lights only where the HDRI leaves something dull.

It needs the HDRI Backdrop plugin enabled in the project. The tool says so
plainly if it is not.

---

## 7. Cameras

`ArchvizCameraTools` cameras are cine cameras with real lens physics -
focal length, aperture, focus distance and filmback, not a field-of-view
slider.

- `create_cine_camera` then `set_lens`. 24-35 mm reads as architectural
  interior; 50 mm as a natural eye view; wider than 18 mm distorts verticals
  in a way clients notice and dislike.
- `frame_actors` points and pulls back until the given actors fit, with
  padding. Use it instead of nudging a transform.
- `create_orbit_cameras` rings a scheme with evenly spaced cameras - the
  fastest route to a set of covering views for a review.
- `pilot_camera` puts the viewport *through* a camera, so
  `EditorAppToolset.CaptureViewport` shows the actual shot.
- Aperture drives depth of field. f/2.8 throws a background out beautifully
  and hides unresolved detail; f/8 keeps a whole interior sharp.

---

## 8. Diagnostic order for an image that looks wrong

Work down this list. Stop at the first thing that is true.

1. **Black or nearly black.** Manual exposure against a dim sun. Check
   `get_level_summary` warnings, then `set_exposure`.
2. **Blown out.** Sun at a real lux value with default exposure. Same fix,
   other direction.
3. **Flat, no contact shadows, everything evenly lit.** No sky light, or the
   sky light is not real-time capturing. `create_sky(real_time_capture=True)`.
4. **Blotchy indirect light.** `lumen_final_gather_quality`, then engine
   scalability via `apply_quality_preset`.
5. **Small objects and planting look pasted on.** `lumen_scene_detail`.
6. **Reflections smeared, dark, or showing the wrong room.**
   `create_reflection_capture` per room, then `update_reflection_captures`.
7. **Patches of geometry that receive light but never bounce it.** Inverted
   normals in the source model. Fix upstream and re-import.
8. **Looks right in the viewport, wrong in the render.** The render is at a
   different quality level, or the captures are stale. Apply the `final`
   preset, refresh the captures, save the level, render again.

Always confirm the fix with `CaptureViewport`. A value that reads correctly
and looks wrong is still wrong.
