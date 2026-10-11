"""MUSE: three adjacent DLPFC sections as on Visium slides, stacked, with spot-to-spot matches between them."""
import numpy as np
from base import *


def slice_group(svg, sec, M, theme, gid, rng, drop=0.0, frame=True):
    a, b, c, d, e, f_ = M
    tr = f'matrix({f(a)} {f(b)} {f(c)} {f(d)} {f(e)} {f(f_)})'
    out = [f'<g transform="{tr}">']
    lt = theme == 'light'
    if frame:   # the capture area: a framed square with fiducial dots, as on a Visium slide
        fr = (-1.26, -1.02, 2.52, 2.04)
        out.append(f'<rect x="{fr[0]}" y="{fr[1]}" width="{fr[2]}" height="{fr[3]}" rx="0.03" '
                   f'fill="{"#FFFFFF" if lt else "#121E2B"}" fill-opacity="{0.86 if lt else 0.9}" stroke="{"#C3CEDA" if lt else "#2C4157"}" stroke-width="0.006"/>')
        fid = []
        for k in range(36):
            t = k / 36
            for (x0, y0, x1, y1) in [(-1.22, -0.98, 1.22, -0.98), (-1.22, 0.98, 1.22, 0.98)]:
                fid.append((x0 + (x1 - x0) * t, y0))
            for (x0, y0, x1, y1) in [(-1.22, -0.98, -1.22, 0.98), (1.22, -0.98, 1.22, 0.98)]:
                if k < 30: fid.append((x0, y0 + (y1 - y0) * k / 30))
        col = '#B9C5D2' if lt else '#34495F'
        out.append(''.join(f'<circle cx="{f(x)}" cy="{f(y)}" r="0.007" fill="{col}"/>' for x, y in fid))
    pd = smooth_path(sec.outline, True, 0.6)
    r = sec.s * 0.47
    out.append(f'<path d="{pd}" fill="{"#EADFE6" if lt else "#1E2530"}" stroke="{"#D5C3CE" if lt else "#33404F"}" stroke-width="0.008"/>')
    keep = rng.random(len(sec.spots)) >= drop
    out.append(''.join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{tone(LAYER[l], theme)}"/>'
                       for (x, y), l, k in zip(sec.spots, sec.layer, keep) if k))
    out.append('</g>')
    svg.add(''.join(out))


def ap(M, p):
    a, b, c, d, e, f_ = M
    return np.c_[a * p[:, 0] + c * p[:, 1] + e, b * p[:, 0] + d * p[:, 1] + f_]


def draw(theme):
    svg = SVG(theme)
    rng = np.random.default_rng(7)
    sec = Section(seed=11, spacing=0.040, T=1.35, C=(1.9, 2.0), R0=3.15)
    # placements: the same tissue on three slides, each a little rotated and shifted (adjacent sections)
    S = 205
    def place(rot_deg, dx, dy):
        th = np.radians(rot_deg); cr, sr = np.cos(th), np.sin(th)
        # rotate in the slide plane, then the oblique view
        A = np.array([[0.95, 0.42], [-0.13, 0.40]]) * S
        R = np.array([[cr, -sr], [sr, cr]])
        Mx = A @ R
        return (Mx[0, 0], Mx[1, 0], Mx[0, 1], Mx[1, 1], 480 + dx, 240 + dy)
    Ms = [place(4, -26, 112), place(-3, 6, 4), place(2, 30, -104)]
    lt = theme == 'light'
    # matched spots between neighbouring sections (what the alignment recovers)
    picks = []
    for l in range(7):
        idx = np.where(sec.layer == l)[0]
        picks += list(rng.choice(idx, size=min(len(idx), 3), replace=False))
    P = sec.spots[np.array(picks)]
    L = sec.layer[np.array(picks)]
    for k in range(3):
        M = Ms[k]
        a, b, c, d, e, f_ = M
        svg.add(f'<g transform="matrix({f(a)} {f(b)} {f(c)} {f(d)} {f(e)} {f(f_ + 4)})">'
                f'<rect x="-1.26" y="-1.02" width="2.52" height="2.04" rx="0.03" fill="{"#B7C3CF" if lt else "#05090E"}"/></g>')
        slice_group(svg, sec, M, theme, f's{k}', np.random.default_rng(20 + k), drop=0.012)
        if k > 0:   # lines from the slide below to this one
            lo, hi = ap(Ms[k - 1], P), ap(M, P)
            svg.add(''.join(f'<line x1="{f(x0)}" y1="{f(y0)}" x2="{f(x1)}" y2="{f(y1)}" stroke="{mix(LAYER[l], INK[theme], 0.25 if lt else 0.0)}" '
                            f'stroke-width="1.8" stroke-opacity="0.9"/>'
                            f'<circle cx="{f(x0)}" cy="{f(y0)}" r="2.2" fill="{mix(LAYER[l], INK[theme], 0.3 if lt else 0.0)}"/>'
                            for (x0, y0), (x1, y1), l in zip(lo, hi, L)))
    # the matched spots on the top slide get a ring
    hi = ap(Ms[2], P)
    svg.add(''.join(f'<circle cx="{f(x)}" cy="{f(y)}" r="3.4" fill="{tone(LAYER[l], theme)}" stroke="{INK[theme]}" stroke-width="1"/>' for (x, y), l in zip(hi, L)))
    return svg.text()

