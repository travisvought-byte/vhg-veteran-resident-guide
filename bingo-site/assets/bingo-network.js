/* Shared state finder. Day matching uses venue-local dates; unknown/stale schedules never match. */
'use strict';
function localDate(timezone, now = new Date()) {
  const parts = new Intl.DateTimeFormat('en-US', {timeZone:timezone,year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(now);
  return ['year','month','day'].map(k=>parts.find(p=>p.type===k).value).join('-');
}
function onDate(r, iso) {
  if (!r.schedule || iso > r.review_due || (r.excluded_dates||[]).includes(iso)) return false;
  if (r.session_dates.length) return r.session_dates.includes(iso);
  const d=new Date(iso+'T12:00:00Z'), day=d.getUTCDay();
  return r.session_days.includes(day) || r.session_monthly.some(rule=>rule.weekday===day && rule.weeks.includes(Math.ceil(d.getUTCDate()/7)));
}
function matchesDay(r, day, today) {
  if (!day) return true;
  if (day==='today') return onDate(r,today);
  const start=new Date(today+'T12:00:00Z');
  // A weekday selection means an upcoming occurrence within the next 35 days.
  for(let n=0;n<35;n++) { const d=new Date(start);d.setUTCDate(d.getUTCDate()+n);if(d.getUTCDay()===Number(day)&&onDate(r,d.toISOString().slice(0,10)))return true; }
  return false;
}
function filterVenues(rows, filters, today) {
  const q=filters.q.trim().toLocaleLowerCase();
  return rows.filter(r=>(!q||[r.name,r.city,r.address].join(' ').toLocaleLowerCase().includes(q))&&(!filters.kind||r.kind===filters.kind)&&matchesDay(r,filters.day,today));
}
if(typeof module!=='undefined') module.exports={localDate,onDate,matchesDay,filterVenues};
if(typeof document!=='undefined') {
  const data=JSON.parse(document.getElementById('bingo-data').textContent), $=id=>document.getElementById(id);
  const params=new URLSearchParams(location.search);
  $('search').value=params.get('q')||'';
  $('day').value=params.get('day')||'';
  $('kind').value=params.get('kind')||'';
  $('filters').hidden=false;
  function draw() {
    const today=localDate(data.state.timezone), filters={q:$('search').value,day:$('day').value,kind:$('kind').value};
    const rows=filterVenues(data.venues,filters,today), ids=new Set(rows.map(r=>r.id));
    for(const r of data.venues){const el=document.getElementById(r.id);el.hidden=!ids.has(r.id);if(today>r.review_due)el.querySelector('.schedule').textContent='Schedule needs rechecking. Contact the organizer for current dates.';else if(r.session_dates.length && !r.session_dates.some(d=>d>=today))el.querySelector('.schedule').textContent='Listed event has passed. Contact the organizer for future dates.';}
    $('status').textContent=rows.length+' matching '+(rows.length===1?'place':'places')+(filters.day && filters.day!=='today'?' with a published occurrence within 35 days':'')+'. Times are local to '+data.state.name+'.';
    $('empty').hidden=rows.length>0;
    const p=new URLSearchParams();for(const [k,v] of Object.entries(filters))if(v)p.set(k,v);
    history.replaceState(null,'',location.pathname+(p.size?'?'+p:'')+location.hash);
  }
  $('filters').addEventListener('submit',e=>e.preventDefault());
  $('filters').addEventListener('input',draw);
  $('filters').addEventListener('change',draw);
  $('filters').addEventListener('reset',()=>setTimeout(draw,0));
  $('print').addEventListener('click',()=>window.print());
  draw();
}
