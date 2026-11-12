# Clawd Desk Mascot - 3D print STL (2.5x, for streaming)

Claude Code mascot "Clawd", scaled **2.5x** so it is easy to see on a desk or on camera.
Printer: Elegoo Neptune 4 Pro (225 x 225 mm bed), PLA. No supports needed.

## Files (for humans and agents)

| File | What it is |
|---|---|
| `stl/clawd_2.5x.stl` | **Main print.** Eyes raised 5 mm; swap to black filament at Z = 82.5 mm. |
| `stl/clawd_2.5x_singlecolor.stl` | Single-color version, eyes recessed 7.5 mm. No filament swap. |
| `previews/clawd_preview_hero.png` | Render of the finished print on a desk. |
| `previews/clawd_preview_back_angle.png` | Back/side angle render. |
| `previews/clawd_scale_comparison.png` | Original vs 2.5x vs 12 oz mug. |
| `previews/clawd_spec_sheet.png` | Dimensions and print plan. |
| `source/` | Scripts that produced the STLs and renders (trimesh, Blender bpy). |

## Size

- Original: 66 x 52 x 35 mm
- This print: **165 x 130 x 87.5 mm** (6.5 x 5.1 x 3.4 in), uniform 250 % scale
- Volume 1330 cm3, watertight, single body

## Print settings

- Orientation: lying on its back, face up (as the STL is oriented, Z up). No supports.
- Slice estimate (PrusaSlicer, 0.2 mm standard, 10 % infill): **7 h 32 m, about 286 g PLA**
- Colors: orange body, black eyes. Add a color change at Z = 82.5 mm (layer where the eyes start).

## Direct download (raw)

```
https://raw.githubusercontent.com/Kickyourdad/clawd-desk-mascot-3d-print-stl/main/stl/clawd_2.5x.stl
https://raw.githubusercontent.com/Kickyourdad/clawd-desk-mascot-3d-print-stl/main/stl/clawd_2.5x_singlecolor.stl
```

or `git clone https://github.com/Kickyourdad/clawd-desk-mascot-3d-print-stl.git`

## Credit and license

Based on **"Simple Claude Code Mascot - Clawd"** (Printables model 1655582,
https://www.printables.com/model/1655582-simple-claude-code-mascot-clawd), licensed
**Creative Commons Attribution (CC BY)**. This repo only rescales it 2.5x and adds previews.
Please keep this attribution if you redistribute.

Tags: 3d-print, stl, claude-code, clawd, mascot, desk, streaming, elegoo-neptune-4-pro, pla
