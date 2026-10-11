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


def brain(theme, x, y, s, highlight=True, uid=''):
    lt = theme == 'light'
    edge, sulc = (('#BBA9A2', '#D6C7C1') if lt else ('#6A5E72', '#4B4153'))
    g0, g1, cb = (('#F8F2EE', '#E8DBD5', '#EADFDA') if lt else ('#302A36', '#211C27', '#262130'))
    o = (f'<defs><radialGradient id="tis{theme}{uid}" cx="0.36" cy="0.3" r="0.85"><stop offset="0" stop-color="{g0}"/>'
         f'<stop offset="1" stop-color="{g1}"/></radialGradient>'
         f'<filter id="dl{theme}{uid}" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="7"/></filter></defs>')
    o += f'<g transform="translate({f(x)} {f(y)}) scale({f(s)})">'
    o += f'<path d="{BRAIN["cerebellum"]}" fill="{cb}" stroke="{edge}" stroke-width="1.6"/>'
    o += ''.join(f'<path d="{d}" fill="none" stroke="{sulc}" stroke-width="1.3" stroke-linecap="round"/>' for d in BRAIN['cbl_lines'])
    o += f'<path d="{BRAIN["stem"]}" fill="{cb}" stroke="{edge}" stroke-width="1.6"/>'
    o += f'<path d="{BRAIN["cerebrum"]}" fill="url(#tis{theme}{uid})" stroke="{edge}" stroke-width="1.8" stroke-linejoin="round"/>'
    o += ''.join(f'<path d="{d}" fill="none" stroke="{sulc}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>' for d in BRAIN['sulci'])
    if highlight:
        o += f'<path d="{BRAIN["dlpfc"]}" fill="#F2A54A" opacity="{0.55 if lt else 0.6}" filter="url(#dl{theme}{uid})"/>'
        o += f'<path d="{BRAIN["dlpfc"]}" fill="#F4B166" stroke="#D9822B" stroke-width="2"/>'
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
    serif = 'font-family="Gelasio, Georgia, serif"'
    sans = 'font-family="Inter, Helvetica, Arial, sans-serif"'
    # 1. where from and from whom: the DLPFC, 111 donors
    bx, by, bs = 40, 50, 0.6
    svg.add(brain(theme, bx, by, bs))
    lx, ly = bx + 104 * bs, by + 92 * bs
    svg.add(f'<path d="M{f(lx)} {f(ly - 4)} L{f(lx - 10)} 40 L 94 40" fill="none" stroke="#C77A22" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{f(lx)}" cy="{f(ly - 4)}" r="2.6" fill="#C77A22"/>'
            f'<text x="42" y="45" {sans} font-size="14" font-weight="700" letter-spacing="0.6" fill="#C77A22">DLPFC</text>')
    groups = [('#3E6A9A' if lt else '#6E9FD2', 36), ('#D6A040', 36), ('#B3BDC7' if lt else '#566676', 39)]
    k = 0
    for col, n in groups:
        for _ in range(n):
            cx = 48 + (k % 15) * 14.6; cy = 268 + (k // 15) * 14.6
            svg.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="4.7" fill="{col}"/>'); k += 1
    svg.add(f'<text x="44" y="420" {serif} font-size="40" fill="{ink}">111<tspan dx="10" {sans} font-size="18" fill="{mute}">donors</tspan></text>')
    # 2. two million nuclei in seven cell types
    P, C = umap(rng)
    cx, cy, s = 470, 205, 175
    o = []
    for i in rng.permutation(len(P)):
        x, y = P[i]
        o.append(f'<circle cx="{f(cx + s * x)}" cy="{f(cy + s * y)}" r="1.45" fill="{tone(CT[C[i]], theme, 0.05)}" fill-opacity="0.8"/>')
    svg.add(''.join(o))
    svg.add(f'<text x="332" y="420" {serif} font-size="40" fill="{ink}">2,051,149<tspan dx="10" {sans} font-size="18" fill="{mute}">nuclei</tspan></text>')
    # 3. four assays: expression, open chromatin, both in one nucleus, and a spatial panel
    X0 = 672
    types = list(CT)
    svg.defn(f'<clipPath id="hm{theme}"><rect x="{X0}" y="34" width="260" height="111" rx="5"/></clipPath>')
    hm = [f'<g clip-path="url(#hm{theme})">']
    cols = 42; rows = 12
    for j in range(cols):
        t = types[min(j * 7 // cols, 6)]
        hm.append(f'<rect x="{f(X0 + j * 6.2)}" y="34" width="6.3" height="6" fill="{tone(CT[t], theme)}"/>')
        for i in range(rows):
            hi = (i * 7 // rows) == (j * 7 // cols)
            v = rng.uniform(0.55, 1) if hi else rng.uniform(0, 0.26)
            base = '#FFFFFF' if lt else '#101B27'
            hm.append(f'<rect x="{f(X0 + j * 6.2)}" y="{f(41 + i * 8.7)}" width="6.3" height="8.8" fill="{mix(base, "#B83D5A" if lt else "#E07A93", v)}"/>')
    hm.append('</g>')
    svg.add(''.join(hm))
    # open chromatin: peaks per cell type above a gene model
    y0 = 160
    for r_, t in enumerate(['EXN', 'IN', 'OLG', 'AST']):
        base_y = y0 + r_ * 23
        xs = np.linspace(0, 260, 160); yv = np.zeros_like(xs)
        for _ in range(rng.integers(3, 6)):
            c0 = rng.uniform(10, 250); yv += rng.uniform(5, 18) * np.exp(-((xs - c0) / rng.uniform(2, 5)) ** 2)
        yv += 16 * np.exp(-((xs - 128) / 3.2) ** 2) * (1 if t in ('EXN', 'IN') else 0.15)
        pts = [(X0 + x, base_y + 20 - min(v, 19)) for x, v in zip(xs, yv)]
        d = 'M' + f'{f(X0)} {f(base_y + 20)} ' + ' '.join(f'L{f(x)} {f(y)}' for x, y in pts) + f' L{f(X0 + 260)} {f(base_y + 20)} Z'
        svg.add(f'<path d="{d}" fill="{tone(CT[t], theme)}" fill-opacity="0.85"/><line x1="{X0}" y1="{f(base_y + 20)}" x2="{X0 + 260}" y2="{f(base_y + 20)}" stroke="{line}" stroke-width="1"/>')
    gy = y0 + 4 * 23 + 9
    svg.add(f'<line x1="{X0 + 40}" y1="{gy}" x2="{X0 + 220}" y2="{gy}" stroke="{ink}" stroke-width="1.5"/>' +
            ''.join(f'<rect x="{X0 + x}" y="{gy - 5}" width="{w}" height="10" rx="1.5" fill="{ink}"/>' for x, w in ((40, 10), (78, 7), (120, 12), (160, 6), (205, 15))))
    # spatial panel: cells in a strip of cortex, from the pial surface (top) to the white matter (bottom)
    tx, ty, tw, th = X0, 292, 260, 94
    top = lambda x: ty + 5 + 3.2 * np.sin((x - tx) / 31 + 0.6)
    bot = lambda x: ty + th - 4 + 2.4 * np.sin((x - tx) / 47 + 2.0)
    xs = np.linspace(tx, tx + tw, 60)
    outline = [(x, top(x)) for x in xs] + [(x, bot(x)) for x in xs[::-1]]
    sd = path_d(outline)
    svg.defn(f'<clipPath id="sp{theme}"><path d="{sd}"/></clipPath>')
    svg.add(f'<path d="{sd}" fill="{"#F2EBEF" if lt else "#1D2532"}" stroke="{"#DCCFD6" if lt else "#33404F"}" stroke-width="1"/>')
    dots = [f'<g clip-path="url(#sp{theme})">']
    sp_ = 4.6
    for j, yy in enumerate(np.arange(ty, ty + th, sp_ * 0.87)):
        for xx in np.arange(tx, tx + tw, sp_) + (sp_ / 2 if j % 2 else 0):
            x = xx + rng.uniform(-1, 1); y = yy + rng.uniform(-1, 1)
            depth = (y - top(x)) / (bot(x) - top(x)) + 0.03 * np.sin((x - tx) / 23)
            if depth < 0 or depth > 1:
                continue
            if depth < 0.13:                      # layer 1: few cells, mostly glia
                if rng.random() < 0.62:
                    continue
                p = [0.02, 0.12, 0.04, 0.02, 0.04, 0.56, 0.2]
            elif depth < 0.64:                    # grey matter: neurons
                if rng.random() < 0.12:
                    continue
                p = [0.7, 0.2, 0.03, 0.02, 0.01, 0.03, 0.01]
            else:                                 # white matter: oligodendrocytes
                if rng.random() < 0.1:
                    continue
                p = [0.02, 0.01, 0.82, 0.08, 0.02, 0.03, 0.02]
            p = np.array(p); t = types[rng.choice(7, p=p / p.sum())]
            dots.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="1.7" fill="{tone(CT[t], theme)}"/>')
    dots.append('</g>')
    svg.add(''.join(dots))
    svg.add(f'<text x="{X0}" y="420" {serif} font-size="40" fill="{ink}">4<tspan dx="10" {sans} font-size="18" fill="{mute}">assays · 7 cell types</tspan></text>')
    return svg.text()
