# Ziheng Duan — academic website

A portable, static redesign of zihengduan.cn. No runtime framework or JavaScript dependency installation is required.

## Update

- Publications, talks, and dated News entries: `content/site.json`.
- Homepage biography, affiliations and sections: `build.py`.
- Theme and responsive layouts: `dist/assets/style.css`.
- Search, filters, citations and theme preference: `dist/assets/app.js`.
- Portrait: `dist/assets/portrait.jpg` (the original public website portrait).

Run `python build.py` after content edits. Publish the `dist` directory to a static host, including Netlify. Existing publication and talk routes are preserved. The historical blog text is also retained at its old URLs.

At the owner’s request, the homepage displays the Yale postdoctoral title without the “Incoming” qualifier; the profile omits the start-date qualifier at the owner’s request, while the News entry retains the November 2026 start month. UCI is presented primarily as the Ph.D. institution. Genesis internship and consulting roles are listed separately. The biography's Zhejiang education comes from the user's supplied bio and live homepage. The publication collection includes the 29 original entries and MUSE; it is not a claim to be a complete 2026 CV. Unpublished research and private manuscript details are not included.

## Migration notes

- This project is a separate private redesign. The existing Netlify deployment and domain were not changed.
- 56 linked PDF/BibTeX files were retrieved. Two PDF links were already 404s on the source website; their buttons have been omitted, with working-format publisher DOI links retained.
- Repeated DOI prefixes were corrected.
- Search and filtering work locally; publication titles and bibliographic data render without JavaScript.
- Contact form explicitly opens the visitor's email application. It does not silently submit or collect messages.
- Original Netlify CMS authentication is not reproduced here. The authenticated original source repository would be needed to reconnect its editing/publishing workflow.
- Historical blog content is preserved as plain text. The modern layout is shared across these pages.
- The original social image is preserved; no new sharing card was generated.

Two PDFs exceed the private preview host’s 25 MiB asset limit. Their original files are preserved under `large-assets/`; the preview links to the existing public website for those PDFs. Before replacing the original Netlify site, copy `large-assets/` into `dist/` on a host that accepts the file size.

SCORCH Fall 2026 talk title, September 15 date, and San Diego location were supplied by the owner. The consortium’s public meetings page did not yet list the fall meeting when checked on September 11, 2026. No invitation status, precise venue, or unverified slides are claimed. The CIKM talk entry is removed; its old URL redirects to the iMIRACLE publication.

## Netlify migration and iteration

Keep the existing Netlify project and its domain binding. Back up the original source repository and record the current production deploy before switching the repository or build settings. The old CMS uses git-gateway and the `master` branch; this does not reveal its repository URL. Retrieve that URL from the existing Netlify project before changing it.

1. Put this source in a user-owned GitHub repository (or a migration branch in the original repository). Include `large-assets/`, `dist/`, `content/`, `build.py`, `scripts/`, and `netlify.toml`.
2. Connect the existing Netlify project to that repository. Use the correct production branch, empty base directory, build command `python3 scripts/build-netlify.py`, and publish directory `netlify-dist`. Remove old Hugo-specific build settings if present.
3. Review a branch deploy/Deploy Preview first, including the two large PDFs, homepage, publication details, mobile layout, and contact links.
4. Publish to the existing project. Keep `zihengduan.cn` and its DNS binding unchanged when reusing that project. Keep the prior production deploy available for rollback.
5. Future updates: edit content, push a branch, review the preview, then merge to the production branch. Netlify builds and deploys automatically.

`python3 scripts/build-netlify.py` creates an independent `netlify-dist/` output with the large PDFs restored at their original paths and a local portrait for social previews. The output directory is ignored by Git. The normal Sites preview still uses `dist/` and its asset-size limit. Source changes here are currently synced to the Sites Git remote, not yet to the owner's GitHub or Netlify project.

GSoC mentoring projects are maintained under `mentoring` in `content/site.json`.

Mentoring is verified against the owner-provided CV (cv_ziheng (4).pdf): StaR (2026), RAG-ST (2025), BenchmarkST (2024), all as Mentor. Earlier HistoMoE and Agent4Target project proposals are not listed as mentoring experience.
