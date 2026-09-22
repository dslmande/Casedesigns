#!/usr/bin/env python3
"""Frontpanel-Generator: Jürgen Haible Frequency Shifter FS-1A, 19" / 2 HE.

Erzeugt aus einem gemeinsamen Geometriemodell:

  fs1a_frontpanel.svg   1:1 in mm, Inkscape-Ebenen (Kontur, Ausschnitte, Druck,
                        Bauteile-Vorschau, Bohrmaße)
  fs1a_frontpanel.dxf   DXF R12, Ebenen KONTUR / AUSSCHNITTE / DRUCK
                        (Text als Pfade, Hershey-Strichschrift) – für den
                        DXF-Import-Assistenten von FrontDesign, KiCad, Inkscape …
  fs1a_frontpanel.fpjs  Skript für Schaeffer FrontDesign (Bearbeiten → Skripte):
                        legt Platte, Bohrungen, Textgravuren und Linien nativ an
                        und speichert die .fpd
  fs1a_frontpanel_bohrungen.csv  Bohrtabelle

Nur Standardbibliothek – läuft mit /usr/bin/python3.
Aufruf:  python3 fs1a_panel.py [--no-preview] [--out NAME]
"""
import csv
import math
import sys
from pathlib import Path

# ------------------------------------------------------------------ Panel
W, H = 482.6, 88.1            # 19" Rackblende, 2 HE
PANEL_T = 3.0                 # Blendendicke – 3 mm, damit die M5-Senkung (2,64 mm) hineinpasst
R_CORNER = 2.0
BLEED = 1.0                   # Druckgrafik läuft ≥1 mm über die Plattenkante hinaus (Schaeffer: bündig oder darüber)
PT = 25.4 / 72                # Chrome rundet PDF-Seiten auf ganze Punkte: Seitengröße so wählen, dass nichts gerundet wird
PW = math.ceil((W + 2 * BLEED) / PT) * PT    # Druckseite Breite (mm)
PH = math.ceil((H + 2 * BLEED) / PT) * PT    # Druckseite Höhe (mm)
BX, BY = (PW - W) / 2, (PH - H) / 2          # tatsächlicher Beschnitt je Seite
INSET = 2.5                   # Abstand der Rahmenlinien vom Panelrand
TITLE = "JH FS-1A FREQUENCY SHIFTER"
BRAND = "Made by DSL-man.de"

# Farben (SVG)
CREAM = "#F2E7C6"             # Panel (etwa RAL 1015 Hellelfenbein)
INK = "#22307C"               # Druckfarbe (Dunkelblau)
BLACK = "#161616"
GREY = "#BEC1C4"
SILVER = "#C9CCD0"
BLUE = "#2E6FD8"
RED = "#E8431C"
LED_BLUE, LED_ORANGE, LED_GREEN, LED_OFF = "#3B7BFF", "#FF8C1A", "#3CE05A", "#4A3A2A"

# Bohrdurchmesser (mm) – vor Fertigung mit den eigenen Bauteilen abgleichen
DRILL = {
    "pot": 7.5,        # Alpha 16 mm, M7-Gewinde
    "jack": 9.5,       # 6,35-mm-Klinke (Neutrik NYS / Cliff)
    "combo": 24.0,     # Neutrik Combo NCJ6FI-S (Lötversion): Ausschnitt >= Ø23,8 (Zeichnung 3102ST1728)
    "combo_screw": 3.2,
    "toggle": 6.0,     # Miniatur-Kippschalter, M6-Gewindebuchse
    "led3": 3.2,
    "led5": 5.2,
    "screw": 5.3,      # M5 Durchgang (Rückwand, ohne Senkung)
    "screw_csk": 5.6,  # M5 mit Senkung DIN 74A für Senkkopfschrauben (Schaeffer-Maß)
}
# Netzschalter: Marquardt 1555.3102 (Wippschalter 2-polig, rot beleuchtet, Snap-in, Reichelt WIPPE 1555.3102)
# Datenblatt: Ausschnitt 27,2 ±0,1 x 12,2 +0,2 mm, Wandstärke 0,8–5 mm, Blende 30 x 15 mm – hochkant eingebaut
POWER_CUT_W, POWER_CUT_H, POWER_CUT_R = 12.3, 27.2, 1.0
COMBO_SCREW_DX, COMBO_SCREW_DY = 10.0, 11.5   # Combo-Befestigung NCJ6FI-S: 20 x 23 mm (oben links / unten rechts)
                                              # PCB-Version NCJ6FA-H wäre Ø22 und 19,8 x 19,8 mm
SLOT_W, SLOT_H = 10.0, 6.4    # Rack-Langloch
SLOT_X = 8.75                 # Lochmitte vom Rand (465,1 mm Rastermaß)
SLOT_DY = 38.1                # Lochmitte von der Panelmitte

# Schriftgrößen (SVG-font-size in mm; Versalhöhe ≈ 0,72 × font-size)
F_LABEL, F_SUB, F_NUM, F_BIGNUM, F_TITLE, F_BRAND = 3.4, 3.1, 2.5, 2.8, 6.2, 3.6
CAP = 0.72
FPD_TEXT = 0.88   # FrontDesign-Schriftgröße = 0,88 × SVG-font-size (Versalhöhe stimmt dann überein)
FONT = "'Segoe UI', 'Myriad Pro', 'Helvetica Neue', Helvetica, Arial, sans-serif"

# Linienbreiten (mm)
LW_FRAME, LW_TICK, LW_ARC, LW_FINE = 0.35, 0.3, 0.35, 0.25

# FrontDesign (Schaeffer) – Material, Farben, Schriften, Werkzeuge
FPD = {
    "name": "FS-1A Frontpanel",
    "thickness": "thick_3mm",
    "material": "alu_powder_coated",      # oder alu_elox
    "matcolor": "pcoat_grey_white",       # RAL 9002, dem Creme am nächsten; elox_natural bei alu_elox
    "elox_color": "elox_natural",         # Druckvariante: Digitaldruck geht nur auf eloxiertem Alu
    "ink": "engrave_night_blue",          # RAL 5022
    "font": "helvetica-light-1stroke",
    "font_title": "helvetica-medium-outline",
    "tool": "engraver_0_4mm",
    "tool_fine": "engraver_0_2mm",
    "printed": True,                      # Druck statt Gravur (wie beim Vorbild)
    "save_as": str(Path(__file__).resolve().parent / "fs1a_frontpanel.fpd"),   # FrontDesign braucht einen absoluten Pfad
}

# ------------------------------------------------------------------ Layout
Y_TOP, Y_BOT = 26.5, 67.0     # Mitten der oberen / unteren Bauteilreihe
Y_MID = 45.0                  # Trennlinie links
LBL_DY = 16.0                 # Namenszeile unter der Bauteilmitte – eine Zeile unter den Skalenenden
Y_LBL_TOP, Y_LBL_BOT = Y_TOP + LBL_DY, Y_BOT + LBL_DY
X0, X1 = 38.0, 427.5          # linker / rechter Rand der Rahmenblöcke (rechts verkürzt: Wippschalter muss vor dem Profil bleiben)
X_PRE, X_AUX = 133.5, 122.5   # Preamp-Block rechts / AUX-Block rechts
X_EXP = 174.0                 # Invert/EXP- und V/OCT-Block rechts
X_MAIN = 273.0                # Hauptblock rechts
X_LIN = 301.0                 # LIN-Block rechts
X_LFO = 335.0                 # LFO-Block rechts (breit genug für die Skalenzahlen der FREQ-Skala)
Y_TITLE = 12.0                # Titelrahmen unten
Y_OUT = 50.5                  # Trennlinie Out A / Out B
X_OUT_C = (X_LFO + X1) / 2
# Befestigung an Gie-Tec Seitenteilprofil 4 (Art. 122040), Seitenteil für 19-Zoll-Gehäuse 2 HE:
# Profil 88,30 mm hoch, Anlagefläche 16 mm breit (hinten bis 20,5), Schraubkanäle Ø4,5 für M5,
# Kanalmitte je 5 mm von Ober- und Unterkante (Abstand 78,3) und 5 mm hinter der Außenfläche.
PROFILE_HOLE_PITCH = 78.3
PROFILE_HOLE_INSET = 5.0
PROFILE_FACE = 16.0           # so weit ragt das Profil hinter der Blende nach innen
PROF_H = 88.30                # Profilhöhe
GROOVE_LO = (1.4, 3.0)        # Blechnut unten: Höhenband über der Profilunterkante
GROOVE_HI = (PROF_H - 3.0, PROF_H - 1.4)      # Blechnut oben
GROOVE_BOTTOM = 10.0          # Nutgrund, von der Außenfläche des Profils
COVER_T = 1.5                 # Deckel-/Bodenblech
# Montagewinkel Keystone 633 (Messing vernickelt): Schenkel 9,5 x 9,5 mm, Breite 7,1 mm,
# Materialstärke 0,81 mm, beide Löcher Ø3,7 – Lochmitte je 5,5 mm von der Außenfläche des
# jeweils anderen Schenkels. Ein Schenkel kommt auf den Gewindebolzen hinter der Blende,
# der andere wird ans Deckel- bzw. Bodenblech geschraubt.
BRACKET_HOLE_OFF = 5.5
BRACKET_T = 0.81
BOLT_TYPE, BOLT_LEN = "GU30", 6               # Einklebebolzen M3, 6 mm (kürzeste Länge)
# Senkung für die Befestigungsschrauben der Blende.
# Randbedingung: die Schraubkanäle liegen 5 mm von der Profilkante, die Blende ist 0,2 mm
# niedriger -> Lochmitte nur 4,9 mm von der Blendenkante. Schaeffers fertige Senkung
# DIN 74A-M5 ist bei 3 mm Platte Ø10,94 und würde die Kante anschneiden; ein Senkkopf
# DIN 7991 (dk 10,0) ebenfalls. Passend ist nur DIN 965 / ISO 7046, dk 9,2 -> 0,3 mm
# Restmaterial zur Kante. Deshalb eine kundendefinierte Senkung auf genau dieses Maß.
# Schraube: DIN 965 M5 x 20, A2, Kreuzschlitz PH2 (dk 9,2 / k 2,5 / 90°).
CSK_CONE, CSK_DRILL, CSK_CYL, CSK_ANGLE = 9.2, 5.3, 0.2, 90
CSK_DEPTH = (CSK_CONE - CSK_DRILL) / 2 + CSK_CYL     # 2,15 mm in der 3-mm-Platte
CSK_TYPE = f"custom:{CSK_CONE},{CSK_DRILL},{CSK_CYL},{CSK_ANGLE}"
BOX_WIDTH = 437.0             # Außenbreite des Gehäuses (Außenfläche zu Außenfläche der Profile)
X_PROFILE_IN_L = (W - BOX_WIDTH) / 2 + PROFILE_FACE      # ab hier ist hinter der Blende frei
X_PROFILE_IN_R = W - X_PROFILE_IN_L
X_EAR_L = (W - BOX_WIDTH) / 2 + PROFILE_HOLE_INSET
X_EAR_R = W - X_EAR_L
Y_EAR = (H / 2 - PROFILE_HOLE_PITCH / 2, H / 2 + PROFILE_HOLE_PITCH / 2)
# Gewindebolzen mittig oben und unten: der Winkel liegt flach am Blech an, seine Lochmitte
# sitzt 5,5 mm von der Blechfläche entfernt.
Z_PROF = (H - PROF_H) / 2                                  # Profilunterkante zur Blendenunterkante
_Z_COVER_LO = Z_PROF + GROOVE_LO[0] + ((GROOVE_LO[1] - GROOVE_LO[0]) - COVER_T) / 2 + COVER_T
_Z_COVER_HI = Z_PROF + GROOVE_HI[0] + ((GROOVE_HI[1] - GROOVE_HI[0]) - COVER_T) / 2
Y_BOLT_TOP = H - (_Z_COVER_HI - BRACKET_HOLE_OFF)          # von der Blendenoberkante
Y_BOLT_BOT = H - (_Z_COVER_LO + BRACKET_HOLE_OFF)

# ------------------------------------------------------- Geometriemodell
# Koordinaten wie in der SVG: x nach rechts, y nach unten, Ursprung oben links.
# Winkel: 0° = oben, positiv im Uhrzeigersinn (Bogen immer von a0 nach a1 im UZS).
PRINT = []    # ("line", x1,y1,x2,y2,w) | ("arc", cx,cy,r,a0,a1,w) | ("poly", pts,w)
              # | ("text", x,y,s,size,anchor,style)
CUTS = []     # ("circle", kind,x,y,d,note) | ("slot", x,y,w,h)
PREV = []     # SVG-Fragmente (nur Vorschau)


def f(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


def pol(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def p_line(x1, y1, x2, y2, w=LW_FRAME):
    PRINT.append(("line", x1, y1, x2, y2, w))


def p_arc(cx, cy, r, a0, a1, w=LW_ARC):
    PRINT.append(("arc", cx, cy, r, a0, a1, w))


def p_poly(pts, w=LW_FRAME):
    PRINT.append(("poly", list(pts), w))


def p_text(x, y, s, size=F_LABEL, anchor="middle", style="label"):
    """y ist die optische Mitte der Versalien."""
    PRINT.append(("text", x, y, s, size, anchor, style))


SINK = {}     # (x, y) -> FrontDesign-Senkungskonstante


def hole(kind, x, y, d, note="", sink=None):
    CUTS.append(("circle", kind, x, y, d, note))
    if sink:
        SINK[(round(x, 3), round(y, 3))] = sink


def slot(x, y):
    CUTS.append(("slot", x, y, SLOT_W, SLOT_H))


def rect_cut(kind, x, y, w, h, r, note=""):
    CUTS.append(("rect", kind, x, y, w, h, r, note))


BOLTS = []    # (x, y, typ, laenge, note) – Gewindebolzen auf der Rückseite, kein Loch


def bolt(x, y, note="", typ=BOLT_TYPE, laenge=BOLT_LEN):
    BOLTS.append((x, y, typ, laenge, note))
    PREV.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="3" fill="none" stroke="#8A8D92" '
                f'stroke-width="0.3" stroke-dasharray="1.2 0.8"/>'
                f'<line x1="{f(x - 2)}" y1="{f(y)}" x2="{f(x + 2)}" y2="{f(y)}" stroke="#8A8D92" '
                f'stroke-width="0.25"/>'
                f'<line x1="{f(x)}" y1="{f(y - 2)}" x2="{f(x)}" y2="{f(y + 2)}" stroke="#8A8D92" '
                f'stroke-width="0.25"/>')


# --------------------------------------------------------------- Skalen
def ticks(cx, cy, r_in, r_out, angles, w=LW_TICK):
    for a in angles:
        x1, y1 = pol(cx, cy, r_in, a)
        x2, y2 = pol(cx, cy, r_out, a)
        p_line(x1, y1, x2, y2, w)


def small_scale(cx, cy, kind):
    """Skala für 19-mm-Knöpfe: 11 Striche über 300°, Zahlen je nach Typ."""
    angles = [-150 + 30 * i for i in range(11)]
    ticks(cx, cy, 10.3, 11.8, angles)
    labels = {
        "full": {a: str(i) for i, a in enumerate(angles)},
        "ends": {-150: "0", 0: "5", 150: "10"},
        "drywet": {-150: "dry", 150: "wet"},
        "bipolar": {-150: "-5", 0: "0", 150: "+5"},
        "fine": {-150: "b", 0: "0", 150: "#"},
    }[kind]
    for a, s in labels.items():
        x, y = pol(cx, cy, 13.6, a)
        p_text(x, y, s, size=F_NUM)


def big_scale(cx, cy, labels, name):
    """Skala der großen Knöpfe: Bogen 300°, Feinteilung, Klammer zum Namen."""
    R = 20.2
    ticks(cx, cy, 17.2, R, [-150 + 30 * i for i in range(11)], w=LW_ARC)
    ticks(cx, cy, 18.6, R, [-150 + 6 * i for i in range(51) if i % 5], w=LW_FINE)
    p_arc(cx, cy, R, -150, 150, LW_ARC)
    y_end = cy + 19.8
    for a in (-150, 150):
        x, y = pol(cx, cy, R, a)
        p_line(x, y, x, y_end, LW_ARC)
    for a, s in labels.items():
        x, y = pol(cx, cy, 22.8, a)
        p_text(x, y, s, size=F_BIGNUM)
    p_text(cx, cy + 20.6, name)


# ------------------------------------------------------ Vorschau (SVG)
def _c(cx, cy, r, fill, stroke="none", w=0):
    PREV.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="{f(w)}"/>')


def _l(x1, y1, x2, y2, w, color):
    PREV.append(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" '
                f'stroke="{color}" stroke-width="{f(w)}" stroke-linecap="round"/>')


def knob_preview(cx, cy, style, angle=0):
    if style == "big":
        _c(cx, cy, 18.0, BLACK)
        _c(cx, cy, 16.5, "#262626")
        _c(cx, cy, 14.5, GREY, "#9A9DA0", 0.3)
        x1, y1 = pol(cx, cy, 14.8, angle)
        x2, y2 = pol(cx, cy, 17.6, angle)
        _l(x1, y1, x2, y2, 1.4, "#E8E8E8")
        return
    _c(cx, cy, 9.5, BLACK)
    _c(cx, cy, 8.3, "#262626")
    if style in ("blue", "red"):
        col = BLUE if style == "blue" else RED
        _c(cx, cy, 7.0, col)
        p = [pol(cx, cy, 6.6, angle - 14), pol(cx, cy, 9.3, angle), pol(cx, cy, 6.6, angle + 14)]
        PREV.append('<polygon points="' + " ".join(f"{f(x)},{f(y)}" for x, y in p) + f'" fill="{col}"/>')
        x1, y1 = pol(cx, cy, 2.5, angle)
        x2, y2 = pol(cx, cy, 9.0, angle)
        _l(x1, y1, x2, y2, 0.5, "#FFFFFF")
    else:
        cap = GREY if style == "grey" else "#2C2C2C"
        _c(cx, cy, 6.8, cap, "#8E9194" if style == "grey" else "#000", 0.25)
        x1, y1 = pol(cx, cy, 7.0, angle)
        x2, y2 = pol(cx, cy, 9.2, angle)
        _l(x1, y1, x2, y2, 1.1, "#E8E8E8")


def jack_preview(cx, cy):
    _c(cx, cy, 9.0, BLACK)
    _c(cx, cy, 7.6, "#242424")
    _c(cx, cy, 4.3, SILVER)
    _c(cx, cy, 3.2, "#0A0A0A")


def combo_screws(cx, cy):
    """Von vorn gesehen: oben links und unten rechts (Neutrik 3102ST1728, Ausschnitt Vorderseite)."""
    return [(cx - COMBO_SCREW_DX, cy - COMBO_SCREW_DY), (cx + COMBO_SCREW_DX, cy + COMBO_SCREW_DY)]


def combo_preview(cx, cy):
    for sx, sy in combo_screws(cx, cy):           # Schraubenohren des Gehäuses
        _c(sx, sy, 3.4, BLACK)
    _c(cx, cy, 11.7, BLACK)
    _c(cx, cy, 10.6, "#242424")
    _c(cx, cy, 8.6, "#161616", "#3A3A3A", 0.3)
    _c(cx, cy, 3.6, SILVER)
    _c(cx, cy, 2.9, "#0A0A0A")
    for a in (-100, 100, 200):
        x, y = pol(cx, cy, 6.3, a)
        _c(x, y, 1.4, SILVER)
        _c(x, y, 0.9, "#0A0A0A")
    for sx, sy in combo_screws(cx, cy):
        _c(sx, sy, 1.9, "#3A3A3A")
        _c(sx, sy, 1.3, "#1E1E1E")


def toggle_preview(cx, cy, size=1.0):
    r = 5.0 * size
    pts = " ".join(f"{f(x)},{f(y)}" for x, y in (pol(cx, cy, r, 30 + 60 * i) for i in range(6)))
    PREV.append(f'<polygon points="{pts}" fill="{SILVER}" stroke="#8A8D92" stroke-width="0.25"/>')
    _c(cx, cy, 3.1 * size, "#9DA0A5", "#6E7176", 0.2)
    x2, y2 = pol(cx, cy, 4.6 * size, 0)
    _l(cx, cy, x2, y2, 2.0 * size, "#B5B8BD")
    _c(x2, y2, 1.2 * size, "#D5D8DC", "#8A8D92", 0.2)


def rocker_preview(cx, cy, w=15.0, h=30.0):
    """Beleuchteter Wippschalter, hochkant: Blende 15 x 30, Wippe mit rotem Fenster."""
    PREV.append(f'<rect x="{f(cx - w / 2)}" y="{f(cy - h / 2)}" width="{f(w)}" height="{f(h)}" rx="1" '
                f'fill="{BLACK}"/>')
    PREV.append(f'<rect x="{f(cx - w / 2 + 1.6)}" y="{f(cy - h / 2 + 1.6)}" width="{f(w - 3.2)}" '
                f'height="{f(h / 2 - 1.2)}" rx="0.8" fill="#2A2A2A"/>')
    PREV.append(f'<rect x="{f(cx - w / 2 + 1.6)}" y="{f(cy + 0.4)}" width="{f(w - 3.2)}" '
                f'height="{f(h / 2 - 2.0)}" rx="0.8" fill="#3A3A3A"/>')
    PREV.append(f'<rect x="{f(cx - 3.2)}" y="{f(cy - h / 2 + 4.5)}" width="6.4" height="4.2" rx="0.6" '
                f'fill="#C8332A" stroke="#5A1510" stroke-width="0.2"/>')
    PREV.append(f'<line x1="{f(cx)}" y1="{f(cy + 6.5)}" x2="{f(cx)}" y2="{f(cy + 10)}" stroke="#D0D0D0" '
                f'stroke-width="0.7"/>')
    PREV.append(f'<circle cx="{f(cx)}" cy="{f(cy + 3.5)}" r="1.4" fill="none" stroke="#D0D0D0" '
                f'stroke-width="0.6"/>')


def led_preview(cx, cy, color, r=1.5):
    _c(cx, cy, r + 0.6, color + "55")
    _c(cx, cy, r, color, "#333", 0.15)


def screw_preview(cx, cy):
    _c(cx, cy, 4.3, "#1C1C1C")
    _c(cx, cy, 2.2, "none", "#3C3C3C", 0.45)


# --------------------------------------------------------------- Elemente
def pot(x, y, label, scale, style, ly=None, angle=0, note=None):
    hole("Poti", x, y, DRILL["pot"], note or label)
    small_scale(x, y, scale)
    if label:
        p_text(x, ly if ly is not None else y + LBL_DY, label)
    knob_preview(x, y, style, angle)


def jack(x, y, label, ly=None):
    hole("Klinke 6,35", x, y, DRILL["jack"], label)
    p_text(x, ly if ly is not None else y + LBL_DY, label)
    jack_preview(x, y)


def toggle(x, y, above=None, below=None, dy=7.5, size=F_SUB, note=None):
    note = note or f"{above or ''}/{below or ''}".strip("/").replace("\n", " ")
    hole("Kippschalter", x, y, DRILL["toggle"], note)
    if above:
        lines = above.split("\n")
        for i, s in enumerate(lines):
            p_text(x, y - dy - (len(lines) - 1 - i) * 3.6, s, size=size)
    if below:
        p_text(x, y + dy, below, size=size)
    toggle_preview(x, y)


def led(x, y, color, note, d=None):
    d = d or DRILL["led3"]
    hole("LED", x, y, d, note)
    led_preview(x, y, color, r=d / 2 - 0.1)


def screw(x, y, note):
    """Befestigung der Blende an den Schraubkanälen der Seitenteilprofile."""
    d = CSK_DRILL if CSK_TYPE else DRILL["screw"]
    hole("Schraube M5", x, y, d, note, sink=CSK_TYPE)
    if CSK_TYPE:
        PREV.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(CSK_CONE / 2)}" fill="#C9CCD0" '
                    f'stroke="#8A8D92" stroke-width="0.2"/>')
    screw_preview(x, y)


def corner_arc(x_h0, x_h1, x_v, y_h=6.5, r=3.0):
    """Signalfluss-Klammer: waagerecht von x_h0 nach x_h1, Viertelbogen, kurz senkrecht."""
    p_line(x_h0, y_h, x_h1, y_h)
    cx, cy = x_h1, y_h + r               # Mittelpunkt senkrecht unter dem Linienende
    if x_v > x_h1:                       # Bogen nach rechts unten: endet bei (x_h1 + r, cy)
        p_arc(cx, cy, r, 0, 90)
    else:                                # Bogen nach links unten: endet bei (x_h1 - r, cy)
        p_arc(cx, cy, r, -90, 0)
    p_line(x_v, cy, x_v, cy + 1.1)


# --------------------------------------------------------------- Aufbau
def build():
    for sx in (SLOT_X, W - SLOT_X):
        for sy in (H / 2 - SLOT_DY, H / 2 + SLOT_DY):
            slot(sx, sy)
    for ex in (X_EAR_L, X_EAR_R):
        for ey in Y_EAR:
            screw(ex, ey, "M5 Senkkopf DIN 965 in den Schraubkanal des Seitenteilprofils")

    # Rahmen
    y0, y1 = INSET, H - INSET
    for (xa, ya, xb, yb) in [
        (X0, y0, X1, y0), (X0, y1, X1, y1),
        (X0, Y_MID, X_EXP, Y_MID),
        (X_LFO, Y_TITLE, X1, Y_TITLE),
        (X_LFO, Y_OUT, X1, Y_OUT),
        (X0, y0, X0, y1), (X_PRE, y0, X_PRE, Y_MID), (X_AUX, Y_MID, X_AUX, y1),
        (X_EXP, y0, X_EXP, y1), (X_MAIN, y0, X_MAIN, y1), (X_LIN, y0, X_LIN, y1),
        (X_LFO, y0, X_LFO, y1), (X1, y0, X1, y1),
    ]:
        p_line(xa, ya, xb, yb)

    # ---- Preamp (oben links)
    # Preamp/AUX so weit links wie möglich: Combo-Gehäuse Ø23,4 braucht 1,2 mm Luft zum Profil (ab x 38,8)
    x_combo, x_gain, x_pad, x_lvl = 52.0, 80.0, 101.0, 120.5
    hole("Combo XLR/Klinke", x_combo, Y_TOP, DRILL["combo"], "Preamp, Neutrik NCJ6FI-S")
    for sx, sy in combo_screws(x_combo, Y_TOP):
        hole("Combo-Schraube", sx, sy, DRILL["combo_screw"], "M3, Neutrik-Zeichnung 3102ST1728 (20 x 23 mm)")
    p_text(x_combo, Y_LBL_TOP, "Preamp")
    combo_preview(x_combo, Y_TOP)
    pot(x_gain, Y_TOP, "GAIN", "full", "blue", angle=20)
    toggle(x_pad, Y_TOP, note="PAD")
    p_text(x_pad, Y_LBL_TOP, "PAD")
    pot(x_lvl, Y_TOP, "LEVEL", "ends", "blue", angle=-25)

    # ---- AUX / Feedback (unten links)
    x_fb1, x_fb2 = 101.0, 113.0
    jack(x_combo, Y_BOT, "AUX")
    pot(x_gain, Y_BOT, "LEVEL", "full", "red", angle=-150)
    toggle(x_fb1, Y_BOT, "Deep\nPhase", "Norm", dy=8.0)
    toggle(x_fb2, Y_BOT, "Up", "Down", dy=8.0)
    p_text((x_fb1 + x_fb2) / 2, Y_LBL_BOT, "FEEDBACK")

    # ---- Invert / EXP (oben) und V/OCT / CV IN (unten)
    x_inv, x_exp, x_voct = 139.5, 158.5, 134.0
    toggle(x_inv, Y_TOP, "+", None, dy=8.5, size=F_LABEL, note="Invert +/-")
    p_line(x_inv - 1.2, Y_TOP + 8.5, x_inv + 1.2, Y_TOP + 8.5, 0.4)     # Minus
    p_text(x_inv, Y_LBL_TOP, "Invert")
    pot(x_exp, Y_TOP, "EXP", "ends", "black", angle=-150)
    jack(x_voct, Y_BOT, "V/OCT")
    jack(x_exp, Y_BOT, "CV IN")
    corner_arc(X_EXP, x_exp + 3, x_exp)                     # Klammer zum Hauptblock
    p_line(x_exp, Y_LBL_TOP + 2.8, x_exp, Y_BOT - 9.6)      # EXP -> CV IN

    # ---- Hauptblock: RANGE / MANUAL / Fine Tune / LEDs
    x_mc = (X_EXP + X_MAIN) / 2
    x_rng, x_man, y_big = x_mc - 24.5, x_mc + 24.5, 27.0
    for x, labels, name in (
        (x_rng, {-150 + 30 * i: str(i) for i in range(1, 10)}, "RANGE"),
        (x_man, {-120 + 30 * i: f"{i - 4:+d}".replace("+0", "0") for i in range(9)}, "MANUAL"),
    ):
        hole("Poti (groß)", x, y_big, DRILL["pot"], name)
        big_scale(x, y_big, labels, name)
        knob_preview(x, y_big, "big", angle=-20 if name == "RANGE" else 150)
    for x in (x_rng, x_man):
        pot(x, Y_BOT, "Fine Tune", "fine", "grey", angle=15)
    # keine mittleren Befestigungsschrauben: bei Gie-Tec-Profilgehäuse gibt es dort keinen Gegenhalt
    y_led = 56.0
    led(x_mc - 9.5, y_led, LED_BLUE, "Freq Up")
    led(x_mc - 4.5, y_led, LED_ORANGE, "Freq Down")
    led(x_mc + 4.0, y_led, LED_BLUE, "Dir Up")
    led(x_mc + 9.0, y_led, LED_OFF, "Dir Down")
    p_text(x_mc - 7.0, y_led + 4.6, "Freq", size=F_SUB)
    p_text(x_mc + 6.5, y_led + 4.6, "Dir", size=F_SUB)

    # ---- LIN / CV IN
    x_lin = (X_MAIN + X_LIN) / 2
    pot(x_lin, Y_TOP, "LIN", "bipolar", "black", angle=-40)
    jack(x_lin, Y_BOT, "CV IN")
    corner_arc(X_MAIN, x_lin - 3, x_lin)
    p_line(x_lin, Y_LBL_TOP + 2.8, x_lin, Y_BOT - 9.6)

    # ---- LFO
    x_lfo = (X_LIN + X_LFO) / 2
    p_text(x_lfo, 6.2, "LFO", size=F_SUB)
    p_text(x_lfo, 9.9, "FREQ", size=F_SUB)
    pot(x_lfo, 26.5, None, "full", "red", angle=10, note="LFO FREQ")
    pot(x_lfo, 51.0, "AMPLITUDE", "ends", "red", angle=5)
    # Schalterreihe: 3-mm-LED (Ø3,2) in der Mitte, Beschriftung EXP/LIN und Wellenform-Symbole
    # ober- und unterhalb der LED mit ≥2,4 mm Abstand zum Lochrand
    y_sw = 77.0
    toggle(x_lfo - 9.5, y_sw, note="LFO EXP/LIN")
    toggle(x_lfo + 9.5, y_sw, note="LFO Dreieck/Rechteck")
    led(x_lfo, y_sw, LED_GREEN, "LFO")
    p_text(x_lfo - 3.3, y_sw - 5.2, "EXP", size=2.6)
    p_text(x_lfo - 3.3, y_sw + 5.2, "LIN", size=2.6)
    xs = x_lfo + 3.3
    p_poly([(xs - 1.6, y_sw - 4.0), (xs, y_sw - 6.4), (xs + 1.6, y_sw - 4.0)], 0.35)
    p_poly([(xs - 1.6, y_sw + 6.6), (xs - 1.6, y_sw + 4.0), (xs + 1.6, y_sw + 4.0),
            (xs + 1.6, y_sw + 6.6)], 0.35)

    # ---- Ausgangsblock: Titel, Out A, Out B
    p_text(X_OUT_C, (INSET + Y_TITLE) / 2 + 0.2, TITLE, size=F_TITLE, style="title")
    p_text(X_OUT_C, 47.0, BRAND, size=F_BRAND)
    x_mix, x_vol, x_ud, x_byp, x_out = 348.0, 372.0, 389.0, 402.0, 416.5
    for ch, yc in (("A", Y_TOP), ("B", Y_BOT)):
        pot(x_mix, yc, f"Mix {ch}", "drywet", "grey", angle=-60 if ch == "A" else 30)
        pot(x_vol, yc, f"Vol {ch}", "ends", "grey", angle=25 if ch == "A" else 120)
        toggle(x_ud, yc, "Up", "Down", dy=8.0)
        toggle(x_byp, yc, None, "Bypass", dy=8.0)
        jack(x_out, yc, f"OUT {ch}")

    # ---- Gewindebolzen M3 fuer die Montagewinkel zu Deckel und Boden
    for by in (Y_BOLT_TOP, Y_BOLT_BOT):
        bolt(W / 2, by, "Winkel Keystone 633 zum Blech")

    # ---- Netzschalter
    x_pwr, y_pwr = 436.5, H / 2               # Wippenkörper 12,3 breit: 430,4–442,7, 1,1 mm vor dem Profil
    rect_cut("Netzschalter", x_pwr, y_pwr, POWER_CUT_W, POWER_CUT_H, POWER_CUT_R,
             "Marquardt 1555.3102 Wippschalter, Ausschnitt 27,2 ±0,1 x 12,2 +0,2 hochkant")
    # keine On/Off-Beschriftung: der beleuchtete Wippschalter zeigt die Stellung selbst an
    rocker_preview(x_pwr, y_pwr)


# ================================================================ SVG
def svg_arc_path(cx, cy, r, a0, a1):
    x0, y0 = pol(cx, cy, r, a0)
    x1, y1 = pol(cx, cy, r, a1)
    large = 1 if (a1 - a0) > 180 else 0
    return f"M {f(x0)} {f(y0)} A {f(r)} {f(r)} 0 {large} 1 {f(x1)} {f(y1)}"


def write_svg(path, preview=True):
    def layer(idx, label, items, hidden=False):
        style = ' style="display:none"' if hidden else ""
        body = "\n".join("    " + i for i in items)
        return (f'  <g inkscape:groupmode="layer" inkscape:label="{idx} {esc(label)}" '
                f'id="layer{idx}"{style}>\n{body}\n  </g>')

    def text_svg(x, y, s, size, anchor, color=INK, extra=""):
        base = y + 0.5 * CAP * size
        return (f'<text x="{f(x)}" y="{f(base)}" font-family="{FONT}" font-size="{f(size)}" '
                f'text-anchor="{anchor}" fill="{color}"{extra}>{esc(s)}</text>')

    bg = [f'<rect x="0" y="0" width="{W}" height="{H}" rx="{R_CORNER}" fill="{CREAM}"/>']
    outline = [f'<rect x="0" y="0" width="{W}" height="{H}" rx="{R_CORNER}" fill="none" '
               f'stroke="{INK}" stroke-width="0.2"/>']
    cuts, dims = [], []
    for c in CUTS:
        if c[0] == "circle":
            _, kind, x, y, d, note = c
            cuts.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(d / 2)}" fill="#FFFFFF" '
                        f'stroke="{INK}" stroke-width="0.15"/>')
            dims.append(text_svg(x + d / 2 + 0.8, y, f"Ø{f(d)}", 1.8, "start", "#C0392B"))
        elif c[0] == "slot":
            _, x, y, w, h = c
            cuts.append(f'<rect x="{f(x - w / 2)}" y="{f(y - h / 2)}" width="{f(w)}" height="{f(h)}" '
                        f'rx="{f(h / 2)}" fill="#FFFFFF" stroke="{INK}" stroke-width="0.15"/>')
            dims.append(text_svg(x + w / 2 + 0.8, y, f"{f(w)}x{f(h)}", 1.8, "start", "#C0392B"))
        else:
            _, kind, x, y, w, h, r, note = c
            cuts.append(f'<rect x="{f(x - w / 2)}" y="{f(y - h / 2)}" width="{f(w)}" height="{f(h)}" '
                        f'rx="{f(r)}" fill="#FFFFFF" stroke="{INK}" stroke-width="0.15"/>')
            dims.append(text_svg(x + w / 2 + 0.8, y, f"{f(w)}x{f(h)}", 1.8, "start", "#C0392B"))
    prt = []
    for e in PRINT:
        if e[0] == "line":
            _, x1, y1, x2, y2, w = e
            prt.append(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{INK}" '
                       f'stroke-width="{f(w)}" stroke-linecap="round"/>')
        elif e[0] == "arc":
            _, cx, cy, r, a0, a1, w = e
            prt.append(f'<path d="{svg_arc_path(cx, cy, r, a0, a1)}" fill="none" stroke="{INK}" '
                       f'stroke-width="{f(w)}" stroke-linecap="round"/>')
        elif e[0] == "poly":
            _, pts, w = e
            prt.append('<polyline points="' + " ".join(f"{f(x)},{f(y)}" for x, y in pts) +
                       f'" fill="none" stroke="{INK}" stroke-width="{f(w)}" stroke-linejoin="round"/>')
        else:
            _, x, y, s, size, anchor, style = e
            if style == "title":
                prt.append(text_svg(x, y, s, size, anchor, "none",
                                    f' font-weight="600" stroke="{INK}" stroke-width="0.28" '
                                    f'stroke-linejoin="round" textLength="{f(X1 - X_LFO - 6)}" '
                                    f'lengthAdjust="spacingAndGlyphs"'))
            else:
                prt.append(text_svg(x, y, s, size, anchor))
    layers = [layer(0, "Hintergrund (Vorschau)", bg, not preview), layer(1, "Kontur", outline),
              layer(2, "Ausschnitte", cuts), layer(3, "Druck", prt),
              layer(4, "Bauteile (Vorschau)", PREV, not preview), layer(5, "Bohrmaße", dims, True)]
    Path(path).write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
        f'width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">\n'
        f'  <title>{esc(TITLE)} – Frontpanel 19" 2HE</title>\n' + "\n".join(layers) + "\n</svg>\n",
        encoding="utf-8")


def write_print_svg(path):
    """Druckgrafik für den UV-Digitaldruck: Panelfarbe vollflächig + Druckelemente, sonst nichts."""
    items = []
    for e in PRINT:
        if e[0] == "line":
            _, x1, y1, x2, y2, w = e
            items.append(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{INK}" '
                         f'stroke-width="{f(w)}" stroke-linecap="round"/>')
        elif e[0] == "arc":
            _, cx, cy, r, a0, a1, w = e
            items.append(f'<path d="{svg_arc_path(cx, cy, r, a0, a1)}" fill="none" stroke="{INK}" '
                         f'stroke-width="{f(w)}" stroke-linecap="round"/>')
        elif e[0] == "poly":
            _, pts, w = e
            items.append('<polyline points="' + " ".join(f"{f(x)},{f(y)}" for x, y in pts) +
                         f'" fill="none" stroke="{INK}" stroke-width="{f(w)}" stroke-linejoin="round"/>')
        else:
            _, x, y, t, size, anchor, style = e
            base = y + 0.5 * CAP * size
            extra = ""
            fill = INK
            if style == "title":
                fill = "none"
                extra = (f' font-weight="600" stroke="{INK}" stroke-width="0.28" stroke-linejoin="round" '
                         f'textLength="{f(X1 - X_LFO - 6)}" lengthAdjust="spacingAndGlyphs"')
            items.append(f'<text x="{f(x)}" y="{f(base)}" font-family="{FONT}" font-size="{f(size)}" '
                         f'text-anchor="{anchor}" fill="{fill}"{extra}>{esc(t)}</text>')
    Path(path).write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW:.4f}mm" height="{PH:.4f}mm" '
        f'viewBox="{-BX:.4f} {-BY:.4f} {PW:.4f} {PH:.4f}">\n'
        f'  <rect x="{-BX:.4f}" y="{-BY:.4f}" width="{PW:.4f}" height="{PH:.4f}" '
        f'fill="{CREAM}"/>\n  ' + "\n  ".join(items) + "\n</svg>\n",
        encoding="utf-8")


CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def write_print_pdf(svg_path, pdf_path):
    """Vektor-PDF 1:1 (482,6 x 88,1 mm) über Chrome headless; Rückgabe: True bei Erfolg."""
    import subprocess
    if not Path(CHROME).exists():
        return False
    html = Path(str(svg_path) + ".html")
    svg = Path(svg_path).read_text(encoding="utf-8").split("?>", 1)[1]
    html.write_text('<!doctype html><meta charset="utf-8"><style>@page{size:' + f"{PW:.4f}mm {PH:.4f}mm" +
                    ';margin:0}html,body{margin:0;padding:0}svg{display:block}</style>' + svg,
                    encoding="utf-8")
    r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf_path}", f"file://{html.resolve()}"],
                       capture_output=True, timeout=120)
    html.unlink(missing_ok=True)
    if not (Path(pdf_path).exists() and r.returncode == 0):
        return None
    import re
    m = re.search(rb'/MediaBox\s*\[([^\]]+)\]', Path(pdf_path).read_bytes())
    x0, y0, x1, y1 = (float(v) for v in m.group(1).split())
    return ((x1 - x0) * 25.4 / 72, (y1 - y0) * 25.4 / 72)     # Seitengröße in mm


# ================================================================ Hershey-Strichschrift (DXF)
_HERSHEY = {}


def hershey_font():
    """Hershey 'Roman Simplex' (rowmans.jhf): Versalien von y=-12 bis Grundlinie y=+9."""
    if _HERSHEY:
        return _HERSHEY
    src = Path(__file__).parent / "rowmans.jhf"
    for i, line in enumerate(src.read_text(encoding="latin-1").splitlines()):
        if len(line) < 10:
            continue
        left, right = ord(line[8]) - 82, ord(line[9]) - 82
        strokes, cur = [], []
        coords = line[10:]
        for k in range(0, len(coords) - 1, 2):
            pair = coords[k:k + 2]
            if pair == " R":
                strokes.append(cur)
                cur = []
            else:
                cur.append((ord(pair[0]) - 82, ord(pair[1]) - 82))
        strokes.append(cur)
        _HERSHEY[chr(32 + i)] = (left, right, [s for s in strokes if len(s) > 1])
    return _HERSHEY


def hershey_paths(x, y, s, size, anchor):
    """Textzeile als Polylinien (SVG-Koordinaten); size = SVG-font-size."""
    font = hershey_font()
    sc = CAP * size / 21.0
    glyphs = [font.get(ch, font["?"]) for ch in s]
    width = sum((r - l) for l, r, _ in glyphs) * sc
    x0 = {"middle": x - width / 2, "start": x, "end": x - width}[anchor]
    base = y + 0.5 * CAP * size
    paths, cursor = [], x0
    for l, r, strokes in glyphs:
        for st in strokes:
            paths.append([(cursor + (px - l) * sc, base + (py - 9) * sc) for px, py in st])
        cursor += (r - l) * sc
    return paths


# ================================================================ DXF (R12)
def write_dxf(path):
    out = []

    def add(*pairs):
        for code, val in pairs:
            out.append(str(code))
            out.append(f(val) if isinstance(val, float) else str(val))

    def Y(y):
        return H - y

    def line(layer, x1, y1, x2, y2):
        add((0, "LINE"), (8, layer), (10, x1), (20, Y(y1)), (30, 0.0), (11, x2), (21, Y(y2)), (31, 0.0))

    def circle(layer, cx, cy, r):
        add((0, "CIRCLE"), (8, layer), (10, cx), (20, Y(cy)), (30, 0.0), (40, r))

    def arc(layer, cx, cy, r, a0, a1):
        add((0, "ARC"), (8, layer), (10, cx), (20, Y(cy)), (30, 0.0), (40, r),
            (50, 90.0 - a1), (51, 90.0 - a0))

    def poly(layer, verts, closed):
        add((0, "POLYLINE"), (8, layer), (66, 1), (70, 1 if closed else 0))
        for v in verts:
            add((0, "VERTEX"), (8, layer), (10, v[0]), (20, Y(v[1])), (30, 0.0))
            if len(v) > 2 and v[2]:
                add((42, v[2]))
        add((0, "SEQEND"), (8, layer))

    add((0, "SECTION"), (2, "HEADER"), (9, "$ACADVER"), (1, "AC1009"),
        (9, "$EXTMIN"), (10, 0.0), (20, 0.0), (30, 0.0),
        (9, "$EXTMAX"), (10, W), (20, H), (30, 0.0), (0, "ENDSEC"))
    add((0, "SECTION"), (2, "TABLES"),
        (0, "TABLE"), (2, "LTYPE"), (70, 1),
        (0, "LTYPE"), (2, "CONTINUOUS"), (70, 64), (3, "Solid line"), (72, 65), (73, 0), (40, 0.0),
        (0, "ENDTAB"),
        (0, "TABLE"), (2, "LAYER"), (70, 3))
    for name, color in (("KONTUR", 7), ("AUSSCHNITTE", 1), ("DRUCK", 5)):
        add((0, "LAYER"), (2, name), (70, 0), (62, color), (6, "CONTINUOUS"))
    add((0, "ENDTAB"), (0, "ENDSEC"), (0, "SECTION"), (2, "ENTITIES"))

    # Kontur: geschlossene Polylinie, Ecken R 2 als Bulge, gegen den Uhrzeigersinn (y nach oben).
    # Punkte in SVG-Koordinaten (y nach unten), Y() spiegelt.
    b = math.tan(math.radians(22.5))
    R = R_CORNER
    poly("KONTUR", [(R, H, 0), (W - R, H, b), (W, H - R, 0), (W, R, b),
                    (W - R, 0, 0), (R, 0, b), (0, R, 0), (0, H - R, b)], True)

    for c in CUTS:
        if c[0] == "circle":
            circle("AUSSCHNITTE", c[2], c[3], c[4] / 2)
        elif c[0] == "slot":
            _, x, y, w, h = c
            L, r = (w - h) / 2, h / 2
            poly("AUSSCHNITTE", [(x - L, y + r, 0), (x + L, y + r, 1.0),
                                 (x + L, y - r, 0), (x - L, y - r, 1.0)], True)
        else:
            _, kind, x, y, w, h, r, note = c
            bq = math.tan(math.radians(22.5))
            x0, x1, y0, y1 = x - w / 2, x + w / 2, y - h / 2, y + h / 2
            # gegen den Uhrzeigersinn (y nach oben), Ecken als Bulge
            poly("AUSSCHNITTE", [(x0 + r, y1, 0), (x1 - r, y1, bq), (x1, y1 - r, 0), (x1, y0 + r, bq),
                                 (x1 - r, y0, 0), (x0 + r, y0, bq), (x0, y0 + r, 0), (x0, y1 - r, bq)], True)

    for e in PRINT:
        if e[0] == "line":
            line("DRUCK", *e[1:5])
        elif e[0] == "arc":
            arc("DRUCK", *e[1:6])
        elif e[0] == "poly":
            poly("DRUCK", [(x, y, 0) for x, y in e[1]], False)
        else:
            _, x, y, s, size, anchor, style = e
            for p in hershey_paths(x, y, s, size, anchor):
                poly("DRUCK", [(px, py, 0) for px, py in p], False)

    add((0, "ENDSEC"), (0, "EOF"))
    Path(path).write_text("\n".join(out) + "\n", encoding="ascii")


# ================================================================ FrontDesign-Skript (.fpjs)
def write_fpjs(path, mode="engrave", pdf_path=None, pdf_size=None, save_as=None):
    """mode="engrave": Text/Linien als FrontDesign-Elemente (gravieren oder drucken).
    mode="print":   nur Bohrungen + eine Druckgrafik (PDF) über die ganze Platte, UV-Farbdruck."""
    js = []
    n = [0]
    save_as = save_as or FPD["save_as"]
    printing = (mode == "print")
    pw, ph = pdf_size or (PW, PH)
    if abs(pw - PW) > 0.05 or abs(ph - PH) > 0.05:
        print(f"Warnung: PDF-Seite {pw:.2f} x {ph:.2f} mm statt {PW:.2f} x {PH:.2f} mm")
    material = "alu_elox" if printing else FPD["material"]          # Druck nur auf eloxiertem Alu
    matcolor = FPD["elox_color"] if printing else FPD["matcolor"]

    def nm(prefix):
        n[0] += 1
        return f"{prefix}{n[0]:03d}"

    def Y(y):
        return H - y

    def q(s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

    js.append(f"""// FS-1A Frontpanel – erzeugt von fs1a_panel.py
// Ausführen in Schaeffer FrontDesign: Bearbeiten → Skripte → Hinzufügen (diese Datei) → Start
// oder Inhalt in das PastePad kopieren und Start drücken.
// Koordinaten in mm, Ursprung unten links (FrontDesign-Konvention).

var SAVE_AS  = {q(save_as)};   // "" = nicht speichern, nur anzeigen
var PRINTED  = {"true" if (FPD["printed"] and not printing) else "false"};   // true: Elemente drucken statt gravieren
var INK      = {FPD["ink"]};
var FONT     = {q(FPD["font"])};
var FONT_TTL = {q(FPD["font_title"])};

var fp = new Frontpanel({q(FPD["name"] + (" Druck" if printing else ""))}, {FPD["thickness"]}, {f(W)}, {f(H)}, {material}, {matcolor});
fp.SetCornerRadii({f(R_CORNER)}, {f(R_CORNER)}, {f(R_CORNER)}, {f(R_CORNER)});
fp.SetRemark({q(FPD.get("remark", "Jürgen Haible Frequency Shifter FS-1A, 19 Zoll 2 HE. Bohrungen vor Fertigung mit Bauteilen abgleichen."))});

function text(name, s, x, y, size, align, font) {{
    var t = new TextEngraving(name, s);
    try {{ t.SetFont(font + ":" + size + "mm"); }} catch (e) {{}}
    try {{ t.SetTextSize(size); }} catch (e) {{}}
    t.SetAlignment(align);
    try {{ t.SetVAlignment(valign_center); }} catch (e) {{}}
    t.SetColor(INK);
    fp.AddElement(t, x, y);
    return t;
}}
""")
    for c in CUTS:
        if c[0] == "circle":
            _, kind, x, y, d, note = c
            name = nm("B") + " " + (note or kind)
            sink = SINK.get((round(x, 3), round(y, 3)))
            if sink:
                v = f"b{n[0]}"
                call = (f"SetCountersinkWithParameters({sink[7:]})" if sink.startswith("custom:")
                        else f"SetCountersink({sink})")
                js.append(f'var {v} = new DrillHole({q(name)}, {f(d)}); '
                          f'{v}.{call}; fp.AddElement({v}, {f(x)}, {f(Y(y))});')
            else:
                js.append(f'fp.AddElement(new DrillHole({q(name)}, {f(d)}), {f(x)}, {f(Y(y))});')
        elif c[0] == "slot":
            _, x, y, w, h = c
            js.append(f'fp.AddElement(new RectHole({q(nm("L") + " Rack")}, {f(w)}, {f(h)}, {f(h / 2)}), '
                      f'{f(x)}, {f(Y(y))});')
        else:
            _, kind, x, y, w, h, r, note = c
            js.append(f'fp.AddElement(new RectHole({q(nm("R") + " " + kind)}, {f(w)}, {f(h)}, {f(r)}), '
                      f'{f(x)}, {f(Y(y))});')

    has_geo = any(e[0] in ("line", "arc", "poly") for e in PRINT)
    if printing:
        js.append(f"""
// Druckgrafik (UV-Farbdruck) über die ganze Platte: Bezugspunkt unten links = Plattenursprung
// Parameter 4/5 sind Skalierung X/Y in Prozent – das PDF ist bereits 1:1 in mm ({f(pw)} x {f(ph)} mm)
var pg = new PrintGraphic("Druckgrafik", {q(str(pdf_path))}, refpoint_leftbottom, 100, 100);
fp.AddElement(pg, {f(round(-BX, 3))}, {f(round(-BY, 3))});
""")
    elif has_geo:
        js.append(f"""
var g = new HpglEngraving("Druck Linien", "", refpoint_file, 100, 0, 0);
var penLine = g.DefinePen(INK, {FPD["tool"]});
var penFine = g.DefinePen(INK, {FPD["tool_fine"]});
g.ChangePen(penLine);""")
    for e in ([] if (printing or not has_geo) else PRINT):
        if e[0] == "line":
            _, x1, y1, x2, y2, w = e
            js.append(f'g.ChangePen({"penFine" if w < 0.3 else "penLine"}); '
                      f'g.Start({f(x1)}, {f(Y(y1))}); g.LineTo({f(x2)}, {f(Y(y2))}); g.Finish();')
        elif e[0] == "arc":
            _, cx, cy, r, a0, a1, w = e
            x0, y0 = pol(cx, cy, r, a0)
            x1, y1 = pol(cx, cy, r, a1)
            js.append(f'g.ChangePen(penLine); g.Start({f(x0)}, {f(Y(y0))}); '
                      f'g.ArcToMP({f(x1)}, {f(Y(y1))}, {f(cx)}, {f(Y(cy))}, 0); g.Finish();')
        elif e[0] == "poly":
            _, pts, w = e
            seg = "; ".join(f"g.LineTo({f(x)}, {f(Y(y))})" for x, y in pts[1:])
            js.append(f'g.ChangePen(penLine); g.Start({f(pts[0][0])}, {f(Y(pts[0][1]))}); {seg}; g.Finish();')
    if not printing and has_geo:
        js.append("fp.AddElement(g, 0, 0);\n")

    for e in ([] if printing else PRINT):
        if e[0] != "text":
            continue
        _, x, y, s, size, anchor, style = e
        align = {"middle": "align_center", "start": "align_left", "end": "align_right"}[anchor]
        font = "FONT_TTL" if style == "title" else "FONT"
        js.append(f'text({q(nm("T") + " " + s)}, {q(s)}, {f(x)}, {f(Y(y))}, '
                  f'{f(round(FPD_TEXT * size, 2))}, {align}, {font});')

    for bx, by, typ, lng, note in BOLTS:
        js.append(f'fp.AddElement(new Bolt({q(nm("S") + " " + note)}, {q(typ)}, {lng}), '
                  f'{f(bx)}, {f(Y(by))});   // sitzt auf der Rueckseite')

    js.append("""
if (PRINTED) { try { fp.SetPrinted(); } catch (e) { Print("SetPrinted nicht verfügbar\\n"); } }
AddFrontpanel(fp);
if (SAVE_AS != "") {
    try { SaveFrontpanel(fp, SAVE_AS, true); Print("Gespeichert: " + SAVE_AS + "\\n"); }
    catch (e) { Print("Speichern fehlgeschlagen: " + e + "\\n"); }
}
Print("FS-1A Frontpanel: " + fp.Count() + " Elemente\\n");
""")
    Path(path).write_text("\n".join(js), encoding="utf-8")


# ================================================================ CSV
def write_holes(path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["Nr", "Bauteil", "x_mm_von_links", "y_mm_von_oben", "Durchmesser_mm", "Bemerkung"])
        for i, c in enumerate(CUTS, 1):
            if c[0] == "circle":
                _, kind, x, y, d, note = c
                sink = SINK.get((round(x, 3), round(y, 3)))
                if sink:
                    note = (f"{note} – Senkung Kegel {CSK_CONE} / {CSK_ANGLE} Grad, "
                            f"{CSK_DEPTH:.2f} mm tief (Senkkopf DIN 965 M5)")
                w.writerow([i, kind, f(round(x, 3)), f(round(y, 3)), f(d), note])
            elif c[0] == "slot":
                _, x, y, sw, sh = c
                w.writerow([i, "Rack-Langloch", f(round(x, 3)), f(round(y, 3)), "", f"{sw} x {sh} mm"])
            else:
                _, kind, x, y, cw, ch, r, note = c
                w.writerow([i, kind, f(round(x, 3)), f(round(y, 3)), "", f"{cw} x {ch} mm, R {r} – {note}"])
        for j, (x, y, typ, lng, note) in enumerate(BOLTS, len(CUTS) + 1):
            w.writerow([j, "Gewindebolzen M3", f(round(x, 3)), f(round(y, 3)), "",
                        f"kein Loch – Einklebebolzen {typ} {lng} mm auf der Rueckseite, {note}"])


if __name__ == "__main__":
    args = sys.argv[1:]
    preview = "--no-preview" not in args
    name = args[args.index("--out") + 1] if "--out" in args else "fs1a_frontpanel"
    out = Path(__file__).parent
    build()
    write_svg(out / f"{name}.svg", preview)
    write_dxf(out / f"{name}.dxf")
    write_fpjs(out / f"{name}.fpjs")
    write_holes(out / f"{name}_bohrungen.csv")
    write_print_svg(out / f"{name}_druck.svg")
    pdf = out / f"{name}_druck.pdf"
    pdf_size = write_print_pdf(out / f"{name}_druck.svg", pdf)
    write_fpjs(out / f"{name}_druck.fpjs", mode="print", pdf_path=pdf.resolve(), pdf_size=pdf_size,
               save_as=str(Path(FPD["save_as"]).with_name(f"{name}_druck.fpd")))
    print(f"{name}.svg / .dxf / .fpjs / _bohrungen.csv  ({len(CUTS)} Ausschnitte, "
          f"{sum(1 for e in PRINT if e[0] == 'text')} Texte, {len(PRINT)} Druckelemente)")
    print(f"{name}_druck.svg / _druck.pdf ({'%.2f x %.2f mm' % pdf_size if pdf_size else 'kein Chrome – PDF fehlt'}) / _druck.fpjs")
