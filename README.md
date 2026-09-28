# luce-step

Original **Luce Base** STEP Part 21 geometry reader. Public export:
`step.Step.load(path, segments=16)` and `Step.decode(text, segments=16)`.
These convenience APIs return `three.PolygonMesh` by tessellating a CAD model.
`Step.load_model(path)` and `Step.decode_model(text)` instead return an analytic
`cad.CadModel`. File entity/reference decoding lives here; model validation,
surface ownership and trim semantics belong to `luce-cad`; numerical surface
sampling belongs to `luce-tesselator`.

Current supported subset:

- Faceted `FACE`/`POLY_LOOP` geometry.
- `ADVANCED_FACE` B-reps with shared `VERTEX_POINT`/`EDGE_CURVE` topology,
  oriented edge uses, outer boundaries and holes. Lines, circles and trimmed
  B-spline/rational B-spline and elliptical edges are retained analytically.
- Plane, cylinder, cone, sphere, torus and B-spline support surfaces. CAD meshing currently
  supports planar trims, circular bands, ruled patches and bounded nonperiodic
  NURBS UV trim projection.
- `STYLED_ITEM` surface-fill `COLOUR_RGB` styles are retained on CAD faces.
  Shell/solid colors are inherited, with explicit face styles taking priority.
  Tessellation emits primitive `Cd`; no material/texture or transparency shader
  is inferred. RGB values are retained without color-space conversion.
- Declared length uncertainty is used for boundary agreement in source units.
- Unique-occurrence rigid assemblies using representation relationships and
  item-defined transformations retain composed face placements.
- Surface-only untrimmed `B_SPLINE_SURFACE_WITH_KNOTS` datasets, including complex
  rational B-spline entities and explicit weights.

This is **not full STEP support**. General p-curves/surface curves,
general periodic/singular NURBS trims, mapped/repeated instances,
oriented shells/void solids and automatic unit conversion remain unsupported.
Unsupported face/placement topology fails instead of importing support surfaces
as if they were trimmed parts. Source units/coordinates are retained; the editor
uses a separate Transform node for scale. Shared STEP edges tessellate once.

The Part 21 scanner handles strings, references, simple and complex entities;
it is not a general EXPRESS schema validator. References use a bounded hash table.
Limits: 256 MiB input, 2,097,152 entities, 8,192 B-rep faces, 32,768 shared
vertices/edges, 64 trim loops, and the separate luce-3d polygon-mesh budgets.
Curves may have 256 controls; NURBS surfaces are bounded to 1,024 per direction
and 262,144 controls total. Entity allocation follows a counted preflight;
topology references use hashed lookup. Spline trim endpoints must still agree
within the file's declared tolerance; automatic tolerance healing is not enabled.
Uniform surface sampling is not a tolerance-controlled CAD tessellator.

Tests run through sibling `luced-3d/tests/run.py`. The external-file probe
`luced-3d/tools/cad_probe.py` tests a real STEP against a reference OBJ without
using that OBJ to generate geometry. See `luced-3d/docs/CAD_TESSELLATION.md`.
