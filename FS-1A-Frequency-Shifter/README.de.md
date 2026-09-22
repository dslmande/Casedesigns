# Frontpanel – Jürgen Haible Frequency Shifter FS-1A (19", 2 HE)

Gestaltung nach dem Vorbild des Van-Daal-Aufbaus (cremefarbene Blende,
dunkelblauer Druck, Funktionsblöcke mit Rahmenlinien, große RANGE/MANUAL-Knöpfe).

## Dateien

| Datei | Inhalt |
|---|---|
| `fs1a_panel.py` | Generator (nur Python-Standardbibliothek): `/usr/bin/python3 fs1a_panel.py` schreibt alle Ausgabedateien neu |
| `fs1a_frontpanel_druck.fpd` | **FrontDesign, Farbdruck-Variante:** eloxiert natur + vollflächige Druckgrafik (Creme + Blau), Bohrungen als Bohrelemente |
| `fs1a_frontpanel_druck.pdf` | Die Druckgrafik: Vektor-PDF 1:1, 484,7 × 90,3 mm (1 mm Beschnitt rundum), ohne Bohrungen/Kontur |
| `fs1a_frontpanel_druck.fpjs` | FrontDesign-Skript, das die Druck-Variante erzeugt |
| `fs1a_frontpanel.fpd` | FrontDesign, Gravur-Variante: Text/Linien als native Elemente (gravieren oder „Gravuren drucken“) |
| `fs1a_frontpanel.fpjs` | FrontDesign-Skript für die Gravur-Variante |
| `fs1a_frontpanel.dxf` | DXF R12, Ebenen `KONTUR` / `AUSSCHNITTE` / `DRUCK`, Text als Pfade |
| `fs1a_frontpanel.svg` | 1:1 in mm mit Inkscape-Ebenen und Bauteil-Vorschau |
| `fs1a_frontpanel_druck.svg` | Quelle der Druckgrafik (nur Panelfarbe + Druck) |
| `fs1a_frontpanel_bohrungen.csv` | Bohrtabelle: Nr, Bauteil, x (von links), y (von oben), Ø, Bemerkung |
| `fs1a_frontpanel_vorschau.png` | Render mit Knöpfen, Buchsen, Schaltern |
| `fs1a_rueckwand.py` | Generator der Rückwand (nutzt `fs1a_panel.py` als Bibliothek) |
| `fs1a_rueckwand.fpd` | FrontDesign, Rückwand 437 × 88,1 × 2 mm, Alu eloxiert natur |
| `fs1a_rueckwand.svg` / `.dxf` / `.fpjs` / `_bohrungen.csv` / `_vorschau.png` | Rückwand in denselben Formaten |
| `rowmans.jhf` | Hershey-Strichschrift „Roman Simplex“ für den DXF-Text (gemeinfrei) |

Alle Maße und Positionen stehen als Konstanten am Anfang von `fs1a_panel.py`
(Blockgrenzen `X_*`, Reihenhöhen `Y_TOP/Y_BOT`, Bohrdurchmesser `DRILL`, Farben,
Schriftgrößen, `TITLE`, `BRAND`, FrontDesign-Einstellungen `FPD`, Beschnitt `BLEED`).
Die PDF-Erzeugung nutzt Google Chrome headless (`CHROME`-Pfad im Script).

## Farbdruck (UV-Digitaldruck) – `fs1a_frontpanel_druck.fpd`

So sieht die Platte aus wie das Vorbild. Regeln aus Schaeffers „Hinweise zur Erstellung
Ihrer Druckdaten“ (Druckdateien.pdf), die der Generator einhält:

- Vektor-PDF, Farben in sRGB (Creme `#F2E7C6`, Blau `#22307C`) – RAL wird nur angenähert.
- Die Druckgrafik läuft rundum ≥ 1 mm über die Plattenkante hinaus (sonst kann unbedruckter Rand sichtbar werden).
- Keine Bohrungen und keine Plattenkontur in der Druckdatei (würden mitgedruckt).
- Bedruckt wird nur Schaeffers eloxiertes Aluminium – daher Material `alu_elox` / natur,
  pulverbeschichtete Platten sind nicht bedruckbar.
- Weiß: standardmäßig wird Weiß nicht gedruckt. Für die deckende Creme-Fläche in den
  Platteneigenschaften (Strg-F) **„Weiß fluten“** (weiße Grundierung der ganzen Platte) einschalten;
  ohne Weiß schimmert das Aluminium durch und die Creme wird grau.

Das Skript erzeugt Bohrungen + `PrintGraphic` (Bezugspunkt unten links bei (−1,06, −1,11) mm,
Skalierung 100 %). Neu erzeugen: Bearbeiten → Skripte → PastePad →
`EvalFile("/…/fs1a_frontpanel_druck.fpjs");` → Start.

## Gravur-Variante – `fs1a_frontpanel.fpd`

Platte 482,6 × 88,1 × 2 mm, Aluminium pulverbeschichtet Grauweiß RAL 9002 (Creme gibt es
nicht), Eckenradius 2 mm, 52 Bohrungen/Langlöcher, 125 Textgravuren (Helvetica Light
1-stroke, Titel Helvetica Medium outline), HPGL-Gravur mit Rahmen, Skalen und Bögen.
Gravurfarbe Nachtblau RAL 5022, Option „Gravuren drucken“ gesetzt. Für echte Gravur mit
Farbauslegung `FPD["printed"] = False` setzen.

## DXF (Alternative)

Datei → Importieren… → `fs1a_frontpanel.dxf`. Der Import-Assistent erkennt die größte
geschlossene Kontur als Plattenumriss, Kreise als Bohrungen und die Langlöcher als freie
Konturen. Ebene `DRUCK` enthält den Text als Pfade (Strichschrift). Auch für KiCad/Inkscape.

## Ebenen in der SVG (Inkscape-Ebenen)

| Ebene | Zweck |
|---|---|
| 0 Hintergrund | Panelfarbe – nur Vorschau |
| 1 Kontur | Außenkontur 482,6 × 88,1 mm, Ecken R 2 |
| 2 Ausschnitte | Bohrungen und Rack-Langlöcher mit Ist-Durchmesser |
| 3 Druck | Beschriftung, Rahmen, Skalen |
| 4 Bauteile | Knöpfe, Buchsen, Schalter, LEDs – nur Vorschau |
| 5 Bohrmaße | Durchmesser neben jeder Bohrung, standardmäßig aus |

`python3 fs1a_panel.py --no-preview` schreibt die SVG ohne Vorschau-Ebenen.

## Bohrungen (Standardwerte)

| Bauteil | Ø | Anmerkung |
|---|---|---|
| Potis (Alpha 16 mm) | 7,5 | Verdrehsicherung ggf. ergänzen |
| Klinke 6,35 mm | 9,5 | Neutrik NYS / Cliff |
| Neutrik Combo NCJ6FI-S (Lötversion) | 24,0 | + 2 × Ø 3,2 oben links / unten rechts, 20 × 23 mm versetzt (Neutrik-Zeichnung 3102ST1728). PCB-Version NCJ6FA-H bräuchte Ø 22 und 19,8 × 19,8 mm – Konstanten `COMBO_SCREW_DX/DY` |
| Mini-Kippschalter | 6,0 | M6-Gewindebuchse, 9 Stück |
| LED 3 mm | 3,2 | Freq/Dir ×4, LFO ×1 |
| Netzschalter | 12,3 × 27,2, R 1 | Marquardt 1555.3102 Wippschalter (Reichelt WIPPE 1555.3102), Snap-in, hochkant; Datenblatt 27,2 ±0,1 × 12,2 +0,2, Wandstärke 0,8–5 mm, Blende 30 × 15. Keine On/Off-Beschriftung |
| Schrauben M5 | 5,3 | 4 × Befestigung an den Seitenteilprofilen (x 27,8 / 454,8, y 4,9 / 83,2) |
| Rack-Langlöcher | 10 × 6,4 | Lochmitten 465,1 mm, ±38,1 mm von der Panelmitte |
| Gewindebolzen M3 | kein Loch | 2 × Einklebebolzen GU30, 6 mm, auf der **Rückseite** bei x 241,3 / y 8,35 und 79,75 |

Vor der Bestellung die Durchmesser mit den tatsächlich verwendeten Bauteilen abgleichen.

## Gehäuse

Blende wird an zwei **Gie-Tec Seitenteilprofilen 4** (Art. 122040) verschraubt – Seitenteil für
19-Zoll-Gehäuse 2 HE, 88,30 mm hoch, Anlagefläche 16 mm (hinten bis 20,5 mm), Schraubkanäle Ø 4,5
für M5, Kanalmitte je 5 mm von Ober-/Unterkante (Abstand **78,3 mm**) und 5 mm hinter der
Außenfläche.

Gehäuse-Außenbreite `BOX_WIDTH = 437` mm → Profile belegen hinter der Blende x 22,8–38,8 und
443,8–459,8. Kein Bauteilkörper darf dort hineinragen; im Generator stehen die Grenzen als
`X_PROFILE_IN_L` / `X_PROFILE_IN_R`. Deshalb:

- Preamp-Combo bei x 52 (Gehäuse Ø 23,4 → 1,5 mm Luft zum Profil)
- Ausgangsblock endet bei x 426, Wippschalter bei x 435 (Blende 427,5–442,5 → 1,3 mm Luft)
- keine Befestigungsschrauben in der Blendenmitte (dort gibt es keinen Gegenhalt)

`pruefung_gehaeusezonen.png` zeigt die Profilzonen rot über dem Layout.

## Versteifung: Winkel zwischen Blende und Blechen

Damit sich die Blende nicht gegen die Bleche verwindet, sitzt oben und unten mittig je ein
**Gewindebolzen M3** auf der Rückseite der Frontplatte (FrontDesign-Element `Bolt`,
Typ GU30 = Einklebebolzen mit 3-mm-Gewinde, 6 mm lang). Darauf kommt ein Winkel
**Keystone 633**, dessen zweiter Schenkel ans Deckel- bzw. Bodenblech geschraubt wird.

Maße des Winkels (Messing vernickelt): Schenkel 9,5 × 9,5 mm, Breite 7,1 mm, Material
0,81 mm, beide Löcher Ø 3,7 mm, **Lochmitte je 5,5 mm von der Außenfläche des anderen
Schenkels**. Daraus folgt alles Weitere:

Hinten dasselbe, nur mit Schraube statt Bolzen: die Rückwand bekommt an der gleichen
Stelle zwei Durchgangslöcher, der Winkel wird von außen angeschraubt.

| Merkmal | Wert |
|---|---|
| Bolzen Frontplatte | x 241,3 (Mitte), y **8,35** und **79,75** von der Oberkante |
| Löcher Rückwand | Ø **3,2**, x 218,5 (Mitte), y **8,35** und **79,75** von der Oberkante |
| Löcher in Deckel und Boden | Ø **3,2**, mittig (208 mm von links), **5,5 mm von der Vorderkante** und **5,0 mm von der Hinterkante** |
| Abstand Bolzen-/Schraubenachse ↔ Blechfläche | 5,5 mm (= Maß D des Winkels) |
| Nächstes Bauteil | Fine-Tune-Poti, 14,4 mm entfernt – frei |

Warum hinten 5,0 statt 5,5 mm: Das Blech endet 0,5 mm vor der Profilstirnfläche, an der die
Rückwand anliegt.

Zusätzlich nötig: 2 × Mutter M3 (auf die Bolzen der Blende), 6 × Schraube M3 + Mutter
(2 × Winkel an die Rückwand, 4 × Winkel an Deckel und Boden).

## Rückwand – `fs1a_rueckwand.fpd`

437 × 88,1 × 2 mm (Gehäuse-Außenbreite, deckt die Stirnflächen der Seitenteilprofile ab),
Alu eloxiert natur, Eckenradius 2 mm, unbedruckt.

| Bohrung | Position | Ø |
|---|---|---|
| 4 × M5 in die Schraubkanäle | x 5 / 432, y 4,9 / 83,2 | 5,3 |
| Kabeldurchführung | x 40 (von links), y 58,1 (= 30 mm von unten) | 12,0 |
| 2 × Winkelschraube M3 | x 218,5 (Mitte), y 8,35 / 79,75 | 3,2 |

Erzeugen: `python3 fs1a_rueckwand.py`, dann in FrontDesign
`EvalFile("/…/fs1a_rueckwand.fpjs");`. Maße stehen oben in `fs1a_rueckwand.py`
(`HOLE_D`, `HOLE_X`, `HOLE_Y_FROM_BOTTOM`).

## Gehäuse – Seitenteile, Deckel, Boden

`python3 fs1a_gehaeuse.py` erzeugt die Gehäuseteile und gibt die Stückliste aus.
Gehäusetiefe `BOX_DEPTH = 250` mm (Profillänge), Außentiefe 254 mm mit Front und Rückwand.

| Anz. | Teil | Maß / Datei |
|---|---|---|
| 2 | Seitenteilprofil | Gie-Tec 122040, Zuschnitt **250 mm** (Sonderlänge bestellbar) |
| 1 | Frontplatte | 482,6 × 88,1 × 2 – `fs1a_frontpanel.fpd` bzw. `_druck.fpd` |
| 1 | Rückwand | 437 × 88,1 × 2 – `fs1a_rueckwand.fpd` |
| 2 | Deckel / Boden | **416 × 249,5 × 1,5 mm Alu-Blech**, 2 Löcher Ø 3,2 – `fs1a_deckel_boden.dxf` |
| 8 | Schraube M5 | gewindeformend in die Profilkanäle, 4 vorn + 4 hinten |
| 4 | Winkel Keystone 633 | oben/unten mittig, vorn an der Blende und hinten an der Rückwand |
| 2 | Mutter M3 | auf die Gewindebolzen der Blende |
| 6 | Schraube M3 + Mutter | 2 × Winkel an die Rückwand, 4 × Winkel an Deckel/Boden |

Blechmaße aus der Profilkontur (`gietec_122040_profil.dat`, aus Gie-Tecs `cad_122040.dxf`):
Blechnut 1,6 mm breit auf Höhe 1,4–3,0 bzw. 85,3–86,9 mm, Nutgrund 10 mm hinter der
Außenfläche → freie Weite zwischen den Nutgründen 417 mm, Blech 416 mm (je 2,5 mm Eingriff,
0,5 mm Spiel). Länge 249,5 mm = Profillänge − 0,5 mm.

**Deckel/Boden nicht bei Schaeffer:** 416 × 249,5 mm gibt es dort nicht in 1,5 mm
(im Frontplatten Designer geprüft: „Das größere Maß der Frontplatte ist zu groß oder die
Frontplatte ist zu dünn"). 2 mm wäre lieferbar, passt aber nicht in die 1,6-mm-Nut.
Also Blechzuschnitt (DXF) beim Blechner bestellen.

`fs1a_gehaeuse_schnitt.svg/.png` zeigt den Querschnitt mit beiden Profilen, Blechen,
Schraubkanälen und Frontplatte; `fs1a_deckel_boden_zeichnung.svg/.png` ist die bemaßte
Blechzeichnung.

## 3D-Baugruppe – `fs1a_gehaeuse.step`

`fs1a_step.py` baut alle sechs Teile in FreeCAD (headless) aus denselben Quellen wie die
Fertigungsdateien und schreibt eine STEP-Datei (AP214) mit benannten Produkten:

```bash
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd fs1a_step.py
```

| Teil | Maß (mm) | Volumen |
|---|---|---|
| Frontplatte | 482,6 × 2 × 88,1 | 79,98 cm³ |
| Rückwand | 437 × 2 × 88,1 | 76,59 cm³ |
| Seitenteil links / rechts | 20,5 × 250 × 88,3 | je 150,86 cm³ |
| Deckel / Boden | 416 × 249,5 × 1,5 | je 155,69 cm³ |

Baugruppe 482,6 × 254 × 88,3 mm, zusammen 769,7 cm³ Aluminium ≈ 2,1 kg.

Koordinaten: X = Breite (0 = linke Kante der Frontplatte), Y = Tiefe (0 = Rückseite der
Frontplatte, +Y nach hinten), Z = Höhe (0 = Unterkante der Frontplatte). Die Seitenteile
stehen 0,1 mm über und unter der Blende (Profil 88,3 vs. Blende 88,1).

Die Profilkontur wird entlang y = 0 geschlossen – die drei M3-Nuten an der vorderen
Anlagefläche fehlen deshalb im Modell; alles andere entspricht der Gie-Tec-Kontur.
`fs1a_gehaeuse_iso.png` und `fs1a_gehaeuse_vorderansicht.png` sind Kontrollansichten
der importierten STEP.

## Koordinaten

SVG, DXF-Rücklesung und CSV: x von links, y von oben. FrontDesign und DXF-Datei:
y von unten (Ursprung unten links) – der Generator rechnet um.

## Bedienelemente (von links nach rechts)

Preamp (Combo, GAIN, PAD, LEVEL) · AUX-Eingang mit LEVEL, FEEDBACK (Deep Phase/Norm, Up/Down) ·
Invert, EXP-Abschwächer · V/OCT, CV IN · RANGE, MANUAL, 2 × Fine Tune, Freq/Dir-LEDs ·
LIN-Abschwächer, CV IN · LFO (FREQ, AMPLITUDE, EXP/LIN, Dreieck/Rechteck) ·
Out A / Out B (Mix dry/wet, Vol, Up/Down, Bypass, OUT) · Netzschalter.
