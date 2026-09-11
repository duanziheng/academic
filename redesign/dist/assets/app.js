'use strict';
const $=(s)=>document.querySelector(s), $$=(s)=>[...document.querySelectorAll(s)];
const theme=$('#theme-toggle');
function themeLabel(){const dark=document.documentElement.dataset.theme==='dark';theme?.setAttribute('aria-pressed',String(dark));theme?.setAttribute('aria-label',`Switch to ${dark?'light':'dark'} mode`)}
themeLabel();theme?.addEventListener('click',()=>{const t=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=t;try{localStorage.setItem('theme',t)}catch{}themeLabel()});
$('.menu-toggle')?.addEventListener('click',e=>{const open=e.currentTarget.getAttribute('aria-expanded')==='true';e.currentTarget.setAttribute('aria-expanded',String(!open));$('#mobile-nav').hidden=open});
$$('#mobile-nav a').forEach(a=>a.addEventListener('click',()=>{$('#mobile-nav').hidden=true;$('.menu-toggle').setAttribute('aria-expanded','false')}));
$$('[data-close]').forEach(b=>b.addEventListener('click',()=>b.closest('dialog').close()));
$$('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close()}}));
const pq=$('#publication-query');
function filterPubs(){if(!pq)return;const q=pq.value.trim().toLowerCase(),y=$('#publication-year').value,t=$('#publication-type').value;let count=0;$$('#publication-list .paper').forEach(p=>{const show=(!q||p.dataset.search.includes(q))&&(!y||p.dataset.year===y)&&(!t||p.dataset.type===t);p.hidden=!show;if(show)count++});$('#publication-count').textContent=`${count} publication${count===1?'':'s'}`;$('#no-results').hidden=count!==0;const url=new URL(location.href);for(const[k,v]of Object.entries({q,year:y,type:t})){if(v)url.searchParams.set(k,v);else url.searchParams.delete(k)}history.replaceState(null,'',url)}
if(pq){const params=new URLSearchParams(location.search);pq.value=params.get('q')||'';$('#publication-year').value=params.get('year')||'';$('#publication-type').value=params.get('type')||'';[pq,$('#publication-year'),$('#publication-type')].forEach(el=>el.addEventListener('input',filterPubs));$('#clear-filters').addEventListener('click',()=>{pq.value='';$('#publication-year').value='';$('#publication-type').value='';filterPubs();pq.focus()});filterPubs()}
let searchData;
async function openSearch(){$('#search-dialog').showModal();$('#site-search').focus();if(!searchData){$('#search-results').textContent='Loading…';try{const r=await fetch('/assets/content.json');if(!r.ok)throw Error();const d=await r.json();searchData=[{title:'News and latest updates',path:'/#news',type:'Page'},{title:'Research',path:'/#research',type:'Page'},{title:'Selected work',path:'/#publication',type:'Page'},{title:'Industry experience — Genesis Molecular AI',path:'/#experience',type:'Page'},{title:'Contact',path:'/#contact',type:'Page'},{title:'Academic service and teaching',path:'/#service',type:'Page'},...d.publications.map(x=>({...x,type:`Publication · ${x.year}`})),...d.talks.map(x=>({...x,type:`Talk · ${x.year}`}))]}catch{$('#search-results').textContent='Search could not load. Please try again.';return}}renderSearch()}
function renderSearch(){if(!searchData)return;const q=$('#site-search').value.trim().toLowerCase();const results=searchData.filter(x=>(x.title+' '+(x.authors||[]).join(' ')+' '+(x.venue||'')+' '+(x.event||'')+' '+(x.location||'')).toLowerCase().includes(q)).slice(0,15);const box=$('#search-results');box.replaceChildren();if(!q){const p=document.createElement('p');p.textContent='Search by title, author, or research topic.';box.append(p);return}if(!results.length){const p=document.createElement('p');p.textContent='No results. Try a different keyword.';box.append(p)}results.forEach(x=>{const a=document.createElement('a');a.href=x.path;const small=document.createElement('small');small.textContent=x.type;a.append(small,document.createTextNode(x.title));a.addEventListener('click',()=>$('#search-dialog').close());box.append(a)})}
$('#search-open')?.addEventListener('click',openSearch);$('#site-search')?.addEventListener('input',renderSearch);
let citeRequest=0;
$$('[data-cite]').forEach(b=>b.addEventListener('click',async()=>{const request=++citeRequest;$('#cite-dialog').showModal();$('#citation-text').textContent='Loading citation…';$('#cite-status').textContent='';$('#copy-citation').disabled=true;$('#download-citation').href=b.dataset.cite;try{const r=await fetch(b.dataset.cite);if(!r.ok)throw Error();const text=await r.text();if(request!==citeRequest)return;$('#citation-text').textContent=text;$('#copy-citation').disabled=false}catch{if(request===citeRequest)$('#citation-text').textContent='Citation could not load. You can try the download link.'}}));
$('#copy-citation')?.addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('#citation-text').textContent);$('#cite-status').textContent='Citation copied.'}catch{$('#cite-status').textContent='Please select and copy the citation above, or download it.'}});
$('#contact-form')?.addEventListener('submit',e=>{e.preventDefault();const f=new FormData(e.currentTarget);const subject=encodeURIComponent(`Website message from ${f.get('name')}`);const body=encodeURIComponent(`${f.get('message')}\n\n${f.get('name')}\n${f.get('email')}`);location.href=`mailto:duanziheng1206@gmail.com?subject=${subject}&body=${body}`});

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
  sectionLinks.forEach(a=>{if(a.hash==='#'+active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current')});
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
