#!/usr/bin/env python3
"""Rückwand zum FS-1A-Frontpanel – Gie-Tec Seitenteilprofil 4, Gehäuse 437 mm breit.

Erzeugt fs1a_rueckwand.svg / .dxf / .fpjs / _bohrungen.csv mit denselben Routinen
wie fs1a_panel.py (dort stehen auch alle Konstanten).

Inhalt: Außenkontur 437 x 88,1 mm, vier M5-Durchgänge in die Schraubkanäle der
Seitenteilprofile, zwei M3-Löcher für die Montagewinkel zu Deckel und Boden
und ein Durchbruch Ø 12 mm für die Kabeldurchführung.

Aufruf:  python3 fs1a_rueckwand.py
"""
from pathlib import Path

import fs1a_panel as p

# ------------------------------------------------------------------ Maße
W, H = p.BOX_WIDTH, 88.1      # Rückwand deckt die Profil-Stirnflächen ab
HOLE_D = 12.0                 # Kabeldurchführung
HOLE_X = 40.0                 # von der linken Kante
HOLE_Y_FROM_BOTTOM = 30.0
BRACKET_SCREW_D = 3.2         # M3-Durchgang für die Winkel zu Deckel und Boden

NAME = "fs1a_rueckwand"
OUT = Path(__file__).parent


def build():
    p.W, p.H = W, H
    p.CUTS.clear()
    p.PRINT.clear()
    p.PREV.clear()

    # Befestigung: dieselben Schraubkanäle wie vorn, 5 mm von der Außenkante,
    # 78,3 mm Abstand, mittig zur Wandhöhe
    xs = (p.PROFILE_HOLE_INSET, W - p.PROFILE_HOLE_INSET)
    ys = (H / 2 - p.PROFILE_HOLE_PITCH / 2, H / 2 + p.PROFILE_HOLE_PITCH / 2)
    for x in xs:
        for y in ys:
            p.hole("Schraube M5", x, y, p.DRILL["screw"], "M5 in Schraubkanal Seitenteilprofil 4")
            p.screw_preview(x, y)

    # Löcher für die Montagewinkel (Keystone 633) zu Deckel und Boden,
    # auf derselben Höhe wie die Gewindebolzen der Frontplatte
    for by in (p.Y_BOLT_TOP, p.Y_BOLT_BOT):
        p.hole("Winkelschraube M3", W / 2, by, BRACKET_SCREW_D,
               "Keystone 633 zu Deckel/Boden, Schraube von außen")
        p.PREV.append(f'<circle cx="{p.f(W / 2)}" cy="{p.f(by)}" '
                      f'r="{p.f(BRACKET_SCREW_D / 2)}" fill="#2A2A2A"/>')

    # Kabeldurchführung
    y_hole = H - HOLE_Y_FROM_BOTTOM
    p.hole("Kabeldurchführung", HOLE_X, y_hole, HOLE_D,
           f"{HOLE_X:.0f} mm von links, {HOLE_Y_FROM_BOTTOM:.0f} mm von unten")
    p.PREV.append(f'<circle cx="{p.f(HOLE_X)}" cy="{p.f(y_hole)}" r="{p.f(HOLE_D / 2)}" fill="#2A2A2A"/>')


if __name__ == "__main__":
    build()
    p.FPD = dict(p.FPD,
                 name="FS-1A Rückwand",
                 material="alu_elox",
                 matcolor="elox_natural",
                 printed=False,
                 remark="FS-1A Rückwand, Gehäuse 437 mm (Gie-Tec Seitenteilprofil 4). "
                        "Bohrung Ø12 für Kabeldurchführung.",
                 save_as=str((OUT / f"{NAME}.fpd").resolve()))
    p.write_svg(OUT / f"{NAME}.svg", preview=True)
    p.write_dxf(OUT / f"{NAME}.dxf")
    p.write_fpjs(OUT / f"{NAME}.fpjs")
    p.write_holes(OUT / f"{NAME}_bohrungen.csv")
    print(f"{NAME}.svg / .dxf / .fpjs / _bohrungen.csv  ({len(p.CUTS)} Ausschnitte, "
          f"{W:.1f} x {H:.1f} mm)")
