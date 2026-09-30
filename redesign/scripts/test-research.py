"""Regression tests for research rendering and readable multiscale illustrations."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('research', ROOT / 'scripts/render-research.py')
research = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research)
CONTENT = json.loads((ROOT / 'content/research.json').read_text())
FIXTURE = '''<!doctype html><html><head><meta name="description" content="old"><meta property="og:description" content="old"></head><body>
<nav class="section-nav"><a href="#news">News</a><a href="#research">Research</a><a href="#publication">Selected work</a></nav>
<p class="position">Postdoctoral researcher · Yale University</p><p class="hero-description">Old hero</p>
<div class="education"><p>Before. OLD_BIO After.</p></div>
<section id="news">KEEP NEWS</section><section id="research"><div><section>OLD NESTED SECTION</section></div></section>
<section id="publication">KEEP PUBLICATIONS</section><section id="experience">KEEP EXPERIENCE</section><section id="talks">KEEP TALKS</section></body></html>'''.replace('OLD_BIO', research.OLD_BIO)


class ResearchTests(unittest.TestCase):
    def test_three_current_interests_and_three_phd_rows(self):
        text = research.render(CONTENT)
        self.assertEqual(text.count('class="current-interest"'), 3)
        self.assertEqual(text.count('class="phd-theme"'), 3)
        self.assertLess(text.index('Current Research Interests'), text.index('From Cells to Atlases'))

    def test_all_seven_doctoral_project_links(self):
        text = research.render(CONTENT)
        for name in ['scENCORE', 'iHerd', 'ExAD-GNN', 'Impeller', 'iMIRACLE', 'DISCO', 'MUSE']:
            self.assertIn('/publication/?q=' + name, text)
        self.assertIn('proquest.com/openview/99d988134b9f87818fa69b4df2239c17', text)

    def test_other_homepage_sections_preserved(self):
        text = research.update_homepage(FIXTURE, CONTENT)
        for name in ['news', 'publication', 'experience', 'talks']:
            a, b = research.ElementLocator(FIXTURE, 'section', 'id', name).spans[0]
            self.assertIn(FIXTURE[a:b], text)
        self.assertIn('Postdoctoral researcher · Yale University', text)
        self.assertNotIn('OLD NESTED SECTION', text)
        self.assertNotIn('Old hero', text)

    def test_idempotent_nested_section_replacement(self):
        once = research.update_homepage(FIXTURE, CONTENT)
        twice = research.update_homepage(once, CONTENT)
        self.assertEqual(once, twice)
        self.assertEqual(twice.count('id="phd-research"'), 1)
        self.assertEqual(twice.count('/assets/research.css?'), 1)
        self.assertEqual(twice.count('/assets/noir.css?'), 1)
        self.assertEqual(twice.count('/assets/research-scene.js?'), 1)

    def test_missing_or_duplicate_section_fails(self):
        with self.assertRaises(ValueError):
            research.update_homepage(FIXTURE.replace('id="research"', 'id="renamed"'), CONTENT)
        with self.assertRaises(ValueError):
            research.update_homepage(FIXTURE + '<section id="research"></section>', CONTENT)

    def test_escaped_copy_and_attributes(self):
        data = copy.deepcopy(CONTENT)
        data['interests'][0]['title'] = '<script> & "test"'
        text = research.render(data)
        self.assertNotIn('<script>', text)
        self.assertIn('&lt;script&gt; &amp; &quot;test&quot;', text)
        self.assertIn('&amp;cbl=18750', text)

    def test_search_entries_and_navigation(self):
        entries = research.search_entries(CONTENT)
        self.assertEqual(len(entries), 4)
        self.assertEqual(entries[-1]['path'], '/#phd-research')
        self.assertIn('ExAD-GNN', entries[-1]['summary'])
        text = research.update_homepage(FIXTURE, CONTENT)
        self.assertIn('href="#research">Current interests', text)
        self.assertIn('href="#phd-research">PhD research', text)
        self.assertIn(research.esc(CONTENT['description']), text)

    def test_invalid_interest_ids_fail(self):
        data = copy.deepcopy(CONTENT)
        data['interests'][1]['id'] = data['interests'][0]['id']
        with self.assertRaises(ValueError):
            research.render(data)

    def test_removed_vague_captions(self):
        text = research.render(CONTENT)
        for phrase in ['A study in biological systems', 'Conceptual visualization', 'not experimental data', 'slice-sculpture']:
            self.assertNotIn(phrase, text)
        self.assertIn('Virtual cell modeling', text)
        self.assertIn('Predicted responses', text)

    def test_full_cells_to_atlases_sequence(self):
        text = research.render(CONTENT)
        self.assertEqual(text.count('class="atlas-stage"'), 4)
        for label in ['Within cells', 'Cell niches', 'Tissues', 'Atlases']:
            self.assertIn('>' + label + '</span>', text)
        self.assertIn('gene regulation', text)

    def test_svg_references_and_ids(self):
        class IDs(HTMLParser):
            def __init__(self):
                super().__init__(); self.ids = []; self.refs = []
            def handle_starttag(self, tag, attrs):
                values = dict(attrs)
                if 'id' in values: self.ids.append(values['id'])
                if values.get('href', '').startswith('#'): self.refs.append(values['href'][1:])
                self.refs.extend(values.get('aria-controls', '').split())
        doc = IDs(); doc.feed(research.render(CONTENT))
        self.assertEqual(len(doc.ids), len(set(doc.ids)))
        self.assertTrue(set(doc.refs).issubset(set(doc.ids)))

    def test_previous_assets_replaced_once(self):
        before = FIXTURE.replace('</head>', '<link rel="stylesheet" href="/assets/noir.css?v=20260930-preview"></head>').replace('</body>', '<script src="/assets/research-scene.js?v=20260930-preview" defer></script></body>')
        text = research.update_homepage(before, CONTENT)
        self.assertNotIn('20260930-preview', text)
        self.assertEqual(text.count('/assets/noir.css?'), 1)
        self.assertEqual(text.count('/assets/research-scene.js?'), 1)


if __name__ == '__main__':
    unittest.main()
