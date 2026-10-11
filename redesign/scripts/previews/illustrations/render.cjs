// node render.cjs a.svg a.png [b.svg b.png ...]: render 960x480 SVGs to PNG at 2x in Chromium, with Gelasio loaded
// for the numerals. Set PLAYWRIGHT=/path/to/playwright when it is not installed where node can find it.
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const fs = require('fs'), path = require('path');
const FONT = 'file://' + path.resolve(__dirname, '../../../dist/assets/fonts/gelasio-latin-400-normal.woff2');
const a = process.argv.slice(2), pairs = [];
for (let i = 0; i < a.length; i += 2) pairs.push([a[i], a[i + 1]]);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 960, height: 480 }, deviceScaleFactor: 2 });
  for (const [svg, png] of pairs) {
    const html = `<!doctype html><html><head><meta charset="utf-8"><style>
      @font-face{font-family:Gelasio;src:url(${FONT})}
      html,body{margin:0;width:960px;height:480px;overflow:hidden} svg{display:block}</style></head><body>${fs.readFileSync(svg, 'utf8')}</body></html>`;
    const tmp = path.join(path.dirname(path.resolve(png)), '_render.html'); fs.writeFileSync(tmp, html);
    await p.goto('file://' + tmp, { waitUntil: 'load' }); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(100);
    await p.screenshot({ path: png });
  }
  await b.close();
})();
