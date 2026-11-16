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
      // The same counter runs on findbingo.org (and the retired bingo.vethomeguard.org). Pages away from
      // the guide's own address carry their site name, so findbingo.org's home never reads as the guide's.
      var host = location.hostname.replace(/^www\./, '');
      var site = /(^|\.)(findbingo\.org|bingo\.vethomeguard\.org)$/.test(host) ? '/' + host : '';
      data.p = site + location.pathname.replace(/\/index\.html$/, '/');
      data.q = '';
      // Retain referral attribution without query strings or fragments.
      try {
        var referrer = new URL(document.referrer);
        data.r = referrer.origin + referrer.pathname;
      } catch (_) { data.r = ''; }
      return data;
    };
    counter.count();
  };
  document.head.appendChild(script);
}());
