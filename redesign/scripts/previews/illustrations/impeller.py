"""Impeller: one DLPFC section with sparse measured expression, the paths that reach a missing spot,
and the same section after imputation."""
import numpy as np
from base import *
from muse import ap

SEQ = {'light': ['#E9EEF4', '#BFD6E6', '#7FB1D3', '#3F86B8', '#1D5A8A'], 'dark': ['#1A2633', '#24445E', '#2F6C93', '#4C9CC8', '#8FD0EE']}


def ramp(v, theme):
    c = SEQ[theme]; v = np.clip(v, 0, 1) * (len(c) - 1); i = np.minimum(v.astype(int), len(c) - 2); t = v - i
    return [mix(c[a], c[a + 1], b) for a, b in zip(i, t)]


def draw(theme):
    svg = SVG(theme); lt = theme == 'light'
    rng = np.random.default_rng(5)
    sec = Section(seed=4, spacing=0.05, T=1.35, C=(1.9, 2.0), R0=3.15)
    dep = sec.depth(sec.spots)
    # a marker of the middle layers (L3-L4): expression peaks in the band, low elsewhere
    true = np.exp(-((dep - 0.50) / 0.17) ** 2) * 0.95 + 0.05 * rng.random(len(dep))
    obs_nz = rng.random(len(dep)) < 0.24
    S = 168
    ML = (S, 0, 0, S, 236, 252)
    MR = (S, 0, 0, S, 724, 252)
    # slides
    for M in (ML, MR):
        a, b, c, d, e, f_ = M
        svg.add(f'<g transform="matrix({f(a)} 0 0 {f(d)} {f(e)} {f(f_ + 3)})"><rect x="-1.26" y="-1.02" width="2.52" height="2.04" rx="0.03" fill="{"#C3CDD8" if lt else "#05090E"}"/></g>')
    # left: what is measured — most values come back as zero
    gl = f'<g transform="matrix({S} 0 0 {S} 236 252)">'
    frame = (f'<rect x="-1.26" y="-1.02" width="2.52" height="2.04" rx="0.03" fill="{"#FFFFFF" if lt else "#121E2B"}" stroke="{"#C3CEDA" if lt else "#2C4157"}" stroke-width="0.006"/>')
    pd = smooth_path(sec.outline, True, 0.6)
    tissue = f'<path d="{pd}" fill="{"#EADFE6" if lt else "#1E2530"}" stroke="{"#D5C3CE" if lt else "#33404F"}" stroke-width="0.008"/>'
    r = sec.s * 0.44
    zero = '#D9DEE5' if lt else '#2A3542'
    cols = ramp(true * (0.75 + 0.5 * rng.random(len(true))), theme)
    spots_l = ''.join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r if nz else r * 0.62)}" fill="{c if nz else zero}"/>'
                      for (x, y), nz, c in zip(sec.spots, obs_nz, cols))
    svg.add(gl + frame + tissue + spots_l + '</g>')
    # the target: a missing spot in the band
    cand = np.where((~obs_nz) & (np.abs(dep - 0.5) < 0.05) & (np.abs(sec.spots[:, 0]) < 0.35))[0]
    t = cand[np.argmin(np.abs(sec.spots[cand, 1] - 0.05))]
    pts = sec.spots
    def scr(i, M=ML): return ap(M, pts[[i]])[0]
    # spatial walks: neighbour to neighbour
    nb = lambda i: np.where((np.hypot(*(pts - pts[i]).T) < sec.s * 1.05) & (np.arange(len(pts)) != i))[0]
    walks = []
    for w in range(4):
        cur, path = t, [t]
        for _ in range(6):
            n = nb(cur); cur = rng.choice(n); path.append(cur)
        walks.append(path)
    for path in walks:
        P = ap(ML, pts[path])
        svg.add(f'<path d="{path_d(P, False)}" fill="none" stroke="{"#24476B" if lt else "#9CC6EA"}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round" opacity="0.9"/>')
        svg.add(''.join(f'<circle cx="{f(x)}" cy="{f(y)}" r="2.6" fill="{"#24476B" if lt else "#9CC6EA"}"/>' for x, y in P[1:]))
    # similarity walks: jumps to far spots with a similar profile (same band)
    far = np.where(obs_nz & (np.abs(dep - 0.5) < 0.08) & (np.hypot(*(pts - pts[t]).T) > 0.45))[0]
    hops = rng.choice(far, 5, replace=False)
    p0 = scr(t)
    for h in hops:
        p1 = scr(h); mx, my = (p0 + p1) / 2; dx, dy = p1 - p0
        cx, cy = mx - dy * 0.28, my + dx * 0.28 - 22
        svg.add(f'<path d="M{f(p0[0])} {f(p0[1])} Q{f(cx)} {f(cy)} {f(p1[0])} {f(p1[1])}" fill="none" stroke="{"#7B4FC2" if lt else "#C3A6F2"}" stroke-width="2" stroke-dasharray="5 4" opacity="0.95"/>'
                f'<circle cx="{f(p1[0])}" cy="{f(p1[1])}" r="4.2" fill="none" stroke="{"#7B4FC2" if lt else "#C3A6F2"}" stroke-width="1.8"/>')
    svg.add(f'<circle cx="{f(p0[0])}" cy="{f(p0[1])}" r="7.5" fill="{BG[theme]}" stroke="{INK[theme]}" stroke-width="2.4"/>'
            f'<circle cx="{f(p0[0])}" cy="{f(p0[1])}" r="2.4" fill="{INK[theme]}"/>')
    # right: the imputed section
    colsR = ramp(true, theme)
    spots_r = ''.join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{c}"/>' for (x, y), c in zip(sec.spots, colsR))
    svg.add(f'<g transform="matrix({S} 0 0 {S} 724 252)">' + frame + tissue + spots_r + '</g>')
    q = scr(t, MR)
    svg.add(f'<circle cx="{f(q[0])}" cy="{f(q[1])}" r="7.5" fill="{colsR[t]}" stroke="{INK[theme]}" stroke-width="2.4"/>')
    # arrow between the two
    ac = INK[theme]
    svg.add(f'<path d="M455 252 H500" stroke="{ac}" stroke-width="3" stroke-linecap="round"/><path d="M492 242 L505 252 L492 262" fill="none" stroke="{ac}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg.text()

