# Share-card art: the drawing area of one walkthrough step, in the dark page colours, for cards.cjs.
# Render the steps first with frames.cjs at scale 2 (dark), then:
#   python3 scripts/previews/card_art.py <frames dir>
# which writes <frames dir>/vis/<name>.png. (The Selected-work thumbnails are drawn by illustrations/make.py.)
from PIL import Image
import os, sys
FRAMES = sys.argv[1] if len(sys.argv) > 1 else 'frames'
CROPS = {   # name: (step, x0, y0, x1, y1) as fractions of the 1148x646 stage
  'muse':       (12, 0.05, 0.31, 0.885, 0.755),
  'targetsage': (2,  0.02, 0.17, 0.905, 0.86),
  'imiracle':   (14, 0.005, 0.18, 0.975, 0.85),
  'impeller':   (12, 0.02, 0.215, 0.49, 0.64),
  'ptsd':       (1,  0.50, 0.256, 0.99, 0.765),
  '388-brains': (4,  0.03, 0.262, 0.50, 0.62),
}
if __name__ == '__main__':
    os.makedirs(f'{FRAMES}/vis', exist_ok=True)
    for n, (step, x0, y0, x1, y1) in CROPS.items():
        im = Image.open(f'{FRAMES}/{n}-dark-s{step:02d}.png').convert('RGB'); w, h = im.size
        out = f'{FRAMES}/vis/{n}.png'
        im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h))).save(out)
        print(n, os.path.getsize(out))
