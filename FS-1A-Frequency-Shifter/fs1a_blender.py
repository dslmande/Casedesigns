"""FS-1A: fotorealistische Ansichten des Gehaeuses, gerendert mit Blender.

    /Applications/Blender.app/Contents/MacOS/Blender -b -P fs1a_blender.py

Holt sich selbst, was es braucht, wenn es fehlt oder aelter als die Quelle ist:
  * die Dreiecksnetze aus FS1A_Gehaeuse_<REV>.step   (FreeCAD, headless)
  * die Druckgrafik als Textur fuer die Blende       (Chrome, headless)
Beides landet neben dem Skript und wird nicht mitversioniert.

Zwei Fallen, die Zeit gekostet haben: die Szene steht in Millimetern, also muss
das Kamera-Clipping hoch (Standard 1000 schneidet die Baugruppe weg), und Chrome
zeichnet eine SVG in Originalgroesse in das Fenster - die Fenstergroesse muss die
natuerliche Groesse sein, die Aufloesung kommt ueber den Skalierungsfaktor.
"""
import json, math, os, subprocess, sys, tempfile
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(bpy.data.filepath or __file__)) or os.getcwd()
HERE = os.path.dirname(os.path.abspath(sys.argv[sys.argv.index("-P") + 1])) if "-P" in sys.argv else HERE
OUT = HERE
MESH = os.path.join(HERE, "fs1a_mesh.json")
TEX = os.path.join(HERE, "fs1a_panel_tex.png")
sys.path.insert(0, HERE)
from fs1a_panel import REV            # Versionsstand kommt aus dem Generator
STEP = os.path.join(HERE, f"FS1A_Gehaeuse_{REV}.step")
DRUCK = os.path.join(HERE, f"FS1A_Frontpanel_{REV}_druck.svg")
FREECAD = "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SKIP = {"FS1A"}                      # Sammelobjekt der STEP, waere doppelt

# Druckgrafik: 484,72 x 90,34 mm, 1,06 / 1,12 mm Beschnitt je Seite
TEX_W, TEX_H, TEX_X0, TEX_Z0 = 484.72, 90.34, -1.06, -1.12


def _veraltet(ziel, quelle):
    return not os.path.exists(ziel) or os.path.getmtime(ziel) < os.path.getmtime(quelle)


def quellen():
    if _veraltet(MESH, STEP):
        skript = os.path.join(tempfile.mkdtemp(), "_tess.py")   # nicht ins Projekt: sonst bleibt ein __pycache__ liegen
        open(skript, "w").write(
            "import json, FreeCAD, Import\n"
            f"doc = FreeCAD.newDocument('a'); Import.insert({STEP!r}, 'a')\n"
            "p = []\n"
            "for o in doc.Objects:\n"
            "    sh = getattr(o, 'Shape', None)\n"
            "    if sh is None or sh.isNull(): continue\n"
            "    v, f = sh.tessellate(0.25)\n"
            "    p.append({'name': o.Label, 'v': [[a.x, a.y, a.z] for a in v], 'f': [list(t) for t in f]})\n"
            f"json.dump(p, open({MESH!r}, 'w'))\n")
        subprocess.run([FREECAD, skript], check=True, capture_output=True)
        os.remove(skript)
        print("Netze erzeugt:", MESH)
    if _veraltet(TEX, DRUCK):
        w = round(TEX_W * 96 / 25.4)          # natuerliche CSS-Groesse der SVG
        h = round(TEX_H * 96 / 25.4)
        subprocess.run([CHROME, "--headless", "--disable-gpu", f"--screenshot={TEX}",
                        f"--window-size={w},{h}", "--force-device-scale-factor=4",
                        "--hide-scrollbars", "file://" + DRUCK], check=True, capture_output=True)
        print("Textur erzeugt:", TEX)


quellen()

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ------------------------------------------------------------------ Material
def principled(name, color, rough, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m

def panel_material():
    m = bpy.data.materials.new("Blende")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.42
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(TEX)
    tex.extension = "EXTEND"
    mp = nt.nodes.new("ShaderNodeMapping")
    co = nt.nodes.new("ShaderNodeTexCoord")
    mp.inputs["Location"].default_value = (-TEX_X0 / TEX_W, -TEX_Z0 / TEX_H, 0)
    mp.inputs["Scale"].default_value = (1 / TEX_W, 1 / TEX_H, 1)
    # Objektkoordinaten x,z -> u,v: erst skalieren, dann verschieben
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    com = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(co.outputs["Object"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["X"], com.inputs["X"])
    nt.links.new(sep.outputs["Z"], com.inputs["Y"])
    nt.links.new(com.outputs["Vector"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    return m

MAT = {
    "Rueckwand":        principled("Alu natur", (0.74, 0.75, 0.76), 0.33, 0.85),
    "Seitenteil links": principled("Profil",    (0.60, 0.61, 0.63), 0.30, 0.90),
    "Seitenteil rechts":principled("Profil2",   (0.60, 0.61, 0.63), 0.30, 0.90),
    "Deckel":           principled("Blech",     (0.68, 0.69, 0.70), 0.38, 0.85),
    "Boden":            principled("Blech2",    (0.68, 0.69, 0.70), 0.38, 0.85),
    "Gewindebolzen oben":  principled("Stahl",  (0.55, 0.56, 0.58), 0.25, 1.0),
    "Gewindebolzen unten": principled("Stahl2", (0.55, 0.56, 0.58), 0.25, 1.0),
}
PANEL = panel_material()

# ------------------------------------------------------------------ Geometrie
objs = []
for p in json.load(open(MESH)):
    if p["name"] in SKIP or not p["f"]:
        continue
    me = bpy.data.meshes.new(p["name"])
    me.from_pydata([tuple(v) for v in p["v"]], [], [tuple(f) for f in p["f"]])
    me.validate()
    ob = bpy.data.objects.new(p["name"], me)
    sc.collection.objects.link(ob)
    ob.data.materials.append(PANEL if p["name"] == "Frontplatte" else
                             MAT.get(p["name"], principled("x", (0.7, 0.7, 0.7), 0.4)))
    objs.append(ob)

for ob in objs:                      # runde Flaechen glatt, Kanten scharf
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))
    ob.select_set(False)

# Mitte und Groesse der Baugruppe
co = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
mn = Vector((min(c[i] for c in co) for i in range(3)))
mx = Vector((max(c[i] for c in co) for i in range(3)))
mid = (mn + mx) / 2
size = (mx - mn).length

# ------------------------------------------------------------------ Szene
def light(name, loc, energy, sz):
    d = bpy.data.lights.new(name, "AREA")
    d.energy, d.size, d.shape = energy, sz, "SQUARE"
    o = bpy.data.objects.new(name, d)
    o.location = loc
    sc.collection.objects.link(o)
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = (mid - Vector(loc)).to_track_quat("-Z", "Y")
    return o

light("Key",  (mid.x - size * 0.6, mid.y - size * 0.9, mid.z + size * 0.8), size ** 2 * 9, size * 0.7)
light("Fill", (mid.x + size * 1.0, mid.y - size * 0.6, mid.z + size * 0.2), size ** 2 * 3, size * 0.9)
light("Rim",  (mid.x, mid.y + size * 1.1, mid.z + size * 0.9),              size ** 2 * 4, size * 0.8)

world = bpy.data.worlds.new("W")
sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.58, 0.60, 0.63, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.75

LENS = 135.0
SENSOR = 36.0
cam_d = bpy.data.cameras.new("Cam")
cam_d.lens = LENS
cam_d.sensor_width = SENSOR
cam_d.clip_start = 1.0        # Szene ist in Millimetern
cam_d.clip_end = 100000.0
cam = bpy.data.objects.new("Cam", cam_d)
sc.collection.objects.link(cam)
sc.camera = cam

sc.render.engine = "CYCLES"
try:
    sc.cycles.device = "GPU"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
except Exception as e:
    print("GPU nicht nutzbar:", e)
sc.cycles.samples = 300
sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.render.resolution_x, sc.render.resolution_y = 1800, 1050
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"


def shot(name, az, el, only=None, margin=1.10, res=None):
    """Kamera so setzen, dass alle sichtbaren Teile ins Bild passen."""
    sc.render.resolution_x, sc.render.resolution_y = res or (1800, 1050)
    for o in objs:
        o.hide_render = bool(only) and o.name not in only
    vis = [o for o in objs if not o.hide_render]
    pts = [o.matrix_world @ Vector(c) for o in vis for c in o.bound_box]
    lo = Vector((min(p[i] for p in pts) for i in range(3)))
    hi = Vector((max(p[i] for p in pts) for i in range(3)))
    c = (lo + hi) / 2

    a, e = math.radians(az), math.radians(el)
    n = Vector((math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e)))  # Mitte -> Kamera
    up = Vector((0, 0, 1))
    right = n.cross(up).normalized()
    upv = right.cross(n).normalized()

    kx = (SENSOR / 2) / LENS
    ky = kx * sc.render.resolution_y / sc.render.resolution_x
    d = 0.0
    for p in pts:
        v = p - c
        d = max(d, v.dot(n) + abs(v.dot(right)) / kx, v.dot(n) + abs(v.dot(upv)) / ky)
    d *= margin

    cam.location = c + n * d
    cam.rotation_mode = "QUATERNION"
    cam.rotation_quaternion = (c - cam.location).to_track_quat("-Z", "Y")
    sc.render.filepath = os.path.join(OUT, name)
    bpy.ops.render.render(write_still=True)
    print("fertig:", name)


shot(f"FS1A_Gehaeuse_{REV}_3d_iso.png", az=-34, el=24)
shot(f"FS1A_Gehaeuse_{REV}_3d_rueckseite.png", az=146, el=22)
shot(f"FS1A_Frontpanel_{REV}_3d.png", az=-18, el=14, only={"Frontplatte"}, res=(1800, 470))
