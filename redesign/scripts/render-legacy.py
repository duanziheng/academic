"""Render the eight legacy blog posts from their original Hugo Markdown (content/blogs/**/index.md at the repo root).

    pip install markdown pillow # only needed to run this script, not for the site build
    python3 redesign/scripts/render-legacy.py

writes one HTML fragment per post to redesign/content/legacy/<slug>.html and saves each post's images, as WebP,
next to its page in redesign/dist/blogs/. build.py uses a fragment when it exists. Before this, the posts were built from the
search index's plain text, which had lost the code blocks, line breaks and images and escaped entities twice.
"""
import json
import re
import urllib.parse
from pathlib import Path

import markdown
from PIL import Image

R = Path(__file__).resolve().parents[1]          # redesign/
SRC = R.parent / 'content/blogs'                 # the Hugo site's posts
OUT = R / 'content/legacy'
ALT = {   # the posts' images had a placeholder alt ('Image Title')
    'ascii.png': 'DOSBox 中程序的运行结果：按列显示的 ASCII 码表',
    'add.png': 'DOSBox 中乘法器程序的运行结果',
    'page.jpg': '用 turtle 画出的小猪佩奇',
    'superman.png': '手绘插图：站在星球上的小人，头顶两颗星星',
}


def slug(relpermalink):
    return urllib.parse.unquote(relpermalink).strip('/').replace('/', '__')


def source_dir(relpermalink):
    # the URL path is lower case; the source folders keep their original case
    want = urllib.parse.unquote(relpermalink).strip('/').split('/')[1:]   # drop 'blogs'
    d = SRC
    for part in want:
        d = next(x for x in d.iterdir() if x.is_dir() and x.name.lower() == part.lower())
    return d


def body(md):
    text = re.sub(r'\A---\n.*?\n---\n', '', md, count=1, flags=re.S)
    return text.replace('<!--more-->', '')


def main():
    data = json.loads((R / 'content/site.json').read_text(encoding='utf-8'))
    OUT.mkdir(exist_ok=True)
    for b in data['blogs']:
        src = source_dir(b['relpermalink'])
        html = markdown.markdown(body((src / 'index.md').read_text(encoding='utf-8')),
                                 extensions=['fenced_code', 'tables', 'sane_lists'], output_format='html')
        # images are page-bundle files: save each beside the built page as WebP (at most 1520 px wide, twice the text
        # column) and give it its size, so the page does not shift when it loads
        dest = R / 'dist' / urllib.parse.unquote(b['relpermalink']).strip('/')
        for name in sorted(set(re.findall(r'<img[^>]*src="\./([^"]+)"', html))):
            dest.mkdir(parents=True, exist_ok=True)
            im = Image.open(src / name)
            im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
            if im.width > 1520:
                im = im.resize((1520, round(im.height * 1520 / im.width)), Image.LANCZOS)
            webp = Path(name).stem + '.webp'
            im.save(dest / webp, 'WEBP', quality=85, method=6)
            html = re.sub(r'alt="[^"]*" src="\./' + re.escape(name) + '"',
                          f'alt="{ALT.get(name, "")}" src="./{webp}" width="{im.width}" height="{im.height}"', html)
        html = re.sub(r'<img([^>]*)src="\./', r'<img loading="lazy" decoding="async"\1src="./', html)
        html = html.replace('<pre>', '<pre tabindex="0">')   # wide code scrolls sideways; keyboard users can focus it to scroll
        (OUT / (slug(b['relpermalink']) + '.html')).write_text(html + '\n', encoding='utf-8')
        print(b['relpermalink'], len(html))


if __name__ == '__main__':
    main()
