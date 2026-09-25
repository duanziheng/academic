# Ziheng Duan — academic website

Live: https://zihengduan.cn/ · Repository: duanziheng/academic · Netlify: ziheng0805

## Editing

- Publications, talks, News and mentoring: `content/site.json`.
- Homepage biography, section templates and metadata: `build.py`.
- Theme and responsive layout: `dist/assets/style.css`.
- Search, filtering, citations and theme preference: `dist/assets/app.js`.
- CV and talk PDFs: `dist/files/`.

News labels use month and year; full dates can remain in the data for ordering. Search includes News, publications and talks. Past talk badges are omitted during builds and also expire in the browser. Publications retain full bylines and BibTeX; homepage selected papers show a short byline only when Ziheng is first author.

## Build and deployment

Run from this directory:

```sh
python3 scripts/build-netlify.py
```

The script generates pages, canonical URLs, sharing metadata, `sitemap.xml` and `robots.txt`, restores `large-assets/`, then checks local links, anchors, publication citations and the CV. Output is `netlify-dist/`; do not commit generated HTML or that output directory. Static resources under `dist/` remain versioned.

Root `netlify.toml` uses base `redesign`, command `python3 scripts/build-netlify.py`, and publish directory `netlify-dist`. No Hugo build or Node package installation is required. `master` auto-deploys to the existing domain. Use a branch and Netlify Deploy Preview for substantial changes; Git history and prior Netlify deploys support rollback.

## Content notes

At the owner's request, the homepage uses the Yale postdoctoral title without “Incoming”; News retains the November 2026 start month. The publication archive is not a complete 2026 CV: the two newly accepted NeurIPS 2026 papers currently appear in News, pending complete publication metadata. Historical blog routes and the CIKM-to-iMIRACLE redirect remain available.

The contact form opens the visitor's email app; it does not submit or store messages. Publisher PDFs can require institutional access. Large original PDFs are preserved in `large-assets/` and included in every production build.
