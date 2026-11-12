import bpy, sys, math, os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
mode = sys.argv[sys.argv.index("--") + 1]  # hero | side | scale | closeup
SAMPLES = int(os.environ.get("SAMPLES", "96"))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.cycles.device = 'CPU'
sc.render.resolution_x, sc.render.resolution_y = 1800, 1125
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Medium High Contrast'
CM = 0.1  # 1 blender unit = 1 cm; STL is in mm


def hexc(h):
    h = h.lstrip('#')
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = lambda c: ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
    return (lin(r), lin(g), lin(b), 1)


def mat(name, color, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = color
    b.inputs["Roughness"].default_value = rough
    return m


def pla(name, color):
    m = mat(name, hexc(color), 0.42)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    # subtle FDM layer-line bump along the print axis (object local Z = depth axis)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = 'BANDS'
    wv.bands_direction = 'Z'
    wv.wave_profile = 'SAW'
    wv.inputs["Scale"].default_value = 1.0 / (0.25 * CM)  # ~ layer pitch in cm
    wv.inputs["Distortion"].default_value = 0.0
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.08
    bp.inputs["Distance"].default_value = 0.005
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    nt.links.new(wv.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


ORANGE = "#E2713E"
BLACK = "#0c0c0e"


def clawd(scale=1.0, loc=(0, 0, 0), yaw=0.0, name="c"):
    """Standing on its feet, eyes toward -Y. scale is relative to the 2.5x print (0.4 = original 66 mm)."""
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    for f, m in (("_body.stl", pla("o" + name, ORANGE)), ("_eyes.stl", pla("k" + name, BLACK))):
        bpy.ops.wm.stl_import(filepath=os.path.join(ROOT, "out", f))
        o = bpy.context.selected_objects[0]
        o.scale = (CM, CM, CM)
        o.rotation_euler = (math.radians(90), 0, 0)
        o.location = (0, 0, 6.5)  # y(height) spans -65..65 mm -> lift feet to z=0
        o.data.materials.append(m)
        o.parent = root
    root.scale = (scale,) * 3
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(yaw))
    return root


def desk(size=600):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    d = bpy.context.object
    m = mat("desk", hexc("#202128"), 0.38)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = 0.8
    n.inputs["Detail"].default_value = 6
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.22
    rr.inputs["To Max"].default_value = 0.42
    nt.links.new(n.outputs["Fac"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], b.inputs["Roughness"])
    d.data.materials.append(m)


def world():
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = hexc("#0b0d14")
    bg.inputs["Strength"].default_value = 0.6


def emissive_plane(loc, size, color, strength, rot=(math.radians(90), 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    p = bpy.context.object
    p.scale = (size[0], size[1], 1)
    p.rotation_euler = rot
    m = bpy.data.materials.new("em")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = hexc(color)
    e.inputs["Strength"].default_value = strength
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs[0], o.inputs[0])
    p.data.materials.append(m)


def area(loc, target, energy, size, color="#ffffff"):
    bpy.ops.object.light_add(type='AREA', location=loc)
    l = bpy.context.object
    l.data.energy = energy * 9
    l.data.size = size
    l.data.color = hexc(color)[:3]
    d = Vector(target) - Vector(loc)
    l.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def camera(loc, target, lens=70, fstop=None, focus=None):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    d = Vector(target) - Vector(loc)
    c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    c.data.lens = lens
    c.data.sensor_width = 36
    if fstop:
        c.data.dof.use_dof = True
        c.data.dof.aperture_fstop = fstop
        c.data.dof.focus_distance = focus if focus else d.length
    sc.camera = c


def bokeh():
    import random
    random.seed(7)
    cols = ["#ff8a4c", "#7a8bff", "#4fd0ff", "#ff5fa2", "#ffd24f", "#8a5cff"]
    for i in range(16):
        x = random.uniform(-85, 85); z = random.uniform(5, 48); r = random.uniform(2.5, 6)
        bpy.ops.mesh.primitive_circle_add(vertices=48, radius=r, fill_type='NGON', location=(x, 110, z),
                                          rotation=(math.radians(90), 0, 0))
        p = bpy.context.object
        m = bpy.data.materials.new("bk"); m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes): nt.nodes.remove(n)
        e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = hexc(random.choice(cols)); e.inputs["Strength"].default_value = 2.0
        o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(e.outputs[0], o.inputs[0])
        p.data.materials.append(m)


world()
desk()

if mode in ("hero", "closeup"):
    clawd(1.0, (0, 0, 0), yaw=-38)
    bokeh()
    area((-38, -42, 48), (0, -4, 7), 5200, 34, "#fff1e3")
    area((55, -30, 22), (0, 0, 8), 1800, 30, "#9fb8ff")
    area((0, 36, 40), (0, 0, 10), 2500, 30, "#ffd0b0")
    if mode == "hero":
        camera((-20, -78, 20), (2.5, -4, 6.6), lens=62, fstop=5.6, focus=80)
    else:
        camera((-8, -34, 11), (-3.7, -8.7, 8.3), lens=70, fstop=3.2, focus=26)
elif mode == "side":
    clawd(1.0, (0, 0, 0), yaw=-125)
    bokeh()
    area((38, -42, 48), (0, 0, 7), 5200, 34, "#fff1e3")
    area((-55, -30, 22), (0, 0, 8), 1800, 30, "#9fb8ff")
    area((0, 36, 40), (0, 0, 10), 2500, 30, "#ffd0b0")
    camera((26, -60, 17), (0, -3, 6.2), lens=62, fstop=5.6, focus=65)
elif mode == "scale":
    clawd(1.0, (3, 0, 0), yaw=-12, name="big")
    clawd(0.4, (-16.5, -3, 0), yaw=-12, name="small")
    mm = mat("mug", hexc("#f2f2f2"), 0.18)
    bpy.ops.mesh.primitive_cylinder_add(radius=4.1, depth=9.5, location=(19, -2, 4.75), vertices=96)
    mug = bpy.context.object
    mug.data.materials.append(mm)
    bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_torus_add(major_radius=2.7, minor_radius=0.55, location=(24.3, -2, 4.9),
                                     rotation=(math.radians(90), 0, 0))
    bpy.context.object.data.materials.append(mm)
    bpy.ops.mesh.primitive_cylinder_add(radius=3.8, depth=0.2, location=(19, -2, 9.4), vertices=96)
    bpy.context.object.data.materials.append(mat("coffee", hexc("#2b1a10"), 0.05))
    bokeh()
    area((-30, -50, 50), (0, -3, 6), 6000, 40, "#fff1e3")
    area((50, -30, 25), (0, 0, 8), 2200, 30, "#9fb8ff")
    area((0, 36, 40), (0, 0, 10), 2000, 30, "#ffd0b0")
    sc.render.resolution_x, sc.render.resolution_y = 2000, 1000
    camera((0, -66, 12), (2, -3, 6.2), lens=42, fstop=11, focus=66)

sc.render.filepath = os.path.join(ROOT, "out", "_r_%s.png" % mode)
bpy.ops.render.render(write_still=True)
print("DONE", sc.render.filepath)
