/* Restored noir particle study. Exact spherical geometry, no radial noise or
   unequal axis scaling. Decorative only; academic content remains in HTML. */
(() => {
  'use strict';
  const figure = document.querySelector('.research-scene');
  const section = document.querySelector('.research-overview');
  const canvas = document.getElementById('cellular-canvas');
  if (!figure || !section || !canvas) return;
  let ctx;
  try { ctx = canvas.getContext('2d', { alpha: true }); } catch { return; }
  if (!ctx) return;
  const title = document.getElementById('scene-title');
  const viewport = figure.querySelector('.scene-viewport');
  const atlas = section.querySelector('.atlas-journey');
  const cards = [...section.querySelectorAll('.current-interest')];
  const selectors = [...section.querySelectorAll('.scene-select')];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const compact = matchMedia('(max-width: 760px)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const labels = ['01 / Cellular states', '02 / Target networks', '03 / Scientific feedback'];
  const TAU = Math.PI * 2, DISTANCE = 4.5;
  const clamp = (n, a, b) => Math.min(b, Math.max(a, n));
  const mix = (a, b, t) => a + (b - a) * t;
  let seed = 314159;
  const random = () => { seed = (1664525 * seed + 1013904223) >>> 0; return seed / 4294967296; };
  let width = 480, height = 290, dpr = 1;
  let mode = 0, phase = 0, atlasPhase = 0, frame = 0, last = 0;
  let pointer = { x: 0, y: 0 }, camera = { x: 0, y: 0 };
  const visible = new Set();
  const shell = [], filaments = [], nucleus = [], network = [], edges = [];
  function membrane(u, v, scale = 1) {
    const r = Math.sin(v) * scale;
    return [r * Math.cos(u), scale * Math.cos(v), r * Math.sin(u)];
  }
  for (let i = 0; i < 920; i++) {
    const u = i * 2.399963229728653, v = Math.acos(1 - 2 * (i + .5) / 920);
    shell.push({ p: membrane(u, v), r: .38 + random() * .5, a: .2 + random() * .55 });
  }
  for (let j = 0; j < 9; j++) {
    const points = [], v = Math.PI * (j + 1) / 10;
    for (let i = 0; i <= 108; i++) points.push(membrane(i / 108 * TAU, v));
    filaments.push(points);
  }
  for (let j = 0; j < 7; j++) {
    const points = [];
    for (let i = 0; i <= 108; i++) points.push(membrane(j / 7 * TAU, i / 108 * Math.PI));
    filaments.push(points);
  }
  for (let j = 0; j < 5; j++) {
    const points = [], v = (j + 1) / 6 * Math.PI;
    for (let i = 0; i <= 80; i++) {
      const p = membrane(i / 80 * TAU, v, .32);
      points.push([p[0] - .16, p[1] - .035, p[2]]);
    }
    nucleus.push(points);
  }
  for (let i = 0; i < 39; i++) {
    const a = random() * TAU, z = random() * 2 - 1, rr = Math.cbrt(random()) * .74;
    const r = Math.sqrt(1 - z * z) * rr;
    network.push([r * Math.cos(a), z * rr, r * Math.sin(a)]);
  }
  for (let i = 0; i < network.length; i++) {
    const nearest = network.map((p, j) => ({ j, d: p.reduce((v, x, k) => v + (x - network[i][k]) ** 2, 0) }))
      .filter(p => p.j !== i).sort((a, b) => a.d - b.d).slice(0, 3);
    for (const { j } of nearest) if (j > i) edges.push([i, j]);
  }
  const targets = new Set([5, 17, 28]);
  const halos = atlas ? [...atlas.querySelectorAll('.scale-halo')] : [];
  const atlasLabels = atlas ? [...atlas.querySelectorAll('.atlas-labels span')] : [];
  const atlasPath = atlas?.querySelector('#atlas-flow');
  const atlasDot = atlas?.querySelector('.atlas-flow-dot');
  const atlasLength = atlasPath?.getTotalLength() || 0;
  // No playback UI. Preserve automatic desktop motion and a static mobile view.
  function moving() { return !reduced.matches && !compact.matches; }
  function scale() { return Math.min(width * .325, height * .40); }
  function project(p) {
    const a = -.4 + phase * .038 + camera.x, b = -.18 + camera.y;
    const x = p[0] * Math.cos(a) + p[2] * Math.sin(a);
    let z = -p[0] * Math.sin(a) + p[2] * Math.cos(a);
    const y = p[1] * Math.cos(b) - z * Math.sin(b);
    z = p[1] * Math.sin(b) + z * Math.cos(b);
    const perspective = DISTANCE / (DISTANCE - z);
    return { x: width * .5 + x * scale() * perspective, y: height * .5 + y * scale() * perspective, z, s: perspective };
  }
  function line(a, b, rgb, alpha, thickness = .65) {
    ctx.strokeStyle = `rgba(${rgb},${clamp(alpha, 0, 1)})`; ctx.lineWidth = thickness;
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
      line(a, b, rgb, alpha * (.4 + (a.z + b.z + 2.5) / 6), thickness); a = b;
    }
  }
  function render() {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, width, height);
    // Perspective silhouette of a unit sphere: one exact circle in every view.
    const radius = scale() * DISTANCE / Math.sqrt(DISTANCE * DISTANCE - 1);
    const light = ctx.createRadialGradient(width * .46, height * .43, 0, width * .5, height * .5, radius);
    light.addColorStop(0, 'rgba(163,151,131,.055)'); light.addColorStop(1, 'rgba(163,151,131,0)');
    ctx.fillStyle = light; ctx.beginPath(); ctx.arc(width * .5, height * .5, radius, 0, TAU); ctx.fill();
    const fade = mode === 0 ? 1 : mode === 1 ? .48 : .38;
    const dots = shell.map(n => ({ ...n, q: project(n.p) })).sort((a, b) => a.q.z - b.q.z);
    for (const n of dots) if (n.q.z < 0) dot(n.q, n.r, '132,147,146', n.a * .4 * fade);
    for (const f of filaments) strokePath(f, '146,151,142', .19 * fade);
    for (const f of nucleus) strokePath(f, '178,157,124', mode === 0 ? .40 : .17, .65);
    const nn = network.map(project);
    for (const [i, j] of edges) {
      const highlighted = mode === 1 && (targets.has(i) || targets.has(j));
      line(nn[i], nn[j], highlighted ? '184,157,113' : '151,165,161', highlighted ? .58 : mode === 0 ? .18 : .22, highlighted ? 1 : .65);
    }
    [...nn.keys()].sort((a, b) => nn[a].z - nn[b].z).forEach(i => {
      const highlighted = targets.has(i) && mode === 1;
      dot(nn[i], highlighted ? 3.5 : 1.6, highlighted ? '206,179,138' : '159,179,173', highlighted ? .98 : .64);
      if (highlighted) {
        ctx.strokeStyle = 'rgba(192,165,123,.35)'; ctx.lineWidth = .8;
        ctx.beginPath(); ctx.arc(nn[i].x, nn[i].y, 7 * nn[i].s, 0, TAU); ctx.stroke();
      }
    });
    for (const n of dots) if (n.q.z >= 0) dot(n.q, n.r, '170,177,165', n.a * .7 * fade);
    ctx.strokeStyle = `rgba(189,170,143,${mode === 0 ? .45 : .27})`; ctx.lineWidth = .7;
    ctx.beginPath(); ctx.arc(width * .5, height * .5, radius, 0, TAU); ctx.stroke();
    if (mode === 2) {
      // Center the feedback orbit on the exact same screen-space center as the sphere.
      const rotation = -.32;
      const c = Math.cos(rotation), s = Math.sin(rotation);
      const rx = radius * .82, ry = radius * .27;
      // Warm-gold primary orbit with one restrained Yale-blue accent arc.
      ctx.strokeStyle = 'rgba(207,173,105,.62)';
      ctx.lineWidth = 1.05;
      ctx.beginPath();
      ctx.ellipse(width * .5, height * .5, rx, ry, rotation, 0, TAU);
      ctx.stroke();
      ctx.strokeStyle = 'rgba(40,104,165,.48)';
      ctx.lineWidth = .9;
      ctx.beginPath();
      ctx.ellipse(width * .5, height * .5, rx * 1.018, ry * 1.018, rotation, .18 * Math.PI, .92 * Math.PI);
      ctx.stroke();
      const orbitColors = ['rgba(220,185,116,.98)', 'rgba(74,133,190,.94)', 'rgba(232,218,190,.96)'];
      for (let k = 0; k < 3; k++) {
        const angle = ((phase * .34 + k / 3) % 1) * TAU;
        const ex = rx * Math.cos(angle), ey = ry * Math.sin(angle);
        const x = width * .5 + ex * c - ey * s;
        const y = height * .5 + ex * s + ey * c;
        ctx.fillStyle = orbitColors[k];
        ctx.beginPath(); ctx.arc(x, y, 3, 0, TAU); ctx.fill();
      }
    }
    ctx.strokeStyle = 'rgba(156,166,170,.21)'; ctx.lineWidth = .7;
    [[18, 18, 1, 1], [width - 18, height - 18, -1, -1]].forEach(([x, y, sx, sy]) => {
      ctx.beginPath(); ctx.moveTo(x + 11 * sx, y); ctx.lineTo(x, y); ctx.lineTo(x, y + 11 * sy); ctx.stroke();
    });
  }
  function renderAtlas() {
    const progress = (atlasPhase / 12) % 1, active = Math.min(3, Math.floor(progress * 4));
    halos.forEach((halo, i) => { halo.style.opacity = i === active ? '.8' : '.25'; });
    atlasLabels.forEach((label, i) => { label.dataset.active = String(i === active); });
    if (atlasPath && atlasDot) {
      const p = atlasPath.getPointAtLength(atlasLength * progress);
      atlasDot.setAttribute('cx', p.x.toFixed(2)); atlasDot.setAttribute('cy', p.y.toFixed(2));
    }
  }
  function stop() { if (frame) cancelAnimationFrame(frame); frame = 0; last = 0; }
  function tick(now) {
    frame = 0;
    if (!visible.size || document.hidden || !moving()) { last = 0; return; }
    if (!last || now - last >= 1000 / 30) {
      const dt = last ? Math.min((now - last) / 1000, .08) : 0; last = now;
      if (visible.has(figure)) {
        phase += dt; camera.x = mix(camera.x, pointer.x, .055); camera.y = mix(camera.y, pointer.y, .055); render();
      }
      if (atlas && visible.has(atlas)) { atlasPhase += dt; renderAtlas(); }
    }
    frame = requestAnimationFrame(tick);
  }
  function sync() {
    const enabled = moving(); section.dataset.motion = enabled ? 'on' : 'off';
    for (const el of [figure, atlas].filter(Boolean)) {
      el.dataset.motion = section.dataset.motion;
      el.dataset.running = String(enabled && visible.has(el) && !document.hidden);
    }
    if (!enabled) {
      pointer = { x: 0, y: 0 };
      cards.forEach(card => { card.style.removeProperty('--tilt-x'); card.style.removeProperty('--tilt-y'); });
    }
    if (enabled && visible.size && !document.hidden) { if (!frame) frame = requestAnimationFrame(tick); }
    else stop();
  }
  function resize() {
    const rect = viewport.getBoundingClientRect(); width = Math.max(1, rect.width); height = Math.max(1, rect.height);
    dpr = Math.min(devicePixelRatio || 1, compact.matches ? 1.25 : 1.5);
    canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr); render(); sync();
  }
  function selectMode(next) {
    if (!Number.isInteger(next) || next < 0 || next >= labels.length) return;
    mode = next; title.textContent = labels[mode]; figure.dataset.scene = String(mode);
    cards.forEach((card, i) => { card.dataset.active = String(i === mode); });
    selectors.forEach((button, i) => button.setAttribute('aria-pressed', String(i === mode))); render();
  }
  selectors.forEach((button, i) => {
    button.hidden = false; button.disabled = false; button.addEventListener('click', () => selectMode(i)); button.addEventListener('focus', () => selectMode(i));
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
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) { if (entry.isIntersecting) visible.add(entry.target); else visible.delete(entry.target); } sync();
    }, { threshold: .05 });
    observer.observe(figure); if (atlas) observer.observe(atlas);
  } else { visible.add(figure); if (atlas) visible.add(atlas); }
  if ('ResizeObserver' in window) new ResizeObserver(resize).observe(viewport);
  else window.addEventListener('resize', resize, { passive: true });
  reduced.addEventListener('change', () => { sync(); render(); });
  compact.addEventListener('change', resize);
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('pagehide', stop); window.addEventListener('pageshow', sync);
  resize(); selectMode(0); renderAtlas(); figure.dataset.ready = 'true'; sync();
})();
