# Ziheng Duan — academic website

Live: https://zihengduan.cn/ · Repository: duanziheng/academic · Netlify: ziheng0805

## Editing

- Current research interests, doctoral themes, dissertation link, homepage research biography and description: `content/research.json`.
- Research component and homepage research navigation: `scripts/render-research.py`.
- Research cards and compact doctoral rows: `dist/assets/research.css`.
- Talks (canonical source for homepage, detail pages and search): `content/talks.json`.
- Publications, News and mentoring: `content/site.json`. Its legacy `talks` array is no longer used by the builder; edit `content/talks.json` instead.
- Base page templates, affiliations, other biography text and metadata: `build.py`.
- Search metadata, also in `build.py`. Every publication page carries Google Scholar's `citation_*` tags, built from `site.json` and the paper's `cite.bib`, and schema.org ScholarlyArticle JSON-LD; the homepage carries Person JSON-LD. Scholar reads a PDF only from the directory of its abstract page, so the build writes `dist/_redirects` (generated, not committed). Its rewrite rules also serve each hosted PDF from its paper's own directory, which is where `citation_pdf_url` points. The Person data names the ORCID iD (0000-0003-4696-0042) and lists the OpenReview, ORCID, Scholar, GitHub, LinkedIn and X profiles in `sameAs`. OpenReview and ORCID also appear in the contact links.
- Main theme and responsive layout: `dist/assets/style.css`.
- Response headers: `dist/_headers`. It sets `nosniff`, a referrer policy and a permissions policy on every page, and long caching for fonts: a year for `assets/fonts/`, whose files are never replaced under the same name, and a week for `walkthroughs/fonts/`, which are regenerated in place. Everything else revalidates on each visit, because images and stylesheets are replaced under the same names. Netlify itself adds the HTTPS redirect and HSTS.
- Redirects: the build writes `dist/_redirects`. It holds `/cv`, a temporary (302) redirect to the CV PDF in `site.json`'s `cv.url`, and the paper-PDF rewrites described above.
- Link check: `.github/workflows/link-check.yml` runs `scripts/check-links.py` against the live site every Monday. If a link is broken, it opens an issue titled “Broken links on zihengduan.cn”, or adds the report to the one already open. Sites that refuse automated requests (403, 429, 999) are listed as unverified rather than broken; DOIs are checked through doi.org's handle API.
- Search, filtering, citations and theme preference: `dist/assets/app.js`.
- CV and talk PDFs: `dist/files/`.
- Legacy blog posts: the historic `/blogs/` URLs, not linked from the navigation, rendered from the original Hugo Markdown in `content/blogs/` at the repository root.
  - `python3 scripts/render-legacy.py` does the rendering. It needs `markdown` and Pillow; run it by hand after editing a post.
  - It writes an HTML fragment per post to `content/legacy/`, with code blocks, line breaks and images kept, and saves WebP copies of the posts' images beside their pages in `dist/blogs/`.
  - `build.py` uses a post's fragment when one exists.
- Paper pages with more than twelve authors shorten the byline as the archive does. The full list sits behind an “All N authors” toggle; the Scholar tags always carry every author.
- Refinements from October 2026 (selected-work thumbnails, the year-grouped archive, talk slide previews, search keys and highlights, the dark-mode research band, phone layout, heading font): `dist/assets/polish.css`, which `scripts/build-netlify.py` links last on every page built from the site template.
- Preview images, made with `scripts/previews/`:
  - Selected-work thumbnails are drawn illustrations, one Python script per paper in `illustrations/` (numpy, scipy, matplotlib; Pillow and Playwright to render). `python3 scripts/previews/illustrations/make.py <work dir> dist/assets` writes `dist/assets/thumbs/<walkthrough>-light|dark.webp` (640×320) and `-960.webp` (960×480, which phones load through srcset).
  - What they show: TargetSage, the karyotype of the 19,032 protein-coding genes it ranks, a magnifier on one target gene and that protein with a drug in its pocket. PTSD, the DLPFC, 111 donors, 2,051,149 nuclei and the four assays in seven cell types. MUSE, three adjacent DLPFC sections on Visium slides with matched spots. iMIRACLE, a sender and a receiver cell with labelled ligands, receptors and the target gene. Impeller, a section labelled Measured, where most spots are missing (hollow rings) and the spatial and similarity paths reach one missing spot ('?'), and an arrow to the same section labelled Imputed, with every spot filled. 388 brains, a brain drawn as its cells with cortical layers and white matter, in front of a stack of brains, with cell-type regulatory networks and an eQTL. The numbers come from the papers.
  - Share cards: `node scripts/previews/cards.cjs <work dir> dist/assets` renders the 1200×630 cards in `dist/assets/og/` and the PNG icons. A paper card sets the title beside that paper's dark illustration, from the `vis/` folder that `make.py` writes into the work dir. A talk card sets it beside the first slide of `dist/files/talks/<name>.pdf`, written to `og/talk-<name>.jpg`. Add arguments to render only some of them: `home`, `papers`, `talks` or `icons`. `frames.cjs` renders walkthrough steps from a locally served build, for checking them.
  - A publication shows a thumbnail when its walkthrough has one. A talk shows the first slide of its deck when `dist/assets/thumbs/talk-<pdf name>.webp` exists. Pages use `og/home.jpg` as their share card, except papers with a walkthrough, which use `og/<walkthrough>.jpg`.
- Portrait: `dist/assets/portrait-{480,720,1080}.{avif,webp}` and `portrait-720.jpg`, served with srcset; `portrait.jpg` is the original. Headings use Georgia; where it is not installed (Android, Linux) they fall back to the self-hosted, metric-compatible Gelasio in `dist/assets/fonts/` (SIL Open Font License).
- Animated paper walkthroughs: self-contained pages in `dist/walkthroughs/<name>/index.html`, with self-hosted fonts in `dist/walkthroughs/fonts/`. A publication links to one with a `Walkthrough` entry in its `links`. When the page supports embed mode (it reports its height, as all current pages do), the publication page also shows the walkthrough above the abstract (an iframe of `/walkthroughs/<name>/?embed`, which hides the page title, follows the site theme and reports its height to the page). These pages use the site's colours in both themes (page, text and lines; panels in the page colour), and the slides, drawn for a white screen, have their colours mapped to the current theme by a small script in each page. The font files are cut down to the characters these pages use, so regenerate them with the pages. Full screen uses the Fullscreen API where there is one. Where there is none (iPhone Safari), the slide becomes a fixed overlay, turned sideways when the phone is upright, with a close button and Esc; an embedded copy opens its full page with `#full`, which shows the overlay. A step has its own address: `/walkthroughs/<name>/#step-12` opens step 12, and the address follows the reader's step. Embedded copies leave their address alone. The iPhone overlay uses `#step-12&full`.

News labels use month and year; full dates can remain in the data for ordering. Search includes research interests, doctoral work, News, publications and talks. Past talk badges are omitted during builds and also expire in the browser. Publications retain full bylines and BibTeX; homepage selected papers show a short byline only when Ziheng is first author.

Talks use title case while preserving project names such as scENCORE and iHerd. Each entry presents the title given in the event's program or abstracts and on the slides, followed by Talk, the event or institution, the date and any known location. Preserve the precision of known dates; do not invent days or locations. Past talks omit clock times and use retrospective descriptions rather than future-tense agendas. Resource labels describe their content: Slides, Abstracts, Event and Recording. Keep historical talk routes and original resource URLs intact. Do not infer Invited or Contributed status.

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

Current Research Interests presents three directions: Virtual Cell Modeling, Therapeutic Intervention Design, and Closed-Loop Scientific Discovery. They are three steps of one line of work, in order: modeling cells, designing interventions, and learning from experiments. The section's introduction and the three labels of its animation follow the same order. The homepage biography, the page description, the home share card and the CV's Research Interests name the directions with the same words; the CV also gives the descriptions, followed by a Methods line. Keep the headings parallel, each a noun phrase naming a step, and each description a gerund phrase with its purpose; application goals such as precision medicine go in the descriptions. These are interests, not claims that all corresponding systems or experiments have been completed.

PhD Research — From Cells to Atlases follows the dissertation's three-part structure: genomic/cellular analysis (scENCORE, iHerd, ExAD-GNN), microenvironments/intercellular regulation (Impeller, iMIRACLE), and region completion/multi-slice integration (DISCO, MUSE). The dissertation entry points to the owner's supplied public ProQuest record; the large thesis attachment is not republished in the repository.

At the owner's request, the homepage retains the existing Yale postdoctoral title without “Incoming”; News retains the November 2026 start month. Employment dates, publication statuses, author metadata and News remain unchanged. Of the two NeurIPS 2026 papers announced in News, TargetSage now has a selected publication entry; sMMC-22M appears only in News, pending complete publication metadata. Historical blog routes and the CIKM-to-iMIRACLE redirect remain available.

The publication archive groups papers by year; when a year has two or more PsychENCODE Consortium papers they fold into one group, which opens when a search or filter matches inside it. The Authorship filter reads first author, co-author or consortium from the byline and `consortium_member`.

The contact form opens the visitor's email app; it does not submit or store messages. Publisher PDFs can require institutional access. Large original PDFs are preserved in `large-assets/` and included in every production build.
