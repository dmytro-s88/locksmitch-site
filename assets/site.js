(function () {
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
  var grid = document.getElementById('areaGrid');
  counties.forEach(function (c) {
    var div = document.createElement('div'); div.className = 'county';
    var h = document.createElement('h3'); h.textContent = c[0] + ' County';
    var ul = document.createElement('ul');
    c[1].forEach(function (city) {
      var li = document.createElement('li'); var a = document.createElement('a');
      if (PAGES[city]) { a.href = PAGES[city]; } else { a.href = 'https://' + city.toLowerCase().replace(/\s+/g, '') + '.locksmitch.com'; a.target = '_blank'; a.rel = 'noopener'; }
      if (city === HERE) { a.className = 'current'; a.setAttribute('aria-current', 'page'); }
      a.textContent = city; var s = document.createElement('span'); s.textContent = 'city page'; a.appendChild(s);
      li.appendChild(a); ul.appendChild(li);
    });
    div.appendChild(h); div.appendChild(ul); grid.appendChild(div);
  });

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
    if (bad.length) { bad[0].focus(); bad[0].setAttribute('aria-invalid', 'true'); showErr('Fill in the vehicle, your name and phone number.'); return; }
    var phone = form.phone.value.trim();
    if ((phone.match(/\d/g) || []).length < 7) { form.phone.focus(); showErr('Check the phone number. It needs at least 7 digits.'); return; }
    var data = new URLSearchParams({
      service: (form.querySelector('input[name="svc"]:checked') || {}).value || '',
      second_key: (document.getElementById('s1').checked && document.getElementById('f-second').checked) ? 'yes' : '',
      vehicle: form.vehicle.value.trim(),
      name: form.name.value.trim(),
      phone: phone,
      company: form.company.value,
      page: location.href
    });
    sendBtn.disabled = true; sendBtn.textContent = 'Sending…';
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
        showErr('Your request didn’t go through. Call or text <a href="tel:7702703333">(770) 270-3333</a> and we’ll help right away.');
      })
      .then(function () { sendBtn.disabled = false; sendBtn.textContent = 'Get my free estimate'; });
  });
  form.addEventListener('input', function (e) { e.target.removeAttribute('aria-invalid'); });
  document.getElementById('estAgain').addEventListener('click', function () {
    form.reset();
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
    a.addEventListener('click', function () { var r = document.getElementById(a.getAttribute('data-svc')); if (r) r.checked = true; });
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
  btn.addEventListener('click', function () {
    var done = function () { btn.textContent = 'Copied'; setTimeout(function () { btn.textContent = 'Copy number'; }, 1800); };
    try {
      navigator.clipboard.writeText('(770) 270-3333').then(done, function () { selectNum(); });
    } catch (e) { selectNum(); }
  });
  function selectNum() { var r = document.createRange(); r.selectNodeContents(document.getElementById('phoneNum')); var s = getSelection(); s.removeAllRanges(); s.addRange(r); }
})();
