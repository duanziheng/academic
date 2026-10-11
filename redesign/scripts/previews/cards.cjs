// Share cards (1200x630, assets/og/*.jpg) and PNG icons (favicon-32, apple-touch-icon, icon-192/512).
// node scripts/previews/cards.cjs <frames dir> dist/assets
// The paper cards use <frames dir>/vis/<name>.png, written by thumbs.py; titles are set in Gelasio.
const { chromium } = require(process.env.PLAYWRIGHT || 'playwright');
const fs = require('fs'), path = require('path');
const HERE = path.resolve(process.argv[2]);
const A = path.resolve(process.argv[3]);
const FONT = 'file://' + path.join(A, 'fonts/gelasio-latin-400-normal.woff2');
const PAPERS = [
  ['targetsage', 'NeurIPS · 2026', 'TargetSage: Identifying Therapeutic Target Genes with Interpretable and Robust LLM Reasoning'],
  ['ptsd', 'Nature · 2025', 'Single-cell transcriptomic and chromatin dynamics of the human brain in PTSD'],
  ['muse', 'CIKM · 2025', 'MUSE: A Multi-slice Joint Analysis Method for Spatial Transcriptomics Experiments'],
  ['imiracle', 'CIKM · 2024', 'iMIRACLE: An Iterative Multi-View Graph Neural Network to Model Intercellular Gene Regulation From Spatial Transcriptomic Data'],
  ['impeller', 'Bioinformatics · 2024', 'Impeller: a path-based heterogeneous graph learning method for spatial transcriptomic data imputation'],
  ['388-brains', 'Science · 2024', 'Single-cell genomics and regulatory networks for 388 human brains'],
];
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const BASE = `<style>
@font-face{font-family:Gelasio;src:url(${FONT}) format('woff2');font-weight:400}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1200px;height:630px;overflow:hidden}
body{background:#071522;color:#eef4f8;font-family:Inter,sans-serif;position:relative;-webkit-font-smoothing:antialiased}
.glow{position:absolute;inset:0;background:radial-gradient(820px 460px at 92% -8%,rgba(29,95,150,.30),transparent 62%),radial-gradient(640px 380px at -6% 112%,rgba(17,58,98,.30),transparent 60%)}
.frame{position:absolute;inset:0;display:flex;flex-direction:column;padding:46px 64px 48px}
.top{display:flex;align-items:center;justify-content:space-between}
.brand{display:flex;align-items:center;gap:14px;font-weight:600;font-size:22px;letter-spacing:-.01em}
.mono{width:40px;height:40px;background:#0b477c;display:grid;place-items:center;font:21px/1 Gelasio,serif;letter-spacing:-1px;color:#fff}
.url{font-size:20px;color:#8eb9de;letter-spacing:.01em}
.eyebrow{margin-top:34px;font-size:19px;font-weight:600;letter-spacing:.02em;color:#8eb9de}
.eyebrow span{color:#5f8bb0}
h1{font-family:Gelasio,serif;font-weight:400;color:#f3f7fa}
.title{margin-top:14px;font-size:50px;line-height:1.12;letter-spacing:-.018em}
.vis{flex:1;margin-top:28px;min-height:0;background:#0a111a;border:1px solid rgba(142,185,222,.17);border-radius:12px;position:relative;overflow:hidden}
.vis img{position:absolute;left:24px;top:16px;width:calc(100% - 48px);height:calc(100% - 32px);object-fit:contain;display:block}
</style>`;
function paperCard([name, eyebrow, title]) {
  return `<!doctype html><html><head><meta charset="utf-8">${BASE}</head><body><div class="glow"></div><div class="frame">
<div class="top"><div class="brand"><span class="mono">ZD</span>Ziheng Duan</div><div class="url">zihengduan.cn</div></div>
<p class="eyebrow">${esc(eyebrow)} <span>·&nbsp; Animated walkthrough</span></p>
<h1 class="title">${esc(title)}</h1>
<div class="vis"><img src="file://${path.join(HERE, 'vis', name + '.png')}"></div></div>
<script>const t=document.querySelector('.title');let s=50;while(t.getBoundingClientRect().height>3*1.12*s+2&&s>34){s-=2;t.style.fontSize=s+'px'}</script></body></html>`;
}
function homeCard() {
  return `<!doctype html><html><head><meta charset="utf-8">${BASE}<style>
.home{position:absolute;inset:0;display:grid;grid-template-columns:1fr 404px;gap:64px;align-items:center;padding:0 72px 0 76px}
.home .eyebrow{margin:0 0 26px;font-size:15px;letter-spacing:.16em;text-transform:uppercase}
.name{font-size:104px;line-height:.95;letter-spacing:-.045em;margin-bottom:30px}
.pos{font-size:27px;font-weight:500;color:#e2ebf2;margin-bottom:10px}
.pos span{color:#6f93b3;padding:0 8px}
.lab{font-size:21px;color:#a9bccb;margin-bottom:34px}
.interests{font-size:18px;line-height:1.55;color:#8eb9de;max-width:600px}
.site{position:absolute;left:76px;bottom:46px;font-size:19px;color:#6f93b3;letter-spacing:.02em}
.pic{position:relative}
.pic:before{content:'';position:absolute;left:0;top:-18px;width:66px;height:4px;background:#8eb9de}
.pic img{width:404px;height:404px;object-fit:cover;object-position:55% center;display:block;border-radius:3px;filter:saturate(.85) brightness(.95)}
</style></head><body><div class="glow"></div><div class="home"><div>
<p class="eyebrow">Artificial Intelligence &amp; Computational Biology</p>
<h1 class="name">Ziheng Duan</h1>
<p class="pos">Postdoctoral researcher<span>·</span>Yale University</p>
<p class="lab">Prof. Mark Gerstein’s lab</p>
<p class="interests">Virtual cells for precision medicine · AI for therapeutic discovery · Closed-loop AI for science</p>
</div><figure class="pic"><img src="file://${path.join(A, 'portrait-1080.webp')}"></figure></div>
<p class="site">zihengduan.cn</p></body></html>`;
}
function icon(size, radius) {
  return `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Gelasio;src:url(${FONT}) format('woff2')}
html,body{margin:0;width:${size}px;height:${size}px;background:transparent}
div{width:${size}px;height:${size}px;border-radius:${radius}px;background:#00356b;color:#fff;display:grid;place-items:center;
font:${Math.round(size * 0.5)}px/1 Gelasio,serif;letter-spacing:${-size * 0.02}px;padding-top:${Math.round(size * 0.02)}px;box-sizing:border-box}
</style></head><body><div>ZD</div></body></html>`;
}
(async () => {
  const b = await chromium.launch();
  fs.mkdirSync(path.join(A, 'og'), { recursive: true });
  const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  const shots = [['home', homeCard()], ...PAPERS.map(x => [x[0], paperCard(x)])];
  for (const [name, html] of shots) {
    const tmp = path.join(HERE, '_card.html'); fs.writeFileSync(tmp, html);
    await p.goto('file://' + tmp, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(150);
    const fit = await p.evaluate(() => { const t = document.querySelector('.title'); return t ? t.style.fontSize || '50px' : '' });
    await p.screenshot({ path: path.join(A, 'og', name + '.jpg'), type: 'jpeg', quality: 88 });
    console.log('card', name, fit, fs.statSync(path.join(A, 'og', name + '.jpg')).size);
  }
  for (const [file, size, radius] of [['favicon-32.png', 32, 5], ['apple-touch-icon.png', 180, 0], ['icon-192.png', 192, 24], ['icon-512.png', 512, 64]]) {
    const q = await b.newPage({ viewport: { width: size, height: size }, deviceScaleFactor: 1 });
    const tmpi = path.join(HERE, '_icon.html'); fs.writeFileSync(tmpi, icon(size, radius));
    await q.goto('file://' + tmpi, { waitUntil: 'load' });
    await q.evaluate(() => document.fonts.ready); await q.waitForTimeout(80);
    await q.screenshot({ path: path.join(A, file), omitBackground: true });
    console.log('icon', file, fs.statSync(path.join(A, file)).size);
    await q.close();
  }
  await b.close();
})();
