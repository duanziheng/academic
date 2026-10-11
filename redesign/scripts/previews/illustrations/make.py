"""Selected-work illustrations: one drawing per paper with a walkthrough, in the page's light and dark colours.

    python3 scripts/previews/illustrations/make.py <work dir> dist/assets

writes the SVGs and their 2x renders to <work dir>, the dark render of each to <work dir>/vis/<name>.png for the
share cards (node scripts/previews/cards.cjs <work dir> dist/assets), and the thumbnails to
dist/assets/thumbs/<name>-<light|dark>.webp (640x320) and <name>-<light|dark>-960.webp (960x480, for phones).
Needs numpy, scipy, matplotlib and Pillow, and Playwright for render.cjs.
"""
import importlib
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
PAPERS = {'targetsage': 'targetsage', 'ptsd': 'ptsd', 'muse': 'muse', 'imiracle': 'imiracle',
          'impeller': 'impeller', '388-brains': 'brains388'}   # walkthrough name: module


def main(work, assets):
    work, thumbs = Path(work), Path(assets) / 'thumbs'
    (work / 'vis').mkdir(parents=True, exist_ok=True); thumbs.mkdir(parents=True, exist_ok=True)
    jobs = []
    for name, mod in PAPERS.items():
        draw = importlib.import_module(mod).draw
        for theme in ('light', 'dark'):
            svg = work / f'{name}-{theme}.svg'
            svg.write_text(draw(theme))
            jobs += [str(svg), str(work / f'{name}-{theme}.png')]
    subprocess.run(['node', str(HERE / 'render.cjs'), *jobs], check=True)
    for name in PAPERS:
        for theme in ('light', 'dark'):
            im = Image.open(work / f'{name}-{theme}.png').convert('RGB')
            for width, suffix in ((640, ''), (960, '-960')):
                out = thumbs / f'{name}-{theme}{suffix}.webp'
                im.resize((width, width // 2), Image.LANCZOS).save(out, 'WEBP', quality=82, method=6)
                print(out.name, out.stat().st_size)
            if theme == 'dark':
                im.save(work / 'vis' / f'{name}.png')


if __name__ == '__main__':
    main(*sys.argv[1:3])
