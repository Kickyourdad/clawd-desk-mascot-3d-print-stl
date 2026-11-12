import os, shutil
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import trimesh
from shapely.geometry import Polygon as SPoly

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "deliver")
os.makedirs(OUT, exist_ok=True)
FONT = "C:/Windows/Fonts/segoeuib.ttf"
FONT_R = "C:/Windows/Fonts/segoeui.ttf"


def label(img, xy, lines, anchor="ma"):
    d = ImageDraw.Draw(img)
    y = xy[1]
    for i, (txt, size, col) in enumerate(lines):
        f = ImageFont.truetype(FONT if i == 0 else FONT_R, size)
        # shadow
        d.text((xy[0] + 2, y + 2), txt, font=f, fill=(0, 0, 0), anchor=anchor)
        d.text((xy[0], y), txt, font=f, fill=col, anchor=anchor)
        y += size + 6


# ---- scale comparison with labels
im = Image.open(os.path.join(ROOT, "out", "_r_scale.png")).convert("RGB")
W = (255, 255, 255); O = (255, 170, 110); G = (200, 200, 210)
label(im, (285, 810), [("ORIGINAL", 34, O), ("66 x 52 mm", 28, W)])
label(im, (995, 830), [("YOUR PRINT  (2.5x)", 40, O), ("165 x 130 x 87.5 mm", 32, W), ("6.5 x 5.1 x 3.4 in", 26, G)])
label(im, (1612, 790), [("12 oz MUG", 32, G), ("~95 mm tall", 26, G)])
im.save(os.path.join(OUT, "clawd_scale_comparison.png"))

for src, dst in (("_r_hero.png", "clawd_preview_hero.png"), ("_r_side.png", "clawd_preview_back_angle.png")):
    shutil.copy(os.path.join(ROOT, "out", src), os.path.join(OUT, dst))

# ---- spec sheet (front / side / top silhouettes) from the real STL
m = trimesh.load(os.path.join(ROOT, "out", "clawd_2.5x.stl"))
sec = m.section(plane_origin=[0, 0, 5], plane_normal=[0, 0, 1])
p2, T = sec.to_2D()
poly = max(p2.polygons_full, key=lambda p: p.area)
# to_2D may rotate/offset; recover true XY by transforming back
import numpy as np
pts = np.array(poly.exterior.coords)
pts3 = trimesh.transformations.transform_points(np.c_[pts, np.zeros(len(pts))], T)[:, :2]

fig = plt.figure(figsize=(14, 7.4), facecolor="#14151a")
ax = fig.add_axes([0.04, 0.12, 0.50, 0.78], facecolor="#14151a")
ax.add_patch(Polygon(pts3, closed=True, fc="#E2713E", ec="#ffb48a", lw=1.5))
for ex in ((37.5, 52.5), (-52.5, -37.5)):
    ax.add_patch(plt.Rectangle((ex[0], 16.25), 15, 16.25, fc="#0c0c0e", ec="#555", lw=1))
ax.set_xlim(-100, 100); ax.set_ylim(-85, 85); ax.set_aspect("equal"); ax.axis("off")
kw = dict(color="#ddd", fontsize=13, ha="center", va="center")
ax.annotate("", xy=(-82.5, -72), xytext=(82.5, -72), arrowprops=dict(arrowstyle="<->", color="#ddd"))
ax.text(0, -79, "165 mm  (6.5 in)", **kw)
ax.annotate("", xy=(92, -65), xytext=(92, 65), arrowprops=dict(arrowstyle="<->", color="#ddd"))
ax.text(95, 0, "130 mm\n(5.1 in)", color="#ddd", fontsize=13, ha="left", va="center", rotation=0)
ax.annotate("", xy=(-52.5, 40), xytext=(-37.5, 40), arrowprops=dict(arrowstyle="<->", color="#aaa"))
ax.text(-45, 46, "eye 15 x 16 mm", color="#aaa", fontsize=10, ha="center")
ax.set_title("FRONT  (as it sits on your desk)", color="#E2713E", fontsize=15, loc="left", pad=6)

ax2 = fig.add_axes([0.58, 0.45, 0.38, 0.45], facecolor="#14151a")
ax2.add_patch(plt.Rectangle((0, 0), 82.5, 130, fc="#E2713E", ec="#ffb48a"))
ax2.add_patch(plt.Rectangle((82.5, 65 + 16.25), 5, 16.25, fc="#0c0c0e", ec="#555"))
ax2.set_xlim(-10, 115); ax2.set_ylim(-20, 150); ax2.set_aspect("equal"); ax2.axis("off")
ax2.annotate("", xy=(0, -10), xytext=(87.5, -10), arrowprops=dict(arrowstyle="<->", color="#ddd"))
ax2.text(43, -17, "87.5 mm deep (incl. 5 mm raised eyes)", color="#ddd", fontsize=11, ha="center", va="top")
ax2.set_title("SIDE", color="#E2713E", fontsize=15, loc="left", pad=6)

fig.text(0.58, 0.36, "PRINT PLAN", color="#E2713E", fontsize=15, weight="bold")
lines = [
    "File: clawd_2.5x.stl  (eyes raised 5 mm)",
    "Orientation: lying on its BACK, face up - no supports",
    "Eyes: swap to black filament at Z = 82.5 mm",
    "   (PrusaSlicer: add colour change at that layer)",
    "Single-colour option: clawd_2.5x_singlecolor.stl",
    "   (eyes recessed 7.5 mm, fill with black or leave)",
    "Fits Neptune 4 Pro bed: 165 x 130 vs 225 x 225",
    "Scale: uniform 250 % of Printables #1655582",
]
for i, t in enumerate(lines):
    fig.text(0.58, 0.31 - i * 0.034, t, color="#ddd", fontsize=11.5, family="DejaVu Sans")
fig.text(0.04, 0.03, "Model: 'Simple Claude Code Mascot - Clawd' (Printables 1655582), CC BY - scaled 2.5x", color="#888", fontsize=10)
fig.savefig(os.path.join(OUT, "clawd_spec_sheet.png"), dpi=130, facecolor=fig.get_facecolor())

for f in ("clawd_2.5x.stl", "clawd_2.5x_singlecolor.stl"):
    shutil.copy(os.path.join(ROOT, "out", f), os.path.join(OUT, f))
print(os.listdir(OUT))
