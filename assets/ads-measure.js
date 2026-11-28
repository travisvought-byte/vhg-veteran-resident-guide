// Google Ad Grants measurement for Veteran Home Guardians (Google Ads account 121-655-5178).
// The Google tag loads on every page that includes this script, so Google Ads can confirm the tag is installed
// (Ad Grants requires working conversion tracking). Ad personalization signals are turned off.
// When a visitor taps a local office phone link, the page sends one "call a veterans office" conversion ping.
// Google Ads only counts it when the visitor arrived by clicking one of our Google ads; for everyone else Google
// has no ad click to match it to, so nothing is counted. Sending the ping on every tap also lets Google confirm
// the conversion is set up, which Ad Grants needs before the campaigns can run fully.
// Nothing about the county, the number or anything typed is sent: only that the conversion happened.
(function () {
  'use strict';
  if (window.vhgAdsMeasure) return;
  window.vhgAdsMeasure = true;
  var TAG = 'AW-18593576535';
  var CALL = TAG + '/rqT3CMn14L4dENfsjaJF';
  // National lines are never counted as reaching a local office: 988, 911, and the VA's national housing, benefits and main lines.
  var NATIONAL = {'988': 1, '911': 1, '8774243838': 1, '8008271000': 1, '8006982411': 1, '8772228387': 1};
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', TAG, {allow_ad_personalization_signals: false});
  var script = document.createElement('script');
  script.async = true;
  script.src = 'https://www.googletagmanager.com/gtag/js?id=' + TAG;
  document.head.appendChild(script);

  var counted = false;
  document.addEventListener('click', function (event) {
    if (counted || !event.target || !event.target.closest) return;
    var link = event.target.closest('a[href^="tel:"]');
    if (!link) return;
    var digits = link.getAttribute('href').replace(/\D/g, '').replace(/^1(?=\d{10}$)/, '');
    if (digits.length < 10 || NATIONAL[digits]) return;
    counted = true;
    window.gtag('event', 'conversion', {send_to: CALL, transport_type: 'beacon'});
  }, true);
}());
