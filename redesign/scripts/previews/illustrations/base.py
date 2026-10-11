"""Shared helpers for the Selected-work illustrations (960x480 SVG, light and dark)."""
import numpy as np
from matplotlib.path import Path as MPath

W, H = 960, 480
BG = {'light': '#F6F8FA', 'dark': '#0B141E'}
INK = {'light': '#22313F', 'dark': '#E3EAF1'}
MUTE = {'light': '#7C8B99', 'dark': '#7F92A6'}
LINE = {'light': '#CBD5DF', 'dark': '#2A3B4D'}
# cortical layers L1..L6, white matter (the walkthroughs' palette)
LAYER = ['#E79BBE', '#7FA7D6', '#8DC4AB', '#B9A5DB', '#E6CD80', '#EBA27A', '#8F9AA8']
LR = ['#7B68D9', '#2E9C7A', '#D29A12', '#D14F7C']
CT = {'EXN': '#D9776B', 'IN': '#5FA36B', 'OLG': '#5E8DBF', 'OPC': '#8E7CC3', 'END': '#C9A227', 'AST': '#4FA3A5', 'MG': '#B5651D'}


def hx(c):
    c = c.lstrip('#'); return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], float)


def to_hex(v):
    v = np.clip(np.round(v), 0, 255).astype(int); return '#%02x%02x%02x' % tuple(v)


def mix(a, b, t):
    return to_hex(hx(a) * (1 - t) + hx(b) * t)


def tone(c, theme, dark_mix=0.12, light=0.0):
    """data colours: unchanged in light; in dark a touch deeper so they do not glare"""
    if theme == 'light':
        return mix(c, '#ffffff', light) if light else c
    return mix(c, BG['dark'], dark_mix)


def f(v):
    return ('%.2f' % v).rstrip('0').rstrip('.')


def f4(v):
    """for coordinates inside a scaled group (section units), where two decimals would be pixels off"""
    return ('%.4f' % v).rstrip('0').rstrip('.')


class SVG:
    def __init__(self, theme, w=W, h=H):
        self.theme, self.w, self.h = theme, w, h
        self.defs, self.body = [], []

    def add(self, s):
        self.body.append(s); return self

    def defn(self, s):
        self.defs.append(s); return self

    def text(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                f'font-family="Inter, Helvetica, Arial, sans-serif"><defs>{"".join(self.defs)}</defs>'
                f'<rect width="{self.w}" height="{self.h}" fill="{BG[self.theme]}"/>{"".join(self.body)}</svg>')


def smooth_noise(rng, n=6, amp=1.0):
    """a smooth 2D noise field from a few random plane waves: returns f(x, y)"""
    ks = rng.normal(0, 1, (n, 2)) * rng.uniform(1.5, 4.5, (n, 1))
    ph = rng.uniform(0, 2 * np.pi, n)
    w = rng.uniform(0.5, 1, n); w /= w.sum()
    return lambda x, y: amp * sum(wi * np.sin(k[0] * x + k[1] * y + p) for wi, k, p in zip(w, ks, ph))


def periodic_noise(rng, t, n=5, amp=0.05):
    return amp * sum(rng.uniform(0.3, 1) * np.sin(k * t + rng.uniform(0, 2 * np.pi)) / k ** 0.6 for k in range(2, 2 + n))


def path_d(pts, close=True, fmt=f):
    s = 'M' + ' L'.join(f'{fmt(x)} {fmt(y)}' for x, y in pts)
    return s + (' Z' if close else '')


def smooth_path(pts, close=True, tension=0.5, fmt=f):
    """Catmull-Rom through the points as cubic Beziers"""
    P = np.asarray(pts, float); n = len(P)
    if close:
        idx = lambda i: P[i % n]
        rng_ = range(n)
    else:
        idx = lambda i: P[min(max(i, 0), n - 1)]
        rng_ = range(n - 1)
    d = f'M{fmt(P[0][0])} {fmt(P[0][1])}'
    for i in rng_:
        p0, p1, p2, p3 = idx(i - 1), idx(i), idx(i + 1), idx(i + 2)
        c1 = p1 + (p2 - p0) * tension / 3; c2 = p2 - (p3 - p1) * tension / 3
        d += f' C{fmt(c1[0])} {fmt(c1[1])} {fmt(c2[0])} {fmt(c2[1])} {fmt(p2[0])} {fmt(p2[1])}'
    return d + (' Z' if close else '')


class Section:
    """A DLPFC section like a 10x Visium slide: an irregular tissue piece whose top edge is the pial surface,
    cortical layers L1..L6 as curved bands parallel to it, white matter below; spots on a hex grid."""
    FR = np.array([0.10, 0.09, 0.27, 0.08, 0.20, 0.18]); FR = FR / FR.sum()

    def __init__(self, seed=1, spacing=0.045, wobble=1.0, T=1.08, C=(0.12, 3.25), R0=3.98, ab=(1.12, 0.86)):
        rng = np.random.default_rng(seed)
        self.C, self.R0, self.T = np.array(C), R0, T
        t = np.linspace(0, 2 * np.pi, 220, endpoint=False)
        n = 3.0; a, b = ab
        rr = 1 + periodic_noise(rng, t, 6, 0.07 * wobble)
        x = a * np.sign(np.cos(t)) * np.abs(np.cos(t)) ** (2 / n) * rr
        y = b * np.sign(np.sin(t)) * np.abs(np.sin(t)) ** (2 / n) * rr + 0.02
        P = np.c_[x, y]
        # clip to the pial surface: tissue ends at the brain surface, which is gently wavy
        d = np.hypot(P[:, 0] - C[0], P[:, 1] - C[1])
        ang = np.arctan2(P[:, 1] - C[1], P[:, 0] - C[0])
        ph = rng.uniform(0, 2 * np.pi)
        Rw = R0 * (1 + 0.012 * np.sin(9 * ang + ph))
        out = d > Rw
        P[out] = np.c_[C[0] + (P[out, 0] - C[0]) * Rw[out] / d[out], C[1] + (P[out, 1] - C[1]) * Rw[out] / d[out]]
        self.outline = P
        self.mpath = MPath(P)
        self.noise = smooth_noise(rng, 7, 0.022 * wobble)
        # hex grid
        s = spacing; pts = []
        ey, ex = max(1.0, b + 0.1), max(1.3, a + 0.15)
        ys = np.arange(-ey, ey, s * np.sqrt(3) / 2)
        for j, yy in enumerate(ys):
            xs = np.arange(-ex, ex, s) + (s / 2 if j % 2 else 0)
            pts += [(xx, yy) for xx in xs]
        pts = np.array(pts)
        inside = self.mpath.contains_points(pts, radius=-s * 0.6)
        self.spots = pts[inside]
        self.layer = self.layer_of(self.spots, rng)
        self.s = s

    def depth(self, P):
        """cortical depth from the pial surface, 0 at the surface, 1 at the white-matter border"""
        d = np.hypot(P[:, 0] - self.C[0], P[:, 1] - self.C[1])
        return (self.R0 - d) / self.T + self.noise(P[:, 0], P[:, 1])

    def layer_of(self, P, rng=None):
        dep = self.depth(P)
        cuts = np.cumsum(self.FR)
        lay = np.searchsorted(cuts, dep)
        lay = np.clip(lay, 0, 6)
        if rng is not None:   # a few spots near borders carry a neighbour's label, as clustering does on real data
            near = np.abs(dep[:, None] - cuts[None, :]).min(1) < 0.025
            flip = near & (rng.random(len(P)) < 0.35)
            lay[flip] = np.clip(lay[flip] + rng.choice([-1, 1], flip.sum()), 0, 6)
        return lay

