# Ziheng Duan — academic website

Live: https://zihengduan.cn/ · Repository: duanziheng/academic · Netlify: ziheng0805

## Editing

- Current research interests, doctoral themes, dissertation link, homepage research biography and description: `content/research.json`.
- Research component and homepage research navigation: `scripts/render-research.py`.
- Research cards and compact doctoral rows: `dist/assets/research.css`.
- Talks (canonical source for homepage, detail pages and search): `content/talks.json`.
- Publications, News and mentoring: `content/site.json`. Its legacy `talks` array is no longer used by the builder; edit `content/talks.json` instead.
- Base page templates, affiliations, other biography text and metadata: `build.py`.
- Main theme and responsive layout: `dist/assets/style.css`.
- Search, filtering, citations and theme preference: `dist/assets/app.js`.
- CV and talk PDFs: `dist/files/`.

News labels use month and year; full dates can remain in the data for ordering. Search includes research interests, doctoral work, News, publications and talks. Past talk badges are omitted during builds and also expire in the browser. Publications retain full bylines and BibTeX; homepage selected papers show a short byline only when Ziheng is first author.

Talks use title case while preserving project names such as scENCORE and iHerd. Each entry presents the research title, followed by Talk, the event or institution, the date and any known location. Preserve the precision of known dates; do not invent days or locations. Past talks omit clock times and use retrospective descriptions rather than future-tense agendas. Resource labels describe their content: Slides, Abstracts, Event and Recording. Keep historical talk routes and original resource URLs intact. Do not infer Invited or Contributed status.

## Build and deployment

Run from this directory:

```sh
python3 scripts/test-research.py
python3 scripts/build-netlify.py
```

The deployment script runs the base generator, restores `large-assets/`, then renders the research component from `content/research.json`. That rendering stage replaces the legacy research placeholder, updates the homepage research biography and descriptions, adds the PhD sidebar entry, and indexes the new research content for search. It fails rather than silently publishing a partial update if expected template landmarks change. Do not edit the legacy inline research copy in `build.py`; use `content/research.json` instead.

The build then checks local links, anchors, publication citations and the CV. Output is `netlify-dist/`; do not commit generated HTML or that output directory. Static resources under `dist/` remain versioned. Running `build.py` alone does not produce the final deployment; use `scripts/build-netlify.py`.

Root `netlify.toml` uses base `redesign`, command `python3 scripts/build-netlify.py`, and publish directory `netlify-dist`. No Hugo build or Node package installation is required. `master` auto-deploys to the existing domain. Use a branch and Netlify Deploy Preview for substantial changes; Git history and prior Netlify deploys support rollback.

## Content notes

Current Research Interests presents three directions: Virtual Cells for Precision Medicine, AI for Therapeutic Discovery, and Closed-Loop AI for Science. These are interests, not claims that all corresponding systems or experiments have been completed. In the first heading, virtual cells are the modeling direction and precision medicine is the application goal, not a parallel category.

PhD Research — From Cells to Atlases follows the dissertation's three-part structure: genomic/cellular analysis (scENCORE, iHerd, ExAD-GNN), microenvironments/intercellular regulation (Impeller, iMIRACLE), and region completion/multi-slice integration (DISCO, MUSE). The dissertation entry points to the owner's supplied public ProQuest record; the large thesis attachment is not republished in the repository.

At the owner's request, the homepage retains the existing Yale postdoctoral title without “Incoming”; News retains the November 2026 start month. Employment dates, publication statuses, author metadata and News remain unchanged. The two newly accepted NeurIPS 2026 papers currently appear in News, pending complete publication metadata. Historical blog routes and the CIKM-to-iMIRACLE redirect remain available.

The contact form opens the visitor's email app; it does not submit or store messages. Publisher PDFs can require institutional access. Large original PDFs are preserved in `large-assets/` and included in every production build.
