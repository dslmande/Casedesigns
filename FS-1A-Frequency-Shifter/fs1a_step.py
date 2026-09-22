#!/usr/bin/env python3
"""Baugruppe FS-1A als STEP – erzeugt mit FreeCAD (headless).

Baut alle Teile aus denselben Quellen wie die Fertigungsdateien:
Frontplatte und Rückwand aus dem Geometriemodell von fs1a_panel.py /
fs1a_rueckwand.py, die Seitenteile aus der Gie-Tec-Profilkontur
(gietec_122040_profil.dat), Deckel und Boden aus fs1a_gehaeuse.py.

Koordinaten der Baugruppe (mm):
  X  Gehäusebreite, 0 = linke Kante der Frontplatte
  Y  Tiefe, 0 = Rückseite der Frontplatte, +Y nach hinten
  Z  Höhe, 0 = Unterkante der Frontplatte

Aufruf:
  /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd fs1a_step.py
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import FreeCAD as App
import Part
from FreeCAD import Vector

import fs1a_panel as P
import fs1a_rueckwand as R
import fs1a_gehaeuse as G

OUT = HERE / "fs1a_gehaeuse.step"

# --------------------------------------------------------------- Geometrie
P.build()
FRONT_CUTS, FRONT_W, FRONT_H = list(P.CUTS), P.W, P.H
FRONT_SINK = dict(P.SINK)
FRONT_T = P.PANEL_T

R.build()                       # setzt P.W/P.H auf die Rückwand und leert CUTS
REAR_CUTS, REAR_W, REAR_H = list(P.CUTS), P.W, P.H
REAR_T = 2.0

DEPTH = G.BOX_DEPTH             # Profillänge = Gehäusetiefe
BOX_W = G.BOX_WIDTH
X_OUT_L = (FRONT_W - BOX_W) / 2          # Außenfläche linkes Profil
X_OUT_R = FRONT_W - X_OUT_L
Z_PROF = (FRONT_H - G.PROF_H) / 2        # Profil mittig zur Blende (−0,1 mm)


def dedupe(pts):
    out = []
    for p_ in pts:
        if not out or (abs(p_[0] - out[-1][0]) > 1e-7 or abs(p_[1] - out[-1][1]) > 1e-7):
            out.append(p_)
    return out


# --------------------------------------------------------------- Bausteine
def plate(w, h, t, r):
    """Platte in der X-Z-Ebene, Dicke t in Y, Ecken mit Radius r."""
    box = Part.makeBox(w, t, h)
    if r > 0:
        edges = [e for e in box.Edges
                 if e.BoundBox.XLength < 1e-6 and e.BoundBox.ZLength < 1e-6]
        box = box.makeFillet(r, edges)
    return box


def cut_cyl(x, z, d, t):
    return Part.makeCylinder(d / 2.0, t + 2, Vector(x, -1, z), Vector(0, 1, 0))


def cut_slot(x, z, w, h, t):
    L = w - h
    s = Part.makeBox(L, t + 2, h, Vector(x - L / 2, -1, z - h / 2))
    for dx in (-L / 2, L / 2):
        s = s.fuse(Part.makeCylinder(h / 2, t + 2, Vector(x + dx, -1, z), Vector(0, 1, 0)))
    return s


def cut_rect(x, z, w, h, r, t):
    b = Part.makeBox(w, t + 2, h, Vector(x - w / 2, -1, z - h / 2))
    if r > 0:
        edges = [e for e in b.Edges
                 if e.BoundBox.XLength < 1e-6 and e.BoundBox.ZLength < 1e-6]
        b = b.makeFillet(r, edges)
    return b


def panel_solid(w, h, t, r, cuts, x_off=0.0, sinks=None):
    """Platte mit allen Ausschnitten; Ausschnittkoordinaten x von links, y von oben."""
    body = plate(w, h, t, r)
    sinks = sinks or {}
    tools = []
    for c in cuts:
        if c[0] == "circle":
            _, _kind, cx, cy, d, _n = c
            tools.append(cut_cyl(cx, h - cy, d, t))
            if (round(cx, 3), round(cy, 3)) in sinks:
                # 90°-Senkung: Kegel von der Vorderseite (y = 0) nach innen
                cone_h = (P.CSK_CONE - d) / 2.0
                tools.append(Part.makeCone(P.CSK_CONE / 2.0, d / 2.0, cone_h,
                                           Vector(cx, 0, h - cy), Vector(0, 1, 0)))
        elif c[0] == "slot":
            _, cx, cy, cw, ch = c
            tools.append(cut_slot(cx, h - cy, cw, ch, t))
        else:
            _, _kind, cx, cy, cw, ch, rr, _n = c
            tools.append(cut_rect(cx, h - cy, cw, ch, rr, t))
    if tools:
        body = body.cut(tools[0].multiFuse(tools[1:]) if len(tools) > 1 else tools[0])
    body.translate(Vector(x_off, 0, 0))
    return body


def profile_solid(side):
    """Seitenteilprofil, aus der Gie-Tec-Kontur extrudiert. side: -1 links, +1 rechts."""
    pts = dedupe(G.profile_points())
    x0 = X_OUT_L if side < 0 else X_OUT_R
    sgn = 1.0 if side < 0 else -1.0
    verts = [Vector(x0 + sgn * d, 0, Z_PROF + hgt) for hgt, d in pts]
    wire = Part.makePolygon(verts + [verts[0]])
    return Part.Face(wire).extrude(Vector(0, DEPTH, 0))


def cover_solid(top):
    z_lo = Z_PROF + (G.GROOVE_HI[0] if top else G.GROOVE_LO[0])
    z = z_lo + ((G.GROOVE_HI[1] - G.GROOVE_HI[0]) - G.COVER_T) / 2.0
    x = (FRONT_W - G.COVER_W) / 2.0
    body = Part.makeBox(G.COVER_W, G.COVER_L, G.COVER_T, Vector(x, 0, z))
    for hx, hy in G.cover_holes():
        body = body.cut(Part.makeCylinder(G.COVER_HOLE_D / 2.0, G.COVER_T + 2,
                                          Vector(x + hx, hy, z - 1), Vector(0, 0, 1)))
    return body


def bolt_solid(y_from_top):
    """Gewindebolzen M3 auf der Rueckseite der Frontplatte."""
    return Part.makeCylinder(3.0 / 2, P.BOLT_LEN,
                             Vector(FRONT_W / 2.0, 0, FRONT_H - y_from_top), Vector(0, 1, 0))


# --------------------------------------------------------------- Baugruppe
doc = App.newDocument("FS1A")

parts = [
    ("Frontplatte", panel_solid(FRONT_W, FRONT_H, FRONT_T, P.R_CORNER, FRONT_CUTS,
                               sinks=FRONT_SINK)),
    ("Rueckwand", panel_solid(REAR_W, REAR_H, REAR_T, 2.0, REAR_CUTS, x_off=X_OUT_L)),
    ("Seitenteil_links", profile_solid(-1)),
    ("Seitenteil_rechts", profile_solid(+1)),
    ("Deckel", cover_solid(True)),
    ("Boden", cover_solid(False)),
    ("Gewindebolzen_oben", bolt_solid(P.Y_BOLT_TOP)),
    ("Gewindebolzen_unten", bolt_solid(P.Y_BOLT_BOT)),
]
# Frontplatte nach vorn, Rückwand nach hinten schieben
parts[0][1].translate(Vector(0, -FRONT_T, 0))
parts[1][1].translate(Vector(0, DEPTH, 0))

objs = []
for name, shape in parts:
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    o.Label = name.replace("_", " ")
    objs.append(o)
doc.recompute()

# Import.export schreibt die Teilenamen als PRODUCT in die STEP-Datei
try:
    import Import
    Import.export(objs, str(OUT))
except Exception as exc:                      # Rückfall
    print("Import.export nicht moeglich:", exc)
    Part.export(objs, str(OUT))

print(f"{OUT.name}: {len(objs)} Teile")
for name, shape in parts:
    bb = shape.BoundBox
    print(f"  {name:<18} {bb.XLength:7.2f} x {bb.YLength:7.2f} x {bb.ZLength:6.2f} mm"
          f"   Volumen {shape.Volume / 1000.0:8.2f} cm3   ok={shape.isValid()}")
gesamt = Part.makeCompound([s for _, s in parts]).BoundBox
print(f"  Baugruppe          {gesamt.XLength:7.2f} x {gesamt.YLength:7.2f} x {gesamt.ZLength:6.2f} mm")
