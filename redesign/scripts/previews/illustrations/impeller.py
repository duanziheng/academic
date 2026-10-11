"""Impeller: one DLPFC section, before and after imputation, split at a missing spot. Left of it, what is measured:
most values come back as zero, and the spatial walks (neighbour to neighbour) and the similarity walks (to far spots
with a similar profile) reach the missing spot. Right of it, the same section after imputation."""
import numpy as np
from base import *

SEQ = {'light': ['#E9EEF4', '#BFD6E6', '#7FB1D3', '#3F86B8', '#1D5A8A'], 'dark': ['#1A2633', '#24445E', '#2F6C93', '#4C9CC8', '#8FD0EE']}


def ramp(v, theme):
    c = SEQ[theme]; v = np.clip(v, 0, 1) * (len(c) - 1); i = np.minimum(v.astype(int), len(c) - 2); t = v - i
    return [mix(c[a], c[a + 1], b) for a, b in zip(i, t)]


def draw(theme):
    svg = SVG(theme); lt = theme == 'light'
    rng = np.random.default_rng(5)
    ink, bg = INK[theme], BG[theme]
    # a wide strip of cortex: pial surface at the top, layers running across, white matter below
    sec = Section(seed=6, spacing=0.042, T=1.55, C=(0.1, 3.4), R0=4.12, ab=(1.52, 0.8))
    pts, dep = sec.spots, sec.depth(sec.spots)
    # a marker of the middle layers (L3-L4): expression peaks in the band, low elsewhere
    true = np.exp(-((dep - 0.48) / 0.16) ** 2) * 0.95 + 0.05 * rng.random(len(dep))
    obs_nz = rng.random(len(dep)) < 0.24
    S, X, Y = 262, 480, 232
    scr = lambda p: np.c_[X + S * p[:, 0], Y + S * p[:, 1]]
    # the missing spot, in the band at the middle of the section
    cand = np.where((~obs_nz) & (np.abs(dep - 0.48) < 0.05) & (np.abs(pts[:, 0]) < 0.12))[0]
    t = cand[np.argmin(np.abs(pts[cand, 0] - 0.02))]
    xs = pts[t, 0]
    svg.defn(f'<clipPath id="left{theme}"><rect x="-2" y="-1.5" width="{f4(xs + 2)}" height="3"/></clipPath>'
             f'<clipPath id="right{theme}"><rect x="{f4(xs)}" y="-1.5" width="{f4(2 - xs)}" height="3"/></clipPath>'
             '<filter id="tshadow" x="-20%" y="-30%" width="140%" height="160%"><feGaussianBlur stdDeviation="12"/></filter>')
    pd = smooth_path(sec.outline, True, 0.6, f4)
    r = sec.s * 0.4
    zero = '#D6DCE3' if lt else '#2A3542'
    cols = ramp(true * (0.75 + 0.5 * rng.random(len(true))), theme)
    colsR = ramp(true, theme)
    left = ''.join(f'<circle cx="{f4(x)}" cy="{f4(y)}" r="{f4(r if nz else r * 0.58)}" fill="{cc if nz else zero}"/>'
                   for (x, y), nz, cc in zip(pts, obs_nz, cols))
    right = ''.join(f'<circle cx="{f4(x)}" cy="{f4(y)}" r="{f4(r)}" fill="{cc}"/>' for (x, y), cc in zip(pts, colsR))
    tissue, rim = ('#EFE6EB', '#DCCBD5') if lt else ('#1C2430', '#33404F')
    svg.add(f'<g filter="url(#tshadow)" opacity="{0.14 if lt else 0.6}"><g transform="translate({X + 8} {Y + 18}) scale({S})">'
            f'<path d="{pd}" fill="{"#28405A" if lt else "#000000"}"/></g></g>')
    svg.add(f'<g transform="translate({X} {Y}) scale({S})"><path d="{pd}" fill="{tissue}" stroke="{rim}" stroke-width="0.006"/>'
            f'<g clip-path="url(#left{theme})">{left}</g><g clip-path="url(#right{theme})">{right}</g></g>')
    # the split between measured and imputed, through the missing spot
    top = sec.outline[np.argmin(np.abs(sec.outline[:, 0] - xs) + 9 * (sec.outline[:, 1] > 0))]
    botm = sec.outline[np.argmin(np.abs(sec.outline[:, 0] - xs) + 9 * (sec.outline[:, 1] < 0))]
    (x1, y1), (x2, y2) = scr(np.array([top, botm]))
    svg.add(f'<line x1="{f(x1)}" y1="{f(y1 - 16)}" x2="{f(x2)}" y2="{f(y2 + 16)}" stroke="{ink}" stroke-width="1.6" stroke-opacity="0.5"/>')
    # spatial walks on the measured side
    nb = lambda i: np.where((np.hypot(*(pts - pts[i]).T) < sec.s * 1.05) & (np.arange(len(pts)) != i) & (pts[:, 0] < xs + 1e-6))[0]
    walk_c = '#24476B' if lt else '#9CC6EA'
    for ang in (150, 180, 212):        # three walks, heading up-left, left and down-left
        u = np.array([np.cos(np.radians(ang)), -np.sin(np.radians(ang))])
        cur, path = t, [t]
        for _ in range(8):
            n = nb(cur); n = n[~np.isin(n, path)]
            if not len(n):
                break
            score = (pts[n] - pts[cur]) @ u / sec.s + rng.normal(0, 0.3, len(n))
            cur = n[np.argmax(score)]; path.append(cur)
        P = scr(pts[path])
        svg.add(f'<path d="{smooth_path(P, False, 0.5)}" fill="none" stroke="{walk_c}" stroke-width="2.3" stroke-linejoin="round" stroke-linecap="round" opacity="0.92"/>'
                + ''.join(f'<circle cx="{f(x)}" cy="{f(y)}" r="2.6" fill="{walk_c}"/>' for x, y in P[1:]))
    # similarity walks: jumps to far measured spots with a similar profile (the same band)
    far = np.where(obs_nz & (np.abs(dep - 0.48) < 0.07) & (pts[:, 0] < xs - 0.4))[0]
    far = far[np.argsort(pts[far, 0])]
    hop_c = '#7B4FC2' if lt else '#C3A6F2'
    p0 = scr(pts[[t]])[0]
    for h in far[np.linspace(0, len(far) - 1, 4).astype(int)]:
        p1 = scr(pts[[h]])[0]; dx = p1[0] - p0[0]
        cx, cy = (p0[0] + p1[0]) / 2, min(p0[1], p1[1]) - 34 - 0.12 * abs(dx)
        svg.add(f'<path d="M{f(p0[0])} {f(p0[1])} Q{f(cx)} {f(cy)} {f(p1[0])} {f(p1[1])}" fill="none" stroke="{hop_c}" stroke-width="2" stroke-dasharray="5 4" opacity="0.95"/>'
                f'<circle cx="{f(p1[0])}" cy="{f(p1[1])}" r="4.6" fill="none" stroke="{hop_c}" stroke-width="1.8"/>')
    # the missing spot: empty on the measured side, its imputed value on the other
    x0, y0 = p0
    svg.defn(f'<clipPath id="half{theme}"><rect x="{f(x0)}" y="{f(y0 - 20)}" width="20" height="40"/></clipPath>')
    svg.add(f'<circle cx="{f(x0)}" cy="{f(y0)}" r="9" fill="{bg}"/>'
            f'<circle cx="{f(x0)}" cy="{f(y0)}" r="9" fill="{colsR[t]}" clip-path="url(#half{theme})"/>'
            f'<circle cx="{f(x0)}" cy="{f(y0)}" r="9" fill="none" stroke="{ink}" stroke-width="2.4"/>')
    return svg.text()
