"""Impeller: imputation on one DLPFC section, measured on the left and imputed on the right. In the measured section most
spots are missing (hollow rings); for one missing spot ('?') the spatial paths (neighbour to neighbour) and the
similarity paths (to far spots with a similar profile) reach the measured spots it is filled from. The imputed section
has every spot filled, and the layer pattern of the gene shows."""
import numpy as np
from base import *

SEQ = {'light': ['#E9EEF4', '#BFD6E6', '#7FB1D3', '#3F86B8', '#1D5A8A'], 'dark': ['#1A2633', '#24445E', '#2F6C93', '#4C9CC8', '#8FD0EE']}


def ramp(v, theme):
    c = SEQ[theme]; v = np.clip(v, 0, 1) * (len(c) - 1); i = np.minimum(v.astype(int), len(c) - 2); t = v - i
    return [mix(c[a], c[a + 1], b) for a, b in zip(i, t)]


def draw(theme):
    svg = SVG(theme); lt = theme == 'light'
    rng = np.random.default_rng(5)
    ink, mute, bg = INK[theme], MUTE[theme], BG[theme]
    sans = 'font-family="Inter, Helvetica, Arial, sans-serif"'
    # a strip of cortex: pial surface at the top, layers running across, white matter below
    sec = Section(seed=6, spacing=0.064, T=1.5, C=(0.1, 3.4), R0=4.12, ab=(1.3, 0.86))
    pts, dep = sec.spots, sec.depth(sec.spots)
    # a marker of the middle layers: expression peaks in the band, low elsewhere
    true = np.exp(-((dep - 0.45) / 0.16) ** 2) * 0.95 + 0.05 * rng.random(len(dep))
    measured = rng.random(len(dep)) < 0.3
    S, Y = 160, 268
    XL, XR = 236, 724
    scrL = lambda p: np.c_[XL + S * p[:, 0], Y + S * p[:, 1]]
    scrR = lambda p: np.c_[XR + S * p[:, 0], Y + S * p[:, 1]]
    pd = smooth_path(sec.outline, True, 0.6, f4)
    r = sec.s * 0.4
    tissue, rim = ('#EFE6EB', '#DCCBD5') if lt else ('#1C2430', '#33404F')
    hollow = '#B9C3CE' if lt else '#43546A'
    svg.defn('<filter id="tshadow" x="-20%" y="-30%" width="140%" height="160%"><feGaussianBlur stdDeviation="10"/></filter>')
    for X in (XL, XR):
        svg.add(f'<g filter="url(#tshadow)" opacity="{0.14 if lt else 0.6}"><g transform="translate({X + 6} {Y + 14}) scale({S})">'
                f'<path d="{pd}" fill="{"#28405A" if lt else "#000000"}"/></g></g>')
    # measured: a few values, most spots missing
    cols = ramp(true * (0.8 + 0.4 * rng.random(len(true))), theme)
    left = ''.join(f'<circle cx="{f4(x)}" cy="{f4(y)}" r="{f4(r)}" fill="{cc}"/>' if m else
                   f'<circle cx="{f4(x)}" cy="{f4(y)}" r="{f4(r * 0.78)}" fill="none" stroke="{hollow}" stroke-width="{f4(0.0072)}"/>'
                   for (x, y), m, cc in zip(pts, measured, cols))
    svg.add(f'<g transform="translate({XL} {Y}) scale({S})"><path d="{pd}" fill="{tissue}" stroke="{rim}" stroke-width="0.008"/>{left}</g>')
    # imputed: every spot filled
    colsR = ramp(true, theme)
    right = ''.join(f'<circle cx="{f4(x)}" cy="{f4(y)}" r="{f4(r)}" fill="{cc}"/>' for (x, y), cc in zip(pts, colsR))
    svg.add(f'<g transform="translate({XR} {Y}) scale({S})"><path d="{pd}" fill="{tissue}" stroke="{rim}" stroke-width="0.008"/>{right}</g>')
    # the missing spot to fill: in the band, right of centre so its paths run left across the section
    cand = np.where((~measured) & (np.abs(dep - 0.45) < 0.05) & (np.abs(pts[:, 0] - 0.42) < 0.12))[0]
    t = cand[np.argmin(np.abs(pts[cand, 0] - 0.42))]
    p0 = scrL(pts[[t]])[0]
    # spatial paths: neighbour to neighbour until they reach measured spots
    near = lambda i: np.where((np.hypot(*(pts - pts[i]).T) < sec.s * 1.05) & (np.arange(len(pts)) != i))[0]
    walk_c = '#24476B' if lt else '#9CC6EA'
    for ang in (125, 200, 255):
        u = np.array([np.cos(np.radians(ang)), -np.sin(np.radians(ang))])
        cur, path = t, [t]
        for _ in range(5):
            n = near(cur); n = n[~np.isin(n, path)]
            score = (pts[n] - pts[cur]) @ u / sec.s + rng.normal(0, 0.25, len(n)) + 0.6 * measured[n]
            cur = n[np.argmax(score)]; path.append(cur)
            if measured[cur] and len(path) > 2:
                break
        P = scrL(pts[path])
        svg.add(f'<path d="{smooth_path(P, False, 0.5)}" fill="none" stroke="{walk_c}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>'
                f'<circle cx="{f(P[-1][0])}" cy="{f(P[-1][1])}" r="{f(S * r + 1.6)}" fill="none" stroke="{walk_c}" stroke-width="1.8"/>')
    # similarity paths: jumps to far measured spots with a similar profile (the same band)
    far = np.where(measured & (np.abs(dep - 0.45) < 0.06) & (pts[:, 0] < pts[t, 0] - 0.55))[0]
    far = far[np.argsort(pts[far, 0])]
    hop_c = '#7B4FC2' if lt else '#C3A6F2'
    for h in far[np.linspace(0, len(far) - 1, 3).astype(int)]:
        p1 = scrL(pts[[h]])[0]
        cx, cy = (p0[0] + p1[0]) / 2, min(p0[1], p1[1]) - 30 - 0.18 * abs(p1[0] - p0[0])
        svg.add(f'<path d="M{f(p0[0])} {f(p0[1])} Q{f(cx)} {f(cy)} {f(p1[0])} {f(p1[1])}" fill="none" stroke="{hop_c}" stroke-width="2" stroke-dasharray="5 4"/>'
                f'<circle cx="{f(p1[0])}" cy="{f(p1[1])}" r="{f(S * r + 1.8)}" fill="none" stroke="{hop_c}" stroke-width="1.8"/>')
    # the '?' spot, and the same spot filled on the imputed side
    svg.add(f'<circle cx="{f(p0[0])}" cy="{f(p0[1])}" r="11" fill="{bg}" stroke="{ink}" stroke-width="2.4"/>'
            f'<text x="{f(p0[0])}" y="{f(p0[1] + 5)}" text-anchor="middle" {sans} font-size="14" font-weight="700" fill="{ink}">?</text>')
    q = scrR(pts[[t]])[0]
    svg.add(f'<circle cx="{f(q[0])}" cy="{f(q[1])}" r="11" fill="{colsR[t]}" stroke="{ink}" stroke-width="2.4"/>')
    # labels and the arrow between
    svg.add(f'<text x="{XL}" y="94" text-anchor="middle" {sans} font-size="25" font-weight="600" fill="{ink}">Measured</text>'
            f'<text x="{XR}" y="94" text-anchor="middle" {sans} font-size="25" font-weight="600" fill="{ink}">Imputed</text>')
    svg.add(f'<path d="M458 {Y} H502" stroke="{mute}" stroke-width="3.2" stroke-linecap="round"/>'
            f'<path d="M491 {Y - 11} L504 {Y} L491 {Y + 11}" fill="none" stroke="{mute}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg.text()
