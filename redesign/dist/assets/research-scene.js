/* Conceptual 3D geometry projected onto a native canvas. No libraries, tracking,
   external requests, or experimental data. Decorative; all content stays HTML. */
(() => {
  'use strict';
  const figure = document.querySelector('.research-scene');
  const section = document.querySelector('.research-overview');
  const canvas = document.getElementById('cellular-canvas');
  if (!figure || !section || !canvas) return;
  let ctx;
  try { ctx = canvas.getContext('2d', { alpha: true }); } catch { return; }
  if (!ctx) return; // The inline SVG remains visible without canvas support.
  const toggle = figure.querySelector('.motion-toggle');
  const title = document.getElementById('scene-title');
  const viewport = figure.querySelector('.scene-viewport');
  const cards = [...section.querySelectorAll('.current-interest')];
  const selectors = [...section.querySelectorAll('.scene-select')];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const compact = matchMedia('(max-width: 760px)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const labels = ['01 / Cellular states', '02 / Target networks', '03 / Scientific feedback'];
  let seed = 314159;
  const random = () => { seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296; };
  const TAU = Math.PI * 2;
  const clamp = (n, a, b) => Math.min(b, Math.max(a, n));
  const mix = (a, b, t) => a + (b - a) * t;
  let width = 480, height = 290, dpr = 1;
  let mode = 0, phase = 0, frame = 0, last = 0, visible = false;
  let pointer = { x: 0, y: 0 }, camera = { x: 0, y: 0 };
  let manuallyPlaying = false, paused = false;
  try { paused = localStorage.getItem('research-motion') === 'paused'; } catch { /* Optional. */ }
  const shell = [], filaments = [], network = [], edges = [];
  // An asymmetric cellular envelope, rather than a geographic globe.
  function membrane(u, v, scale = 1) {
    const ripple = 1 + .055 * Math.sin(3 * u + 2 * v) + .033 * Math.cos(5 * v - u);
    const r = Math.sin(v) * ripple * scale;
    return [1.12 * r * Math.cos(u), .84 * scale * Math.cos(v), .9 * r * Math.sin(u)];
  }
  for (let i = 0; i < 920; i++) {
    const u = i * 2.399963229728653;
    const v = Math.acos(1 - 2 * (i + .5) / 920);
    shell.push({ p: membrane(u, v), r: .38 + random() * .5, a: .2 + random() * .55 });
  }
  for (let j = 0; j < 10; j++) {
    const points = [];
    const v = Math.PI * (.12 + .76 * j / 9);
    for (let i = 0; i <= 108; i++) points.push(membrane(i / 108 * TAU, v));
    filaments.push(points);
  }
  // Irregular arcs give the shell a folded biological texture, not a wire globe.
  for (let j = 0; j < 7; j++) {
    const points = [];
    for (let i = 0; i <= 80; i++) {
      const v = .16 + i / 80 * (Math.PI - .32);
      points.push(membrane(j / 7 * TAU + .23 * Math.sin(v * 3 + j), v));
    }
    filaments.push(points);
  }
  for (let i = 0; i < 39; i++) {
    const a = random() * TAU, z = random() * 2 - 1, rr = Math.cbrt(random()) * .75;
    const r = Math.sqrt(1 - z * z) * rr;
    network.push([r * Math.cos(a) * 1.05, z * rr * .86, r * Math.sin(a)]);
  }
  for (let i = 0; i < network.length; i++) {
    const distances = network.map((p, j) => ({ j, d: p.reduce((v, x, k) => v + (x - network[i][k]) ** 2, 0) }))
      .filter(p => p.j !== i).sort((a, b) => a.d - b.d).slice(0, 3);
    for (const { j } of distances) if (j > i) edges.push([i, j]);
  }
  const targets = new Set([5, 17, 28]);
  const loop = [];
  for (let i = 0; i <= 120; i++) {
    const a = i / 120 * TAU;
    loop.push([1.2 * Math.cos(a), .38 * Math.sin(a), .9 * Math.sin(a)]);
  }
  function moving() { return !reduced.matches && !paused && (!compact.matches || manuallyPlaying); }
  function project(p) {
    const a = -.4 + phase * .038 + camera.x;
    const b = -.18 + camera.y;
    const x = p[0] * Math.cos(a) + p[2] * Math.sin(a);
    let z = -p[0] * Math.sin(a) + p[2] * Math.cos(a);
    const y = p[1] * Math.cos(b) - z * Math.sin(b);
    z = p[1] * Math.sin(b) + z * Math.cos(b);
    const perspective = 4.5 / (4.5 - z);
    const scale = Math.min(width * .325, height * .425);
    return { x: width * .5 + x * scale * perspective, y: height * .5 + y * scale * perspective, z, s: perspective };
  }
  function line(a, b, rgb, alpha, thickness = .65) {
    ctx.strokeStyle = `rgba(${rgb},${clamp(alpha, 0, 1)})`;
    ctx.lineWidth = thickness;
    ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
  }
  function dot(p, radius, rgb, alpha) {
    ctx.fillStyle = `rgba(${rgb},${clamp(alpha, 0, 1)})`;
    ctx.beginPath(); ctx.arc(p.x, p.y, Math.max(.1, radius * p.s), 0, TAU); ctx.fill();
  }
  function strokePath(points, rgb, alpha, thickness = .6) {
    let a = project(points[0]);
    for (let i = 1; i < points.length; i++) {
      const b = project(points[i]);
      line(a, b, rgb, alpha * (.4 + (a.z + b.z + 2.5) / 6), thickness);
      a = b;
    }
  }
  function render() {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);
    const size = Math.min(width, height);
    // Diffuse illumination and an understated grounded shadow, no bloom effect.
    let light = ctx.createRadialGradient(width * .48, height * .47, 0, width * .5, height * .5, size * .53);
    light.addColorStop(0, 'rgba(132,151,153,.07)'); light.addColorStop(.68, 'rgba(123,138,144,.025)'); light.addColorStop(1, 'rgba(123,138,144,0)');
    ctx.fillStyle = light; ctx.fillRect(0, 0, width, height);
    const fade = mode === 0 ? 1 : mode === 1 ? .43 : .32;
    const dots = shell.map(n => ({ ...n, q: project(n.p) })).sort((a, b) => a.q.z - b.q.z);
    for (const n of dots) if (n.q.z < 0) dot(n.q, n.r, '122,147,155', n.a * .4 * fade);
    for (const f of filaments) strokePath(f, '133,153,158', .19 * fade);
    // A folded nucleus inside the envelope.
    for (let j = 0; j < 5; j++) {
      const points = [];
      for (let i = 0; i <= 80; i++) {
        const a = i / 80 * TAU, v = (j + 1) / 6 * Math.PI;
        points.push([-.18 + .35 * Math.cos(a) * Math.sin(v), -.04 + .3 * Math.cos(v), .26 * Math.sin(a) * Math.sin(v)]);
      }
      strokePath(points, '169,157,134', mode === 0 ? .37 : .14, .65);
    }
    const nn = network.map(project);
    for (const [i, j] of edges) {
      const highlighted = mode === 1 && (targets.has(i) || targets.has(j));
      line(nn[i], nn[j], highlighted ? '184,157,113' : '151,165,168', highlighted ? .58 : mode === 0 ? .18 : .22, highlighted ? 1 : .65);
    }
    [...nn.keys()].sort((a, b) => nn[a].z - nn[b].z).forEach(i => {
      const highlighted = targets.has(i) && mode === 1;
      dot(nn[i], highlighted ? 3.5 : 1.6, highlighted ? '206,179,138' : '159,179,182', highlighted ? .98 : .64);
      if (highlighted) {
        ctx.strokeStyle = 'rgba(192,165,123,.35)'; ctx.lineWidth = .8;
        ctx.beginPath(); ctx.arc(nn[i].x, nn[i].y, 7 * nn[i].s, 0, TAU); ctx.stroke();
      }
    });
    for (const n of dots) if (n.q.z >= 0) dot(n.q, n.r, '155,180,185', n.a * .7 * fade);
    if (mode === 2) {
      strokePath(loop, '171,153,124', .45, .9);
      for (let k = 0; k < 3; k++) {
        const t = (phase * .034 + k / 3) % 1, pos = t * 120, i = Math.floor(pos);
        const p = loop[i].map((v, n) => mix(v, loop[i + 1][n], pos - i));
        dot(project(p), 3.1, '207,182,146', .95);
        for (let h = 1; h < 9; h++) {
          const a = (t - h * .004 + 1) % 1 * TAU;
          dot(project([1.2 * Math.cos(a), .38 * Math.sin(a), .9 * Math.sin(a)]), 1.2, '184,165,137', .36 * (1 - h / 9));
        }
      }
    }
    // Quiet framing marks: graphic cues only, not scale bars or measured axes.
    ctx.strokeStyle = 'rgba(156,166,170,.21)'; ctx.lineWidth = .7;
    [[18, 18, 1, 1], [width - 18, height - 18, -1, -1]].forEach(([x, y, sx, sy]) => {
      ctx.beginPath(); ctx.moveTo(x + 11 * sx, y); ctx.lineTo(x, y); ctx.lineTo(x, y + 11 * sy); ctx.stroke();
    });
  }
  function stop() { if (frame) cancelAnimationFrame(frame); frame = 0; last = 0; }
  function tick(now) {
    frame = 0;
    if (!visible || document.hidden || !moving()) { last = 0; return; }
    const interval = compact.matches ? 1000 / 24 : 1000 / 30;
    if (!last || now - last >= interval) {
      const dt = last ? Math.min((now - last) / 1000, .08) : 0;
      last = now; phase += dt;
      camera.x = mix(camera.x, pointer.x, .055); camera.y = mix(camera.y, pointer.y, .055);
      render();
    }
    frame = requestAnimationFrame(tick);
  }
  function sync() {
    const enabled = moving();
    section.dataset.motion = enabled ? 'on' : 'off'; figure.dataset.motion = section.dataset.motion;
    toggle.disabled = reduced.matches;
    toggle.textContent = reduced.matches ? 'Motion reduced' : enabled ? 'Pause motion' : 'Play motion';
    toggle.setAttribute('aria-pressed', String(enabled));
    toggle.setAttribute('aria-label', reduced.matches ? 'Animation disabled by reduced-motion preference' : enabled ? 'Pause all research motion' : 'Play research motion');
    if (!enabled) {
      pointer = { x: 0, y: 0 };
      cards.forEach(card => { card.style.removeProperty('--tilt-x'); card.style.removeProperty('--tilt-y'); });
    }
    if (enabled && visible && !document.hidden) { if (!frame) frame = requestAnimationFrame(tick); }
    else stop();
  }
  function resize() {
    const rect = viewport.getBoundingClientRect();
    width = Math.max(1, rect.width); height = Math.max(1, rect.height);
    dpr = Math.min(devicePixelRatio || 1, compact.matches ? 1.25 : 1.5);
    canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
    render(); sync();
  }
  function selectMode(next) {
    mode = next; title.textContent = labels[mode]; figure.dataset.scene = String(mode);
    cards.forEach((card, i) => { card.dataset.active = String(i === mode); });
    selectors.forEach((button, i) => button.setAttribute('aria-pressed', String(i === mode)));
    render();
  }
  toggle.addEventListener('click', () => {
    if (reduced.matches) return;
    const play = !moving(); paused = !play; manuallyPlaying = play;
    try { if (paused) localStorage.setItem('research-motion', 'paused'); else localStorage.removeItem('research-motion'); } catch { /* Optional. */ }
    sync();
  });
  selectors.forEach((button, i) => {
    button.hidden = false;
    button.addEventListener('click', () => selectMode(i));
    button.addEventListener('focus', () => selectMode(i));
  });
  cards.forEach((card, i) => {
    card.addEventListener('pointerenter', () => { if (fine.matches) selectMode(i); });
    card.addEventListener('pointermove', event => {
      if (!fine.matches || !moving()) return;
      const r = card.getBoundingClientRect();
      card.style.setProperty('--tilt-x', `${clamp((.5 - (event.clientY - r.top) / r.height) * 2.4, -1.2, 1.2)}deg`);
      card.style.setProperty('--tilt-y', `${clamp(((event.clientX - r.left) / r.width - .5) * 2.4, -1.2, 1.2)}deg`);
    });
    card.addEventListener('pointerleave', () => { card.style.removeProperty('--tilt-x'); card.style.removeProperty('--tilt-y'); });
  });
  viewport.addEventListener('pointermove', event => {
    if (!fine.matches || !moving()) return;
    const r = viewport.getBoundingClientRect();
    pointer = { x: clamp((event.clientX - r.left) / r.width - .5, -.5, .5) * .25, y: clamp((event.clientY - r.top) / r.height - .5, -.5, .5) * .16 };
  });
  viewport.addEventListener('pointerleave', () => { pointer = { x: 0, y: 0 }; });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => { visible = entries[0].isIntersecting; sync(); }, { threshold: .05 }).observe(figure);
  } else { visible = true; }
  if ('ResizeObserver' in window) new ResizeObserver(resize).observe(viewport);
  else window.addEventListener('resize', resize, { passive: true });
  reduced.addEventListener('change', () => { manuallyPlaying = false; sync(); render(); });
  compact.addEventListener('change', () => { manuallyPlaying = false; resize(); });
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('pagehide', stop);
  window.addEventListener('pageshow', sync);
  window.addEventListener('storage', event => { if (event.key === 'research-motion') { paused = event.newValue === 'paused'; sync(); } });
  resize(); selectMode(0);
  figure.dataset.ready = 'true'; toggle.hidden = false; sync();
})();
