"""Render current interests and thesis-aligned visual components after the base build.

Research prose lives in content/research.json. Illustration fragments are separate
from the prose and use SVG so that meaningful static diagrams survive without JS.
Only generated homepage markup and the research search index are rewritten.
"""
from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CSS = '<link rel="stylesheet" href="/assets/research.css?v=20260929-research">'
VISUAL_CSS = '<link rel="stylesheet" href="/assets/noir.css?v=20260930-yale-noir-v7">'
VISUAL_SCRIPT = '<script src="/assets/research-scene.js?v=20260930-card-select-v8" defer></script>'
QUIET_CSS = '<link rel="stylesheet" href="/assets/quiet-controls.css?v=20260930-centered-v6">'
OLD_BIO = (
    'My research integrates artificial intelligence with single-cell genomics '
    'and spatial transcriptomics to advance drug discovery.'
)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


class ElementLocator(HTMLParser):
    """Locate a unique non-void element, including nested elements of its type."""

    def __init__(self, document: str, tag: str, attr: str, value: str) -> None:
        super().__init__(convert_charrefs=False)
        self.document, self.tag, self.attr, self.value = document, tag, attr, value
        self.offsets = [0]
        for line in document.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.depth = 0
        self.start = 0
        self.spans: list[tuple[int, int]] = []
        self.feed(document)
        self.close()
        if self.depth or len(self.spans) != 1:
            raise ValueError(f'Expected one complete {tag}[{attr}={value!r}]')

    def char_offset(self) -> int:
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag != self.tag:
            return
        if self.depth:
            self.depth += 1
            return
        actual = dict(attrs).get(self.attr, '') or ''
        matches = self.value in actual.split() if self.attr == 'class' else actual == self.value
        if matches:
            self.start = self.char_offset()
            self.depth = 1

    def handle_endtag(self, tag: str) -> None:
        if tag == self.tag and self.depth:
            self.depth -= 1
            if not self.depth:
                end = self.document.index('>', self.char_offset()) + 1
                self.spans.append((self.start, end))


def replace_element(document: str, tag: str, attr: str, value: str, replacement: str) -> str:
    start, end = ElementLocator(document, tag, attr, value).spans[0]
    return document[:start] + replacement + document[end:]


def validate(content: dict) -> None:
    if len(content['interests']) != 3 or len(content['phd']['themes']) != 3:
        raise ValueError('Expected three current interests and three doctoral themes')
    ids = [item['id'] for item in content['interests']]
    if len(set(ids)) != len(ids) or any(not item.replace('-', '').isalnum() for item in ids):
        raise ValueError('Interest IDs must be unique, simple HTML anchors')
    if urlsplit(content['phd']['dissertation_url']).scheme != 'https':
        raise ValueError('The dissertation must use an HTTPS link')


def render(content: dict) -> str:
    validate(content)
    visual = (ROOT / 'content/research-visual.html').read_text(encoding='utf-8')
    atlas_visual = (ROOT / 'content/phd-visual.html').read_text(encoding='utf-8')
    cards = []
    for number, item in enumerate(content['interests'], 1):
        cards.append(
            f'<article class="current-interest" id="{esc(item["id"])}" '
            f'aria-labelledby="{esc(item["id"])}-heading" data-scene="{number - 1}" '
            f'role="button" tabindex="0" aria-pressed="{str(number == 1).lower()}" '
            f'aria-controls="cellular-model">'
            f'<span class="research-number" aria-hidden="true">{number}</span>'
            f'<h3 id="{esc(item["id"])}-heading">{esc(item["title"])}</h3>'
            f'<p>{esc(item["description"])}</p></article>'
        )
    phd = content['phd']
    rows = []
    for theme in phd['themes']:
        projects = ''.join(
            f'<a href="/publication/?q={quote(project, safe="")}">{esc(project)}</a>'
            for project in theme['projects']
        )
        rows.append(
            '<div class="phd-theme">'
            f'<dt>{esc(theme["title"])}</dt>'
            f'<dd class="phd-theme-description">{esc(theme["description"])}</dd>'
            f'<dd class="phd-projects">{projects}</dd></div>'
        )
    return (
        '<section id="research" class="research-band research-overview" aria-labelledby="research-heading">'
        '<div class="wrap"><div class="section-heading research-intro visual-intro">'
        '<div class="research-copy"><p class="eyebrow">01 / Research</p>'
        f'<h2 id="research-heading">{esc(content["heading"])}</h2>'
        f'<p class="research-lead">{esc(content["introduction"])}</p></div>' + visual + '</div>'
        '<div class="current-interest-grid">' + ''.join(cards) + '</div>'
        '<section id="phd-research" class="phd-research" aria-labelledby="phd-heading">'
        '<div class="phd-heading-row">' + atlas_visual + '<div class="phd-identity">'
        '<p class="eyebrow">PhD Research · UC Irvine</p>'
        f'<h3 id="phd-heading">{esc(phd["title"])}</h3>'
        f'<p class="phd-subtitle">{esc(phd["subtitle"])}</p></div>'
        f'<a class="dissertation-link" href="{esc(phd["dissertation_url"])}" '
        'target="_blank" rel="noopener" '
        f'aria-label="Doctoral dissertation: {esc(phd["dissertation_title"])} (opens in a new tab)">'
        'Doctoral dissertation <span aria-hidden="true">↗</span></a></div>'
        f'<p class="phd-summary">{esc(phd["description"])}</p>'
        '<dl class="phd-themes">' + ''.join(rows) + '</dl></section></div></section>'
    )


def update_homepage(document: str, content: dict) -> str:
    document = replace_element(document, 'section', 'id', 'research', render(content))
    document = replace_element(
        document, 'p', 'class', 'hero-description',
        f'<p class="hero-description">{esc(content["hero"])}</p>',
    )
    if OLD_BIO in document:
        document = document.replace(OLD_BIO, esc(content['doctoral_bio']), 1)
    elif esc(content['doctoral_bio']) not in document:
        raise ValueError('The biography template changed; review it before publishing')
    start, end = ElementLocator(document, 'nav', 'class', 'section-nav').spans[0]
    nav = document[start:end]
    old_link = '<a href="#research">Research</a>'
    new_links = (
        '<a href="#research">Current interests</a>'
        '<a href="#phd-research">PhD research</a>'
    )
    if old_link in nav:
        nav = nav.replace(old_link, new_links, 1)
    elif new_links not in nav:
        raise ValueError('The sidebar template changed; review research navigation')
    document = document[:start] + nav + document[end:]
    import re
    for attribute in ('name="description"', 'property="og:description"'):
        pattern = rf'<meta {attribute} content="[^"]*">'
        replacement = f'<meta {attribute} content="{esc(content["description"])}">'
        document, count = re.subn(pattern, lambda _: replacement, document)
        if count != 1:
            raise ValueError(f'Expected one homepage meta tag: {attribute}')
    if CSS not in document:
        document = document.replace('</head>', CSS + '</head>', 1)
    # Replace previous preview assets instead of accumulating style/script layers.
    document = re.sub(r'<link rel="stylesheet" href="/assets/noir\.css\?[^\"]*">', '', document)
    document = re.sub(r'<script src="/assets/research-scene\.js\?[^\"]*" defer></script>', '', document)
    document = re.sub(r'<link rel="stylesheet" href="/assets/quiet-controls\.css\?[^\"]*">', '', document)
    document = document.replace('</head>', VISUAL_CSS + QUIET_CSS + '</head>', 1)
    document = document.replace('</body>', VISUAL_SCRIPT + '</body>', 1)
    return document


def search_entries(content: dict) -> list[dict]:
    entries = [
        {'title': item['title'], 'path': '/#' + item['id'], 'summary': item['description']}
        for item in content['interests']
    ]
    phd = content['phd']
    entries.append({
        'title': 'PhD Research — ' + phd['title'],
        'path': '/#phd-research',
        'summary': phd['description'] + ' ' + ' '.join(
            theme['title'] + ' ' + ' '.join(theme['projects']) for theme in phd['themes']
        ),
    })
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='Built deployment directory')
    args = parser.parse_args()
    content = json.loads((ROOT / 'content/research.json').read_text(encoding='utf-8'))
    home = args.output / 'index.html'
    updated = update_homepage(home.read_text(encoding='utf-8'), content)
    index_path = args.output / 'assets/content.json'
    index = json.loads(index_path.read_text(encoding='utf-8'))
    index['research'] = search_entries(content)
    for asset in ('research.css', 'noir.css', 'research-scene.js', 'quiet-controls.css'):
        if not (args.output / 'assets' / asset).is_file():
            raise FileNotFoundError(f'Missing research asset: {asset}')
    home.write_text(updated, encoding='utf-8')
    index_path.write_text(json.dumps(index, ensure_ascii=False), encoding='utf-8')
    print('Rendered current interests, multiscale PhD research, and research search entries.')


if __name__ == '__main__':
    main()
