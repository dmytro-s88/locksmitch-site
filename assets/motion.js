// Shared motion for every page (also /book/): reveal on scroll, floating call button, pointer light on buttons.
// Motion (2026-10-23): reveal on scroll with a small stagger, floating call button on desktop after the hero.
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) return;
  var els = document.querySelectorAll('.sec-head, .spec, .steps li, .area-grid > *, .cred .badge, .faq details, .local-grid > *, .spare, table.prices tbody tr, .price-list li, .svc-steps li, .ch-list li');
  var counts = [];
  Array.prototype.forEach.call(els, function (el) {
    var p = el.parentNode, i = counts.indexOf(p); if (i < 0) { counts.push(p, 0); i = counts.length - 2; }
    el.style.setProperty('--d', (counts[i + 1]++ % 6) * 70 + 'ms');
    el.classList.add('reveal');
  });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -6% 0px', threshold: 0.05 });
  Array.prototype.forEach.call(els, function (el) { io.observe(el); });
  var hero = document.querySelector('.hero');
  if (hero && window.matchMedia('(min-width: 921px)').matches && !document.querySelector('.float-call')) {
    var fb = document.createElement('a');
    fb.className = 'float-call btn btn-call'; fb.href = 'tel:7702703333'; fb.setAttribute('aria-label', 'Call (770) 270-3333');
    fb.innerHTML = '<svg><use href="#i-phone"/></svg><span>(770) 270-3333</span>';
    document.body.appendChild(fb);
    new IntersectionObserver(function (en) { fb.classList.toggle('show', !en[0].isIntersecting); }).observe(hero);
  }
})();

// Cursor spotlight on buttons: --mx/--my follow the pointer inside the button
document.addEventListener('pointermove', function (e) {
  var b = e.target && e.target.closest ? e.target.closest('.btn, .facts span') : null;
  if (!b) return;
  var r = b.getBoundingClientRect();
  var x = e.clientX - r.left, y = e.clientY - r.top;
  b.style.setProperty('--mx', x + 'px');
  b.style.setProperty('--my', y + 'px');
  // the pointer is the light: the glow shadow shifts away from it
  b.style.setProperty('--sx', ((r.width / 2 - x) / r.width * 18).toFixed(1) + 'px');
  b.style.setProperty('--sy', ((r.height / 2 - y) / r.height * 10).toFixed(1) + 'px');
}, { passive: true });

// Vector logo: inline the fob so its waves and glare can move; it tilts like a lit 3D object.
// Desktop: follows the pointer with spring smoothing. Android: follows the phone tilt (gyro). Otherwise: an occasional CSS sway.
(function () {
  var mark = document.querySelector('.brand .brand-mark'); if (!mark || !window.fetch) return;
  var img = mark.querySelector('img'); if (!img) return;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  fetch(img.getAttribute('src')).then(function (r) { return r.ok ? r.text() : Promise.reject(r.status); }).then(function (txt) {
    var box = document.createElement('div'); box.innerHTML = txt.trim();
    var svg = box.querySelector('svg'); if (!svg) return;
    svg.setAttribute('width', img.getAttribute('width')); svg.setAttribute('height', img.getAttribute('height'));
    svg.setAttribute('focusable', 'false');
    mark.replaceChild(svg, img);
    if (reduce) return;
    svg.classList.add('lm-intro');
    var vb = svg.viewBox.baseVal, brand = mark.closest('.brand');
    var cx0 = vb.x + vb.width * 0.35, cy0 = vb.y + vb.height * 0.3;
    var cur = { rx: 0, ry: 0, gx: cx0, gy: cy0 }, tgt = { rx: 0, ry: 0, gx: cx0, gy: cy0 }, raf = 0;
    function apply() {
      mark.style.setProperty('--rx', cur.rx.toFixed(2) + 'deg'); mark.style.setProperty('--ry', cur.ry.toFixed(2) + 'deg');
      svg.style.setProperty('--gx', cur.gx.toFixed(0) + 'px'); svg.style.setProperty('--gy', cur.gy.toFixed(0) + 'px');
    }
    function tick() {
      var k = 0.085, moving = false;
      for (var p in cur) { var d = tgt[p] - cur[p]; if (Math.abs(d) > (p.charAt(0) === 'g' ? 0.5 : 0.02)) { cur[p] += d * k; moving = true; } else cur[p] = tgt[p]; }
      apply(); raf = moving ? requestAnimationFrame(tick) : 0;
    }
    function aim(rx, ry, gx, gy) { tgt.rx = rx; tgt.ry = ry; tgt.gx = gx; tgt.gy = gy; if (!raf) raf = requestAnimationFrame(tick); }
    mark.classList.add('lm-live');
    var hover = window.matchMedia && window.matchMedia('(hover: hover)').matches;
    if (hover && brand) {
      brand.addEventListener('pointermove', function (e) {
        var r = svg.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
        var cx = Math.max(-0.6, Math.min(1.6, x)) - 0.5, cy = Math.max(-0.4, Math.min(1.4, y)) - 0.5;
        aim(-cy * 16, cx * 22, vb.x + x * vb.width, vb.y + y * vb.height);
      }, { passive: true });
      brand.addEventListener('pointerleave', function () { aim(0, 0, cx0, cy0); });
      return;
    }
    // touch devices: Android Chrome gives deviceorientation without a permission prompt (iOS needs one, so iOS keeps the CSS sway)
    if (window.DeviceOrientationEvent && typeof DeviceOrientationEvent.requestPermission !== 'function') {
      var base = null;
      window.addEventListener('deviceorientation', function (e) {
        if (e.beta == null || e.gamma == null) return;
        if (base === null) base = e.beta;
        if (!mark.classList.contains('lm-gyro')) { mark.classList.add('lm-gyro'); svg.classList.add('lm-gyro'); }
        var g = Math.max(-30, Math.min(30, e.gamma)), b = Math.max(-25, Math.min(25, e.beta - base));
        base += (e.beta - base) * 0.01;   // slowly re-centre on how the phone is usually held
        aim(-b * 0.45, g * 0.5, vb.x + (0.5 + g / 60) * vb.width, vb.y + (0.45 + b / 50) * vb.height);
      }, { passive: true });
    }
  }).catch(function () {});
})();
