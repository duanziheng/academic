"""TargetSage (NeurIPS 2026): finding therapeutic targets genome-wide. The human karyotype with the 19,032
protein-coding genes it searches, known targets marked; a magnifier picks out one predicted target gene, and its
protein is drawn as a ribbon model with a small-molecule drug docked in its pocket."""
import numpy as np
from base import *

# GRCh38 chromosome lengths and centromere positions (Mb)
CHR = [('1', 248.9, 123.4), ('2', 242.2, 93.9), ('3', 198.3, 90.9), ('4', 190.2, 50.0), ('5', 181.5, 48.8),
       ('6', 170.8, 59.8), ('7', 159.3, 60.1), ('8', 145.1, 45.2), ('9', 138.4, 43.0), ('10', 133.8, 39.8),
       ('11', 135.1, 53.4), ('12', 133.3, 35.5), ('13', 114.4, 17.7), ('14', 107.0, 17.2), ('15', 102.0, 19.0),
       ('16', 90.3, 36.8), ('17', 83.3, 25.1), ('18', 80.4, 18.5), ('19', 58.6, 26.2), ('20', 64.4, 28.1),
       ('21', 46.7, 12.0), ('22', 50.8, 15.0), ('X', 156.0, 60.6), ('Y', 57.2, 10.4)]
GOLD = '#E3A21A'
AIM = '#E4553F'
SPECTRUM = ['#3E6FD6', '#2AA3D6', '#27B08A', '#93C645', '#EDB532', '#EE803A', '#DE4F4C']


def spectrum(t):
    t = min(max(t, 0), 1) * (len(SPECTRUM) - 1); i = min(int(t), len(SPECTRUM) - 2)
    return mix(SPECTRUM[i], SPECTRUM[i + 1], t - i)


# ---------------------------------------------------------------- karyotype
KX, KP, KW, KY, KS = 44, 18.2, 11.5, 188, 0.95          # first x, pitch, width, centromere line, px per Mb


def karyotype(theme, rng):
    lt = theme == 'light'
    base = '#E9EEF3' if lt else '#203044'
    shades = (['#C5CFD9', '#9AA8B6', '#6F7F90', '#4D5B6B'] if lt else ['#33475D', '#4A6079', '#647C96', '#8299B2'])
    acen = '#E7A3A0' if lt else '#7D4A55'
    out, clips = [], []
    for i, (name, L, cen) in enumerate(CHR):
        x = KX + i * KP
        top, bot = KY - cen * KS, KY + (L - cen) * KS
        r = KW / 2
        # outline: two rounded arms pinched at the centromere
        d = (f'M{f(x)} {f(top + r)} A{f(r)} {f(r)} 0 0 1 {f(x + KW)} {f(top + r)} L{f(x + KW)} {f(KY - 3)} '
             f'L{f(x + KW - 2.6)} {f(KY)} L{f(x + KW)} {f(KY + 3)} L{f(x + KW)} {f(bot - r)} A{f(r)} {f(r)} 0 0 1 {f(x)} {f(bot - r)} '
             f'L{f(x)} {f(KY + 3)} L{f(x + 2.6)} {f(KY)} L{f(x)} {f(KY - 3)} Z')
        cid = f'chr{theme}{i}'
        clips.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        g = [f'<path d="{d}" fill="{base}"/>', f'<g clip-path="url(#{cid})">']
        y = top; dark = False
        while y < bot:
            h = rng.uniform(2.2, 7.5)
            if dark:
                g.append(f'<rect x="{f(x)}" y="{f(y)}" width="{KW}" height="{f(h)}" fill="{shades[rng.choice(4, p=[0.3, 0.3, 0.25, 0.15])]}"/>')
            y += h; dark = not dark
        g.append(f'<rect x="{f(x)}" y="{f(KY - 3)}" width="{KW}" height="6" fill="{acen}"/></g>')
        g.append(f'<path d="{d}" fill="none" stroke="{shades[1]}" stroke-width="0.8" stroke-opacity="0.8"/>')
        out.append(''.join(g))
    return ''.join(clips), ''.join(out)


def chr_xy(i, mb):
    return KX + i * KP + KW / 2, KY - CHR[i][2] * KS + mb * KS


# ---------------------------------------------------------------- protein
def frame(u):
    a = np.array([1.0, 0, 0]) if abs(u[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = np.cross(u, a); e1 /= np.linalg.norm(e1); e2 = np.cross(u, e1)
    return e1, e2


def helix(A, B, phase=0.0):
    A, B = np.array(A, float), np.array(B, float); L = np.linalg.norm(B - A); u = (B - A) / L
    e1, e2 = frame(u)
    t = np.linspace(0, L, int(L * 9))
    th = phase + 2 * np.pi * t / 5.4
    radial = np.cos(th)[:, None] * e1 + np.sin(th)[:, None] * e2
    P = A + t[:, None] * u + 2.3 * radial
    T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]
    Wv = np.cross(radial, T); Wv /= np.linalg.norm(Wv, axis=1)[:, None]
    hw = np.full(len(t), 0.95)
    ramp = np.clip(np.minimum(t, L - t) / 1.6, 0, 1); hw = 0.3 + (hw - 0.3) * ramp
    return P, Wv, hw


def strand(A, B, normal=(0, 0, 1)):
    A, B = np.array(A, float), np.array(B, float); L = np.linalg.norm(B - A); d = (B - A) / L
    t = np.linspace(0, L, int(L * 5))
    P = A + t[:, None] * d
    N = np.array(normal, float); w0 = np.cross(N, d); w0 /= np.linalg.norm(w0)
    tw = -0.28 + 0.56 * t / L
    Wv = np.cos(tw)[:, None] * w0 + np.sin(tw)[:, None] * N
    head = L - 3.2
    hw = np.where(t < head, 1.55, 2.5 * (L - t) / 3.2)
    hw[(t >= head) & (t < head + 0.25)] = 2.5
    return P, Wv, hw


def catmull(pts, n=10):
    P = np.asarray(pts, float); out = []
    P = np.vstack([P[0] - (P[1] - P[0]), P, P[-1] + (P[-1] - P[-2])])
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for s in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    out.append(P[-2]); return np.array(out)


def rotation(rx, ry):
    cx, sx, cy, sy = np.cos(rx), np.sin(rx), np.cos(ry), np.sin(ry)
    return np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]) @ np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])


def protein(theme, cx, cy, s, rng):
    lt = theme == 'light'; bg = BG[theme]
    R = rotation(np.radians(14), np.radians(-24))
    sse = [('H', (-12, -19.5, 2), (10, -21, -3)),
           ('E', (-7.2, -12, -11), (-7.2, 10, -11)), ('E', (-2.4, 11, -12), (-2.4, -11, -12)),
           ('E', (2.4, -11, -12), (2.4, 11, -12)), ('E', (7.2, 11, -11), (7.2, -10, -11)),
           ('H', (15.5, -12, -3), (17, 12.5, 1)), ('H', (12, 19.5, 3), (-11, 18.5, 2)),
           ('H', (-17, 10, -1), (-15, -12.5, -4))]
    pieces = []
    for kind, A, B in sse:
        pieces.append((kind,) + (helix(A, B, rng.uniform(0, 6.28)) if kind == 'H' else strand(A, B)))
    # loops between consecutive elements, bowed outward from the core
    chain = []
    for k, pc in enumerate(pieces):
        chain.append(pc)
        if k + 1 < len(pieces):
            a, b = pc[1][-1], pieces[k + 1][1][0]
            m = (a + b) / 2; out = m - np.array([0, 0, -4]); out = m + 2.8 * out / (np.linalg.norm(out) + 1e-6)
            chain.append(('L', catmull([a, out, b], 12), None, None))
    total = sum(len(p[1]) for p in chain); idx = 0
    items = []
    light_dir = np.array([-0.4, -0.55, 0.73]); light_dir /= np.linalg.norm(light_dir)
    allz = np.vstack([p[1] for p in chain]) @ R.T
    zmin, zmax = allz[:, 2].min(), allz[:, 2].max()

    def scr(p):
        return cx + s * p[0], cy + s * p[1]

    def fade(c, z):
        k = (zmax - z) / (zmax - zmin)
        return mix(c, bg, 0.34 * k)
    for kind, P, Wv, hw in chain:
        Pr = P @ R.T
        if kind == 'L':
            for j in range(len(Pr) - 1):
                z = (Pr[j, 2] + Pr[j + 1, 2]) / 2
                c = fade(mix(spectrum((idx + j) / total), '#8A97A6', 0.35), z)
                (x1, y1), (x2, y2) = scr(Pr[j]), scr(Pr[j + 1])
                items.append((z, f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{c}" stroke-width="{f(0.5 * s)}" stroke-linecap="round"/>'))
            idx += len(Pr); continue
        Wr = Wv @ R.T
        for j in range(len(Pr) - 1):
            q = [Pr[j] - Wr[j] * hw[j], Pr[j] + Wr[j] * hw[j], Pr[j + 1] + Wr[j + 1] * hw[j + 1], Pr[j + 1] - Wr[j + 1] * hw[j + 1]]
            n = np.cross(q[2] - q[0], q[1] - q[3]); nn = np.linalg.norm(n)
            n = n / nn if nn > 1e-9 else np.array([0, 0, 1.0])
            lam = abs(n @ light_dir); face = 0.6 + 0.4 * lam
            base = spectrum((idx + j) / total)
            c = mix('#000000', base, face) if face < 1 else base
            if n[2] < 0:
                c = mix(c, '#FFFFFF' if lt else '#000000', 0.12)
            z = np.mean([v[2] for v in q])
            c = fade(c, z)
            pts = ' '.join(f'{f(cx + s * v[0])},{f(cy + s * v[1])}' for v in q)
            items.append((z, f'<polygon points="{pts}" fill="{c}" stroke="{c}" stroke-width="0.7" stroke-linejoin="round"/>'))
        idx += len(Pr)
    # the drug: a small fused-ring molecule with an amide side chain, in the pocket over the sheet
    ang = np.radians(np.arange(6) * 60 + 30)
    ringA = np.c_[1.4 * np.cos(ang), 1.4 * np.sin(ang)]
    ringB = ringA + [2.42, 0]
    atoms = [(p, 'C') for p in ringA] + [(ringB[k], 'N' if k == 4 else 'C') for k in (1, 2, 3, 4)]
    bonds = [(k, (k + 1) % 6) for k in range(6)] + [(0, 6), (6, 7), (7, 8), (8, 9), (9, 5)]
    c_am = ringB[2] + [1.3, -0.75]; o_am = c_am + [0, -1.25]; n_am = c_am + [1.3, 0.75]; me = n_am + [1.3, -0.75]
    f_at = ringA[3] + [-1.25, -0.72]; oh = ringA[1] + [0, 1.4]
    for p, el in ((c_am, 'C'), (o_am, 'O'), (n_am, 'N'), (me, 'C'), (f_at, 'F'), (oh, 'O')):
        atoms.append((p, el))
    bonds += [(8, 10), (10, 11), (10, 12), (12, 13), (3, 14), (1, 15)]
    double = {(10, 11), (0, 1), (2, 3), (4, 5), (6, 7)}
    M = np.array([a[0] for a in atoms]); M = 1.25 * (M - M.mean(0))
    D3 = np.c_[M, np.zeros(len(M))] @ rotation(np.radians(-28), np.radians(18)).T + [0.4, 0.4, 5.0]
    Dr = D3 @ R.T
    elc = {'C': GOLD, 'N': '#2F63DC', 'O': '#E2453F', 'F': '#2FB566'}
    dc = np.mean(Dr, 0)
    gx, gy = scr(dc)
    items.append((dc[2] - 3, f'<circle cx="{f(gx)}" cy="{f(gy)}" r="{f(7.2 * s)}" fill="{GOLD}" fill-opacity="{0.2 if lt else 0.16}"/>'))
    bond_c = '#7F8B98' if lt else '#9AA7B5'
    for a, b in bonds:
        (x1, y1), (x2, y2) = scr(Dr[a]), scr(Dr[b]); z = (Dr[a, 2] + Dr[b, 2]) / 2 - 0.05
        if (a, b) in double:
            dx, dy = y2 - y1, x1 - x2; nrm = np.hypot(dx, dy); dx, dy = 1.5 * dx / nrm, 1.5 * dy / nrm
            items.append((z, f'<line x1="{f(x1 + dx)}" y1="{f(y1 + dy)}" x2="{f(x2 + dx)}" y2="{f(y2 + dy)}" stroke="{bond_c}" stroke-width="1.8"/>'
                             f'<line x1="{f(x1 - dx)}" y1="{f(y1 - dy)}" x2="{f(x2 - dx)}" y2="{f(y2 - dy)}" stroke="{bond_c}" stroke-width="1.8"/>'))
        else:
            items.append((z, f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{bond_c}" stroke-width="3.4"/>'))
    for (p, el), q in zip(atoms, Dr):
        x, y = scr(q); r = (0.74 if el in 'CN' else 0.8) * s
        c = elc[el]
        items.append((q[2], f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{c}"/>'
                            f'<circle cx="{f(x - 0.28 * r)}" cy="{f(y - 0.3 * r)}" r="{f(0.38 * r)}" fill="#FFFFFF" fill-opacity="0.38"/>'))
    items.sort(key=lambda t: t[0])
    return ''.join(s_ for _, s_ in items), (gx, gy)


def reticle(x, y, r, color, w=2.4, tick=9):
    o = f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="none" stroke="{color}" stroke-width="{w}"/>'
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        o += (f'<line x1="{f(x + dx * (r - tick * 0.45))}" y1="{f(y + dy * (r - tick * 0.45))}" '
              f'x2="{f(x + dx * (r + tick))}" y2="{f(y + dy * (r + tick))}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')
    return o


def draw(theme):
    svg = SVG(theme); lt = theme == 'light'
    rng = np.random.default_rng(8)
    ink, mute, bg = INK[theme], MUTE[theme], BG[theme]
    clips, kar = karyotype(theme, rng)
    svg.defn(clips)
    # known targets on the chromosomes (filled) and new predictions among the unlabeled genes (rings)
    marks = []
    for i, (name, L, cen) in enumerate(CHR):
        for _ in range(rng.integers(0, 3) if i < 23 else 0):
            mb = rng.uniform(6, L - 6); x, y = chr_xy(i, mb)
            marks.append((i, mb, rng.random() < 0.3))
    target = (22, 30.0)                                      # the gene the magnifier finds (on chrX)
    mk = []
    for i, mb, new in marks:
        x, y = chr_xy(i, mb)
        if abs(i - target[0]) <= 1 and abs(mb - target[1]) < 14:
            continue
        x2 = x + KW / 2 + 3.2
        mk.append(f'<line x1="{f(x + KW / 2 - 1)}" y1="{f(y)}" x2="{f(x2)}" y2="{f(y)}" stroke="{GOLD}" stroke-width="1.4"/>'
                  + (f'<circle cx="{f(x2 + 2.4)}" cy="{f(y)}" r="2.6" fill="{bg}" stroke="{GOLD}" stroke-width="1.5"/>' if new else
                     f'<circle cx="{f(x2 + 2.4)}" cy="{f(y)}" r="3" fill="{GOLD}"/>'))
    tx, ty = chr_xy(*target)
    tband = f'<rect x="{f(tx - KW / 2 - 0.5)}" y="{f(ty - 2.2)}" width="{KW + 1}" height="4.4" fill="{GOLD}"/>'
    svg.defn(f'<g id="kar{theme}">{kar}{"".join(mk)}{tband}</g>')
    svg.add(f'<use href="#kar{theme}"/>')
    svg.add(f'<text x="44" y="398" font-size="34" font-weight="700" fill="{ink}">19,032<tspan dx="9" font-size="19" font-weight="400" fill="{mute}">protein-coding genes</tspan></text>')
    # the magnifier over the target gene
    lx, ly, lr, mag = tx, ty, 48, 2.3
    svg.defn(f'<clipPath id="lens{theme}"><circle cx="{f(lx)}" cy="{f(ly)}" r="{lr}"/></clipPath>')
    hx1, hy1 = lx + lr * 0.72, ly + lr * 0.72
    svg.add(f'<line x1="{f(hx1 + 3)}" y1="{f(hy1 + 3)}" x2="{f(hx1 + 40)}" y2="{f(hy1 + 40)}" stroke="{ink}" stroke-width="11" stroke-linecap="round"/>')
    svg.add(f'<circle cx="{f(lx)}" cy="{f(ly)}" r="{lr}" fill="{bg}"/>'
            f'<g clip-path="url(#lens{theme})"><use href="#kar{theme}" transform="translate({f(lx)} {f(ly)}) scale({mag}) translate({f(-lx)} {f(-ly)})"/></g>'
            f'<circle cx="{f(lx)}" cy="{f(ly)}" r="{lr}" fill="#FFFFFF" fill-opacity="{0.10 if lt else 0.04}"/>')
    svg.add(reticle(lx, ly, 15, AIM, 2.2, 8))
    svg.add(f'<circle cx="{f(lx)}" cy="{f(ly)}" r="{lr}" fill="none" stroke="{ink}" stroke-width="5"/>')
    # the target's protein with a drug in its pocket
    prot, (gx, gy) = protein(theme, 776, 240, 6.0, rng)
    svg.add(prot)
    svg.add(reticle(gx, gy, 60, AIM, 2.6, 12))
    # from the gene to its protein
    sx_, sy_ = lx + lr + 6, ly - 10
    svg.add(f'<path d="M{f(sx_)} {f(sy_)} C{f(sx_ + 60)} {f(sy_ - 40)} {f(gx - 150)} {f(gy - 120)} {f(gx - 64)} {f(gy - 46)}" fill="none" '
            f'stroke="{mute}" stroke-width="2" stroke-dasharray="5 5"/>'
            f'<path d="M{f(gx - 64)} {f(gy - 46)} l-11 -1 M{f(gx - 64)} {f(gy - 46)} l-3 -10" stroke="{mute}" stroke-width="2.2" stroke-linecap="round"/>')
    return svg.text()

