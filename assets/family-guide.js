'use strict';
// Family guide filters. Choices live in the URL only: nothing is stored or sent.
(() => {
 const data = JSON.parse(document.getElementById('family-data').textContent);
 const $ = id => document.getElementById(id);
 const states = data.states, pa = data.protection_advocacy;
 const stageIds = new Set(data.stages.map(s => s.id));
 const stageLabel = new Map(data.stages.map(s => [s.id, s.label]));
 const needName = new Map(data.needs.map(n => [n.id, n.label.split(' (')[0]]));
 const counties = new Map(data.ohio_counties.map(c => [c.county, c]));
 const reduceMotion = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
 const el = (tag, attrs = {}, text = '') => { const e = document.createElement(tag); Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v)); if (text) e.textContent = text; return e; };
 const tel = p => 'tel:' + p.replace(/\D/g, '');
 const link = (href, text) => el('a', /^https?:/.test(href) ? {href, target: '_blank', rel: 'noopener'} : {href}, text);
 // Remember authored order so sorting can always return to it.
 const original = new Map();
 document.querySelectorAll('.resource').forEach((c, i) => original.set(c, i));
 let stage = 'all';

 function readParams() {
  const p = new URLSearchParams(location.search);
  const s = (p.get('state') || 'OH').toUpperCase();
  $('state').value = states[s] ? s : 'OH';
  const c = p.get('county') || '';
  $('county').value = counties.has(c) ? c : '';
  const st = p.get('stage') || 'all';
  stage = stageIds.has(st) ? st : 'all';
  const needs = new Set((p.get('need') || '').split(',').filter(n => needName.has(n)));
  document.querySelectorAll('input[name=need]').forEach(i => { i.checked = needs.has(i.value); });
  if (needs.size) $('needs-box').open = true;
 }

 const selectedNeeds = () => [...document.querySelectorAll('input[name=need]:checked')].map(i => i.value);

 function writeParams(state, county, needs) {
  const p = new URLSearchParams();
  p.set('state', state);
  if (state === 'OH' && county) p.set('county', county);
  if (stage !== 'all') p.set('stage', stage);
  if (needs.length) p.set('need', needs.join(','));
  history.replaceState(null, '', location.pathname + '?' + p.toString() + location.hash);
 }

 function matches(card, state, needs) {
  if (card.dataset.scope === 'OH' && state !== 'OH') return false;
  if ((card.dataset.replaced || '').split(' ').some(r => r.split(':')[0] === state)) return false;
  if (stage !== 'all' && !card.dataset.stages.split(' ').includes(stage)) return false;
  if (needs.length) {
   const cardNeeds = card.dataset.needs.split(' ');
   if (!cardNeeds.includes('any') && !needs.some(n => cardNeeds.includes(n))) return false;
  }
  return true;
 }

 // Show a container's cards: programs made for a checked need first, then the state's own programs, then authored order.
 function showCards(container, state, needs) {
  const cards = [...container.querySelectorAll('.resource')];
  let shown = 0, specific = 0;
  const rank = c => {
   const isMatch = needs.length > 0 && needs.some(n => c.dataset.needs.split(' ').includes(n));
   c.classList.toggle('match', isMatch);
   return (isMatch ? 0 : 2) + (c.dataset.scope === state ? 0 : 1);
  };
  cards.sort((a, b) => rank(a) - rank(b) || original.get(a) - original.get(b)).forEach(c => {
   const ok = matches(c, state, needs);
   c.hidden = !ok;
   if (ok) { shown++; if (c.classList.contains('match')) specific++; }
   container.append(c);
  });
  return {shown, specific};
 }

 function renderAnchors(state, county) {
  const name = states[state];
  $('anchors-title').textContent = 'Your first calls in ' + name;
  const list = $('anchor-list');
  list.replaceChildren();
  for (const a of data.anchors[state === 'OH' ? 'OH' : 'default']) {
   if (stage !== 'all' && !a.stages.includes(stage)) continue;
   const li = el('li'), parts = [];
   li.append(el('strong', {}, a.label + ': '));
   for (const item of a.items) {
    if (item.pa) parts.push(link(pa[state].url, pa[state].name), link(tel(pa[state].phone), pa[state].phone));
    else if (item.tel) parts.push(link(tel(item.tel), item.tel));
    else if (item.href) parts.push(link(item.href, item.text.replace('{state}', name)));
    else parts.push(document.createTextNode(item.text));
   }
   parts.forEach((n, i) => { if (i) li.append(' · '); li.append(n); });
   list.append(li);
  }
  const box = $('county-result');
  box.replaceChildren();
  if (state !== 'OH' || !county) return;
  const c = counties.get(county), wrap = el('div', {class: 'county-box'}), ul = el('ul');
  wrap.append(el('h4', {}, county + ' County'));
  const row = (label, nodes) => { const li = el('li'); li.append(el('strong', {}, label + ': ')); nodes.forEach((n, i) => { if (i) li.append(' · '); li.append(n); }); ul.append(li); };
  if (c.dd) row('County board of DD', [link(c.dd.url, county + ' County Board of DD'), link(tel(c.dd.phone), c.dd.phone)]);
  else row('County board of DD', [link('https://www.oacbdd.org/familyresources', 'pick ' + county + ' County on the map'), link('tel:8006176733', '800-617-6733')]);
  row('Veteran families', [link('./?state=OH&county=' + encodeURIComponent(county), county + ' County veterans service office')]);
  wrap.append(ul);
  box.append(wrap);
 }

 function updateReports(state) {
  document.querySelectorAll('a.report').forEach(a => {
   const subject = 'Family guide correction: ' + a.dataset.report + ' (' + state + ')';
   const body = 'Listing: ' + a.dataset.report + '\nState: ' + states[state] + '\nWhat should be corrected?\n\n\nPlease do not include a child\'s name, medical details or other personal information.';
   a.href = 'mailto:travis@vethomeguard.org?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  });
 }

 function apply(write = true) {
  const state = $('state').value, ohio = state === 'OH';
  $('county-wrap').hidden = !ohio;
  if (!ohio) $('county').value = '';
  const county = $('county').value, needs = selectedNeeds();
  document.querySelectorAll('.stage').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.stage === stage)));
  const main = showCards($('cards'), state, needs), mil = showCards($('military-cards'), state, needs);
  $('empty').hidden = main.shown > 0;
  $('military-count').textContent = mil.shown;
  const where = ohio ? (county ? county + ' County, Ohio' : 'Ohio') : states[state];
  const topic = stage === 'all' ? '' : ' for ' + stageLabel.get(stage).toLowerCase();
  let text = 'Showing ' + main.shown + (main.shown === 1 ? ' program' : ' programs') + topic + ' in ' + where + '.';
  if (needs.length) {
   const names = needs.map(n => needName.get(n).toLowerCase()).join(' or ');
   text += main.specific ? ' ' + main.specific + ' made for ' + names + ' are at the top; the rest help with any disability.' : ' None are only for ' + names + ', so these help with any disability.';
  }
  $('result-status').textContent = text;
  $('print-context').textContent = where + (stage === 'all' ? '' : ' · ' + stageLabel.get(stage)) + (needs.length ? ' · ' + needs.map(n => needName.get(n)).join(', ') : '');
  renderAnchors(state, county);
  $('cvso-link').href = './?state=' + state + (ohio && county ? '&county=' + encodeURIComponent(county) : '');
  $('back-guide').href = './?state=' + state;
  updateReports(state);
  if (write) writeParams(state, county, needs);
 }

 function renderAgencies() {
  const list = $('pa-list');
  Object.entries(states).forEach(([code, name]) => {
   const a = pa[code], li = el('li');
   li.append(el('strong', {}, name + ': '), link(a.url, a.name), ' · ', link(tel(a.phone), a.phone));
   list.append(li);
  });
 }

 // After a stage tap, bring the first calls and result count into view so the change is visible.
 function reveal() { if ($('anchors').scrollIntoView) $('anchors').scrollIntoView({behavior: reduceMotion ? 'auto' : 'smooth', block: 'start'}); }
 function openMilitary() { if (location.hash === '#military') $('military-details').open = true; }

 document.querySelectorAll('.stage').forEach(b => b.addEventListener('click', () => { stage = b.dataset.stage; apply(); reveal(); }));
 $('state').addEventListener('change', () => apply());
 $('county').addEventListener('change', () => apply());
 document.querySelectorAll('input[name=need]').forEach(i => i.addEventListener('change', () => apply()));
 document.querySelectorAll('[data-open-military]').forEach(a => a.addEventListener('click', () => { $('military-details').open = true; }));
 window.addEventListener('hashchange', openMilitary);
 $('print').addEventListener('click', () => window.print());
 $('share').addEventListener('click', async () => {
  const url = location.href.split('#')[0];
  try { await navigator.clipboard.writeText(url); $('share-status').textContent = 'Link copied. It includes only your state, county, stage and need choices.'; }
  catch { $('share-status').textContent = 'Copy this link: ' + url; }
 });
 readParams();
 renderAgencies();
 openMilitary();
 apply(false);
})();
