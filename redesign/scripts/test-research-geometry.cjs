/* Execute the production renderer against a small recording canvas. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../dist/assets/research-scene.js'), 'utf8');
const start = source.indexOf('  function scale()');
const end = source.indexOf('  function renderAtlas()', start);
assert(start >= 0 && end > start, 'Production renderer must be present');
const setup = `
const TAU=Math.PI*2, DISTANCE=4.5, dpr=1, mode=2;
let width=480, height=290, phase=0, camera={x:0,y:0};
const clamp=(n,a,b)=>Math.min(b,Math.max(a,n));
const shell=[],filaments=[],nucleus=[],network=[],edges=[],targets=new Set();
let circles=[],ellipses=[];
const ctx={setTransform(){},clearRect(){},beginPath(){},moveTo(){},lineTo(){},stroke(){},fill(){},
  createRadialGradient(){return {addColorStop(){}}},
  arc(x,y,r){circles.push({x,y,r})},
  ellipse(x,y,rx,ry,rotation){ellipses.push({x,y,rx,ry,rotation})}};
`;
const checks = `
let cases=0;
for(const size of [[276,225],[346,225],[500,290]]) {
  [width,height]=size;
  for(const time of [0,10,40,90,160]) {
    phase=time;
    for(const view of [[0,0],[-.125,-.08],[.125,.08]]) {
      [camera.x,camera.y]=view; circles=[];ellipses=[];render();
      assert.equal(ellipses.length,2);
      const e=ellipses[0], accent=ellipses[1], sphere=circles[0];
      assert.equal(e.x,sphere.x);assert.equal(e.y,sphere.y);
      assert.equal(accent.x,sphere.x);assert.equal(accent.y,sphere.y);
      assert.equal(e.x,width*.5);assert.equal(e.y,height*.5);
      assert.equal(e.rx,sphere.r*.82);assert.equal(e.ry,sphere.r*.27);
      assert.equal(accent.rx,e.rx*1.018);assert.equal(accent.ry,e.ry*1.018);
      const particles=circles.filter(p=>p.r===3);assert.equal(particles.length,3);
      for(const p of particles) {
        const dx=p.x-e.x,dy=p.y-e.y,c=Math.cos(e.rotation),s=Math.sin(e.rotation);
        const x=dx*c+dy*s,y=-dx*s+dy*c;
        assert(Math.abs((x/e.rx)**2+(y/e.ry)**2-1)<1e-10,'Particles must follow the same centered ellipse');
        assert(p.x>0&&p.x<width&&p.y>0&&p.y<height);
      }
      cases++;
    }
  }
}
console.log(JSON.stringify({cases,maxCenterErrorPixels:0}));
`;
vm.runInNewContext(setup+source.slice(start,end)+checks,{assert,console},{timeout:10000});
assert(!source.includes('localStorage'),'No unreachable persisted pause state');
assert(!source.includes('toggle.textContent'),'No playback instructions recreated by JavaScript');
assert(!source.includes('motion-toggle'),'No playback event handlers');
