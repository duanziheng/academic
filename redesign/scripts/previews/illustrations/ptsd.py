"""PTSD (Nature 2025): what the data are. Post-mortem DLPFC from 111 donors; two million nuclei profiled for gene
expression and open chromatin (snRNA-seq, snATAC-seq, multiome) plus a Xenium spatial panel, in seven cell types."""
import numpy as np
from base import *

BRAIN = {
    'cerebellum': 'M262 222 C 270 258 312 280 352 270 C 384 262 398 238 386 214 C 376 196 350 190 326 196 C 300 202 276 206 262 222 Z',
    'cbl_lines': ['M282 218 C 306 230 344 236 384 222', 'M276 232 C 300 250 342 258 380 236', 'M284 248 C 306 262 340 268 374 252', 'M300 262 C 318 270 340 272 360 266'],
    'stem': 'M232 222 C 236 246 240 268 244 286 C 248 296 270 296 274 286 C 270 264 268 244 272 220 Z',
    'cerebrum': 'M30 150 C 22 96 60 44 128 26 C 182 12 252 8 302 26 C 350 44 392 88 400 140 C 404 172 392 196 370 208 C 340 222 298 222 262 226 C 220 232 170 242 134 232 C 108 224 96 206 104 190 C 92 186 72 190 56 184 C 40 178 32 166 30 150 Z',
    'sulci': ['M104 190 C 146 174 196 162 238 152 C 254 148 266 142 278 128', 'M136 177 C 140 168 142 162 146 154', 'M118 182 C 110 178 100 176 90 176',
              'M224 14 C 214 40 228 62 214 86 C 202 108 212 128 198 154', 'M184 26 C 176 48 186 66 176 84', 'M170 98 C 160 118 168 134 160 158',
              'M178 70 C 142 66 102 62 64 70', 'M168 110 C 132 110 94 112 54 124', 'M256 20 C 248 46 258 66 246 92 C 236 112 242 128 232 146',
              'M250 86 C 282 94 314 104 348 124', 'M140 212 C 182 198 234 186 288 168 C 302 162 312 154 320 144', 'M168 230 C 210 220 252 214 302 206',
              'M356 64 C 364 90 362 116 372 146'],
    'dlpfc': 'M70 78 C 96 70 128 70 156 76 C 162 86 160 98 152 106 C 122 106 92 110 62 118 C 54 104 58 88 70 78 Z',
}


def brain(theme, x, y, s, highlight=True):
    lt = theme == 'light'
    edge, sulc, tis, tis2 = (('#B4A49E', '#C9B9B3', '#EFE6E2', '#E8DCD7') if lt else ('#6E6275', '#55495C', '#2A2530', '#241F2A'))
    o = f'<g transform="translate({f(x)} {f(y)}) scale({f(s)})">'
    o += f'<path d="{BRAIN["cerebellum"]}" fill="{tis2}" stroke="{edge}" stroke-width="1.4"/>'
    o += ''.join(f'<path d="{d}" fill="none" stroke="{sulc}" stroke-width="1.1" stroke-linecap="round"/>' for d in BRAIN['cbl_lines'])
    o += f'<path d="{BRAIN["stem"]}" fill="{tis2}" stroke="{edge}" stroke-width="1.4"/>'
    o += f'<path d="{BRAIN["cerebrum"]}" fill="{tis}" stroke="{edge}" stroke-width="1.6" stroke-linejoin="round"/>'
    o += ''.join(f'<path d="{d}" fill="none" stroke="{sulc}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>' for d in BRAIN['sulci'])
    if highlight:
        o += f'<path d="{BRAIN["dlpfc"]}" fill="#F2B36A" fill-opacity="{0.85 if lt else 0.8}" stroke="#D9822B" stroke-width="1.8"/>'
    return o + '</g>'


def umap(rng):
    spec = [  # type, centre, spread, n, sub-clusters
        ('EXN', (0.30, -0.18), 0.30, 3400, 6), ('IN', (0.42, 0.42), 0.20, 1500, 4), ('OLG', (-0.55, 0.05), 0.16, 2200, 1),
        ('OPC', (-0.40, 0.55), 0.07, 450, 1), ('AST', (-0.30, -0.52), 0.09, 750, 1), ('MG', (-0.02, 0.62), 0.06, 330, 1), ('END', (-0.75, -0.42), 0.05, 230, 1)]
    P, C = [], []
    for name, (cx, cy), sp, n, k in spec:
        cs = [np.array([cx, cy])] if k == 1 else [np.array([cx, cy]) + sp * np.array([np.cos(a), np.sin(a) * 0.8]) for a in np.linspace(-2.2, 1.6, k)]
        for j, c0 in enumerate(cs):
            m = n // k
            ang = rng.uniform(0, np.pi); R = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
            sd = np.array([rng.uniform(0.05, 0.09), rng.uniform(0.025, 0.045)]) * (1.6 if k == 1 else 1)
            Z = rng.normal(0, 1, (m, 2)) * sd
            # heavier tails toward neighbours make the shapes look like real embeddings
            Z += rng.standard_t(4, (m, 2)) * sd * 0.18
            P.append(Z @ R.T + c0); C += [name] * m
    return np.vstack(P), C


def draw(theme):
    svg = SVG(theme); lt = theme == 'light'
    rng = np.random.default_rng(3)
    ink, mute, line = INK[theme], MUTE[theme], LINE[theme]
    # 1. where from and from whom: the DLPFC, 111 donors
    svg.add(brain(theme, 34, 30, 0.62))
    svg.add('<text x="44" y="38" font-size="15" font-weight="700" fill="#C77A22">DLPFC</text>')
    groups = [('#2F5D8C' if lt else '#6E9FD2', 36), ('#D49A2A', 36), ('#9AA6B2' if lt else '#6B7A89', 39)]
    k = 0
    for col, n in groups:
        for _ in range(n):
            cx = 44 + (k % 15) * 15.5; cy = 254 + (k // 15) * 15.5
            svg.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="5.6" fill="{col}"/>'); k += 1
    svg.add(f'<text x="42" y="420" font-size="34" font-weight="700" fill="{ink}">111<tspan dx="9" font-size="19" font-weight="400" fill="{mute}">donors</tspan></text>')
    # 2. two million nuclei in seven cell types
    P, C = umap(rng)
    cx, cy, s = 470, 205, 175
    o = []
    order = rng.permutation(len(P))
    for i in order:
        x, y = P[i]
        o.append(f'<circle cx="{f(cx + s * x)}" cy="{f(cy + s * y)}" r="1.45" fill="{tone(CT[C[i]], theme, 0.05)}" fill-opacity="0.8"/>')
    svg.add(''.join(o))
    svg.add(f'<text x="330" y="420" font-size="34" font-weight="700" fill="{ink}">2,051,149<tspan dx="9" font-size="19" font-weight="400" fill="{mute}">nuclei</tspan></text>')
    # 3. four assays: expression, open chromatin, both in one nucleus, and a spatial panel
    X0 = 672
    # expression heatmap: marker genes by cell type
    types = list(CT)
    hm = []
    cols = 42; rows = 12
    for j in range(cols):
        t = types[min(j * 7 // cols, 6)]
        hm.append(f'<rect x="{f(X0 + j * 6.2)}" y="34" width="6.2" height="5" fill="{tone(CT[t], theme)}"/>')
        for i in range(rows):
            hi = (i * 7 // rows) == (j * 7 // cols)
            v = rng.uniform(0.55, 1) if hi else rng.uniform(0, 0.28)
            base = '#FFFFFF' if lt else BG['dark']
            hm.append(f'<rect x="{f(X0 + j * 6.2)}" y="{f(42 + i * 6.2)}" width="6.2" height="6.2" fill="{mix(base, "#B83D5A" if lt else "#E07A93", v)}"/>')
    svg.add(''.join(hm))
    # open chromatin: peaks per cell type above a gene model
    y0 = 158
    for r_, t in enumerate(['EXN', 'IN', 'OLG', 'AST']):
        base_y = y0 + r_ * 24
        xs = np.linspace(0, 260, 140); yv = np.zeros_like(xs)
        for _ in range(rng.integers(3, 6)):
            c0 = rng.uniform(10, 250); yv += rng.uniform(5, 19) * np.exp(-((xs - c0) / rng.uniform(2, 5)) ** 2)
        yv += 16 * np.exp(-((xs - 128) / 3.2) ** 2) * (1 if t in ('EXN', 'IN') else 0.15)
        pts = [(X0 + x, base_y + 20 - min(v, 19)) for x, v in zip(xs, yv)]
        d = 'M' + f'{f(X0)} {f(base_y + 20)} ' + ' '.join(f'L{f(x)} {f(y)}' for x, y in pts) + f' L{f(X0 + 260)} {f(base_y + 20)} Z'
        svg.add(f'<path d="{d}" fill="{tone(CT[t], theme)}" fill-opacity="0.85"/><line x1="{X0}" y1="{f(base_y + 20)}" x2="{X0 + 260}" y2="{f(base_y + 20)}" stroke="{line}" stroke-width="1"/>')
    gy = y0 + 4 * 24 + 8
    svg.add(f'<line x1="{X0 + 40}" y1="{gy}" x2="{X0 + 220}" y2="{gy}" stroke="{ink}" stroke-width="1.6"/>' +
            ''.join(f'<rect x="{X0 + x}" y="{gy - 5}" width="{w}" height="10" fill="{ink}"/>' for x, w in ((40, 10), (78, 7), (120, 12), (160, 6), (205, 15))))
    # spatial panel: cell positions in a tissue patch
    tx, ty, tw, th = X0, 290, 260, 96
    svg.add(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="8" fill="{"#F1EAEE" if lt else "#1E2530"}" stroke="{line}" stroke-width="1"/>')
    dots = []
    for _ in range(900):
        x = rng.uniform(tx + 5, tx + tw - 5); y = rng.uniform(ty + 5, ty + th - 5)
        depth = (y - ty) / th + 0.06 * np.sin((x - tx) / 40)
        if depth < 0.12: p = [0.05, 0.05, 0.02, 0.03, 0.15, 0.55, 0.15]
        elif depth < 0.72: p = [0.62, 0.22, 0.04, 0.03, 0.02, 0.05, 0.02]
        else: p = [0.06, 0.03, 0.70, 0.10, 0.03, 0.03, 0.05]
        p = np.array(p); t = types[rng.choice(7, p=p / p.sum())]
        dots.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="1.9" fill="{tone(CT[t], theme)}"/>')
    svg.add(''.join(dots))
    svg.add(f'<text x="{X0}" y="420" font-size="34" font-weight="700" fill="{ink}">4<tspan dx="9" font-size="19" font-weight="400" fill="{mute}">assays · 7 cell types</tspan></text>')
    return svg.text()

