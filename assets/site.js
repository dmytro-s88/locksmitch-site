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

  // Estimate form: posts to the Apps Script endpoint, which emails info@locksmitch.com
  var ENDPOINT = 'https://script.google.com/macros/s/AKfycbwEnPklqAabpkxC7UoInrIwUW17F5hXMmveX2hEEUIxUGt7hskz_RNbpzz9QHiTZIKz/exec';
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
      service: (form.querySelector('input[name="svc"]:checked') || {}).value || '',
      second_key: (document.getElementById('s1').checked && document.getElementById('f-second').checked) ? 'yes' : '',
      vehicle: form.vehicle.value.trim(),
      name: form.name.value.trim(),
      phone: phone,
      company: form.company.value,
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
      im.alt = text || 'LocksMitch job photo';
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

// Touch screens have no hover, so once per visit play it for them: "$15 off" pops, then the four hero badges light up one by one
(function () {
  var tag = document.querySelector('.book-note .tag'), facts = document.querySelectorAll('.facts span');
  if (!tag || !facts.length || !window.matchMedia || !window.IntersectionObserver) return;
  if (!window.matchMedia('(hover: none)').matches || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  function play() {
    tag.classList.add('pop');
    setTimeout(function () { tag.classList.remove('pop'); }, 750);
    Array.prototype.forEach.call(facts, function (f, i) {
      setTimeout(function () { f.classList.add('lit'); }, 550 + i * 280);
      setTimeout(function () { f.classList.remove('lit'); }, 550 + i * 280 + 650);
    });
  }
  // wait a second after load, then play as soon as the badges are on screen
  function arm() {
    var io = new IntersectionObserver(function (es) {
      if (es[0].isIntersecting) { io.disconnect(); play(); }
    }, { threshold: 0.6 });
    io.observe(facts[facts.length - 1].parentNode);
  }
  if (document.readyState === 'complete') setTimeout(arm, 1000);
  else window.addEventListener('load', function () { setTimeout(arm, 1000); });
})();
