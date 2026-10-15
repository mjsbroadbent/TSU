"""Draw the Talas State University seal as plain SVG paths (no fonts needed).

    python3 tools/make_seal.py

Writes assets/seal.svg (full colour), assets/seal-white.svg (one-colour white, for
dark backgrounds) and img/src/seal.png (for the banner compositor).

The seal: navy ring lettered TALAS MAMLEKETTIK UNIVERSITETI above and
TALAS STATE UNIVERSITY below, gold beaded border, and in the field a wreath of
wheat (the founding Faculty of Agriculture) and juniper (arsha), the three peaks of
the Talas Alatau under the eight-pointed star of Irad, an open book, and a ribbon
with the motto BILIM JARYK ("knowledge is light") over the founding year 1958.
Letters are outlined from TeX Gyre Termes Bold with fontTools.
"""
import math
import subprocess
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT = TTFont("/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyretermes-bold.otf")
GS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()
UPM = FONT["head"].unitsPerEm
C = 200.0
NAVY, GOLD, WHITE = "#1f4a86", "#c9a227", "#ffffff"


def glyph_path(ch, matrix):
    name = CMAP.get(ord(ch))
    if not name:
        return ""
    pen = SVGPathPen(GS)
    GS[name].draw(TransformPen(pen, matrix))
    return pen.getCommands()


def adv(ch, size, track):
    name = CMAP.get(ord(ch))
    return (GS[name].width if name else UPM * .25) * size / UPM + track


def arc_text(text, radius, size, center_deg, track=0.0, bottom=False, cx=None, cy=None):
    """Text along a circle. Top: baseline at `radius`, letters point outward, read clockwise.
    Bottom: baseline at `radius`, letters point inward (upright at the bottom), read left to right."""
    widths = [adv(ch, size, track) for ch in text]
    total = sum(widths) - track
    span = total / radius                      # radians
    out = []
    pos = -total / 2
    s = size / UPM
    ox = C if cx is None else cx
    oy = C if cy is None else cy
    for ch, w in zip(text, widths):
        mid = pos + (w - track) / 2            # centre of this glyph along the arc
        if not bottom:
            a = math.radians(center_deg) + mid / radius
            rot = a
            px, py = ox + radius * math.sin(a), oy - radius * math.cos(a)
        else:
            a = math.radians(center_deg) - mid / radius
            rot = a - math.pi
            px, py = ox + radius * math.sin(a), oy - radius * math.cos(a)
        cos, sin = math.cos(rot), math.sin(rot)
        gw = (w - track) / s                   # glyph advance in font units
        # font units -> local (x right, y up), centred on the advance, then rotate and move
        a_, b_ = s * cos, s * sin
        c_, d_ = s * sin, -s * cos
        e_ = px - (gw / 2) * s * cos
        f_ = py - (gw / 2) * s * sin
        out.append(glyph_path(ch, (a_, b_, c_, d_, e_, f_)))
        pos += w
    return "".join(out)


def line_text(text, cx, baseline, size, track=0.0):
    widths = [adv(ch, size, track) for ch in text]
    x = cx - (sum(widths) - track) / 2
    s = size / UPM
    out = []
    for ch, w in zip(text, widths):
        out.append(glyph_path(ch, (s, 0, 0, -s, x, baseline)))
        x += w
    return "".join(out)


def star(cx, cy, r_out, r_in, n=8, rot=0.0):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot) + math.pi * i / n
        pts.append(f"{cx + r * math.sin(a):.2f},{cy - r * math.cos(a):.2f}")
    return "M" + " L".join(pts) + "Z"


def beads(radius, n, r):
    return "".join(f'<circle cx="{C + radius * math.sin(2 * math.pi * i / n):.2f}" cy="{C - radius * math.cos(2 * math.pi * i / n):.2f}" r="{r}"/>' for i in range(n))


def wheat(side):
    """A curved stalk of wheat up one side of the field. side = -1 left, +1 right."""
    out = []
    R = 112
    angles = [216 + i * 7 for i in range(13)] if side < 0 else [144 - i * 7 for i in range(13)]
    # stem
    pts = [(C + R * math.sin(math.radians(a)), C - R * math.cos(math.radians(a))) for a in angles]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    out.append(f'<path d="{d}" fill="none" stroke="{GOLD}" stroke-width="2.2" stroke-linecap="round"/>')
    for k, a in enumerate(angles[1:], 1):
        ar = math.radians(a)
        x, y = C + R * math.sin(ar), C - R * math.cos(ar)
        tang = math.degrees(ar) + (90 if side < 0 else -90)   # direction of growth along the stem
        for off in (-1, 1):                                    # a grain each side of the stem
            ang = tang + off * 32
            gx = x + 6.5 * math.sin(math.radians(ang))
            gy = y - 6.5 * math.cos(math.radians(ang))
            out.append(f'<ellipse cx="{gx:.2f}" cy="{gy:.2f}" rx="2.9" ry="6.6" transform="rotate({ang:.1f} {gx:.2f} {gy:.2f})" fill="{GOLD}"/>')
    # awns at the top
    ax, ay = pts[-1]
    tang = angles[-1] + (90 if side < 0 else -90)
    for off in (-14, 0, 14):
        a2 = math.radians(tang + off)
        out.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{ax + 14 * math.sin(a2):.1f}" y2="{ay - 14 * math.cos(a2):.1f}" stroke="{GOLD}" stroke-width="1.2"/>')
    return "".join(out)


def seal(mono=None):
    navy = mono or NAVY
    gold = mono or GOLD
    field = "none" if mono else WHITE
    ink = mono or NAVY
    parts = []
    parts.append(f'<circle cx="200" cy="200" r="198" fill="{navy}"/>')
    parts.append(f'<circle cx="200" cy="200" r="191" fill="none" stroke="{gold}" stroke-width="2.4"/>')
    parts.append(f'<circle cx="200" cy="200" r="186" fill="none" stroke="{gold}" stroke-width=".9"/>')
    parts.append(f'<path d="{arc_text("TALAS MAMLEKETTIK UNIVERSITETI", 158, 21, 0, track=1.6)}" fill="{gold if not mono else mono}"/>')
    parts.append(f'<path d="{arc_text("TALAS STATE UNIVERSITY", 176, 22, 180, track=3.0, bottom=True)}" fill="{gold if not mono else mono}"/>')
    for a in (90, 270):  # stars between the two inscriptions
        x = C + 166 * math.sin(math.radians(a)); y = C - 166 * math.cos(math.radians(a))
        parts.append(f'<path d="{star(x, y, 9, 3.6, 5)}" fill="{gold}"/>')
    parts.append(f'<g fill="{gold}">{beads(143, 72, 2.1)}</g>')
    if not mono:
        parts.append(f'<circle cx="200" cy="200" r="137" fill="{field}"/>')
    parts.append(f'<circle cx="200" cy="200" r="137" fill="none" stroke="{gold}" stroke-width="1.6"/>')
    parts.append(f'<circle cx="200" cy="200" r="132" fill="none" stroke="{ink}" stroke-width=".8"/>')
    # wreath
    w = wheat(-1) + wheat(1)
    if mono:
        w = w.replace(GOLD, mono)
    parts.append(w)
    # sun rays + star of Irad
    rays = []
    for i in range(24):
        a = math.pi + i * (math.pi / 23)
        r1, r2 = 30, 46 if i % 2 == 0 else 39
        rays.append(f"M{C + r1 * math.cos(a):.1f},{118 + r1 * math.sin(a):.1f} L{C + r2 * math.cos(a):.1f},{118 + r2 * math.sin(a):.1f}")
    parts.append(f'<path d="{" ".join(rays)}" stroke="{gold}" stroke-width="1.6" stroke-linecap="round" clip-path="url(#upper)"/>')
    parts.append(f'<path d="{star(200, 104, 17, 7, 8, 22.5)}" fill="{gold}" stroke="{ink}" stroke-width=".8"/>')
    # three peaks of the Talas Alatau with snow caps
    peaks = "M118,196 L150,150 L163,166 L192,122 L222,160 L236,146 L282,196 Z"
    snow = "M150,150 L141,163 L150,160 L156,165 L160,162 Z M192,122 L180,140 L190,136 L197,143 L204,137 L210,143 Z M236,146 L229,155 L236,153 L241,156 Z"
    parts.append(f'<path d="{peaks}" fill="{ink}"/>')
    if not mono:
        parts.append(f'<path d="{snow}" fill="{WHITE}"/>')
        # engraved relief lines on the shadow side of each peak
        relief = ("M192,122 L198,150 L194,168 L201,190 M150,150 L154,172 L150,190 M236,146 L240,166 L246,190 "
                  "M205,140 L214,158 L211,176 L220,192 M163,166 L170,182 M222,160 L228,176 L232,192")
        parts.append(f'<path d="{relief}" fill="none" stroke="{WHITE}" stroke-width=".9" opacity=".55"/>')
    # ground line
    parts.append(f'<path d="M112,197 Q200,190 288,197" fill="none" stroke="{ink}" stroke-width="2"/>')
    # open book
    book = "M148,206 Q174,198 200,212 Q226,198 252,206 L252,246 Q226,238 200,252 Q174,238 148,246 Z"
    parts.append(f'<path d="{book}" fill="{field if not mono else "none"}" stroke="{ink}" stroke-width="2.6" stroke-linejoin="round"/>')
    parts.append(f'<path d="M200,212 L200,252" stroke="{ink}" stroke-width="2"/>')
    lines = []
    for k in range(4):
        y0 = 214 + k * 8
        lines.append(f"M156,{y0 - 1} Q176,{y0 - 6} 194,{y0 + 4}")
        lines.append(f"M206,{y0 + 4} Q224,{y0 - 6} 244,{y0 - 1}")
    parts.append(f'<path d="{" ".join(lines)}" fill="none" stroke="{ink}" stroke-width="1.2"/>')
    # ribbon with motto
    rib = "M104,262 Q200,282 296,262 L300,286 Q200,306 100,286 Z"
    tails = "M104,262 L84,268 L94,276 L86,288 L100,286 Z M296,262 L316,268 L306,276 L314,288 L300,286 Z"
    parts.append(f'<path d="{tails}" fill="{navy if not mono else "none"}" stroke="{gold}" stroke-width="1.2"/>')
    parts.append(f'<path d="{rib}" fill="{navy if not mono else "none"}" stroke="{gold}" stroke-width="1.4"/>')
    motto = arc_text("BILIM JARYK", 249, 15, 180, track=2.6, bottom=True, cx=200, cy=44)   # ribbon midline is an arc about (200, 44)
    parts.append(f'<path d="{motto}" fill="{gold if not mono else mono}"/>')
    parts.append(f'<path d="{line_text("1958", 200, 324, 20, track=3)}" fill="{ink}"/>')
    defs = '<defs><clipPath id="upper"><rect x="0" y="0" width="400" height="140"/></clipPath></defs>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" role="img" aria-label="Seal of Talas State University">'
            f'{defs}{"".join(parts)}</svg>\n')


def main():
    (ROOT / "assets" / "seal.svg").write_text(seal(), encoding="utf-8")
    (ROOT / "assets" / "seal-white.svg").write_text(seal(mono="#ffffff"), encoding="utf-8")
    print("assets/seal.svg, assets/seal-white.svg")


if __name__ == "__main__":
    main()
