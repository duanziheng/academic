/* SVG research illustrations. No libraries, datasets, or external requests.
   Motion only animates the explanatory diagrams; it does not run a scientific model. */
(() => {
  'use strict';
  const section = document.querySelector('.research-overview');
  const figure = section?.querySelector('.research-scene');
  const atlas = section?.querySelector('.atlas-journey');
  if (!section || !figure || !atlas) return;
  const svg = figure.querySelector('svg');
  const layers = [...figure.querySelectorAll('.scene-layer')];
  const cards = [...section.querySelectorAll('.current-interest')];
  const selectors = [...section.querySelectorAll('.scene-select')];
  const toggles = [...section.querySelectorAll('.motion-toggle,.atlas-motion-toggle')];
  const labels = [...figure.querySelectorAll('.scene-steps span')];
  const title = figure.querySelector('#scene-title');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const compact = matchMedia('(max-width: 760px)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const scenes = [
    {title: 'Virtual cell modeling', steps: ['Cell state', 'Virtual model', 'Predicted responses'], description: "A cell's molecular state enters a virtual model, which predicts responses in different biological contexts."},
    {title: 'Designing cell-state interventions', steps: ['Disease state', 'Gene perturbation', 'Desired state'], description: 'A disease-associated cell state, a selected gene target within a network, and a desired cellular state guide intervention design.'},
    {title: 'Learning through experiments', steps: ['Propose', 'Test', 'Learn'], description: 'A proposed model informs experiments. Experimental evidence feeds back to refine the model and the next hypothesis.'}
  ];
  const clamp = (n, a, b) => Math.min(b, Math.max(a, n));
  let mode = 0, frame = 0, last = 0, paused = false, manualPlay = false;
  let mainTime = 0, atlasTime = 0, atlasFocus = -1;
  const visible = new Set();
  try { paused = localStorage.getItem('research-motion') === 'paused'; } catch { /* Optional preference storage. */ }
  const paths = new Map([...svg.querySelectorAll('path[id]')].map(path => [path.id, path]));
  const lengths = new Map([...paths].map(([id, path]) => [id, path.getTotalLength()]));
  const dots = layers.map(layer => [...layer.querySelectorAll('[data-track]')]);
  const floats = layers.map(layer => [...layer.querySelectorAll('[data-float]')]);
  const halos = [...atlas.querySelectorAll('.scale-halo')];
  const atlasLabels = [...atlas.querySelectorAll('.atlas-labels span')];
  const stack = [...atlas.querySelectorAll('.atlas-stack-layer')];
  const atlasDot = atlas.querySelector('.atlas-flow-dot');
  const atlasPath = atlas.querySelector('#atlas-flow');
  const atlasLength = atlasPath.getTotalLength();

  function moving() { return !reduced.matches && !paused && (!compact.matches || manualPlay); }
  function drawMain(time) {
    for (const dot of dots[mode]) {
      const t = (time / 3.8 + Number(dot.dataset.offset || 0)) % 1;
      const path = paths.get(dot.dataset.track);
      if (!path) continue;
      const p = path.getPointAtLength(lengths.get(path.id) * t);
      dot.setAttribute('cx', p.x.toFixed(2));
      dot.setAttribute('cy', p.y.toFixed(2));
      dot.style.opacity = (.35 + .65 * Math.sin(t * Math.PI)).toFixed(3);
    }
    for (const node of floats[mode]) {
      const p = Number(node.dataset.float);
      node.setAttribute('transform', `translate(0 ${(Math.sin(time * .85 + p * .65) * 2.2).toFixed(2)})`);
    }
    const ring = layers[mode].querySelector('.target-ring');
    if (ring) ring.setAttribute('r', (11.5 + Math.sin(time * 1.35) * 1.8).toFixed(2));
  }
  function drawAtlas(time) {
    const progress = (time / 12) % 1;
    const stage = Math.min(3, Math.floor(progress * 4));
    const active = atlasFocus < 0 ? stage : atlasFocus;
    halos.forEach((halo, i) => {
      const selected = i === active || (atlasFocus === 2 && i === 3);
      halo.style.opacity = selected ? '.9' : '.22';
      atlasLabels[i].dataset.active = String(selected);
    });
    const p = atlasPath.getPointAtLength(atlasLength * progress);
    atlasDot.setAttribute('cx', p.x.toFixed(2));
    atlasDot.setAttribute('cy', p.y.toFixed(2));
    stack.forEach((layer, i) => layer.setAttribute('transform', `translate(0 ${((i - 1) * Math.sin(time * .6) * 1.5).toFixed(2)})`));
  }
  function stop() { if (frame) cancelAnimationFrame(frame); frame = 0; last = 0; }
  function tick(now) {
    frame = 0;
    if (!moving() || document.hidden || !visible.size) { last = 0; return; }
    if (!last || now - last >= 1000 / 30) {
      const dt = last ? Math.min((now - last) / 1000, .10) : 0;
      last = now;
      if (visible.has(figure)) { mainTime += dt; drawMain(mainTime); }
      if (visible.has(atlas)) { atlasTime += dt; drawAtlas(atlasTime); }
    }
    frame = requestAnimationFrame(tick);
  }
  function sync() {
    const enabled = moving();
    section.dataset.motion = enabled ? 'on' : 'off';
    [figure, atlas].forEach(el => {
      el.dataset.motion = section.dataset.motion;
      el.dataset.running = String(enabled && visible.has(el) && !document.hidden);
    });
    for (const toggle of toggles) {
      toggle.hidden = false;
      toggle.disabled = reduced.matches;
      toggle.textContent = reduced.matches ? 'Static' : enabled ? 'Pause' : 'Play';
      toggle.setAttribute('aria-pressed', String(enabled));
      toggle.setAttribute('aria-label', reduced.matches ? 'Animations disabled by reduced-motion preference' : enabled ? 'Pause research animations' : 'Play research animations');
    }
    if (!enabled) {
      svg.style.removeProperty('--camera-x'); svg.style.removeProperty('--camera-y');
      cards.forEach(card => { card.style.removeProperty('--tilt-x'); card.style.removeProperty('--tilt-y'); });
    }
    if (enabled && visible.size && !document.hidden) { if (!frame) frame = requestAnimationFrame(tick); }
    else stop();
  }
  function selectMode(next, scroll = false) {
    if (!Number.isInteger(next) || next < 0 || next >= scenes.length) return;
    mode = next;
    figure.dataset.scene = String(mode);
    title.textContent = scenes[mode].title;
    svg.querySelector('title').textContent = scenes[mode].title;
    svg.querySelector('desc').textContent = scenes[mode].description;
    layers.forEach((layer, i) => { layer.toggleAttribute('hidden', i !== mode); layer.setAttribute('aria-hidden', String(i !== mode)); });
    labels.forEach((label, i) => { label.textContent = scenes[mode].steps[i]; });
    cards.forEach((card, i) => { card.dataset.active = String(i === mode); });
    selectors.forEach((button, i) => button.setAttribute('aria-pressed', String(i === mode)));
    drawMain(mainTime);
    if (scroll) {
      const rect = figure.getBoundingClientRect();
      if (rect.top < 80 || rect.bottom > innerHeight) figure.scrollIntoView({block: 'center', behavior: reduced.matches ? 'auto' : 'smooth'});
    }
  }
  for (const toggle of toggles) toggle.addEventListener('click', () => {
    if (reduced.matches) return;
    const play = !moving(); paused = !play; manualPlay = play;
    try { if (paused) localStorage.setItem('research-motion', 'paused'); else localStorage.removeItem('research-motion'); } catch { /* Optional. */ }
    sync();
  });
  selectors.forEach((button, i) => {
    button.hidden = false;
    button.addEventListener('click', () => selectMode(i, true));
    button.addEventListener('focus', () => selectMode(i));
  });
  cards.forEach((card, i) => {
    card.addEventListener('pointerenter', () => { if (fine.matches) selectMode(i); });
    card.addEventListener('pointermove', event => {
      if (!fine.matches || !moving()) return;
      const r = card.getBoundingClientRect();
      card.style.setProperty('--tilt-x', `${clamp((.5 - (event.clientY - r.top) / r.height) * 2, -1, 1)}deg`);
      card.style.setProperty('--tilt-y', `${clamp(((event.clientX - r.left) / r.width - .5) * 2, -1, 1)}deg`);
    });
    card.addEventListener('pointerleave', () => { card.style.removeProperty('--tilt-x'); card.style.removeProperty('--tilt-y'); });
  });
  svg.addEventListener('pointermove', event => {
    if (!fine.matches || !moving()) return;
    const r = svg.getBoundingClientRect();
    svg.style.setProperty('--camera-x', `${clamp((.5 - (event.clientY - r.top) / r.height) * 5, -2.5, 2.5)}deg`);
    svg.style.setProperty('--camera-y', `${clamp(((event.clientX - r.left) / r.width - .5) * 5, -2.5, 2.5)}deg`);
  });
  svg.addEventListener('pointerleave', () => { svg.style.removeProperty('--camera-x'); svg.style.removeProperty('--camera-y'); });
  [...section.querySelectorAll('.phd-theme')].forEach((row, i) => {
    row.addEventListener('pointerenter', () => { atlasFocus = i; drawAtlas(atlasTime); });
    row.addEventListener('pointerleave', () => { atlasFocus = -1; drawAtlas(atlasTime); });
    row.addEventListener('focusin', () => { atlasFocus = i; drawAtlas(atlasTime); });
    row.addEventListener('focusout', () => { atlasFocus = -1; drawAtlas(atlasTime); });
  });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      for (const entry of entries) { if (entry.isIntersecting) visible.add(entry.target); else visible.delete(entry.target); }
      sync();
    }, {threshold: .05}).observe(figure);
    new IntersectionObserver(entries => {
      for (const entry of entries) { if (entry.isIntersecting) visible.add(entry.target); else visible.delete(entry.target); }
      sync();
    }, {threshold: .05}).observe(atlas);
  } else { visible.add(figure); visible.add(atlas); }
  document.addEventListener('visibilitychange', sync);
  reduced.addEventListener('change', () => { manualPlay = false; sync(); });
  compact.addEventListener('change', () => { manualPlay = false; sync(); });
  selectMode(0); drawAtlas(0); sync();
})();
