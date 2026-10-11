"""iMIRACLE: cell-cell communication in tissue. A sender cell releases ligands that bind receptors on a neighbouring
receiver cell; inside the receiver the signal reaches the nucleus and switches a gene on. Around them, the tissue's
other cells and the communication edges between neighbours."""
import numpy as np
from base import *

TA = '#5B8FCB'   # cell type A (sender)
TB = '#E2955B'   # cell type B (receiver)


def blob(cx, cy, r, rng, n=64, amp=0.05):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    rr = r * (1 + periodic_noise(rng, t, 4, amp))
    return np.c_[cx + rr * np.cos(t), cy + rr * np.sin(t)]


def poisson(rng, n, w, h, dmin, margin=0):
    pts = []
    tries = 0
    while len(pts) < n and tries < 20000:
        p = rng.uniform([margin, margin], [w - margin, h - margin]); tries += 1
        if all(np.hypot(*(p - q)) > dmin for q in pts): pts.append(p)
    return np.array(pts)


def cell(svg, P, col, theme, nuc=None, rng=None, big=False, organelles=False):
    lt = theme == 'light'
    mem = mix(col, '#1E2A36', 0.25) if lt else mix(col, '#FFFFFF', 0.1)
    fill_in = mix(col, '#FFFFFF', 0.82) if lt else mix(col, BG['dark'], 0.72)
    d = smooth_path(P, True, 0.8)
    gid = f'g{abs(hash((round(P[0][0], 1), round(P[0][1], 1)))) % 10**6}'
    cx, cy = P.mean(0)
    r = np.hypot(*(P - [cx, cy]).T).mean()
    svg.defn(f'<radialGradient id="{gid}" cx="{f(cx - r * 0.25)}" cy="{f(cy - r * 0.3)}" r="{f(r * 1.25)}" gradientUnits="userSpaceOnUse">'
             f'<stop offset="0" stop-color="{mix(fill_in, "#FFFFFF", 0.5) if lt else mix(fill_in, col, 0.12)}"/><stop offset="1" stop-color="{fill_in}"/></radialGradient>')
    w = 7 if big else 3
    svg.add(f'<path d="{d}" fill="url(#{gid})" stroke="{mem}" stroke-width="{w}"/>')
    if big:   # the bilayer: a light line inside the membrane
        svg.add(f'<path d="{d}" fill="none" stroke="{mix(col, "#FFFFFF", 0.55) if lt else mix(col, BG["dark"], 0.35)}" stroke-width="2"/>')
    if organelles and rng is not None:
        for k in range(5):   # mitochondria
            a = rng.uniform(0, 2 * np.pi); rr = r * rng.uniform(0.55, 0.72)
            x, y = cx + rr * np.cos(a), cy + rr * np.sin(a); ang = np.degrees(a) + 90 + rng.uniform(-30, 30)
            mc = mix(col, '#7A4A3A', 0.45) if lt else mix(col, '#E8C8A8', 0.3)
            svg.add(f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)})"><ellipse rx="13" ry="6.5" fill="{mix(mc, "#FFFFFF", 0.55) if lt else mix(mc, BG["dark"], 0.5)}" stroke="{mc}" stroke-width="1.4"/>'
                    f'<path d="M-8 -3 Q-6 3 -4 -3 Q-2 3 0 -3 Q2 3 4 -3 Q6 3 8 -3" fill="none" stroke="{mc}" stroke-width="0.9"/></g>')
        # endoplasmic reticulum: arcs around the nucleus
        for k in range(3):
            a0 = rng.uniform(0, 2 * np.pi); rr = r * (0.42 + 0.06 * k)
            pts = [(cx + nuc[2] * 0 + rr * np.cos(a0 + s), cy + rr * np.sin(a0 + s)) for s in np.linspace(0, 1.3, 9)]
            svg.add(f'<path d="{smooth_path(pts, False)}" fill="none" stroke="{mix(col, "#1E2A36", 0.1) if lt else mix(col, "#FFFFFF", 0.05)}" stroke-width="1.3" stroke-opacity="0.55"/>')
    if nuc is not None:
        nx, ny, nr = nuc
        nc = mix(col, '#2B3550', 0.35) if lt else mix(col, '#0B141E', 0.25)
        nfill = mix(col, '#FFFFFF', 0.6) if lt else mix(col, BG['dark'], 0.45)
        Pn = blob(nx, ny, nr, rng or np.random.default_rng(0), 48, 0.04)
        svg.add(f'<path d="{smooth_path(Pn, True, 0.8)}" fill="{nfill}" stroke="{nc}" stroke-width="{2.2 if big else 1.2}"/>')
        if big and rng is not None:
            for k in range(60):   # chromatin
                a = rng.uniform(0, 2 * np.pi); rr = nr * np.sqrt(rng.uniform(0, 0.85))
                svg.add(f'<circle cx="{f(nx + rr * np.cos(a))}" cy="{f(ny + rr * np.sin(a))}" r="{f(rng.uniform(1, 2.4))}" fill="{nc}" fill-opacity="0.35"/>')
            svg.add(f'<circle cx="{f(nx + nr * 0.25)}" cy="{f(ny - nr * 0.2)}" r="{f(nr * 0.2)}" fill="{nc}" fill-opacity="0.75"/>')


def ligand(svg, x, y, col, theme, s=1.0, rot=0):
    """a small signalling protein: three beads"""
    lt = theme == 'light'
    edge = mix(col, '#1E2A36', 0.3) if lt else mix(col, '#FFFFFF', 0.25)
    out = f'<g transform="translate({f(x)} {f(y)}) rotate({f(rot)}) scale({f(s)})">'
    for dx, dy, rr in ((-5, 2, 5), (3, -3, 5.6), (5, 5, 4.2)):
        out += f'<circle cx="{dx}" cy="{dy}" r="{rr}" fill="{col}" stroke="{edge}" stroke-width="1.1"/>'
    svg.add(out + '</g>')


def receptor(svg, x, y, ang, col, theme, bound=False):
    """a transmembrane receptor: helices through the membrane, a cup outside (pointing along ang)"""
    lt = theme == 'light'
    edge = mix(col, '#1E2A36', 0.35) if lt else mix(col, '#FFFFFF', 0.2)
    out = f'<g transform="translate({f(x)} {f(y)}) rotate({f(ang)})">'
    out += f'<rect x="-16" y="-6" width="20" height="12" rx="5" fill="{mix(col, "#FFFFFF", 0.35) if lt else mix(col, BG["dark"], 0.2)}" stroke="{edge}" stroke-width="1.2"/>'   # inside the membrane
    out += f'<path d="M4 -5 L18 -5 Q26 -5 28 -14 L34 -14 Q32 0 22 0 Q32 0 34 14 L28 14 Q26 5 18 5 L4 5 Z" fill="{col}" stroke="{edge}" stroke-width="1.3" stroke-linejoin="round"/>'
    out += f'<path d="M-16 0 L-30 0" stroke="{edge}" stroke-width="3.2" stroke-linecap="round"/>'
    out += '</g>'
    svg.add(out)
    if bound:
        a = np.radians(ang)
        ligand(svg, x + 34 * np.cos(a), y + 34 * np.sin(a), col, theme, 0.95, ang)


def draw(theme):
    svg = SVG(theme); lt = theme == 'light'
    rng = np.random.default_rng(12)
    # the tissue around: many cells of both types, with communication edges between neighbours
    bg = poisson(rng, 70, W, H, 62, -20)
    keep = [p for p in bg if not (np.hypot(p[0] - 262, p[1] - 248) < 172 or np.hypot(p[0] - 706, p[1] - 244) < 174 or (390 < p[0] < 580 and 120 < p[1] < 380))]
    bg = np.array(keep)
    types = rng.random(len(bg)) < 0.5
    E = []
    for i in range(len(bg)):
        dd = np.hypot(*(bg - bg[i]).T)
        for j in np.argsort(dd)[1:4]:
            if i < j: E.append((i, j))
    for i, j in E:
        c = LR[rng.integers(0, 4)]
        svg.add(f'<line x1="{f(bg[i][0])}" y1="{f(bg[i][1])}" x2="{f(bg[j][0])}" y2="{f(bg[j][1])}" stroke="{c}" stroke-width="{f(rng.uniform(1, 3.2))}" stroke-opacity="{0.28 if lt else 0.35}" stroke-linecap="round"/>')
    for p, ta in zip(bg, types):
        r = rng.uniform(22, 30)
        P = blob(p[0], p[1], r, rng, 40, 0.07)
        svg.add('<g opacity="0.55">' if lt else '<g opacity="0.6">')
        cell(svg, P, TA if ta else TB, theme, nuc=(p[0] + rng.uniform(-4, 4), p[1] + rng.uniform(-4, 4), r * 0.42), rng=rng)
        svg.add('</g>')
    # the two cells in focus
    S = (262, 248, 146); R = (706, 244, 150)
    Ps = blob(S[0], S[1], S[2], rng, 90, 0.035); Pr = blob(R[0], R[1], R[2], rng, 90, 0.035)
    # ligands in flight between them
    for k in range(12):
        t = rng.uniform(0.08, 0.92)
        x = 436 + t * 96 + rng.uniform(-5, 5); y = 248 + rng.normal(0, 46)
        c = LR[k % 4]
        svg.add(f'<path d="M{f(x - 26)} {f(y + rng.uniform(-4, 4))} Q{f(x - 13)} {f(y + rng.uniform(-6, 6))} {f(x - 6)} {f(y)}" fill="none" stroke="{c}" stroke-width="2" stroke-opacity="0.35" stroke-linecap="round"/>')
        ligand(svg, x, y, c, theme, 0.8, rng.uniform(0, 360))
    cell(svg, Ps, TA, theme, nuc=(S[0] - 22, S[1] + 6, 58), rng=rng, big=True, organelles=True)
    cell(svg, Pr, TB, theme, nuc=(R[0] + 34, R[1] + 4, 56), rng=rng, big=True, organelles=True)
    # vesicles releasing ligands at the sender's right side
    for k, a in enumerate(np.radians([-34, -12, 10, 30])):
        x, y = S[0] + (S[2] - 6) * np.cos(a), S[1] + (S[2] - 6) * np.sin(a)
        svg.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="11" fill="{mix(LR[k], "#FFFFFF", 0.7) if lt else mix(LR[k], BG["dark"], 0.6)}" stroke="{LR[k]}" stroke-width="1.6"/>')
        ligand(svg, x - 1, y, LR[k], theme, 0.55, 20 * k)
    # receptors on the receiver's left side, some with their ligand bound
    angs = [-38, -19, 0, 19, 38]
    for k, a in enumerate(angs):
        ar = np.radians(180 + a)
        x, y = R[0] + R[2] * np.cos(ar), R[1] + R[2] * np.sin(ar)
        receptor(svg, x, y, 180 + a, LR[k % 4], theme, bound=k in (1, 2, 4))
    # the signal inside the receiver: from the bound receptors to the nucleus, where a gene turns on
    nx, ny, nr = R[0] + 34, R[1] + 4, 56
    ink = mix(TB, '#2B2F45', 0.55) if lt else mix(TB, '#FFFFFF', 0.35)
    for k in (1, 2, 4):
        a = np.radians(180 + angs[k]); x0, y0 = R[0] + (R[2] - 30) * np.cos(a), R[1] + (R[2] - 30) * np.sin(a)
        x1, y1 = nx - nr * 0.95 + 4, ny + (y0 - ny) * 0.35
        svg.add(f'<path d="M{f(x0)} {f(y0)} C{f(x0 + 30)} {f(y0)} {f(x1 - 30)} {f(y1)} {f(x1)} {f(y1)}" fill="none" stroke="{ink}" stroke-width="3.2" stroke-dasharray="1 7" stroke-linecap="round"/>')
        svg.add(f'<path d="M{f(x1 - 9)} {f(y1 - 6)} L{f(x1)} {f(y1)} L{f(x1 - 9)} {f(y1 + 6)}" fill="none" stroke="{ink}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>')
    # DNA in the nucleus with the gene switched on, and mRNA leaving it
    xs = np.linspace(nx - 34, nx + 30, 40)
    for ph, w in ((0, 2.2), (np.pi, 2.2)):
        pts = [(x, ny + 10 * np.sin((x - nx) / 7 + ph)) for x in xs]
        svg.add(f'<path d="{smooth_path(pts, False)}" fill="none" stroke="{ink}" stroke-width="{w}"/>')
    for x in xs[::3]:
        svg.add(f'<line x1="{f(x)}" y1="{f(ny + 10 * np.sin((x - nx) / 7))}" x2="{f(x)}" y2="{f(ny + 10 * np.sin((x - nx) / 7 + np.pi))}" stroke="{ink}" stroke-width="1" stroke-opacity="0.6"/>')
    svg.add(f'<rect x="{f(nx - 10)}" y="{f(ny - 15)}" width="22" height="30" rx="5" fill="#F4C542" fill-opacity="0.55" stroke="#C99A12" stroke-width="1.5"/>')
    for k in range(3):
        y0 = ny - 22 - k * 13; x0 = nx + 6 + k * 10
        pts = [(x0 + i * 6, y0 - 5 * np.sin(i * 1.3)) for i in range(7)]
        svg.add(f'<path d="{smooth_path(pts, False)}" fill="none" stroke="#C99A12" stroke-width="2.2" stroke-linecap="round"/>')
    return svg.text()

