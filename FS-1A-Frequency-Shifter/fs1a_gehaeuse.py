#!/usr/bin/env python3
"""Gehäuse zum FS-1A: Seitenteile, Deckel und Boden.

Gehäuse aus zwei Gie-Tec Seitenteilprofilen 4 (Art. 122040), Frontplatte und
Rückwand angeschraubt, Deckel und Boden in die Blechnuten der Profile geschoben.

Maße aus der Gie-Tec-CAD-Datei cad_122040.dxf (Kontur in gietec_122040_profil.dat):
  Profil 88,30 mm hoch, 20,50 mm breit (vordere Anlagefläche 16 mm)
  Schraubkanäle Ø4,5 für M5 bei Höhe 5 / 83,3 mm, je 5 mm hinter der Außenfläche
  Blechnut 1,6 mm breit auf Höhe 1,4–3,0 bzw. 85,3–86,9 mm, Nutgrund 10 mm
  hinter der Außenfläche, Nuttiefe 3 mm

Erzeugt:
  fs1a_deckel_boden.svg/.dxf/.fpjs/_bohrungen.csv   Blech 1,5 mm, 2 Stück nötig
  fs1a_gehaeuse_schnitt.svg                          Querschnitt des Gehäuses
  Stückliste auf der Konsole

Aufruf:  python3 fs1a_gehaeuse.py
"""
from pathlib import Path

import fs1a_panel as p

OUT = Path(__file__).parent

# ------------------------------------------------------------------ Gehäuse
BOX_WIDTH = p.BOX_WIDTH       # 437 mm, Außenfläche zu Außenfläche
BOX_DEPTH = 250.0             # Profillänge = Gehäusetiefe ohne Front/Rückwand
PANEL_T = 2.0                 # Dicke Frontplatte und Rückwand

# Profilmaße – die gemeinsamen Werte stehen in fs1a_panel.py
PROF_H = p.PROF_H
PROF_W = 20.50
GROOVE_BOTTOM = p.GROOVE_BOTTOM   # Nutgrund, von der Außenfläche des Profils
GROOVE_MOUTH = 13.0               # Nutöffnung (Innenkante des Profilfußes)
GROOVE_LO, GROOVE_HI = p.GROOVE_LO, p.GROOVE_HI
SCREW_INSET = p.PROFILE_HOLE_INSET
SCREW_PITCH = p.PROFILE_HOLE_PITCH

# Deckel/Boden
COVER_T = p.COVER_T           # Blechdicke (Nut nimmt bis 1,6 mm)
COVER_PLAY = 1.0              # Untermaß in der Breite, damit es sich schieben lässt
COVER_W = BOX_WIDTH - 2 * GROOVE_BOTTOM - COVER_PLAY      # 416,0 mm
COVER_L = BOX_DEPTH - 0.5     # 0,5 mm kürzer als die Profile
NAME = "fs1a_deckel_boden"

# Loch für den Montagewinkel (Keystone 633) zum Gewindebolzen der Frontplatte.
# Der Winkel liegt mit einem Schenkel am Blech, seine Lochmitte sitzt 5,5 mm von der
# Blechvorderkante; das Blech schließt vorn bündig mit der Blendenrückseite ab.
COVER_HOLE_D = 3.1
COVER_HOLE_FROM_FRONT = p.BRACKET_HOLE_OFF


def build_cover():
    p.W, p.H = COVER_W, COVER_L
    p.CUTS.clear()
    p.PRINT.clear()
    p.PREV.clear()
    p.hole("Winkelschraube M3", COVER_W / 2, COVER_HOLE_FROM_FRONT, COVER_HOLE_D,
           "Keystone 633 auf den Gewindebolzen der Frontplatte")


# ------------------------------------------------------- Querschnittzeichnung
def profile_points():
    src = OUT / "gietec_122040_profil.dat"
    pts = []
    for line in src.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        a, b = line.split()
        pts.append((float(a), float(b)))
    # Die CAD-Polylinie ist offen (sie endet in der mittleren M3-Nut der Vorderseite).
    # Für die Schnittdarstellung entlang der Außenfläche y = 0 schließen.
    pts.append((pts[-1][0], 0.0))
    return pts


def write_section(path):
    """Gehäusequerschnitt von vorn: beide Profile, Deckel, Boden, Frontplatte."""
    prof = profile_points()
    x_out_l = (p.W_FRONT - BOX_WIDTH) / 2          # Außenfläche linkes Profil
    x_out_r = p.W_FRONT - x_out_l
    HH = p.H_FRONT

    def poly_l(pts):     # linkes Profil: Höhe -> y, Breite -> x nach innen
        return " ".join(f"{x_out_l + y:.3f},{HH - x:.3f}" for x, y in pts)

    def poly_r(pts):     # rechtes Profil gespiegelt
        return " ".join(f"{x_out_r - y:.3f},{HH - x:.3f}" for x, y in pts)

    def dim(x1, y1, x2, y2, text, off=0.0):
        return (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#C0392B" '
                f'stroke-width="0.25"/>'
                f'<text x="{(x1 + x2) / 2:.2f}" y="{(y1 + y2) / 2 - 1.2 + off:.2f}" font-size="3.2" '
                f'text-anchor="middle" fill="#C0392B" font-family="{p.FONT}">{text}</text>')

    g = []
    # Frontplatte als Hintergrund
    g.append(f'<rect x="0" y="0" width="{p.W_FRONT}" height="{HH}" rx="2" fill="{p.CREAM}" '
             f'stroke="{p.INK}" stroke-width="0.3"/>')
    # Profile
    for pl in (poly_l(prof), poly_r(prof)):
        g.append(f'<polygon points="{pl}" fill="#B8BCC0" stroke="#4A4E52" stroke-width="0.3"/>')
    # Bleche in den Nuten
    for lo, hi in (GROOVE_LO, GROOVE_HI):
        y1 = HH - hi
        g.append(f'<rect x="{x_out_l + GROOVE_BOTTOM:.2f}" y="{y1:.2f}" '
                 f'width="{BOX_WIDTH - 2 * GROOVE_BOTTOM:.2f}" height="{hi - lo:.2f}" '
                 f'fill="#8FA0B0" stroke="#3A4A5A" stroke-width="0.25"/>')
    # Schraubkanäle
    for xo, sgn in ((x_out_l, 1), (x_out_r, -1)):
        for hgt in (SCREW_INSET, PROF_H - SCREW_INSET):
            g.append(f'<circle cx="{xo + sgn * SCREW_INSET:.2f}" cy="{HH - hgt:.2f}" r="2.25" '
                     f'fill="#FFFFFF" stroke="#C0392B" stroke-width="0.3"/>')
    # Bemaßung
    g.append(dim(x_out_l, HH + 6, x_out_r, HH + 6, f"Gehäuse {BOX_WIDTH:.0f}"))
    g.append(dim(x_out_l + GROOVE_BOTTOM, HH + 13, x_out_r - GROOVE_BOTTOM, HH + 13,
                 f"Nutgrund {BOX_WIDTH - 2 * GROOVE_BOTTOM:.0f} – Blech {COVER_W:.0f}"))
    g.append(dim(0, HH + 20, p.W_FRONT, HH + 20, f"Frontplatte {p.W_FRONT}"))
    g.append(f'<text x="{p.W_FRONT / 2:.1f}" y="-4" font-size="4.5" text-anchor="middle" '
             f'fill="{p.INK}" font-family="{p.FONT}">FS-1A Gehäusequerschnitt – '
             f'Tiefe {BOX_DEPTH:.0f} mm (Profil), {BOX_DEPTH + 2 * PANEL_T:.0f} mm über alles</text>')

    Path(path).write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{p.W_FRONT + 20}mm" height="{HH + 40}mm" '
        f'viewBox="-10 -10 {p.W_FRONT + 20} {HH + 40}">\n  ' + "\n  ".join(g) + "\n</svg>\n",
        encoding="utf-8")


def write_cover_drawing(path):
    """Bemaßte Blechzeichnung für Deckel und Boden."""
    W_, L_ = COVER_W, COVER_L
    m = 26.0
    g = [f'<rect x="0" y="0" width="{W_}" height="{L_}" rx="{1.5}" fill="#E9EDF1" '
         f'stroke="#333" stroke-width="0.6"/>']

    def dimh(y, x1, x2, txt):
        return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#C0392B" stroke-width="0.5"/>'
                f'<line x1="{x1}" y1="{y - 3}" x2="{x1}" y2="{y + 3}" stroke="#C0392B" stroke-width="0.5"/>'
                f'<line x1="{x2}" y1="{y - 3}" x2="{x2}" y2="{y + 3}" stroke="#C0392B" stroke-width="0.5"/>'
                f'<text x="{(x1 + x2) / 2}" y="{y - 3}" font-size="9" text-anchor="middle" '
                f'fill="#C0392B" font-family="{p.FONT}">{txt}</text>')

    def dimv(x, y1, y2, txt):
        return (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="#C0392B" stroke-width="0.5"/>'
                f'<line x1="{x - 3}" y1="{y1}" x2="{x + 3}" y2="{y1}" stroke="#C0392B" stroke-width="0.5"/>'
                f'<line x1="{x - 3}" y1="{y2}" x2="{x + 3}" y2="{y2}" stroke="#C0392B" stroke-width="0.5"/>'
                f'<text x="{x - 4}" y="{(y1 + y2) / 2}" font-size="9" text-anchor="middle" '
                f'fill="#C0392B" font-family="{p.FONT}" transform="rotate(-90 {x - 4} '
                f'{(y1 + y2) / 2})">{txt}</text>')

    hx, hy = W_ / 2, COVER_HOLE_FROM_FRONT
    g.append(f'<circle cx="{hx}" cy="{hy}" r="{COVER_HOLE_D / 2}" fill="#fff" stroke="#333" '
             f'stroke-width="0.4"/>'
             f'<line x1="{hx - 4}" y1="{hy}" x2="{hx + 4}" y2="{hy}" stroke="#C0392B" stroke-width="0.3"/>'
             f'<line x1="{hx}" y1="{hy - 4}" x2="{hx}" y2="{hy + 4}" stroke="#C0392B" stroke-width="0.3"/>'
             f'<text x="{hx + 7}" y="{hy + 3.5}" font-size="9" fill="#C0392B" '
             f'font-family="{p.FONT}">&#216;{COVER_HOLE_D}</text>')
    g.append(dimh(-12, 0, W_, f"{W_:.0f} mm"))
    g.append(dimv(-12, 0, L_, f"{L_:.1f} mm"))
    g.append(f'<text x="{W_ / 2}" y="{L_ / 2 - 8}" font-size="13" text-anchor="middle" fill="#333" '
             f'font-family="{p.FONT}">FS-1A Deckel und Boden</text>')
    g.append(f'<text x="{W_ / 2}" y="{L_ / 2 + 8}" font-size="9.5" text-anchor="middle" fill="#333" '
             f'font-family="{p.FONT}">Aluminium {COVER_T} mm, 2 Stück – Kanten entgratet</text>')
    g.append(f'<text x="{W_ / 2}" y="{L_ / 2 + 21}" font-size="9.5" text-anchor="middle" fill="#333" '
             f'font-family="{p.FONT}">schiebt in die Blechnuten des Gie-Tec Seitenteilprofils 4 '
             f'(Nut 1,6 mm, Eingriff 2,5 mm je Seite)</text>')
    g.append(f'<text x="{W_ / 2}" y="{L_ / 2 + 32}" font-size="9" text-anchor="middle" '
             f'fill="#C0392B" font-family="{p.FONT}">Bohrung &#216;{COVER_HOLE_D} mittig, '
             f'{COVER_HOLE_FROM_FRONT} mm von der Vorderkante</text>')
    g.append(f'<text x="{W_ / 2}" y="{L_ / 2 + 44}" font-size="9" text-anchor="middle" '
             f'fill="#C0392B" font-family="{p.FONT}">für Winkel Keystone 633 zum '
             f'Gewindebolzen der Frontplatte</text>')
    Path(path).write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{W_ + 2 * m}mm" height="{L_ + 2 * m}mm" '
        f'viewBox="{-m} {-m} {W_ + 2 * m} {L_ + 2 * m}">\n  <rect x="{-m}" y="{-m}" '
        f'width="{W_ + 2 * m}" height="{L_ + 2 * m}" fill="#FFFFFF"/>\n  ' + "\n  ".join(g) + "\n</svg>\n",
        encoding="utf-8")


def stueckliste():
    rows = [
        ("2", "Seitenteilprofil", f"Gie-Tec 122040, Zuschnitt {BOX_DEPTH:.0f} mm"),
        ("1", "Frontplatte", f"{p.W_FRONT} x {p.H_FRONT} x {PANEL_T:.0f} mm – fs1a_frontpanel(.druck).fpd"),
        ("1", "Rückwand", f"{BOX_WIDTH:.0f} x {p.H_FRONT} x {PANEL_T:.0f} mm – fs1a_rueckwand.fpd"),
        ("2", "Deckel / Boden", f"{COVER_W:.0f} x {COVER_L:.1f} x {COVER_T} mm Alu-Blech – {NAME}.dxf (Blechzuschnitt)"),
        ("8", "Schraube M5", "Blechschraube/gewindeformend in die Profilkanäle, 4 vorn + 4 hinten"),
        ("2", "Winkel", "Keystone 633, Frontplatte oben/unten mittig an Deckel und Boden"),
        ("2", "Mutter M3", "auf die Gewindebolzen der Frontplatte"),
        ("2", "Schraube M3", "Winkel an Deckel/Boden, mit Mutter"),
    ]
    w = max(len(r[1]) for r in rows)
    print("\nStückliste Gehäuse")
    for n, t, d in rows:
        print(f"  {n:>2} x  {t:<{w}}  {d}")
    print(f"\n  Außenmaße: {p.W_FRONT} x {p.H_FRONT} x {BOX_DEPTH + 2 * PANEL_T:.0f} mm "
          f"(Blende), Korpus {BOX_WIDTH:.0f} mm breit")


if __name__ == "__main__":
    p.W_FRONT, p.H_FRONT = p.W, p.H          # Frontplattenmaße merken
    write_section(OUT / "fs1a_gehaeuse_schnitt.svg")

    build_cover()
    p.R_CORNER = 1.5
    p.write_svg(OUT / f"{NAME}.svg", preview=False)
    p.write_dxf(OUT / f"{NAME}.dxf")
    write_cover_drawing(OUT / f"{NAME}_zeichnung.svg")
    p.write_holes(OUT / f"{NAME}_bohrungen.csv")
    print(f"{NAME}.svg / .dxf / _zeichnung.svg / _bohrungen.csv  ({COVER_W:.1f} x {COVER_L:.1f} x {COVER_T} mm, 2 Stück)")
    print("  Hinweis: Schaeffer fertigt diese Größe nicht in 1,5 mm (geprüft im "
          "Frontplatten Designer) – Blechzuschnitt beim Blechner bestellen.")
    print("fs1a_gehaeuse_schnitt.svg")
    stueckliste()
