/* Place map: shows the places in a page's list on a map you can zoom, in the style of Nina's Map.
 * The list stays the page: the map only shows what the list shows, and every place on the map is also in the list.
 * Without JavaScript, or until the map files load, the map box stays hidden and the plain list is the page.
 *
 * Markup (written by scripts/place_map.py):
 *   <section class="pm-box" hidden data-pm-list="results" data-pm-base="(folder of the map files)" ...>
 *   - data-pm-list: id of the list container. The map follows it as the page redraws the list.
 *   - data-pm-base: folder with leaflet.js, leaflet.css, leaflet.markercluster.js and markercluster.css (loaded only when needed).
 *   - data-pm-zip-table: name of the page's ZIP code table ({"43334": [lat, lon]}), for cards marked with data-pm-zip.
 *   - data-pm-numbers="0": group nearby pins under a plain dot, with no numbers on it.
 *   - data-pm-dark="1": follow the device's dark mode (only on pages that have one).
 * Cards: any element in the list with data-pm-zip (or data-pm-lat and data-pm-lon) and an id gets a pin.
 *   data-pm-at="zip" says a data-pm-lat/lon point is the middle of the card's ZIP code (the pin's box then says so).
 *   data-pm-kind picks the pin color, data-pm-sub is the line under the name in the pin's box.
 * "Use my location" buttons: [data-pm-locate] with data-pm-zip-input, data-pm-zip-table and data-pm-form. The location
 *   stays on the device: the page finds the nearest ZIP code itself and searches it like a typed one.
 * Map pictures come from OpenStreetMap. Nothing else is sent anywhere, and nothing is stored except whether the map is hidden.
 */
(function () {
  'use strict';
  if (typeof document === 'undefined' || !document.querySelector || !document.addEventListener) return;
  if (window.PlaceMap) return;

  var CSS = [
    '.pm-box{margin:18px 0 10px;background:var(--card,#fff);border:1px solid var(--line,#cfd8d2);border-radius:14px;padding:4px 16px 12px}',
    '.pm-box[hidden],.pm-area[hidden],[data-pm-locate][hidden]{display:none!important}',
    '.pm-head{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:6px 14px}',
    '.pm-head h2{margin:12px 0 6px;font-size:1.3em;line-height:1.2}',
    '.pm-toggle,.pm-show,.pm-locate{font:inherit;font-size:17px;font-weight:700;line-height:1.2;min-height:48px;padding:6px 16px;border-radius:10px;cursor:pointer;',
    'border:2px solid var(--accent,#2f5a45);background:var(--card,#fff);color:var(--accent,#2f5a45)}',
    '.pm-toggle:hover,.pm-show:hover,.pm-locate:hover{text-decoration:underline}',
    '.pm-show{min-height:44px;font-size:16px;padding:4px 14px;margin:4px 0}',
    '.pm-locate{display:inline-flex;align-items:center;gap:8px}',
    '.pm-map{height:min(62vh,480px);min-height:300px;border-radius:10px;border:1px solid var(--line,#cfd8d2);background:#dfe7e4;z-index:0}',
    '.pm-map:focus-visible{outline:3px solid #b8862b;outline-offset:2px}',
    '.pm-hint,.pm-note{font-size:16px;line-height:1.45;margin:8px 0 0}',
    '.pm-legend{list-style:none;padding:0;margin:8px 0 0;display:flex;flex-wrap:wrap;gap:4px 20px;font-size:16px}',
    '.pm-legend li{display:flex;align-items:center;gap:8px;margin:0}',
    '.pm-pin{display:block;box-sizing:border-box;width:24px;height:24px;border-radius:50%;border:3px solid #fff;box-shadow:0 1px 5px rgba(0,0,0,.5);background:#2f7a4f}',
    '.pm-legend .pm-pin{display:inline-block;width:18px;height:18px;border-width:2px;flex:none}.pm-legend .pm-you{display:inline-block;width:16px;height:16px;border-width:3px;flex:none}',
    '.pm-k-game{background:#2f7a4f}.pm-k-nodays{background:#9a6b12}.pm-k-center{background:#1d5f8a}',
    '.pm-k-facility{background:#183449}.pm-k-assisted{background:#6a4a8c}.pm-k-vhg{background:#b5462a}',
    '.pm-you{display:block;box-sizing:border-box;width:22px;height:22px;border-radius:50%;background:#d0451b;border:4px solid #fff;box-shadow:0 0 0 3px #d0451b}',
    '.pm-icon:focus{outline:none}.pm-icon:focus-visible .pm-pin,.pm-icon:focus-visible .pm-you,.pm-cluster:focus-visible span{outline:4px solid #b8862b;outline-offset:2px}',
    '.pm-cluster span{display:block;box-sizing:border-box;width:38px;height:38px;border-radius:50%;background:#2f5a45;border:4px solid #fff;',
    'box-shadow:0 0 0 7px rgba(47,90,69,.3),0 1px 6px rgba(0,0,0,.4)}',
    '.pm-map .marker-cluster{background:rgba(24,52,73,.25);border-radius:50%}',
    '.pm-map .marker-cluster div{background:rgba(24,52,73,.9);color:#fff;font-weight:700;width:32px;height:32px;margin:4px;border-radius:50%;text-align:center;line-height:32px;font-size:14px}',
    '.pm-map.leaflet-container{font:16px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}',
    '.pm-box .pm-map .leaflet-bar a{width:44px;height:44px;line-height:44px;font-size:24px}',
    '.pm-map .leaflet-popup-content{margin:14px 16px;font-size:17px;line-height:1.4;min-width:210px}',
    '.pm-map .leaflet-popup-content-wrapper,.pm-map .leaflet-popup-tip{background:var(--card,#fff);color:var(--ink,#1f2f38)}',
    '.pm-box .pm-map a.leaflet-popup-close-button{width:40px;height:40px;font:28px/38px Tahoma,Verdana,sans-serif;color:var(--ink,#555)}',
    '.pm-pop strong{display:block;font-size:19px;line-height:1.25;padding-right:22px}',
    '.pm-pop .pm-sub{display:block;margin-top:4px}.pm-pop .pm-approx{display:block;margin-top:6px;font-size:15px;opacity:.85}',
    '.pm-acts{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}',
    '.pm-box .pm-acts a,.pm-box .pm-acts button{font:inherit;font-size:16px;font-weight:700;display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:4px 12px;',
    'border-radius:8px;text-decoration:none;cursor:pointer;border:2px solid var(--accent,#2f5a45);background:var(--card,#fff);color:var(--accent,#2f5a45)}',
    '.pm-box .pm-acts .pm-call{background:var(--green,#2f5a45);border-color:var(--green,#2f5a45);color:#fff}',
    '@media (max-width:760px){.pm-map{height:54vh;min-height:280px}.pm-box{padding:2px 12px 10px}}',
    '@media screen and (prefers-color-scheme:dark){.pm-dark .pm-map .leaflet-tile-pane{filter:brightness(.72) contrast(1.12) saturate(.75)}',
    '.pm-dark .pm-map{background:#22313a}.pm-dark .pm-pin,.pm-dark .pm-cluster span{border-color:#e4ecef}',
    '.pm-dark .pm-map .leaflet-bar a,.pm-box.pm-dark .pm-map .leaflet-bar a{background:#1a242b;color:#e4ecef;border-color:#3d4d55}.pm-dark .pm-map .leaflet-control-attribution{background:rgba(16,24,29,.85);color:#c3d0d6}',
    '.pm-box.pm-dark .pm-map .leaflet-control-attribution a{color:#9fd0ef}.pm-box.pm-dark .pm-map a.leaflet-popup-close-button{color:#c3d0d6}}',
    '@media print{.pm-box,.pm-show,[data-pm-locate]{display:none!important}}'
  ].join('');

  function addStyle() {
    if (document.getElementById('pm-style')) return;
    var s = document.createElement('style');
    s.id = 'pm-style';
    s.textContent = CSS;
    (document.head || document.documentElement).appendChild(s);
  }

  function store(key, value) {
    try {
      if (value === undefined) return window.localStorage.getItem(key);
      if (value === null) window.localStorage.removeItem(key); else window.localStorage.setItem(key, value);
    } catch (e) { /* private window or blocked storage: the map just starts shown */ }
    return null;
  }

  // The page's ZIP code table, read by name (a top-level const or let is not a window property).
  function table(name) {
    if (!/^[A-Za-z_$][\w$]*$/.test(name || '')) return null;
    try { return Function('return typeof ' + name + '!=="undefined"?' + name + ':null')(); } catch (e) { return null; }
  }

  function miles(a, b) {
    var r = Math.PI / 180, la = (b[0] - a[0]) * r, lo = (b[1] - a[1]) * r;
    var h = Math.sin(la / 2) * Math.sin(la / 2) + Math.cos(a[0] * r) * Math.cos(b[0] * r) * Math.sin(lo / 2) * Math.sin(lo / 2);
    return 3958.7613 * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(Math.max(0, 1 - h)));
  }

  function nearestZip(zips, at) {
    var best = null, bd = Infinity;
    for (var z in zips) {
      if (!Object.prototype.hasOwnProperty.call(zips, z)) continue;
      var c = zips[z];
      if (!c || Math.abs(c[0] - at[0]) > 3 || Math.abs(c[1] - at[1]) > 4) continue; // only nearby ZIP codes need the exact sum
      var d = miles(at, c);
      if (d < bd) { bd = d; best = z; }
    }
    return best ? { zip: best, miles: bd } : null;
  }

  function reduced() {
    try { return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; }
  }

  // Leaflet and the clustering add-on load from this site, only once a list has places to show.
  var loading = null;
  function load(base) {
    if (window.L && window.L.markerClusterGroup) return Promise.resolve();
    if (loading) return loading;
    function css(href) {
      var l = document.createElement('link');
      l.rel = 'stylesheet'; l.href = href;
      document.head.appendChild(l);
    }
    function js(src) {
      return new Promise(function (ok, fail) {
        var s = document.createElement('script');
        s.src = src; s.onload = ok; s.onerror = fail;
        document.head.appendChild(s);
      });
    }
    css(base + 'leaflet.css');
    css(base + 'markercluster.css');
    loading = js(base + 'leaflet.js').then(function () { return js(base + 'leaflet.markercluster.js'); });
    loading.catch(function () { loading = null; });
    return loading;
  }

  function shown(el) {
    for (var e = el; e && e.nodeType === 1; e = e.parentElement) {
      if (e.hidden) return false;
      try { if (window.getComputedStyle(e).display === 'none') return false; } catch (err) { /* keep looking */ }
    }
    return true;
  }

  function text(el) { return el ? el.textContent.replace(/\s+/g, ' ').trim() : ''; }

  function Box(box) {
    this.box = box;
    this.list = document.getElementById(box.getAttribute('data-pm-list'));
    this.base = box.getAttribute('data-pm-base') || 'assets/map/';
    this.zipTable = box.getAttribute('data-pm-zip-table') || '';
    this.numbers = box.getAttribute('data-pm-numbers') !== '0';
    this.area = box.querySelector('.pm-area');
    this.mapEl = box.querySelector('.pm-map');
    this.toggle = box.querySelector('.pm-toggle');
    this.hint = box.querySelector('.pm-hint');
    this.key = 'pm-hidden:' + location.pathname;
    this.map = null; this.cluster = null; this.youLayer = null; this.markers = {}; this.lastKey = null;
    if (box.getAttribute('data-pm-dark') === '1') box.classList.add('pm-dark');
    var self = this;
    if (this.toggle) this.toggle.addEventListener('click', function () { self.setOpen(self.area.hidden); });
    if (this.list && window.MutationObserver) {
      var t = null;
      new MutationObserver(function () { clearTimeout(t); t = setTimeout(function () { self.refresh(); }, 30); })
        .observe(this.list, { childList: true });
    }
    this.list && this.list.addEventListener('click', function (e) {
      var b = e.target.closest && e.target.closest('.pm-show');
      if (b) self.showCard(b.getAttribute('data-pm-for'));
    });
    this.refresh();
  }

  Box.prototype.points = function () {
    var zips = this.zipTable ? table(this.zipTable) : null, out = [];
    if (!this.list) return out;
    var cards = this.list.querySelectorAll('[data-pm-zip],[data-pm-lat]');
    for (var i = 0; i < cards.length; i++) {
      var c = cards[i], at = null;
      if (!c.id || (c.closest && c.closest('[hidden]'))) continue;
      if (c.hasAttribute('data-pm-lat')) at = [Number(c.getAttribute('data-pm-lat')), Number(c.getAttribute('data-pm-lon'))];
      else if (zips && zips[c.getAttribute('data-pm-zip')]) at = zips[c.getAttribute('data-pm-zip')];
      if (at && isFinite(at[0]) && isFinite(at[1])) out.push({ card: c, id: c.id, at: at });
    }
    return out;
  };

  Box.prototype.origin = function () {
    var zips = this.zipTable ? table(this.zipTable) : null;
    var zip = new URLSearchParams(location.search).get('zip');
    return zips && zip && zips[zip] ? { zip: zip, at: zips[zip] } : null;
  };

  Box.prototype.setOpen = function (open) {
    this.area.hidden = !open;
    this.toggle.setAttribute('aria-expanded', String(open));
    this.toggle.textContent = open ? 'Hide the map' : 'Show the map';
    store(this.key, open ? null : '1');
    var shows = this.list ? this.list.querySelectorAll('.pm-show') : [];
    for (var i = 0; i < shows.length; i++) shows[i].hidden = !open;
    if (open) this.refresh(true);
  };

  Box.prototype.refresh = function (force) {
    var self = this, pts = this.points();
    if (!pts.length) { this.box.hidden = true; return; }
    if (store(this.key) === '1' && !this.map) {
      // The visitor hid the map: keep the box with its "Show the map" button, and load nothing.
      this.box.hidden = false; this.area.hidden = true;
      this.toggle.setAttribute('aria-expanded', 'false'); this.toggle.textContent = 'Show the map';
      return;
    }
    load(this.base).then(function () {
      self.box.hidden = false;
      if (store(self.key) === '1') { self.area.hidden = true; self.toggle.setAttribute('aria-expanded', 'false'); self.toggle.textContent = 'Show the map'; }
      // A map drawn while its page part is hidden (a printed flyer, say) has no size and cannot place its pins: wait.
      if (self.area.hidden || !shown(self.mapEl)) return;
      try { self.draw(self.points(), force); } catch (e) { self.box.hidden = true; /* the list is still the whole page */ }
    }, function () { /* the map files did not load: the list is still the whole page */ });
  };

  Box.prototype.build = function () {
    var L = window.L, self = this, mobile = L.Browser.mobile;
    // On phones one finger scrolls the page, not the map, until the map is tapped. Pinching always zooms.
    var map = L.map(this.mapEl, { maxZoom: 15, minZoom: 3, scrollWheelZoom: false, dragging: !mobile, tap: true, worldCopyJump: true })
      .setView([39.5, -96], 4);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    function wake() {
      if (!map.scrollWheelZoom.enabled()) map.scrollWheelZoom.enable();
      if (!map.dragging.enabled()) {
        map.dragging.enable();
        if (self.hint && self.hint.getAttribute('data-awake')) self.hint.textContent = self.hint.getAttribute('data-awake');
      }
    }
    map.on('click focus', wake);
    if (mobile && this.hint && this.hint.getAttribute('data-touch')) this.hint.textContent = this.hint.getAttribute('data-touch');
    var plain = function () {
      return L.divIcon({ html: '<span></span>', className: 'pm-cluster', iconSize: [38, 38] });
    };
    this.cluster = L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 42, chunkedLoading: true, spiderfyOnMaxZoom: true,
      iconCreateFunction: this.numbers ? undefined : plain });
    map.addLayer(this.cluster);
    this.youLayer = L.layerGroup().addTo(map);
    // Every pin and group is a button with a name, so it can be reached with Tab and opened with Enter.
    map.on('layeradd', function (e) {
      var icon = e.layer && e.layer._icon;
      if (!icon) return;
      if (L.MarkerCluster && e.layer instanceof L.MarkerCluster) {
        icon.setAttribute('aria-label', 'A group of places close together. Press to zoom in.');
        icon.setAttribute('title', 'Places close together: press to zoom in');
      } else if (e.layer.options && e.layer.options.title) {
        icon.setAttribute('aria-label', e.layer.options.title);
      }
    });
    map.on('popupopen', function (e) {
      var src = e.popup._source, icon = src && src._icon;
      if (icon && document.activeElement === icon) {
        var first = e.popup._contentNode && e.popup._contentNode.querySelector('a,button');
        if (first) first.focus();
        e.popup._returnTo = icon;
      }
    });
    map.on('popupclose', function (e) {
      var back = e.popup._returnTo;
      e.popup._returnTo = null;
      if (back && document.body.contains(back) && self.mapEl.contains(document.activeElement)) back.focus();
    });
    this.map = map;
  };

  Box.prototype.popup = function (card) {
    var self = this, d = document.createElement('div');
    d.className = 'pm-pop';
    var name = card.querySelector('h2,h3'), s = document.createElement('strong');
    s.textContent = text(name);
    d.appendChild(s);
    var sub = card.getAttribute('data-pm-sub');
    if (sub) { var p = document.createElement('span'); p.className = 'pm-sub'; p.textContent = sub; d.appendChild(p); }
    if (card.hasAttribute('data-pm-zip') || card.getAttribute('data-pm-at') === 'zip') {
      var n = document.createElement('span'); n.className = 'pm-approx';
      n.textContent = 'The pin is in the middle of the ZIP code. Use the address to get there.';
      d.appendChild(n);
    }
    var acts = document.createElement('div'); acts.className = 'pm-acts';
    var tel = card.querySelector('a[href^="tel:"]');
    if (tel) {
      var a = document.createElement('a'); a.className = 'pm-call'; a.href = tel.getAttribute('href');
      a.textContent = /^call/i.test(text(tel)) ? text(tel).replace(/\s*↗$/, '') : 'Call ' + text(tel);
      acts.appendChild(a);
    }
    var links = card.querySelectorAll('a[href]'), dir = null, lookup = null;
    for (var i = 0; i < links.length; i++) {
      if (!dir && /directions/i.test(text(links[i]))) dir = links[i];
      if (!lookup && /look up (the )?phone/i.test(text(links[i]))) lookup = links[i];
    }
    if (!tel && lookup) {
      var q = document.createElement('a'); q.href = lookup.getAttribute('href'); q.target = '_blank'; q.rel = 'noopener noreferrer';
      q.textContent = 'Look up phone number ↗';
      acts.appendChild(q);
    }
    if (dir) {
      var g = document.createElement('a'); g.href = dir.getAttribute('href'); g.target = '_blank'; g.rel = 'noopener noreferrer';
      g.textContent = 'Directions ↗';
      acts.appendChild(g);
    }
    var more = document.createElement('button'); more.type = 'button'; more.textContent = 'See the full listing';
    more.addEventListener('click', function () {
      self.map.closePopup();
      var smooth = !reduced();
      if (card.scrollIntoView) card.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto', block: 'start' });
      var h = card.querySelector('h2,h3') || card;
      if (!h.hasAttribute('tabindex')) h.setAttribute('tabindex', '-1');
      try { h.focus({ preventScroll: true }); } catch (e) { h.focus(); }
    });
    acts.appendChild(more);
    d.appendChild(acts);
    return d;
  };

  Box.prototype.draw = function (pts, force) {
    var L = window.L, self = this;
    if (!this.map) this.build();
    else this.map.invalidateSize();
    this.cluster.clearLayers();
    this.youLayer.clearLayers();
    this.markers = {};
    var layers = [], bounds = [];
    pts.forEach(function (p) {
      var kind = (p.card.getAttribute('data-pm-kind') || 'game').replace(/[^a-z]/g, '');
      var m = L.marker(p.at, {
        icon: L.divIcon({ html: '<span class="pm-pin pm-k-' + kind + '"></span>', className: 'pm-icon', iconSize: [24, 24], iconAnchor: [12, 12], popupAnchor: [0, -10] }),
        title: text(p.card.querySelector('h2,h3')), riseOnHover: true
      });
      m.bindPopup(function () { return self.popup(p.card); }, { maxWidth: 300, autoPanPadding: [24, 24] });
      layers.push(m);
      self.markers[p.id] = m;
      bounds.push(p.at);
      self.addShowButton(p.card);
    });
    this.cluster.addLayers(layers);
    var o = this.origin();
    if (o) {
      L.marker(o.at, { icon: L.divIcon({ html: '<span class="pm-you"></span>', className: 'pm-icon', iconSize: [22, 22], iconAnchor: [11, 11] }),
        title: 'Your ZIP code, ' + o.zip, keyboard: false, zIndexOffset: 1000 })
        .bindTooltip('Your ZIP code, ' + o.zip).addTo(this.youLayer);
      bounds.push(o.at);
    }
    var key = pts.map(function (p) { return p.id; }).join('|') + '#' + (o ? o.zip : '');
    if (force || key !== this.lastKey) {
      this.lastKey = key;
      if (bounds.length === 1) this.map.setView(bounds[0], 11, { animate: false });
      else this.map.fitBounds(L.latLngBounds(bounds).pad(0.08), { maxZoom: 12, animate: false });
    }
  };

  // A "Show on map" button on each card with a pin, so the map can be reached from the list.
  Box.prototype.addShowButton = function (card) {
    if (card.querySelector('.pm-show')) return;
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'pm-show'; b.setAttribute('data-pm-for', card.id);
    b.textContent = 'Show on the map';
    var slot = card.querySelector('[data-pm-slot]') || card.querySelector('.small-links') || card.querySelector('.actions');
    if (slot) slot.appendChild(b); else card.appendChild(b);
  };

  Box.prototype.showCard = function (id) {
    var m = this.markers[id], self = this;
    if (!m || !this.map) return;
    var smooth = !reduced();
    if (this.box.scrollIntoView) this.box.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto', block: 'start' });
    this.cluster.zoomToShowLayer(m, function () {
      if (m._icon) { try { m._icon.focus({ preventScroll: true }); } catch (e) { m._icon.focus(); } }
      m.openPopup();
    });
  };

  // "Use my location": find the nearest ZIP code on this device and search it like a typed one.
  function locateButton(btn) {
    if (!navigator.geolocation) return;
    btn.hidden = false;
    btn.addEventListener('click', function () {
      var input = document.getElementById(btn.getAttribute('data-pm-zip-input'));
      var form = document.getElementById(btn.getAttribute('data-pm-form'));
      var status = document.getElementById(btn.getAttribute('data-pm-status'));
      var say = function (msg) { if (status) status.textContent = msg; };
      var zips = table(btn.getAttribute('data-pm-zip-table'));
      var ready = false;
      if (zips) for (var k in zips) { ready = true; break; }
      if (!ready || !input || !form) { say('Still loading. Please try again in a moment.'); return; }
      say('Finding where you are…');
      btn.disabled = true;
      navigator.geolocation.getCurrentPosition(function (pos) {
        btn.disabled = false;
        var hit = nearestZip(zips, [pos.coords.latitude, pos.coords.longitude]);
        if (!hit || hit.miles > 60) { say('We could not match your location to a ZIP code we cover. Please type your ZIP code instead.'); return; }
        input.value = hit.zip;
        if (form.requestSubmit) form.requestSubmit(); else form.dispatchEvent(new Event('submit', { cancelable: true }));
      }, function () {
        btn.disabled = false;
        say('Your location was not shared. That is fine: type your ZIP code instead.');
      }, { enableHighAccuracy: false, timeout: 12000, maximumAge: 600000 });
    });
  }

  function init() {
    addStyle();
    var boxes = document.querySelectorAll('.pm-box[data-pm-list]');
    for (var i = 0; i < boxes.length; i++) new Box(boxes[i]);
    var locs = document.querySelectorAll('[data-pm-locate]');
    for (var j = 0; j < locs.length; j++) locateButton(locs[j]);
  }

  window.PlaceMap = { nearestZip: nearestZip, miles: miles };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
