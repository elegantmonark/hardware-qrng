# ED-4 enclosure CAD

The ED-4 enclosure is a parametric case with two parts for FDM printing. It is designed for the planned 89 mm by 52 mm perfboard implementation.

The first base was printed and checked on 18 October 2026. The intended bare perfboard fitted between the locating features. Populated-board clearance, cable routing and lid fit still require confirmation.

## Current dimensions

| Parameter | Value |
|---|---:|
| Perfboard envelope | 89 by 52 mm |
| Clearance around board | 8 mm per side |
| Internal length | 105 mm |
| Internal width | 68 mm |
| Internal height | 34 mm |
| Wall thickness | 2.4 mm |
| Floor thickness | 3 mm |
| Board support height | 8 mm |
| Cable opening | 26 by 12 mm |
| Approximate external size | 109.8 by 72.8 by 37 mm, excluding lid thickness |
| Approximate assembled height | 40 mm |
| Clearance above perfboard | 24.4 mm |

The cable opening carries the four connections currently planned between ED-4 and the Arduino:

1. 5 V
2. 3.3 V
3. GND
4. A0 analogue signal
Arduino AREF remains unconnected.

## Design choices

- Two rails create clearance beneath the perfboard.
- Four corner guides locate the board without assuming particular positions for mounting holes.
- A locating lip held by friction avoids unusually long lid screws on the tall enclosure.
- The wires share one side opening so individual Dupont housings or a sleeved bundle can pass through.
- The enclosure has no ventilation holes beside the source LED, avoiding an unnecessary optical path during early testing.
- The design remains a mechanical prototype. Enclosing the circuit does not establish electrical or statistical performance.

## Exporting printable parts

Open `ed4_enclosure.scad` in OpenSCAD and set the `part` variable to `"base"` or `"lid"`. Render with F6, then export each part as STL.

The repository already includes:

- `ed4_base.stl`
- `ed4_lid.stl`
- `SHA256SUMS` for verifying both exports

Both STL files were rendered successfully from the included source and passed a manifold check with closed edges. Physical fit and print tolerances still require a first test print.

From the command line:

```bash
openscad -D part_id=0 -o ed4_base.stl ed4_enclosure.scad
openscad -D part_id=1 -o ed4_lid.stl ed4_enclosure.scad
```

The default `"layout"` view places both parts in their print orientation side by side. The `"assembled"` view adds a translucent board and lid for fit inspection.

## Recommendations for the first print

- Material: PLA for the fit prototype; PETG if greater temperature resistance is later needed.
- Layer height: 0.20 mm.
- Walls: at least three perimeters.
- Infill: 15% to 25%.
- Supports: none expected for the base or the lid in its print orientation.
- First test: print only the lower 15 mm of the base and the lid lip if the slicer supports cutting models. This checks board fit and lid tolerance before committing to the full height print.

Before the final print, measure the assembled perfboard's tallest component and confirm that 24.4 mm of clearance above the board is sufficient.
