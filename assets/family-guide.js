'use strict';
// Family guide filters. Choices live in the URL only: nothing is stored or sent.
(() => {
 const data = JSON.parse(document.getElementById('family-data').textContent);
 const $ = id => document.getElementById(id);
 const states = data.states, pa = data.protection_advocacy;
 const stageIds = new Set(data.stages.map(s => s.id));
 const stageLabel = new Map(data.stages.map(s => [s.id, s.label]));
 const needIds = new Set(data.needs.map(n => n.id));
 const counties = new Map(data.ohio_counties.map(c => [c.county, c]));
 const ohioAnchors = $('anchor-list').innerHTML;
 const el = (tag, attrs = {}, text = '') => { const e = document.createElement(tag); Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v)); if (text) e.textContent = text; return e; };
 const digits = p => 'tel:' + p.replace(/\D/g, '');
 const link = (href, text, external = true) => { const a = el('a', external ? {href, target: '_blank', rel: 'noopener'} : {href}, text); return a; };
 let stage = 'all';

 function readParams() {
  const p = new URLSearchParams(location.search);
  const s = (p.get('state') || 'OH').toUpperCase();
  $('state').value = states[s] ? s : 'OH';
  const c = p.get('county') || '';
  $('county').value = counties.has(c) ? c : '';
  const st = p.get('stage') || 'all';
  stage = stageIds.has(st) ? st : 'all';
  const needs = new Set((p.get('need') || '').split(',').filter(n => needIds.has(n)));
  document.querySelectorAll('input[name=need]').forEach(i => { i.checked = needs.has(i.value); });
 }

 function selectedNeeds() { return [...document.querySelectorAll('input[name=need]:checked')].map(i => i.value); }

 function writeParams(state, county, needs) {
  const p = new URLSearchParams();
  p.set('state', state);
  if (state === 'OH' && county) p.set('county', county);
  if (stage !== 'all') p.set('stage', stage);
  if (needs.length) p.set('need', needs.join(','));
  history.replaceState(null, '', location.pathname + '?' + p.toString() + location.hash);
 }

 function matches(card, state, needs) {
  const scope = card.dataset.scope;
  if (scope === 'OH' && state !== 'OH') return false;
  const replaced = (card.dataset.replaced || '').split(' ').some(r => r.split(':')[0] === state);
  if (replaced) return false;
  if (stage !== 'all' && !card.dataset.stages.split(' ').includes(stage)) return false;
  if (needs.length) {
   const cardNeeds = card.dataset.needs.split(' ');
   if (!cardNeeds.includes('any') && !needs.some(n => cardNeeds.includes(n))) return false;
  }
  return true;
 }

 function anchorItem(label, nodes) {
  const li = el('li'); li.append(el('strong', {}, label + ': '));
  nodes.forEach((n, i) => { if (i) li.append(' · '); li.append(n); });
  return li;
 }

 function renderAnchors(state, county) {
  const name = states[state];
  $('anchors-title').textContent = 'Your first calls in ' + name;
  const list = $('anchor-list');
  if (state === 'OH') list.innerHTML = ohioAnchors;
  else {
   list.replaceChildren();
   const agency = pa[state];
   list.append(
    anchorItem('Parent center', [link('https://www.parentcenterhub.org/find-your-center/', 'find ' + name + "'s Parent Training and Information Center")]),
    anchorItem('Disability rights and legal help', [link(agency.url, agency.name), link(digits(agency.phone), agency.phone, false)]),
    anchorItem('Under age 3', [link('https://www.cdc.gov/FindEI', 'find ' + name + "'s early intervention program")]),
    anchorItem('Age 3 and older', [document.createTextNode('ask your local public school district for a free evaluation, in writing')]),
    anchorItem('Health care and insurance questions', [link('https://familyvoices.org/sao/', 'find your Family-to-Family Health Information Center')]));
  }
  const box = $('county-result');
  box.replaceChildren();
  if (state !== 'OH' || !county) return;
  const c = counties.get(county), wrap = el('div', {class: 'county-box'});
  wrap.append(el('h4', {}, county + ' County'));
  const ul = el('ul');
  if (c.dd) ul.append(anchorItem('County board of DD', [link(c.dd.url, c.dd.name), link(digits(c.dd.phone), c.dd.phone, false)]));
  else ul.append(anchorItem('County board of DD', [link('https://www.oacbdd.org/familyresources', 'choose ' + county + ' County on the directory map'), link('tel:8006176733', '800-617-6733 (state referral line)', false)]));
  ul.append(anchorItem('Under age 3', [document.createTextNode('Help Me Grow Early Intervention'), link('tel:8007554769', '800-755-4769', false)]));
  ul.append(anchorItem('Veteran families', [link('./?state=OH&county=' + encodeURIComponent(county), county + ' County veterans service office and local resources', false)]));
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
  let shown = 0;
  document.querySelectorAll('#cards .resource').forEach(card => { const ok = matches(card, state, needs); card.hidden = !ok; card.style.order = card.dataset.scope === 'OH' ? '0' : '1'; if (ok) shown++; });
  let mil = 0;
  document.querySelectorAll('#military-cards .resource').forEach(card => { const ok = matches(card, state, needs); card.hidden = !ok; if (ok) mil++; });
  $('empty').hidden = shown > 0;
  const where = ohio ? (county ? county + ' County, Ohio' : 'Ohio') : states[state];
  const topic = stage === 'all' ? 'all ages and topics' : stageLabel.get(stage).toLowerCase();
  const needText = needs.length ? ', matching ' + needs.map(n => data.needs.find(x => x.id === n).label.split(' (')[0].toLowerCase()).join(', ') + ' or any disability' : '';
  $('result-status').textContent = 'Showing ' + shown + (shown === 1 ? ' listing' : ' listings') + ' for ' + topic + ' in ' + where + needText + ', plus ' + mil + ' for military and veteran families.';
  renderAnchors(state, county);
  const guide = './?state=' + state + (ohio && county ? '&county=' + encodeURIComponent(county) : '');
  $('cvso-link').href = guide;
  $('back-guide').href = './?state=' + state;
  updateReports(state);
  if (write) writeParams(state, county, needs);
 }

 function renderAgencies() {
  const list = $('pa-list');
  Object.entries(states).forEach(([code, name]) => {
   const a = pa[code], li = el('li');
   li.append(el('strong', {}, name + ': '), link(a.url, a.name), ' · ', link(digits(a.phone), a.phone, false));
   list.append(li);
  });
 }

 document.querySelectorAll('.stage').forEach(b => b.addEventListener('click', () => { stage = b.dataset.stage; apply(); }));
 $('state').addEventListener('change', () => apply());
 $('county').addEventListener('change', () => apply());
 document.querySelectorAll('input[name=need]').forEach(i => i.addEventListener('change', () => apply()));
 $('print').addEventListener('click', () => window.print());
 $('share').addEventListener('click', async () => {
  const url = location.href.split('#')[0];
  try { await navigator.clipboard.writeText(url); $('share-status').textContent = 'Link copied. It includes only your state, county, stage and need choices.'; }
  catch { $('share-status').textContent = 'Copy this link: ' + url; }
 });
 readParams();
 renderAgencies();
 apply(false);
})();
