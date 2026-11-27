// Page views only. Never send directory filters, ZIPs, searches or form values.
(function () {
  'use strict';
  if (window.vhgAnalyticsLoaded) return;
  window.vhgAnalyticsLoaded = true;
  // Google Tag Manager for VHG's Google Ads account (container GTM-PGHMBBZK, owner direction Nov 24, 2026), guide only.
  // Conversions are not sent from here: assets/ads-measure.js sends the one call conversion, so nothing counts twice.
  if (location.hostname === 'guide.vethomeguard.org') {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({'gtm.start': new Date().getTime(), event: 'gtm.js'});
    var gtm = document.createElement('script');
    gtm.async = true;
    gtm.src = 'https://www.googletagmanager.com/gtm.js?id=GTM-PGHMBBZK';
    document.head.appendChild(gtm);
  }
  // Ad visits on the guide itself: assets/ads-measure.js loads Google's ad tag only for people who came from our ad.
  if (location.hostname === 'guide.vethomeguard.org' && document.currentScript && document.currentScript.src) {
    var ads = document.createElement('script');
    ads.defer = true;
    ads.src = new URL('ads-measure.js', document.currentScript.src).href;
    document.head.appendChild(ads);
  }
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
      // Only ad and campaign tags survive from the query (utm_source, utm_medium, utm_campaign), so a paid
      // Facebook visit shows as its campaign instead of blending into ordinary Facebook visits. Nothing typed is kept.
      data.q = '';
      try {
        var params = new URLSearchParams(location.search), kept = [];
        ['utm_source', 'utm_medium', 'utm_campaign'].forEach(function (k) {
          var v = (params.get(k) || '').replace(/[^\w.-]/g, '').slice(0, 40);
          if (v) kept.push(k + '=' + v);
        });
        if (kept.length) data.q = '?' + kept.join('&');
      } catch (_) { data.q = ''; }
      // Retain referral attribution without query strings or fragments.
      try {
        var referrer = new URL(document.referrer);
        data.r = referrer.origin + referrer.pathname;
      } catch (_) { data.r = ''; }
      return data;
    };
    counter.count();
    // Donation clicks: one event each time someone taps a link to a donation page, so ads can be judged by gifts started.
    document.addEventListener('click', function (e) {
      var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
      if (!a || !/zeffy\.com|\/donate(\.html)?(\b|$)|givebutter|paypal\.com\/donate/i.test(a.href)) return;
      counter.count({path: 'click/donate', title: 'Donate click', event: true});
    }, true);
    // Weekly win count: a hall or reader starting a listing claim or a correction email to us.
    // Only the kind of action is sent, never the listing, the address or anything typed.
    document.addEventListener('click', function (e) {
      var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
      if (!a) return;
      var href = a.getAttribute('href') || '', kind = '';
      if (/^mailto:(travis@vethomeguard\.org|veteranhomeguardians@gmail\.com)/i.test(href)) {
        kind = /subject=[^&]*correction/i.test(href) ? 'email-correction' : 'email-us';
      } else if (/ohiobingo\.org\/claim(\.html)?|[?&#\/]claim\b/i.test(a.href)) {
        kind = 'claim';
      }
      if (kind) counter.count({path: 'click/' + kind, title: 'Win: ' + kind, event: true});
    }, true);
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
