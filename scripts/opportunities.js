// Veteran programs pages (scripts/build_opportunities.py, served as assets/opportunities.js).
// Pick a county to move the programs that name it, then those in its region, to the top; pick a kind of help to
// show only that kind. Without this script every program is still listed, in the page's own order.
(function () {
  'use strict';
  var form = document.getElementById('opp-filter');
  if (!form) return;
  var county = document.getElementById('opp-county');
  var cat = document.getElementById('opp-cat');
  var status = document.getElementById('opp-status');
  var each = function (list, fn) { Array.prototype.forEach.call(list, fn); };
  var cards = Array.prototype.slice.call(document.querySelectorAll('[data-opp]'));
  var tiers = document.querySelectorAll('[data-tier]');
  var list = function (tier) { var s = document.getElementById('tier-' + tier); return s ? s.querySelector('[data-list]') : null; };
  var heading = function (tier) { return document.getElementById('tier-' + tier + '-h'); };
  var yours = list('yours'), nearby = list('nearby'), local = list('local');
  var localDefault = heading('local') ? heading('local').textContent : '';
  var state = form.getAttribute('data-state') || '';
  cards.forEach(function (c, i) { c.oppHome = c.parentNode; c.oppIndex = i; });

  function apply() {
    var cv = county ? county.value : '';
    var opt = county && county.selectedIndex > 0 ? county.options[county.selectedIndex] : null;
    var region = opt ? opt.getAttribute('data-region') : '';
    var kind = cat ? cat.value : '';
    // Put every program back where the page had it, then move the chosen county's up.
    cards.forEach(function (c) { c.oppHome.appendChild(c); });
    if (cv && local) {
      cards.forEach(function (c) {
        if (c.oppHome !== local) return;
        if ((c.getAttribute('data-counties') || '').indexOf('|' + cv + '|') >= 0) yours.appendChild(c);
        else if (region && (c.getAttribute('data-regions') || '').indexOf('|' + region + '|') >= 0) nearby.appendChild(c);
      });
    }
    var shown = 0;
    cards.forEach(function (c) {
      var ok = !kind || c.getAttribute('data-cat') === kind;
      c.hidden = !ok;
      if (ok) shown += 1;
    });
    each(document.querySelectorAll('[data-group]'), function (d) {
      var any = d.querySelector('[data-opp]:not([hidden])');
      d.hidden = !any;
      if (kind && any) d.open = true;
    });
    each(tiers, function (t) { t.hidden = !t.querySelector('[data-opp]:not([hidden])'); });
    var name = opt ? opt.textContent : '';
    if (heading('yours')) heading('yours').textContent = 'Serves ' + name + ' County';
    if (heading('nearby')) heading('nearby').textContent = 'Nearby in ' + (opt ? opt.getAttribute('data-region-name') : '') + ' ' + state;
    if (heading('local')) heading('local').textContent = cv ? 'Elsewhere in ' + state : localDefault;
    var mine = yours ? yours.querySelectorAll('[data-opp]:not([hidden])').length : 0;
    var words = 'Showing ' + shown + (shown === 1 ? ' program' : ' programs');
    if (kind) words += ' for ' + cat.options[cat.selectedIndex].textContent.replace(/\s*\(\d+\)$/, '').toLowerCase();
    if (cv) words += mine ? ', with ' + mine + ' that name ' + name + ' County first.' : '. None name ' + name + ' County yet, so nearby and statewide programs come first.';
    else words += '.';
    status.textContent = words;
    if (window.history && history.replaceState && window.URLSearchParams) {
      var q = new URLSearchParams(location.search);
      if (cv) q.set('county', cv); else q.delete('county');
      if (kind) q.set('cat', kind); else q.delete('cat');
      var s = q.toString();
      history.replaceState(null, '', location.pathname + (s ? '?' + s : '') + location.hash);
    }
  }

  if (window.URLSearchParams) {
    var q = new URLSearchParams(location.search);
    var pick = function (select, value) {
      if (!select || !value) return;
      each(select.options, function (o) { if (o.value === value) select.value = value; });
    };
    pick(county, q.get('county'));
    pick(cat, q.get('cat'));
  }
  if (county) county.addEventListener('change', apply);
  if (cat) cat.addEventListener('change', apply);
  form.hidden = false;
  apply();
}());
