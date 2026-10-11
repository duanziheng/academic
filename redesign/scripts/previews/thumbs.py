# Selected-work thumbnails: crop the drawing area of one walkthrough step and fit it into a 2:1 card,
# in the light and the dark page colours. Render the steps first with frames.cjs at scale 2, then:
#   python3 scripts/previews/thumbs.py <frames dir> dist/assets/thumbs
from PIL import Image
import sys, json
FRAMES = sys.argv[1] if len(sys.argv) > 2 else 'frames'
CROPS = {   # name: (step, x0, y0, x1, y1) as fractions of the 1148x646 stage
  'muse':       (12, 0.05, 0.31, 0.885, 0.755),
  'targetsage': (2,  0.02, 0.17, 0.905, 0.86),
  'imiracle':   (14, 0.005, 0.18, 0.975, 0.85),
  'impeller':   (12, 0.02, 0.215, 0.49, 0.64),
  'ptsd':       (1,  0.50, 0.256, 0.99, 0.765),
  '388-brains': (4,  0.03, 0.262, 0.50, 0.62),
}
W, H, PAD = 640, 320, 0.05
def card(name, theme, out):
    step, x0, y0, x1, y1 = CROPS[name]
    im = Image.open(f'{FRAMES}/{name}-{theme}-s{step:02d}.png').convert('RGB')
    w, h = im.size
    bg = im.getpixel((6, h - 6))
    c = im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
    s = min(W * (1 - 2 * PAD) / c.width, H * (1 - 2 * PAD) / c.height)
    c = c.resize((round(c.width * s), round(c.height * s)), Image.LANCZOS)
    canvas = Image.new('RGB', (W, H), bg)
    canvas.paste(c, ((W - c.width) // 2, (H - c.height) // 2))
    canvas.save(out, 'WEBP', quality=84, method=6)
    return bg
if __name__ == '__main__':
    import os
    OUT = sys.argv[-1]
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(f'{FRAMES}/vis', exist_ok=True)
    for n, (step, x0, y0, x1, y1) in CROPS.items():
        # the dark crop at full resolution, for the share cards (cards.cjs)
        im = Image.open(f'{FRAMES}/{n}-dark-s{step:02d}.png').convert('RGB'); w, h = im.size
        im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h))).save(f'{FRAMES}/vis/{n}.png')
        for t in ('light', 'dark'):
            bg = card(n, t, f'{OUT}/{n}-{t}.webp')
            print(n, t, '#%02x%02x%02x' % bg, os.path.getsize(f'{OUT}/{n}-{t}.webp'))
