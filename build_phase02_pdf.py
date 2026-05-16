#!/usr/bin/env python3
"""
Phase 02 — Police Station Spatial Intelligence
Editorial PDF generator · ReportLab
A4 Landscape · Black background · Helvetica typography

HOW TO RUN:
    1. Open a terminal in this folder
    2. Activate your environment:   .gmlenv\Scripts\activate
    3. Install reportlab if needed: pip install reportlab
    4. Run:                         python build_phase02_pdf.py
"""

try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    from reportlab.lib.utils import ImageReader
except ImportError:
    import subprocess, sys
    print("Installing reportlab...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    from reportlab.lib.utils import ImageReader

import os, math

# ── Project info — update STATION_NAME with the actual building name ──────────
STATION_NAME = "Police Station • Salt, Spain"          # ← replace with the actual name
AUTHOR_NAME  = "Emilie El Chidiac"

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE  = r"C:\Users\chidi\macad\module-03\aia-gml\phase-02-spatial-analysis"
PLOTS = os.path.join(BASE, "plots")
OUT   = os.path.join(BASE, "pdf", "ps-phase-02-presentation.pdf")
os.makedirs(os.path.join(BASE, "pdf"), exist_ok=True)

def plot(name):
    return os.path.join(PLOTS, name)

# ── Page geometry ─────────────────────────────────────────────────────────────
PW, PH = landscape(A4)      # 841.89 × 595.28 pts
MARGIN = 40
BOT_H  = 78                 # bottom strip height
TOP_M  = 22
PLOT_X = MARGIN
PLOT_Y = BOT_H + 6
PLOT_W = PW - 2 * MARGIN
PLOT_H = PH - BOT_H - TOP_M - 6

# ── Colour palette ────────────────────────────────────────────────────────────
BLACK      = HexColor('#000000')
WHITE      = HexColor('#FFFFFF')
GREY_DARK  = HexColor('#2C2C2C')
GREY_MID   = HexColor('#555555')
GREY_LIGHT = HexColor('#AAAAAA')
GREY_LABEL = HexColor('#777777')

F_BOLD = 'Helvetica-Bold'
F_REG  = 'Helvetica'

# ── Thermal colormap (topologicPy "thermal") ──────────────────────────────────
_THERMAL = [
    (0.00, '#03051a'), (0.13, '#0d1060'), (0.27, '#420f6a'),
    (0.40, '#88208a'), (0.53, '#c03a76'), (0.67, '#e96b4a'),
    (0.80, '#f9a833'), (0.93, '#fce480'), (1.00, '#fcffa4'),
]

def _lerp(h1, h2, t):
    def rgb(h): h = h.lstrip('#'); return [int(h[i:i+2], 16) for i in (0,2,4)]
    a, b = rgb(h1), rgb(h2)
    return '#{:02x}{:02x}{:02x}'.format(*[int(a[i]+(b[i]-a[i])*t) for i in range(3)])

def thermal(v):
    for i in range(len(_THERMAL)-1):
        t0,c0 = _THERMAL[i]; t1,c1 = _THERMAL[i+1]
        if v <= t1:
            return _lerp(c0, c1, (v-t0)/max(t1-t0, 1e-9))
    return _THERMAL[-1][1]

# ── Primitives ────────────────────────────────────────────────────────────────

def fill_bg(c):
    c.setFillColor(BLACK)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)

def draw_image_centered(c, path, x, y, max_w, max_h):
    img = ImageReader(path)
    iw, ih = img.getSize()
    scale = min(max_w/iw, max_h/ih)
    w, h  = iw*scale, ih*scale
    cx    = x + (max_w-w)/2
    cy    = y + (max_h-h)/2
    c.drawImage(path, cx, cy, width=w, height=h)

def divider_line(c):
    c.setStrokeColor(GREY_DARK)
    c.setLineWidth(0.4)
    c.line(MARGIN, BOT_H+1, PW-MARGIN, BOT_H+1)

def wrap_text(text, max_chars=62):
    words = text.split(); lines, cur = [], ''
    for w in words:
        trial = (cur+' '+w).strip()
        if len(trial) <= max_chars: cur = trial
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_bottom(c, num, name, finding, page_num, total=9, legend_fn=None):
    divider_line(c)

    # ── Left column: section number + name ───────────────────────────────────
    # Compound names (containing ·) split to two lines so they never overflow
    # into the centre column. Line 1 = main name (bold white), Line 2 = · subtitle (grey).
    c.setFillColor(GREY_MID); c.setFont(F_REG, 6.5)
    c.drawString(MARGIN, 63, num)

    if '·' in name:
        parts = [p.strip() for p in name.split('·', 1)]
        c.setFillColor(WHITE);             c.setFont(F_BOLD, 9)
        c.drawString(MARGIN, 51, parts[0])
        c.setFillColor(HexColor('#888888')); c.setFont(F_REG, 8)
        c.drawString(MARGIN, 38, '\xb7  ' + parts[1])   # · as latin-1 middot
    else:
        c.setFillColor(WHITE); c.setFont(F_BOLD, 9)
        c.drawString(MARGIN, 47, name)

    # ── Centre column: finding text (starts safely after left column) ─────────
    CX    = MARGIN + 215
    lines = wrap_text(finding, 57)
    c.setFillColor(GREY_LIGHT); c.setFont(F_REG, 7.5)
    LH    = 12
    sy    = 55 - ((min(len(lines), 3) - 1) * LH) / 2
    for i, line in enumerate(lines[:3]):
        c.drawString(CX, sy - i * LH, line)

    # ── Right column: legend ──────────────────────────────────────────────────
    if legend_fn:
        legend_fn(c)

    # ── Page counter ──────────────────────────────────────────────────────────
    c.setFillColor(GREY_MID); c.setFont(F_REG, 7)
    c.drawRightString(PW - MARGIN, 14, '{:02d}  /  {:02d}'.format(page_num, total))

# ── Legends ───────────────────────────────────────────────────────────────────

def legend_thermal(c, label, lo='LOW', hi='HIGH'):
    BW, BH, N = 130, 8, 80
    bx = PW-MARGIN-BW; by = 44
    for i in range(N):
        t = i/(N-1)
        c.setFillColor(HexColor(thermal(t)))
        c.rect(bx + i*BW/N, by, BW/N+0.6, BH, fill=1, stroke=0)
    c.setStrokeColor(GREY_DARK); c.setLineWidth(0.3)
    c.line(bx, by, bx, by-3); c.line(bx+BW, by, bx+BW, by-3)
    c.setFillColor(GREY_LABEL); c.setFont(F_REG, 6.5)
    c.drawString(bx, by-11, lo); c.drawRightString(bx+BW, by-11, hi)
    c.setFillColor(GREY_MID); c.setFont(F_REG, 6.5)
    c.drawString(bx, by+BH+5, label)

_COMMUNITIES = [
    ('#1b3068','Zone 1'), ('#6b2d9e','Zone 2'), ('#9e4878','Zone 3'),
    ('#c95648','Zone 4'), ('#e09530','Zone 5'), ('#e0d428','Zone 6'),
]

def legend_community(c):
    SQ   = 9     # swatch size (pt)
    LX   = PW - MARGIN - 188
    COL  = 3     # columns
    CW   = 63    # column width
    ROW_H = 18   # row height
    for i, (col, label) in enumerate(_COMMUNITIES):
        row = i // COL
        ci  = i % COL
        x   = LX + ci * CW
        # Baseline y for text in this row
        y   = 55 - row * ROW_H
        # Square vertically centred on text: square centre = y + ~2.5,
        # so bottom of square = y + 2.5 - SQ/2  = y - 2
        c.setFillColor(HexColor(col))
        c.rect(x, y - 2, SQ, SQ, fill=1, stroke=0)
        c.setFillColor(GREY_LIGHT); c.setFont(F_REG, 6.5)
        c.drawString(x + SQ + 5, y - 1, label)

def legend_path(c):
    LX, LW = PW-MARGIN-200, 22
    c.setStrokeColor(HexColor('#EE3333')); c.setLineWidth(2)
    c.line(LX, 57, LX+LW, 57)
    c.setFillColor(GREY_LIGHT); c.setFont(F_REG, 7)
    c.drawString(LX+LW+7, 53.5, 'Graph path — 90.65 units')
    c.setStrokeColor(HexColor('#3366EE')); c.setLineWidth(2)
    c.line(LX, 40, LX+LW, 40)
    c.setFillColor(GREY_LIGHT); c.setFont(F_REG, 7)
    c.drawString(LX+LW+7, 36.5, 'Straightened — 80.41 units  (-11.3%)')

def legend_isovist(c):
    LX = PW-MARGIN-190
    c.setFillColor(HexColor('#DD2222'))
    c.circle(LX+5, 56, 4.5, fill=1, stroke=0)
    c.setFillColor(GREY_LIGHT); c.setFont(F_REG, 7)
    c.drawString(LX+14, 52.5, 'Viewpoint (61 total)')
    # small polygon glyph
    pp = c.beginPath()
    pp.moveTo(LX, 36); pp.lineTo(LX+12, 44); pp.lineTo(LX+5, 44); pp.close()
    c.setFillColor(HexColor('#BBBBBB'))
    c.drawPath(pp, fill=1, stroke=0)
    c.setFillColor(GREY_LIGHT); c.setFont(F_REG, 7)
    c.drawString(LX+16, 36, 'Isovist (visibility polygon)')

# ── Police badge symbol ───────────────────────────────────────────────────────

def draw_police_badge(c, x, y, size=30):
    """Minimalist shield + 5-pointed star badge."""
    w = size
    h = size * 1.18
    cx = x + w / 2

    # Shield outline (pentagon: flat top, angled sides, pointed bottom)
    shield = c.beginPath()
    shield.moveTo(x,      y + h)           # top-left
    shield.lineTo(x + w,  y + h)           # top-right
    shield.lineTo(x + w,  y + h * 0.48)   # right shoulder
    shield.lineTo(cx,     y)               # bottom point
    shield.lineTo(x,      y + h * 0.48)   # left shoulder
    shield.close()
    c.setFillColor(HexColor('#161616'))
    c.setStrokeColor(HexColor('#505050'))
    c.setLineWidth(0.8)
    c.drawPath(shield, fill=1, stroke=1)

    # 5-pointed star centred inside shield
    sc_x = cx
    sc_y = y + h * 0.58
    ro   = size * 0.265   # outer radius
    ri   = size * 0.110   # inner radius
    pts  = [
        (sc_x + (ro if i % 2 == 0 else ri) * math.cos(math.pi / 5 * i - math.pi / 2),
         sc_y + (ro if i % 2 == 0 else ri) * math.sin(math.pi / 5 * i - math.pi / 2))
        for i in range(10)
    ]
    star = c.beginPath()
    star.moveTo(*pts[0])
    for pt in pts[1:]:
        star.lineTo(*pt)
    star.close()
    c.setFillColor(HexColor('#4A4A4A'))
    c.drawPath(star, fill=1, stroke=0)

# ── Cover page ────────────────────────────────────────────────────────────────

_BRIEF = (
    'This study applies graph-based spatial analysis to the ground floor of a police '
    'station, treating architectural space as a network of nodes and adjacencies. '
    'Using topologicPy and graph theory, Phase 02 examines centrality, community '
    'structure, and isovist visibility — revealing the spatial intelligence embedded '
    'in the organisation of the building.'
)

def page_cover(c):
    fill_bg(c)

    # ── Badge + case study label (upper-left) ─────────────────────────────────
    draw_police_badge(c, MARGIN, 482, size=30)

    c.setFillColor(HexColor('#484848')); c.setFont(F_REG, 6)
    c.drawString(MARGIN + 42, 510, 'CASE  STUDY')

    c.setFillColor(HexColor('#999999')); c.setFont(F_REG, 8.5)
    c.drawString(MARGIN + 42, 495, STATION_NAME)

    # ── First thin rule ───────────────────────────────────────────────────────
    c.setStrokeColor(HexColor('#1E1E1E')); c.setLineWidth(0.4)
    c.line(MARGIN, 472, PW - MARGIN, 472)

    # ── Main title ────────────────────────────────────────────────────────────
    c.setFillColor(WHITE); c.setFont(F_BOLD, 34)
    c.drawString(MARGIN, 442, 'POLICE STATION')

    # ── Second rule (white, slightly visible) ─────────────────────────────────
    c.setStrokeColor(HexColor('#2E2E2E')); c.setLineWidth(0.4)
    c.line(MARGIN, 426, PW - MARGIN, 426)

    # ── Subtitle + phase ──────────────────────────────────────────────────────
    c.setFillColor(HexColor('#BBBBBB')); c.setFont(F_REG, 15)
    c.drawString(MARGIN, 406, 'Spatial Intelligence')

    c.setFillColor(HexColor('#555555')); c.setFont(F_REG, 8.5)
    c.drawString(MARGIN, 383, 'PHASE  02  \xb7  GROUND FLOOR ANALYSIS')

    # ── Third rule ────────────────────────────────────────────────────────────
    c.setStrokeColor(HexColor('#1E1E1E')); c.setLineWidth(0.4)
    c.line(MARGIN, 358, PW - MARGIN, 358)

    # ── Concept brief (3 lines max) ───────────────────────────────────────────
    brief_lines = wrap_text(_BRIEF, 115)
    c.setFillColor(HexColor('#666666')); c.setFont(F_REG, 7.5)
    for i, line in enumerate(brief_lines[:4]):
        c.drawString(MARGIN, 342 - i * 13, line)

    # ── Bottom rule + credits ─────────────────────────────────────────────────
    c.setStrokeColor(GREY_DARK); c.setLineWidth(0.4)
    c.line(MARGIN, 46, PW - MARGIN, 46)

    c.setFillColor(HexColor('#555555')); c.setFont(F_REG, 7)
    c.drawString(MARGIN, 16, AUTHOR_NAME)
    c.drawRightString(PW - MARGIN, 16, 'grapML  \xb7  Wassim Jabi')

    c.showPage()

# ── Content pages ─────────────────────────────────────────────────────────────

def content(c, img_name, num, name, finding, page_num, legend_fn=None):
    fill_bg(c)
    img_path = plot(img_name)
    if os.path.exists(img_path):
        draw_image_centered(c, img_path, PLOT_X, PLOT_Y, PLOT_W, PLOT_H)
    else:
        c.setFillColor(GREY_MID); c.setFont(F_REG, 9)
        c.drawCentredString(PW/2, PH/2, f'[image not found: {img_name}]')
    draw_bottom(c, num, name, finding, page_num, legend_fn=legend_fn)
    c.showPage()

# ── Page definitions ──────────────────────────────────────────────────────────

PAGES = [
    ('ps-gf-analysis-graph.png',        '01', 'ANALYSIS GRAPH',
     'The ground floor plan is discretized into a 2×2m grid, each cell becoming a node '
     'and shared edges becoming connections. This graph encodes spatial proximity as '
     'topological structure — the substrate for all subsequent analysis.',
     None),

    ('ps-gf-closeness-centrality.png',  '02', 'CLOSENESS CENTRALITY  ·  INTEGRATION',
     'The main corridor is the shallowest space in the building — reachable from any '
     'point in the fewest steps. Peripheral wings read as topologically isolated. '
     'Warm tones signal integration; cool tones signal depth.',
     lambda c: legend_thermal(c, 'Closeness Centrality', 'ISOLATED', 'INTEGRATED')),

    ('ps-gf-betweenness-centrality.png','03', 'BETWEENNESS CENTRALITY  ·  CHOICE',
     'A single east–west spine concentrates almost all routing choice. Nearly every '
     'shortest path between any two spaces passes through the corridor — '
     'one structural bottleneck connects the entire building.',
     lambda c: legend_thermal(c, 'Betweenness Centrality', 'LOW CHOICE', 'HIGH CHOICE')),

    ('ps-gf-shortest-path.png',         '04', 'SHORTEST PATH',
     'Cross-building traversal, NW to SE corner. The graph path follows cell boundaries; '
     'geometric straightening cuts across open space, reducing travel distance by 11.3%.',
     lambda c: legend_path(c)),

    ('ps-gf-community.png',             '05', 'COMMUNITY PARTITION',
     '6 spatially coherent zones emerge — clusters of cells more strongly connected '
     'internally than to their neighbours. These map onto the functional wings '
     'of the police station: staff offices, circulation, cells, and public areas.',
     lambda c: legend_community(c)),

    ('ps-gf-community-graph.png',       '06', 'COMMUNITY GRAPH',
     'Communities abstracted to single nodes reveal the inter-zone topology. '
     'The corridor community acts as the hub with the highest degree. '
     'Its removal would fragment the entire building into disconnected clusters.',
     None),

    ('ps-gf-degree-centrality.png',     '07', 'DEGREE CENTRALITY  ·  COMMUNITY SCALE',
     'Degree centrality interpolated from community nodes back to the grid. '
     'Junction zones at the boundary between corridor and wings '
     'emerge as the most topologically connected spaces in the building.',
     lambda c: legend_thermal(c, 'Degree Centrality', 'LOW', 'HIGH')),

    ('ps-gf-isovist-points-grid.png',   '08', 'ISOVIST VIEWPOINTS',
     '61 viewpoints sampled at 5m intervals across the floor plan. '
     'Each isovist polygon captures the total area visible from that position. '
     'Visibility ranges from 6 to 55 grid cells — a 9× spread across the building.',
     lambda c: legend_isovist(c)),

    ('ps-gf-isovist-faces-grid.png',    '09', 'ISOVIST VISIBILITY MAP',
     'Visibility scores interpolated across the full floor plan. Corridor junctions '
     'and open spaces are the most exposed. Subdivided rooms and dead-end wings '
     'register the lowest visibility — effectively hidden from the rest of the building.',
     lambda c: legend_thermal(c, 'Visibility Score', 'HIDDEN', 'EXPOSED')),
]

# ── Build ─────────────────────────────────────────────────────────────────────

print("Building PDF...")
cvs = canvas.Canvas(OUT, pagesize=landscape(A4))
cvs.setTitle('Police Station — Spatial Intelligence | Phase 02')
cvs.setAuthor('grapML · Wassim Jabi')

page_cover(cvs)
for i, (img, num, name, finding, legend_fn) in enumerate(PAGES, start=1):
    print(f"  Page {i}/9 — {name}")
    content(cvs, img, num, name, finding, i, legend_fn=legend_fn)

cvs.save()
print(f"\n✓  Done! PDF saved to:\n   {OUT}")
