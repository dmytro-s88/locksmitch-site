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
