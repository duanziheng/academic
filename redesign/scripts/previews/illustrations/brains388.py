"""388 brains (Science 2024): one brain drawn as its cells, the cortical layers folding along every sulcus and the
white matter inside, in front of a stack of the resource's many brains; beside it the numbers and the cell-type
regulatory networks, with a variant in the DNA (an eQTL) tied to one of them."""
import re
import numpy as np
from matplotlib.path import Path as MPath
from scipy.spatial import cKDTree
from base import *
from ptsd import BRAIN

# excitatory neurons by cortical layer, from the surface down
L23, L4, L5, L6 = '#F2BC48', '#EF953C', '#E05A5C', '#BE4486'
INN = ['#2BAE73', '#7FC25E', '#1AA39B']                     # inhibitory neurons
WM = (['#4A7FD4', '#7A64D8', '#2FAFC0', '#A87055', '#E2C25A'],  # OLG, OPC, AST, MG, END
      [0.6, 0.14, 0.13, 0.08, 0.05])
CBL = ['#8C6FD8', '#A88BE6', '#6F5BC9']                      # cerebellar granule cells


def tokens(d):
    return re.findall(r'[MCLZ]|-?\d+\.?\d*', d)


def svg_to_mpath(d, s, x0, y0):
    toks, verts, codes, i, cmd = tokens(d), [], [], 0, None
    while i < len(toks):
        t = toks[i]
        if t in 'MCLZ':
            cmd = t; i += 1
            if t == 'Z':
                verts.append(verts[0]); codes.append(MPath.CLOSEPOLY)
            continue
        if cmd == 'M':
            verts.append((float(toks[i]), float(toks[i + 1]))); codes.append(MPath.MOVETO); i += 2; cmd = 'L'
        elif cmd == 'L':
            verts.append((float(toks[i]), float(toks[i + 1]))); codes.append(MPath.LINETO); i += 2
        elif cmd == 'C':
            for k in range(3):
                verts.append((float(toks[i]), float(toks[i + 1]))); codes.append(MPath.CURVE4); i += 2
    return MPath(np.array(verts) * s + [x0, y0], codes)


def curve_points(d, s, x0, y0, n=48):
    """points along an SVG path of M/L/C commands (open or closed), densely sampled"""
    toks, pts, i, cmd, cur = tokens(d), [], 0, None, None
    while i < len(toks):
        t = toks[i]
        if t in 'MCLZ':
            cmd = t; i += 1
            if t == 'Z' and pts:
                a, b = np.array(pts[-1]), np.array(pts[0])
                pts += list(a + (b - a) * u for u in np.linspace(0, 1, n)[1:])
            continue
        if cmd == 'M':
            cur = np.array([float(toks[i]), float(toks[i + 1])]); pts.append(cur); i += 2; cmd = 'L'
        elif cmd == 'L':
            nxt = np.array([float(toks[i]), float(toks[i + 1])])
            pts += list(cur + (nxt - cur) * u for u in np.linspace(0, 1, n)[1:]); cur = nxt; i += 2
        elif cmd == 'C':
            c1, c2, p = (np.array([float(toks[i + 2 * k]), float(toks[i + 2 * k + 1])]) for k in range(3))
            for u in np.linspace(0, 1, n)[1:]:
                pts.append((1 - u) ** 3 * cur + 3 * (1 - u) ** 2 * u * c1 + 3 * (1 - u) * u ** 2 * c2 + u ** 3 * p)
            cur = p; i += 6
    return np.array(pts) * s + [x0, y0]


def jitter_grid(rng, box, sp, jit):
    x0, y0, x1, y1 = box; P = []
    for j, y in enumerate(np.arange(y0, y1, sp * 0.866)):
        xs = np.arange(x0, x1, sp) + (sp / 2 if j % 2 else 0)
        P.append(np.c_[xs, np.full_like(xs, y)])
    P = np.vstack(P)
    return P + rng.uniform(-jit, jit, P.shape)


def silhouette(x, y, s, fill, stroke, sw, extra=''):
    return (f'<g transform="translate({f(x)} {f(y)}) scale({f(s)})" {extra}>'
            f'<path d="{BRAIN["cerebellum"]}" fill="{fill}" stroke="{stroke}" stroke-width="{f(sw)}"/>'
            f'<path d="{BRAIN["stem"]}" fill="{fill}" stroke="{stroke}" stroke-width="{f(sw)}"/>'
            f'<path d="{BRAIN["cerebrum"]}" fill="{fill}" stroke="{stroke}" stroke-width="{f(sw)}" stroke-linejoin="round"/></g>')


def draw(theme):
    svg = SVG(theme); lt = theme == 'light'
    rng = np.random.default_rng(21)
    ink, mute, bg = INK[theme], MUTE[theme], BG[theme]
    X0, Y0, S = 26, 84, 1.2
    tissue = '#F4EDEA' if lt else '#1C1923'
    edge = '#CDBFBA' if lt else '#3B3445'
    # the many brains of the resource: a stack of silhouettes fanning up and to the right behind the front one
    back = '#E6DCD8' if lt else '#262130'
    svg.defn('<filter id="stackblur" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.3"/></filter>')
    svg.add('<g filter="url(#stackblur)">')
    for k in range(4, 0, -1):
        svg.add(silhouette(X0 + 15 * k, Y0 - 12 * k, S, mix(back, bg, 0.12 + 0.2 * k), mix(edge, bg, 0.35 + 0.15 * k), 1.0 / S))
    svg.add('</g>')
    # the front brain: a silhouette, then its cells
    svg.add(silhouette(X0, Y0, S, tissue, edge, 1.3 / S))
    cer = svg_to_mpath(BRAIN['cerebrum'], S, X0, Y0)
    cbl = svg_to_mpath(BRAIN['cerebellum'], S, X0, Y0)
    stem = svg_to_mpath(BRAIN['stem'], S, X0, Y0)
    outline = curve_points(BRAIN['cerebrum'], S, X0, Y0)
    sulci = np.vstack([curve_points(d, S, X0, Y0) for d in BRAIN['sulci']])
    folia = np.vstack([curve_points(d, S, X0, Y0) for d in BRAIN['cbl_lines']])
    t_out, t_sul, t_fol = cKDTree(outline), cKDTree(sulci), cKDTree(folia)
    noise = smooth_noise(np.random.default_rng(5), 6, 1.0)
    P = jitter_grid(rng, (X0, Y0, X0 + 410 * S, Y0 + 300 * S), 3.95, 0.55)
    dots = []

    def dot(x, y, c, r=None, op=0.95):
        r = rng.uniform(1.55, 1.8) if r is None else r
        dots.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{tone(c, theme, 0.06)}" fill-opacity="{op}"/>')

    # cerebrum: depth below the nearest surface (the outer edge or a sulcus) sets the layer
    Pc = P[cer.contains_points(P, radius=-1.2)]
    ds, _ = t_sul.query(Pc); do, _ = t_out.query(Pc)
    dep = np.minimum(ds, do) + 1.1 * noise(Pc[:, 0] / 60, Pc[:, 1] / 60)
    for (x, y), d, dsu in zip(Pc, dep, ds):
        if dsu < 1.5:
            continue                                   # the sulcus itself
        r = rng.random()
        if d < 2.4:                                    # L1: few cells
            if r < 0.35:
                dot(x, y, WM[0][2] if r < 0.15 else INN[0], op=0.8)
            continue
        if d < 20.5:
            if r < 0.1:
                c = INN[rng.integers(3)]
            elif r < 0.13:
                c = rng.choice(WM[0], p=WM[1])
            else:
                c = L23 if d < 8.5 else L4 if d < 11.5 else L5 if d < 16 else L6
            dot(x, y, c)
        else:
            dot(x, y, rng.choice(WM[0], p=WM[1]))
    # cerebellum and brainstem
    Pb = P[cbl.contains_points(P, radius=-1.2) & ~cer.contains_points(P, radius=1.5)]
    df, _ = t_fol.query(Pb)
    for (x, y), d in zip(Pb, df):
        if d < 2.0:
            continue
        dot(x, y, '#E07AB8' if d < 3.6 and rng.random() < 0.5 else CBL[rng.integers(3)], r=rng.uniform(1.3, 1.7))
    Ps = P[stem.contains_points(P, radius=-1.2) & ~cer.contains_points(P, radius=1.5) & ~cbl.contains_points(P, radius=1.5)]
    for x, y in Ps:
        dot(x, y, WM[0][0] if rng.random() < 0.7 else WM[0][2], r=rng.uniform(1.3, 1.7))
    sul = '#C9B7B1' if lt else '#3A3344'
    svg.add(f'<g transform="translate({X0} {Y0}) scale({S})" fill="none" stroke="{sul}" stroke-width="{f(1.6 / S)}" stroke-linecap="round">'
            + ''.join(f'<path d="{d}"/>' for d in BRAIN['sulci'] + BRAIN['cbl_lines']) + '</g>')
    svg.add(''.join(dots))
    hx, hy = X0 + 120 * S, Y0 + 50 * S
    svg.defn(f'<clipPath id="cer{theme}"><path transform="translate({X0} {Y0}) scale({S})" d="{BRAIN["cerebrum"]}"/></clipPath>'
             f'<radialGradient id="vol{theme}" gradientUnits="userSpaceOnUse" cx="{f(hx)}" cy="{f(hy)}" r="{f(330 * S)}">'
             f'<stop offset="0" stop-color="#FFFFFF" stop-opacity="{0.2 if lt else 0.1}"/>'
             f'<stop offset="0.45" stop-color="#FFFFFF" stop-opacity="0"/>'
             f'<stop offset="1" stop-color="{"#14263C" if lt else "#000000"}" stop-opacity="{0.24 if lt else 0.42}"/></radialGradient>')
    svg.add(f'<rect x="{X0}" y="{Y0}" width="{f(410 * S)}" height="{f(300 * S)}" fill="url(#vol{theme})" clip-path="url(#cer{theme})"/>')
    # the numbers
    svg.add(f'<text x="604" y="132" font-family="Gelasio, Georgia, serif" font-size="112" fill="{ink}" letter-spacing="-2">388</text>'
            f'<text x="812" y="132" font-size="26" fill="{ink}">brains</text>'
            f'<text x="608" y="170" font-size="19" fill="{mute}">2.8M nuclei · 28 cell types</text>')
    # regulatory networks: transcription-factor hubs of four cell types, their target genes, some shared
    hubs = [(682, 266, L5), (806, 232, INN[0]), (874, 332, WM[0][0]), (744, 372, L23)]
    gene = '#B4C0CC' if lt else '#55687C'
    edges, nodes = [], []
    for hx_, hy, c in hubs:
        for a in np.linspace(0, 2 * np.pi, 11, endpoint=False) + rng.uniform(0, 0.6):
            rr = rng.uniform(34, 60); tx, ty = hx_ + rr * np.cos(a), hy + rr * np.sin(a)
            bend = rng.uniform(-0.25, 0.25)
            mx, my = (hx_ + tx) / 2 - (ty - hy) * bend, (hy + ty) / 2 + (tx - hx_) * bend
            edges.append(f'<path d="M{hx_} {hy} Q{f(mx)} {f(my)} {f(tx)} {f(ty)}" fill="none" stroke="{c}" stroke-width="1.3" stroke-opacity="0.6"/>')
            nodes.append(f'<circle cx="{f(tx)}" cy="{f(ty)}" r="3.2" fill="{gene}"/>')
    for i, j in [(0, 1), (1, 2), (0, 3), (3, 2)]:
        (x1, y1, c1), (x2, y2, c2) = hubs[i], hubs[j]
        gx, gy = (x1 + x2) / 2 + rng.uniform(-8, 8), (y1 + y2) / 2 + rng.uniform(-8, 8)
        edges.append(f'<path d="M{x1} {y1} L{f(gx)} {f(gy)}" stroke="{c1}" stroke-width="2" stroke-opacity="0.75"/>'
                     f'<path d="M{x2} {y2} L{f(gx)} {f(gy)}" stroke="{c2}" stroke-width="2" stroke-opacity="0.75"/>')
        nodes.append(f'<circle cx="{f(gx)}" cy="{f(gy)}" r="5" fill="{ink}" fill-opacity="0.55" stroke="{bg}" stroke-width="2"/>')
    svg.add(''.join(edges) + ''.join(nodes))
    for hx_, hy, c in hubs:
        svg.add(f'<circle cx="{hx_}" cy="{hy}" r="20" fill="{c}" fill-opacity="0.15"/>'
                f'<circle cx="{hx_}" cy="{hy}" r="11.5" fill="{tone(c, theme, 0.04)}" stroke="{bg}" stroke-width="3"/>')
    # a variant in the DNA tied to one cell type's regulation (an eQTL)
    ys = 446; xs = np.linspace(604, 930, 120)
    for ph in (0, np.pi):
        pts_ = [(x, ys + 9 * np.sin((x - 604) / 12 + ph)) for x in xs]
        svg.add(f'<path d="{smooth_path(pts_, False)}" fill="none" stroke="{mute}" stroke-width="2.2"/>')
    for x in xs[::4]:
        svg.add(f'<line x1="{f(x)}" y1="{f(ys + 9 * np.sin((x - 604) / 12))}" x2="{f(x)}" y2="{f(ys + 9 * np.sin((x - 604) / 12 + np.pi))}" '
                f'stroke="{mute}" stroke-width="1" stroke-opacity="0.6"/>')
    vx = xs[52]
    svg.add(f'<path d="M{f(vx)} {ys - 10} C{f(vx)} {ys - 38} 744 416 744 388" fill="none" stroke="#E2445A" stroke-width="2" stroke-dasharray="4 4"/>'
            f'<circle cx="{f(vx)}" cy="{ys}" r="7" fill="#E2445A" stroke="{bg}" stroke-width="2.5"/>')
    return svg.text()

