// Render walkthrough steps from a locally served build (python3 -m http.server 8765 --directory netlify-dist).
// node scripts/previews/frames.cjs <name> <steps|all> <outdir> <light|dark> [scale]
// Writes <outdir>/<name>-<theme>-sNN.png of the slide (#stage), for checking the steps.
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const fs = require('fs'), path = require('path');
const [,, NAME, steps, OUT, theme = 'light', scale = '2'] = process.argv;
const BASE = process.env.SITE || 'http://127.0.0.1:8765';
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: +scale });
  await ctx.addInitScript(t => { try { localStorage.setItem('theme', t); } catch (e) {} }, theme);
  const p = await ctx.newPage();
  await p.goto(`${BASE}/walkthroughs/${NAME}/`, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const N = await p.evaluate(() => window.__muse.N);
  const list = steps === 'all' ? [...Array(N).keys()] : steps.split(',').map(Number);
  for (const j of list) {
    await p.evaluate(j => window.__muse.go(j, false), j); await p.waitForTimeout(120);
    await (await p.$('#stage')).screenshot({ path: path.join(OUT, `${NAME}-${theme}-s${String(j).padStart(2, '0')}.png`) });
  }
  await b.close();
})();
