// Page views only. Never send directory filters, ZIPs, searches or form values.
(function () {
  'use strict';
  if (window.vhgAnalyticsLoaded) return;
  window.vhgAnalyticsLoaded = true;
  window.goatcounter = {no_onload: true, no_events: true};
  var script = document.createElement('script');
  script.async = true;
  script.src = 'https://gc.zgo.at/count.js';
  script.dataset.goatcounter = 'https://vhg-guide.goatcounter.com/count';
  script.onload = function () {
    var counter = window.goatcounter;
    var getData = counter.get_data;
    if (typeof getData !== 'function' || typeof counter.count !== 'function') return;
    counter.get_data = function (vars) {
      var data = getData(vars);
      // One dashboard counts every site (guide.vethomeguard.org, findbingo.org, ohiobingo.org and the rest).
      // Paths start with the site name, so each site's home page gets its own row instead of sharing "/".
      var host = location.hostname.replace(/^www\./, '');
      var site = '/' + host;
      // A state switch on a page arrives as an event named state/xx, kept under the same site name.
      data.p = vars && vars.event && vars.path ? site + '/' + String(vars.path).replace(/^\//, '')
        : site + location.pathname.replace(/\/index\.html$/, '/');
      data.q = '';
      // Retain referral attribution without query strings or fragments.
      try {
        var referrer = new URL(document.referrer);
        data.r = referrer.origin + referrer.pathname;
      } catch (_) { data.r = ''; }
      return data;
    };
    counter.count();
    // Which state's guide people read: the page marks the state it shows on <html data-edition>.
    var root = document.documentElement, shown = root.dataset.edition || '';
    if (window.MutationObserver) new MutationObserver(function () {
      var state = root.dataset.edition || '';
      if (!/^[A-Z]{2}$/.test(state) || state === shown) return;
      shown = state;
      counter.count({path: 'state/' + state.toLowerCase(), title: document.title, event: true});
    }).observe(root, {attributes: true, attributeFilter: ['data-edition']});
  };
  document.head.appendChild(script);
}());
