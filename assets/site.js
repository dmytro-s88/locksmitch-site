(function () {
  // Spanish pages (/es/) use the same script; T(en, es) picks the text by the page language
  var ES = document.documentElement.lang === 'es';
  function T(en, es) { return ES ? es : en; }
  // Where the visit came from (referrer and first page), kept for the tab and sent with the estimate form; /book/ does the same
  var SRC = (function () {
    try {
      var s = sessionStorage.getItem('lm_src');
      if (!s) {
        var r = document.referrer, own = r && new URL(r).hostname.replace(/^www\./, '') === location.hostname.replace(/^www\./, '');
        s = JSON.stringify({ ref: own ? '' : r.slice(0, 300), land: (location.pathname + location.search).slice(0, 300) });
        sessionStorage.setItem('lm_src', s);
      }
      return JSON.parse(s);
    } catch (e) { return { ref: document.referrer.slice(0, 300), land: location.pathname }; }
  })();
  // Service area grouped by county
  var PAGES = {"Cumming": "/cumming/", "Sugar Hill": "/sugarhill/", "Buford": "/buford/", "Suwanee": "/suwanee/", "Duluth": "/duluth/", "Peachtree Corners": "/peachtreecorners/", "Norcross": "/norcross/", "Lawrenceville": "/lawrenceville/", "Milton": "/milton/", "Alpharetta": "/alpharetta/", "Johns Creek": "/johnscreek/", "Roswell": "/roswell/", "Sandy Springs": "/sandysprings/", "Flowery Branch": "/flowerybranch/", "Gainesville": "/gainesville/", "Dawsonville": "/dawsonville/", "Canton": "/canton/", "Woodstock": "/woodstock/", "Dunwoody": "/dunwoody/", "Doraville": "/doraville/", "Braselton": "/braselton/", "Marietta": "/marietta/", "Kennesaw": "/kennesaw/", "Smyrna": "/smyrna/"};
  var HERE = document.documentElement.getAttribute('data-city');
  var counties = [
    ['Forsyth', ['Cumming']],
    ['Gwinnett', ['Sugar Hill', 'Buford', 'Suwanee', 'Duluth', 'Peachtree Corners', 'Norcross', 'Lawrenceville']],
    ['Fulton', ['Milton', 'Alpharetta', 'Johns Creek', 'Roswell', 'Sandy Springs']],
    ['Hall', ['Flowery Branch', 'Gainesville']],
    ['Dawson', ['Dawsonville']],
    ['Cherokee', ['Canton', 'Woodstock']],
    ['DeKalb', ['Dunwoody', 'Doraville']],
    ['Jackson', ['Braselton']],
    ['Cobb', ['Marietta', 'Kennesaw', 'Smyrna']]
  ];
  function cityLink(city) {
    var a = document.createElement('a');
    if (PAGES[city]) { a.href = PAGES[city]; } else { a.href = 'https://' + city.toLowerCase().replace(/\s+/g, '') + '.locksmitch.com'; a.target = '_blank'; a.rel = 'noopener'; }
    if (city === HERE) { a.className = 'current'; a.setAttribute('aria-current', 'page'); }
    a.textContent = city;
    return a;
  }
  function countyHead(c, tagName) {
    var h = document.createElement(tagName); h.textContent = ES ? 'Condado de ' + c[0] : c[0] + ' County';
    if (c[0] === 'Forsyth') { var tag = document.createElement('em'); tag.textContent = T('Home base', 'Nuestra base'); h.appendChild(tag); }
    return h;
  }
  var grid = document.getElementById('areaGrid');
  if (grid) counties.forEach(function (c) {   // pages without the service area block (guides) skip it
    var div = document.createElement('div'); div.className = c[0] === 'Forsyth' ? 'county home' : 'county';
    var ul = document.createElement('ul');
    c[1].forEach(function (city) { var li = document.createElement('li'); li.appendChild(cityLink(city)); ul.appendChild(li); });
    div.appendChild(countyHead(c, 'h3')); div.appendChild(ul); grid.appendChild(div);
  });

  // Top menu: "Service area" gets a city dropdown (the menu itself is hidden on phones)
  var areaLink = document.querySelector('.nav a[href$="#area"]');
  if (areaLink) {
    var dd = document.createElement('div'); dd.className = 'nav-dd';
    areaLink.parentNode.insertBefore(dd, areaLink); dd.appendChild(areaLink);
    var ddBtn = document.createElement('button'); ddBtn.type = 'button'; ddBtn.className = 'nav-dd-btn';
    ddBtn.setAttribute('aria-expanded', 'false'); ddBtn.setAttribute('aria-label', T('Show cities', 'Ver ciudades'));
    ddBtn.innerHTML = '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    var panel = document.createElement('div'); panel.className = 'nav-dd-panel';
    counties.forEach(function (c) {
      var g = document.createElement('div'); g.className = 'grp'; g.appendChild(countyHead(c, 'p'));
      c[1].forEach(function (city) { g.appendChild(cityLink(city)); });
      panel.appendChild(g);
    });
    dd.appendChild(ddBtn); dd.appendChild(panel);
    var setDd = function (open) { dd.classList.toggle('open', open); ddBtn.setAttribute('aria-expanded', String(open)); };
    ddBtn.addEventListener('click', function (e) { e.stopPropagation(); setDd(!dd.classList.contains('open')); });
    document.addEventListener('click', function (e) { if (!dd.contains(e.target)) setDd(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setDd(false); });
  }

  // Estimate form (2026-11-03): posts straight to the LocksMitch bot (same web app as /book/), which saves the lead, shows the
  // Telegram card with the SMS draft and emails a copy to info@. Before: Apps Script form endpoint -> email -> Make -> bot.
  var ENDPOINT = 'https://script.google.com/macros/s/AKfycbynxb1ruxrGOtdWw-uGXRYzHs_Pz7L-ad5lc9KdyqKUzbRcSfJ1-L97VLvmfUbY_cZh/exec';
  var form = document.getElementById('leadForm');
  var err = document.getElementById('formErr');
  var sendBtn = document.getElementById('sendBtn');
  function showErr(html) { err.innerHTML = html; err.hidden = false; }
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    err.hidden = true;
    var bad = Array.prototype.filter.call(form.querySelectorAll('input[required]'), function (i) { return !i.value.trim(); });
    if (bad.length) { bad[0].focus(); bad[0].setAttribute('aria-invalid', 'true'); showErr(T('Fill in the vehicle, your name and phone number.', 'Falta el carro, su nombre o su número de teléfono.')); return; }
    var phone = form.phone.value.trim();
    if ((phone.match(/\d/g) || []).length < 7) { form.phone.focus(); showErr(T('Check the phone number. It needs at least 7 digits.', 'Revise el número de teléfono. Necesita al menos 7 dígitos.')); return; }
    var data = new URLSearchParams({
      site_estimate: '1',
      service: (form.querySelector('input[name="svc"]:checked') || {}).value || '',
      second_key: (document.getElementById('s1').checked && document.getElementById('f-second').checked) ? 'yes' : '',
      vehicle: form.vehicle.value.trim(),
      name: form.name.value.trim(),
      phone: phone,
      extra: form.extra.value,   // bot trap; named without meaning so iPhone autofill leaves it alone (it filled "company" from the contact card)
      page: location.href,
      src_ref: SRC.ref || '',
      src_land: SRC.land || ''
    });
    sendBtn.disabled = true; sendBtn.textContent = T('Sending…', 'Enviando…');
    fetch(ENDPOINT, { method: 'POST', body: data })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.ok) throw new Error(res.error || 'failed');
        if (window.lmTrack) window.lmTrack('generate_lead', { service: data.get('service') || '', second_key: data.get('second_key') || 'no' });
        document.getElementById('estForm').hidden = true;
        document.getElementById('estSent').hidden = false;
        showCard();
      })
      .catch(function () {
        showErr(T('Your request didn’t go through. Call or text <a href="tel:7702703333">(770) 270-3333</a> and we’ll help right away.', 'Su solicitud no se envió. Llame o escriba al <a href="tel:7702703333">(770) 270-3333</a> y le ayudamos enseguida.'));
      })
      .then(function () { sendBtn.disabled = false; sendBtn.textContent = T('Get my free estimate', 'Quiero mi cotización gratis'); });
  });
  form.addEventListener('input', function (e) { e.target.removeAttribute('aria-invalid'); });
  document.getElementById('estAgain').addEventListener('click', function () {
    form.reset();
    var def = document.querySelector('input[name="svc"]:checked'); if (def) def.dispatchEvent(new Event('change', { bubbles: true }));
    document.getElementById('estSent').hidden = true;
    document.getElementById('estForm').hidden = false;
    showCard();
  });
  // After the form swaps for the confirmation (or back), the card gets shorter or taller and the page jumps.
  // Bring the card's top into view under the sticky header and move focus to its heading.
  function showCard() {
    var card = document.getElementById('estimate');
    if (!card) return;
    var hdr = document.querySelector('header');
    var off = (hdr && /sticky|fixed/.test(getComputedStyle(hdr).position) ? hdr.offsetHeight : 0) + 12;
    var r = card.getBoundingClientRect();
    if (r.top < off || r.top > window.innerHeight * 0.4) {
      var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollTo({ top: r.top + window.pageYOffset - off, behavior: reduce ? 'auto' : 'smooth' });
    }
    var h = card.querySelector('#estSent:not([hidden]) h2, #estForm:not([hidden]) h2');
    if (h) { h.setAttribute('tabindex', '-1'); h.style.outline = 'none'; h.focus({ preventScroll: true }); }
  }

  // Recent jobs gallery: photo posts from Instagram @locksmitch.ga (videos are skipped by the feed)
  var FEED = 'https://script.google.com/macros/s/AKfycbwEnPklqAabpkxC7UoInrIwUW17F5hXMmveX2hEEUIxUGt7hskz_RNbpzz9QHiTZIKz/exec?feed=instagram';
  var EMOJI = /[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}\u{200D}]/gu;
  fetch(FEED).then(function (r) { return r.json(); }).then(function (d) {
    if (!d || !d.ok || !d.photos || !d.photos.length) return;
    var gal = document.getElementById('gallery');
    d.photos.slice(0, 9).forEach(function (ph) {
      var a = document.createElement('a'); a.href = ph.link; a.target = '_blank'; a.rel = 'noopener';
      var f = document.createElement('figure');
      var im = document.createElement('img'); im.src = ph.src; im.loading = 'lazy';
      var text = (ph.caption || '').replace(EMOJI, '').replace(/\s+/g, ' ').trim();
      im.alt = text ? '' : 'LocksMitch job photo';
      f.appendChild(im);
      if (text) { var cap = document.createElement('figcaption'); cap.textContent = text; f.appendChild(cap); }
      a.appendChild(f); gal.appendChild(a);
    });
    document.getElementById('work').hidden = false;
  }).catch(function () {});

  // "Get a spare key quote" preselects the service in the form
  Array.prototype.forEach.call(document.querySelectorAll('[data-svc]'), function (a) {
    a.addEventListener('click', function () { var r = document.getElementById(a.getAttribute('data-svc')); if (r) { r.checked = true; r.dispatchEvent(new Event('change', { bubbles: true })); } });
  });

  // Second key add-on only applies to All keys lost
  var addon = document.getElementById('addon');
  function syncAddon() { var c = document.querySelector('input[name="svc"]:checked'); addon.hidden = !(c && c.id === 's1'); }
  Array.prototype.forEach.call(document.querySelectorAll('input[name="svc"]'), function (r) { r.addEventListener('change', syncAddon); });
  syncAddon();

  // Analytics: calls, texts, messengers, online booking (form leads are tracked after a successful send)
  var PAGE_CITY = document.documentElement.getAttribute('data-city') || document.documentElement.getAttribute('data-page') || 'Home';
  function track(name, extra) {
    if (typeof gtag !== 'function') return;
    var p = { page_city: PAGE_CITY };
    for (var k in extra) p[k] = extra[k];
    gtag('event', name, p);
  }
  window.lmTrack = track;
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href');
    var where = a.closest('.callbar') ? 'sticky_bar' : a.closest('.top') ? 'header' : a.closest('.hero') ? 'hero' : a.closest('.spare') ? 'spare_key_banner' : a.closest('.channels') ? 'contacts' : 'page';
    if (/^tel:/.test(href)) track('click_to_call', { link_location: where });
    else if (/^sms:/.test(href)) track('click_to_text', { link_location: where });
    else if (/wa\.me|t\.me\//.test(href)) track('click_messenger', { channel: /wa\.me/.test(href) ? 'whatsapp' : 'telegram', link_location: where });
    else if (/^\/book\/|squareup\.com\/appointments/.test(href)) track('click_book_online', { link_location: where });
  });

  // Copy phone number
  var btn = document.getElementById('copyBtn');
  if (btn) btn.addEventListener('click', function () {
    var done = function () { btn.textContent = T('Copied', 'Copiado'); setTimeout(function () { btn.textContent = T('Copy number', 'Copiar número'); }, 1800); };
    try {
      navigator.clipboard.writeText('(770) 270-3333').then(done, function () { selectNum(); });
    } catch (e) { selectNum(); }
  });
  function selectNum() { var r = document.createRange(); r.selectNodeContents(document.getElementById('phoneNum')); var s = getSelection(); s.removeAllRanges(); s.addRange(r); }

  // Language: remember the choice made with the globe switch; on a Spanish-language device show a small "¿Prefiere español?" hint
  // on English pages (never a redirect: English visitors and search engines see the same page as before)
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  Array.prototype.forEach.call(document.querySelectorAll('a.lang'), function (a) { a.setAttribute('data-tip', a.getAttribute('hreflang') === 'es' ? 'Español' : 'English'); });
  Array.prototype.forEach.call(document.querySelectorAll('a.lang, a[hreflang]'), function (a) {
    a.addEventListener('click', function () { var to = a.getAttribute('hreflang'); if (to) { store('lm_lang', to); track('lang_switch', { to: to }); } });
  });
  // Light / dark theme: sun-moon button next to the globe; a manual choice is remembered for 24 hours (lm_theme + lm_theme_at). The <head> script applies it before paint;
  // with no manual choice it picks light only when the phone is in light mode and it is daytime in Atlanta (sunrise/sunset by month), else dark
  (function () {
    var bar = document.querySelector('.top .wrap'); if (!bar) return;
    var root = document.documentElement, meta = document.querySelector('meta[name="theme-color"]');
    var b = document.createElement('button'); b.type = 'button'; b.className = 'theme-btn';
    b.innerHTML = '<svg class="ico-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>' +
      '<svg class="ico-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>';
    function light() { return root.getAttribute('data-theme') === 'light'; }
    function label() { var t = light() ? T('Dark theme', 'Tema oscuro') : T('Light theme', 'Tema claro'); b.setAttribute('aria-label', t); b.setAttribute('data-tip', t); }
    label();
    b.addEventListener('click', function () {
      var to = light() ? 'dark' : 'light';
      root.classList.add('theme-anim');
      if (to === 'light') root.setAttribute('data-theme', 'light'); else root.removeAttribute('data-theme');
      if (meta) meta.setAttribute('content', to === 'light' ? '#F3F5F1' : '#0E1311');
      store('lm_theme', to); store('lm_theme_at', String(Date.now())); label(); track('theme_switch', { to: to });
      window.dispatchEvent(new Event('lm-theme'));
      setTimeout(function () { root.classList.remove('theme-anim'); }, 400);
    });
    var lang = bar.querySelector('.lang'), call = bar.querySelector('.btn-call');
    bar.insertBefore(b, lang || call || null);
  })();
  // Phone menu: three-line button in the header opens the same links as the desktop nav, plus online booking.
  // On phones it takes the place of the header call button (the bottom bar already has Call now).
  (function () {
    var bar = document.querySelector('.top .wrap'), nav = bar && bar.querySelector('.nav'); if (!nav) return;
    var links = Array.prototype.filter.call(nav.querySelectorAll('a'), function (a) { return !a.closest('.nav-dd-panel'); });
    var b = document.createElement('button'); b.type = 'button'; b.className = 'menu-btn';
    b.setAttribute('aria-label', T('Menu', 'Menú')); b.setAttribute('aria-expanded', 'false'); b.setAttribute('aria-controls', 'mmenu');
    b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path class="mb-l1" d="M4 7h16"/><path class="mb-l2" d="M4 12h16"/><path class="mb-l3" d="M4 17h16"/></svg>';
    var p = document.createElement('nav'); p.id = 'mmenu'; p.className = 'menu-panel'; p.setAttribute('aria-label', T('Menu', 'Menú'));
    links.forEach(function (a) {
      var m = document.createElement('a'); m.href = a.getAttribute('href'); m.textContent = a.textContent.trim(); p.appendChild(m);
    });
    var bk = document.createElement('a'); bk.className = 'btn btn-call menu-book'; bk.href = '/book/';
    bk.textContent = T('Book online, $15 off', 'Reservar en línea, $15 menos'); p.appendChild(bk);
    function set(open) {
      bar.classList.toggle('menu-open', open); b.setAttribute('aria-expanded', open ? 'true' : 'false');
      b.setAttribute('aria-label', open ? T('Close menu', 'Cerrar menú') : T('Menu', 'Menú'));
    }
    b.addEventListener('click', function (e) {
      e.stopPropagation(); var open = !bar.classList.contains('menu-open'); set(open);
      if (open) track('menu_open', {});
    });
    p.addEventListener('click', function (e) {
      var a = e.target.closest('a'); if (!a) return;
      track('menu_click', { item: a.getAttribute('href') }); set(false);
    });
    document.addEventListener('click', function (e) { if (bar.classList.contains('menu-open') && !bar.contains(e.target)) set(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && bar.classList.contains('menu-open')) { set(false); b.focus(); } });
    window.addEventListener('resize', function () { if (window.innerWidth > 900) set(false); });
    bar.insertBefore(b, bar.querySelector('.btn-call') || null);
    bar.appendChild(p);
  })();
  var devLang = String((navigator.languages && navigator.languages[0]) || navigator.language || '');
  var esLink = document.querySelector('a.lang[hreflang="es"]');
  var forceHint = /[?&]eshint\b/.test(location.search);   // ?eshint: показать плашку на любом телефоне (для проверки)
  if (!ES && esLink && (forceHint || (/^es\b/i.test(devLang) && !store('lm_lang') && store('lm_lang_hint') !== 'off'))) {
    var box = document.createElement('div');
    box.className = 'lang-hint'; box.setAttribute('role', 'note'); box.setAttribute('lang', 'es');
    box.innerHTML = '<span>¿Prefiere español?</span><a href="' + esLink.getAttribute('href') + '" hreflang="es">Ver en español</a><button type="button" aria-label="Cerrar">×</button>';
    box.querySelector('a').addEventListener('click', function () { store('lm_lang', 'es'); track('lang_switch', { to: 'es', via: 'hint' }); });
    box.querySelector('button').addEventListener('click', function () { store('lm_lang_hint', 'off'); box.remove(); });
    document.body.appendChild(box);
  }
})();

// Страница цен на телефоне: форма оценки переезжает под цены (человек пришёл смотреть цены, а не форму)
(function () {
  var slot = document.getElementById('estSlot'), est = document.getElementById('estimate');
  if (!slot || !est || !window.matchMedia) return;
  var mq = window.matchMedia('(max-width: 920px)'), home = est.parentNode, next = est.nextSibling;
  function place() { if (mq.matches) slot.appendChild(est); else home.insertBefore(est, next); }
  place();
  if (mq.addEventListener) mq.addEventListener('change', place);
})();

// Hero badges: a tap opens a short explanation under the row (one at a time), a tap anywhere else or Esc closes it
(function () {
  var row = document.querySelector('.facts');
  if (!row) return;
  var open = null;
  function close() {
    if (!open) return;
    open.setAttribute('aria-expanded', 'false');
    document.getElementById(open.getAttribute('aria-controls')).hidden = true;
    open = null;
  }
  Array.prototype.forEach.call(row.querySelectorAll('.fact'), function (b) {
    b.addEventListener('click', function () {
      if (open === b) { close(); return; }
      close();
      var tip = document.getElementById(b.getAttribute('aria-controls'));
      var r = b.getBoundingClientRect(), rr = row.getBoundingClientRect();
      tip.style.setProperty('--ax', Math.round(r.left + r.width / 2 - rr.left) + 'px');
      tip.hidden = false;
      b.setAttribute('aria-expanded', 'true');
      open = b;
      if (window.lmTrack) window.lmTrack('fact_open', { fact: tip.id.slice(3) });
    });
  });
  document.addEventListener('click', function (e) { if (open && !row.contains(e.target)) close(); });
  row.addEventListener('click', function (e) { if (e.target.closest && e.target.closest('.fact-tip a')) close(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
})();

// Estimate card: on a mouse it lifts and tilts toward the pointer (up to ~4 degrees), still while a field has focus; never on touch or with reduced motion.
// The transform is eased by this script every frame (a spring, like the logo fob), not by a CSS transition: restarting a transform
// transition on every pointer move makes Safari snap back by a frame (its main thread lags the accelerated animation), a twitch on Dima's Mac (2026-11-03).
(function () {
  var t = document.querySelector('.estimate');
  if (!t || !window.matchMedia || !matchMedia('(hover: hover) and (pointer: fine)').matches || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var cur = { x: 0, y: 0, l: 0 }, tgt = { x: 0, y: 0, l: 0 }, raf = 0, over = false;
  // Safari (Mac): it re-rasterizes the card's text at every small 3D turn, so the text shimmers while the card tilts (Dima's recording,
  // 2026-11-03); Chrome paints the card once and turns the picture. There the card only lifts with its shadow, no turn.
  var ua = navigator.userAgent, flat = /Version\/[\d.]+.*Safari\//.test(ua) && !/Chrome|Chromium|Edg|OPR/.test(ua);
  t.style.transition = 'box-shadow .6s ease';
  function typing() { return t.contains(document.activeElement) && document.activeElement.matches('input, select, textarea'); }
  function tick() {
    var moving = false;
    for (var p in cur) { var d = tgt[p] - cur[p]; if (Math.abs(d) > 0.005) { cur[p] += d * 0.16; moving = true; } else cur[p] = tgt[p]; }
    t.style.transform = (cur.x || cur.y || cur.l) ? 'perspective(1200px) rotateX(' + cur.x.toFixed(2) + 'deg) rotateY(' + cur.y.toFixed(2) + 'deg) translateY(' + (-4 * cur.l).toFixed(2) + 'px)' : '';
    raf = moving ? requestAnimationFrame(tick) : 0;
  }
  function aim(x, y, l) { tgt.x = x; tgt.y = y; tgt.l = l; if (!raf) raf = requestAnimationFrame(tick); }
  t.addEventListener('pointerenter', function () {
    // the hero rise-in animation keeps its end state and would hide the tilt: drop it once it has played
    if (t.getAnimations) t.getAnimations().forEach(function (a) { if (a.playState === 'finished') a.cancel(); });
    over = true; t.classList.add('lifted');
  });
  t.addEventListener('pointermove', function (e) {
    if (typing()) { aim(0, 0, 1); return; }
    var r = t.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
    aim(flat ? 0 : -y * 4, flat ? 0 : x * 5, 1);
  });
  t.addEventListener('pointerleave', function () { over = false; t.classList.remove('lifted'); aim(0, 0, 0); });
  t.addEventListener('focusin', function () { aim(0, 0, over ? 1 : 0); });
})();

// Touch screens have no hover, so once per visit play it for them: "$15 off" pops, and the four hero badges light up one by one when they scroll into view
(function () {
  var tag = document.querySelector('.book-note .tag'), facts = document.querySelectorAll('.facts .fact');
  if (!tag || !facts.length || !window.matchMedia || !window.IntersectionObserver) return;
  if (!window.matchMedia('(hover: none)').matches || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  // the fixed call bar covers the bottom of the screen, so on screen means above it
  function whenSeen(el, ratio, fn) {
    var bar = document.querySelector('.callbar'), h = bar ? bar.offsetHeight : 0;
    var io = new IntersectionObserver(function (es) {
      if (es[es.length - 1].intersectionRatio >= ratio) { io.disconnect(); fn(); }
    }, { threshold: ratio, rootMargin: '0px 0px -' + h + 'px 0px' });
    io.observe(el);
  }
  function popTag() {
    tag.classList.add('pop');
    setTimeout(function () { tag.classList.remove('pop'); }, 750);
  }
  function lightFacts() {
    Array.prototype.forEach.call(facts, function (f, i) {
      setTimeout(function () { f.classList.add('lit'); }, 200 + i * 280);
      setTimeout(function () { f.classList.remove('lit'); }, 200 + i * 280 + 650);
    });
  }
  // wait a second after load, then each one plays as soon as it is on screen
  function arm() {
    whenSeen(tag, 1, popTag);
    whenSeen(facts[0].parentNode, 0.9, lightFacts);
  }
  if (document.readyState === 'complete') setTimeout(arm, 1000);
  else window.addEventListener('load', function () { setTimeout(arm, 1000); });
})();
