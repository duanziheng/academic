'use strict';
const $=(s)=>document.querySelector(s), $$=(s)=>[...document.querySelectorAll(s)];
const theme=$('#theme-toggle');
function themeLabel(){const dark=document.documentElement.dataset.theme==='dark';theme?.setAttribute('aria-pressed',String(dark));theme?.setAttribute('aria-label',`Switch to ${dark?'light':'dark'} mode`);const tc=$('meta[name="theme-color"]');if(tc)tc.content=dark?'#071522':'#f7f8fa'}
themeLabel();theme?.addEventListener('click',()=>{const t=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=t;try{localStorage.setItem('theme',t)}catch{}themeLabel()});
$('.menu-toggle')?.addEventListener('click',e=>{const open=e.currentTarget.getAttribute('aria-expanded')==='true';e.currentTarget.setAttribute('aria-expanded',String(!open));$('#mobile-nav').hidden=open});
$$('#mobile-nav a').forEach(a=>a.addEventListener('click',()=>{$('#mobile-nav').hidden=true;$('.menu-toggle').setAttribute('aria-expanded','false')}));
$$('[data-close]').forEach(b=>b.addEventListener('click',()=>b.closest('dialog').close()));
$$('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close()}}));
const pq=$('#publication-query'),pr=$('#publication-role');
function filterPubs(){if(!pq)return;const q=pq.value.trim().toLowerCase(),y=$('#publication-year').value,t=$('#publication-type').value,r=pr?.value||'';let count=0;$$('#publication-list .paper').forEach(p=>{const show=(!q||p.dataset.search.includes(q))&&(!y||p.dataset.year===y)&&(!t||p.dataset.type===t)&&(!r||p.dataset.role===r);p.hidden=!show;if(show)count++});
 // A filter opens the folded consortium group when it matches there, and closes it again once cleared.
 const active=!!(q||y||t||r);$$('#publication-list .consortium-group').forEach(g=>{const n=g.querySelectorAll('.paper:not([hidden])').length;g.hidden=!n;if(active&&n&&!g.open){g.open=true;g.dataset.auto='1'}else if(!active&&g.dataset.auto){g.open=false;delete g.dataset.auto}});
 $$('#publication-list .year-group').forEach(g=>{let first=true;g.querySelectorAll(':scope>.year-papers>.paper').forEach(p=>{p.classList.toggle('first-visible',first&&!p.hidden);if(!p.hidden)first=false});g.hidden=!g.querySelector('.paper:not([hidden])')});
 $('#publication-count').textContent=`${count} publication${count===1?'':'s'}`;$('#no-results').hidden=count!==0;const url=new URL(location.href);for(const[k,v]of Object.entries({q,year:y,type:t,role:r})){if(v)url.searchParams.set(k,v);else url.searchParams.delete(k)}history.replaceState(null,'',url)}
if(pq){const params=new URLSearchParams(location.search);pq.value=params.get('q')||'';$('#publication-year').value=params.get('year')||'';$('#publication-type').value=params.get('type')||'';if(pr)pr.value=params.get('role')||'';[pq,$('#publication-year'),$('#publication-type'),pr].filter(Boolean).forEach(el=>el.addEventListener('input',filterPubs));$('#clear-filters').addEventListener('click',()=>{pq.value='';$('#publication-year').value='';$('#publication-type').value='';if(pr)pr.value='';filterPubs();pq.focus()});filterPubs()}
let searchData;
async function openSearch(){$('#search-dialog').showModal();$('#site-search').focus();if(!searchData){$('#search-results').textContent='Loading…';try{const r=await fetch('/assets/content.json');if(!r.ok)throw Error();const d=await r.json();searchData=[{title:'News and latest updates',path:'/#news',type:'Page'},{title:'Research',path:'/#research',type:'Page'},{title:'Selected work',path:'/#publication',type:'Page'},{title:'Industry experience — Genesis Molecular AI',path:'/#experience',type:'Page'},{title:'Contact',path:'/#contact',type:'Page'},{title:'Academic service and teaching',path:'/#service',type:'Page'},...(d.research||[]).map(x=>({...x,type:'Research'})),...(d.news||[]).map(x=>({title:x.text,path:'/#news-'+x.date,type:`News · ${x.label}`})),...d.publications.map(x=>({...x,type:`Publication · ${x.year}`})),...d.talks.map(x=>({...x,type:`Talk · ${x.year}`}))]}catch{$('#search-results').textContent='Search could not load. Please try again.';return}}renderSearch()}
function renderSearch(){if(!searchData)return;const q=$('#site-search').value.trim().toLowerCase();const results=searchData.filter(x=>(x.title+' '+(x.authors||[]).join(' ')+' '+(x.venue||'')+' '+(x.event||'')+' '+(x.location||'')+' '+(x.summary||'')).toLowerCase().includes(q)).slice(0,15);const box=$('#search-results');box.replaceChildren();if(q==='hello'||q==='404'){const p=document.createElement('p');p.textContent=q==='hello'?"Hi, I’m Ziheng. Thanks for exploring.":'This cell hasn’t been annotated yet.';const a=document.createElement('a');a.href=q==='hello'?'/#contact':'/404.html';a.textContent=q==='hello'?'Let’s connect →':'Visit the unannotated cell →';a.addEventListener('click',()=>$('#search-dialog').close());box.append(p,a);return}if(!q){const p=document.createElement('p');p.textContent='Search by title, author, or research topic.';box.append(p);return}if(!results.length){const p=document.createElement('p');p.textContent='No results. Try a different keyword.';box.append(p)}results.forEach(x=>{const a=document.createElement('a');a.href=x.path;const small=document.createElement('small');small.textContent=x.type;a.append(small,...marked(x.title,q));a.addEventListener('click',()=>$('#search-dialog').close());box.append(a)});box.querySelector('a')?.classList.add('is-active')}
// Matched words are wrapped in <mark>; built from text nodes, never parsed as HTML.
function marked(text,q){const out=[],lower=text.toLowerCase();let i=0,j;while(q&&(j=lower.indexOf(q,i))>-1){if(j>i)out.push(document.createTextNode(text.slice(i,j)));const m=document.createElement('mark');m.textContent=text.slice(j,j+q.length);out.push(m);i=j+q.length}out.push(document.createTextNode(text.slice(i)));return out}
$('#search-open')?.addEventListener('click',openSearch);$('#site-search')?.addEventListener('input',renderSearch);
// Keyboard: "/" or Cmd/Ctrl+K opens search; arrows move through results; Enter opens the highlighted one.
function typing(el){return el&&(el.isContentEditable||/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName))}
document.addEventListener('keydown',e=>{if(e.defaultPrevented||!$('#search-dialog'))return;const k=e.key.toLowerCase();if(((e.metaKey||e.ctrlKey)&&k==='k')||(e.key==='/'&&!e.metaKey&&!e.ctrlKey&&!e.altKey&&!typing(e.target)&&!$('dialog[open]'))){e.preventDefault();if(!$('#search-dialog').open)openSearch()}});
$('#search-dialog')?.addEventListener('keydown',e=>{const links=$$('#search-results a');if(!links.length||!['ArrowDown','ArrowUp','Enter'].includes(e.key))return;let i=links.findIndex(a=>a.classList.contains('is-active'));if(e.key==='Enter'){if(e.target===$('#site-search')&&i>-1){e.preventDefault();links[i].click()}return}e.preventDefault();i=e.key==='ArrowDown'?Math.min(links.length-1,i+1):Math.max(0,i-1);links.forEach((a,n)=>a.classList.toggle('is-active',n===i));links[i].scrollIntoView({block:'nearest'})});
let citeRequest=0;
$$('[data-cite]').forEach(b=>b.addEventListener('click',async()=>{const request=++citeRequest;if(!$('#cite-dialog').open)$('#cite-dialog').showModal();$('#citation-work').textContent=b.dataset.citeTitle||'';$('#citation-text').textContent='Loading citation…';$('#cite-status').textContent='';$('#copy-citation').disabled=true;$('#download-citation').href=b.dataset.cite;$('#download-citation').download=b.dataset.citeFilename||'citation.bib';$('#download-citation').hidden=true;try{const r=await fetch(b.dataset.cite);if(!r.ok)throw Error();const text=await r.text();if(!/^\s*@(?:article|inproceedings|misc|book|incollection|proceedings|techreport)\s*[{(]/i.test(text))throw Error('Invalid citation');if(request!==citeRequest)return;$('#citation-text').textContent=text;$('#copy-citation').disabled=false;$('#download-citation').hidden=false}catch{if(request===citeRequest)$('#citation-text').textContent='Citation could not load. Please close this dialog and try again.'}}));
$('#copy-citation')?.addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('#citation-text').textContent);$('#cite-status').textContent='Citation copied.'}catch{$('#cite-status').textContent='Please select and copy the citation above, or download it.'}});
$('#contact-form')?.addEventListener('submit',e=>{e.preventDefault();const f=new FormData(e.currentTarget);const subject=encodeURIComponent(`Website message from ${f.get('name')}`);const body=encodeURIComponent(`${f.get('message')}\n\n${f.get('name')}\n${f.get('email')}`);location.href=`mailto:duanziheng1206@gmail.com?subject=${subject}&body=${body}`});

$('#cite-dialog')?.addEventListener('close',()=>{citeRequest++});

// Retire the upcoming badge after the scheduled presentation date.
$$('[data-event-date]').forEach(el=>{if(new Date()>new Date(el.dataset.eventDate+'T23:59:59-07:00'))el.hidden=true});

// Reflect the current homepage section without changing the URL while scrolling.
const sectionNav=$('.section-nav');
if(sectionNav){
 const sections=$$('.section-nav a').map(a=>document.getElementById(a.hash.slice(1))).filter(Boolean);
 const sectionLinks=$$('.section-nav a, .header-inner nav a, #mobile-nav a');
 let scheduled=false;
 function updateSection(){
  scheduled=false;
  const offset=($('.site-header')?.getBoundingClientRect().height||88)+48;
  let active='';
  for(const section of sections){if(section.getBoundingClientRect().top<=offset)active=section.id;}
  if(window.innerHeight+window.scrollY>=document.documentElement.scrollHeight-4)active=sections.at(-1)?.id||active;
  sectionLinks.forEach(a=>{const current=a.hash==='#'+active||(active==='phd-research'&&a.hash==='#research'&&!sectionNav.contains(a));if(current)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current')});
 }
 function scheduleSection(){if(!scheduled){scheduled=true;requestAnimationFrame(updateSection)}}
 addEventListener('scroll',scheduleSection,{passive:true});
 addEventListener('resize',scheduleSection);
 addEventListener('load',scheduleSection);
 updateSection();
}
function closeMobileMenu(){
 const menu=$('#mobile-nav'),toggle=$('.menu-toggle');
 if(menu&&!menu.hidden){menu.hidden=true;toggle?.setAttribute('aria-expanded','false')}
}
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('#mobile-nav')?.hidden){closeMobileMenu();$('.menu-toggle')?.focus()}});
document.addEventListener('click',e=>{if(!e.target.closest('.site-header'))closeMobileMenu()});
matchMedia('(min-width:1101px)').addEventListener('change',e=>{if(e.matches)closeMobileMenu()});





$$('[data-news-event-date]').forEach(el=>{if(new Date()>new Date(el.dataset.newsEventDate+'T23:59:59-07:00')){const p=el.querySelector('p');const first=p?.firstChild;if(first?.nodeType===Node.TEXT_NODE)first.textContent=first.textContent.replace(/^Upcoming talk:/,'Talk:')}});


// Small, opt-in surprises. The adjacent name remains the homepage link.
$$('[data-open-search]').forEach(button=>button.addEventListener('click',openSearch));
const graphHello=$('#graph-hello');
let graphTimer;
graphHello?.addEventListener('click',()=>{
 clearTimeout(graphTimer);
 graphHello.classList.add('show-graph');
 graphTimer=setTimeout(()=>graphHello.classList.remove('show-graph'),1400);
});
