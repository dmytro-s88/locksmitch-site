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

// Hero grid (2026-10-24, option): a 3D grid behind the hero. Lines light up around the pointer, green signals run
// along the lines from where the pointer passes (from a tap on phones, and on their own now and then). Scroll tilts
// the grid. Modes: "grid" = a wall leaning back a little, "floor" = a floor running to the horizon.
// Picked with ?bg=grid / ?bg=floor or <html data-bg="...">; the night scene stays the default.
(function () {
  var hero = document.querySelector('.hero');
  var mode = (location.search.match(/[?&]bg=(grid|floor|night)/) || [])[1] || document.documentElement.getAttribute('data-bg') || 'grid';
  if (!hero || mode === 'night' || hero.querySelector('.hs')) return;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var small = window.matchMedia('(max-width: 760px)').matches;
  var floor = mode === 'floor';
  var box = document.createElement('div'); box.className = 'hs hs-gridmode'; box.setAttribute('aria-hidden', 'true');
  var cv = document.createElement('canvas'); cv.className = 'hs-grid';
  var scrim = document.createElement('div'); scrim.className = 'hs-scrim';
  box.appendChild(cv); box.appendChild(scrim);
  hero.insertBefore(box, hero.firstChild); hero.classList.add('has-scene', 'grid-scene');
  var ctx = cv.getContext('2d'), dpr = Math.min(window.devicePixelRatio || 1, small ? 1.5 : 2);
  var W = 0, H = 0, S = small ? 46 : 58, N = 0, pulses = [], px = -9999, py = -9999, pAct = 0;
  var rx = 0, ry = 0, trx = 0, tryy = 0, D = 1100;
  function size() { cv.style.height = ''; W = cv.clientWidth; H = Math.min(cv.clientHeight, small ? Math.round(window.innerHeight * 1.15) : 1400); cv.style.height = H + 'px'; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    N = Math.ceil((floor ? Math.max(W, H) * 1.6 : Math.max(W, H) * 1.25) / S); }
  // world (u, v) on the plane -> screen
  var cxr, sxr, cyr, syr, cx0, cy0;
  var lay = 0;   // 0 = wall, 1 = laid down like a floor (wall mode, driven by scroll)
  function prep() { cxr = Math.cos(rx); sxr = Math.sin(rx); cyr = Math.cos(ry); syr = Math.sin(ry); cx0 = W * (floor ? 0.5 : 0.62 - 0.12 * lay); cy0 = floor ? H * 0.42 : H * (0.48 + 0.22 * lay); }
  function proj(u, v) {
    var x = u, y = v, z = 0;
    if (floor) { y = 0; z = v; }
    var x1 = x * cyr + z * syr, z1 = -x * syr + z * cyr;
    var y2 = y * cxr - z1 * sxr, z2 = y * sxr + z1 * cxr;
    var k = D / (D + z2); if (k <= 0) return null;
    return [cx0 + x1 * k, cy0 + y2 * k + (floor ? 120 * k : 0), k];
  }
  function lineAlpha(x, y, k) {
    var a = (floor ? 0.11 : 0.09) * Math.min(1, k * 1.2);
    if (pAct > 0.01) { var dx = x - px, dy = y - py, d = Math.sqrt(dx * dx + dy * dy), R = small ? 140 : 230; if (d < R) a += 0.32 * pAct * (1 - d / R) * (1 - d / R); }
    var ex = Math.min(x, W - x) / (W * 0.18), ey = Math.min(y, H - y) / (H * 0.18);
    return a * Math.max(0, Math.min(1, ex, ey));
  }
  var BUCKETS = 14, paths = [];
  function drawGrid() {
    var seg = small ? 12 : 20, i, j, a, b, u, v, ext = N * S, k;
    for (k = 0; k < BUCKETS; k++) paths[k] = [];
    for (var dir = 0; dir < 2; dir++) {
      for (i = -N; i <= N; i++) {
        a = null;
        for (j = 0; j <= seg; j++) {
          var t = -ext + (2 * ext) * j / seg;
          if (floor && dir === 0) { u = i * S; v = (t + ext) * 0.5; } else if (floor) { u = t; v = (i + N) * S * 0.5; } else if (dir === 0) { u = i * S; v = t; } else { u = t; v = i * S; }
          b = proj(u, v);
          if (a && b) { var mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
            if (mx > -40 && mx < W + 40 && my > -40 && my < H + 40) {   // off-screen segments are skipped
              var al = lineAlpha(mx, my, b[2]);
              if (al > 0.004) { k = Math.min(BUCKETS - 1, Math.floor(al / 0.4 * BUCKETS)); paths[k].push(a[0], a[1], b[0], b[1]); } } }
          a = b;
        }
      }
    }
    for (k = 0; k < BUCKETS; k++) {   // one stroke per brightness level instead of one per segment
      var P = paths[k]; if (!P.length) continue;
      ctx.strokeStyle = 'rgba(166,234,102,' + ((k + 0.5) / BUCKETS * 0.4).toFixed(3) + ')'; ctx.beginPath();
      for (var q = 0; q < P.length; q += 4) { ctx.moveTo(P[q], P[q + 1]); ctx.lineTo(P[q + 2], P[q + 3]); }
      ctx.stroke();
    }
  }
  function spawn(u, v, near) {
    if (pulses.length > (small ? 14 : 26)) return;
    var horiz = Math.random() < 0.5, sgn = Math.random() < 0.5 ? -1 : 1;
    pulses.push({ h: horiz, fu: Math.round(u / S) * S, fv: Math.round(v / S) * S, t: 0, dir: sgn, sp: (near ? 3.2 : 2.2) + Math.random() * 2, life: 1, len: S * (2 + Math.random() * 2.5) });
  }
  function nearestNode(x, y) {
    var best = null, bd = 1e9, ext = N;
    for (var i = -ext; i <= ext; i += 1) for (var j = (floor ? 0 : -ext); j <= ext; j += 1) {
      var u = i * S, v = floor ? j * S * 0.5 : j * S, p = proj(u, v); if (!p) continue;
      var d = (p[0] - x) * (p[0] - x) + (p[1] - y) * (p[1] - y); if (d < bd) { bd = d; best = [u, v]; }
    }
    return best;
  }
  function drawPulses() {
    for (var k = pulses.length - 1; k >= 0; k--) {
      var p = pulses[k]; p.t += p.sp; if (p.t > p.len * 3) p.life -= 0.04;
      if (p.life <= 0) { pulses.splice(k, 1); continue; }
      var steps = 8, prev = null;
      for (var s = 0; s <= steps; s++) {
        var off = (p.t - p.len * s / steps) * p.dir, u = p.h ? p.fu + off : p.fu, v = p.h ? p.fv : p.fv + off;
        var q = proj(u, v); if (!q) { prev = null; continue; }
        if (prev) { var al = (1 - s / steps) * 0.9 * p.life * Math.min(1, q[2] * 1.3);
          ctx.strokeStyle = 'rgba(166,234,102,' + al.toFixed(3) + ')'; ctx.lineWidth = 1.8 * (1 - s / steps) + 0.6;
          ctx.beginPath(); ctx.moveTo(prev[0], prev[1]); ctx.lineTo(q[0], q[1]); ctx.stroke(); }
        if (s === 0) { ctx.fillStyle = 'rgba(214,255,170,' + (0.9 * p.life).toFixed(3) + ')'; ctx.shadowColor = 'rgba(108,198,85,.9)'; ctx.shadowBlur = 10;
          ctx.beginPath(); ctx.arc(q[0], q[1], 2.1, 0, 6.283); ctx.fill(); ctx.shadowBlur = 0; }
        prev = q;
      }
    }
    ctx.lineWidth = 1;
  }
  var t0 = 0, lastSpawn = 0, autoNext = 800, frame = 0, visible = true;
  function render(t) {
    var sc = Math.max(0, Math.min(1, (window.scrollY - (hero.offsetTop || 0) + 80) / Math.max(1, hero.offsetHeight)));
    var breathe = reduce ? 0 : Math.sin(t / 7000) * 0.035 + Math.sin(t / 2900) * 0.012;
    var sl = Math.max(0, Math.min(1, sc / 0.55)); sl = sl * sl * (3 - 2 * sl);   // eased: the wall lies down over the first half of the hero
    trx = floor ? 1.18 + sc * 0.22 + breathe : -(0.2 + sl * 1.05 + breathe * (1 - sl * 0.6));   // negative: the top edge leans away, so it lies down into the distance
    lay += ((floor ? 0 : sl) - lay) * 0.08;
    rx += (trx - rx) * 0.08; ry += (tryy - ry) * 0.05; prep();
    ctx.clearRect(0, 0, W, H); ctx.lineWidth = 1; drawGrid(); drawPulses();
  }
  function loop(t) {
    if (!visible || document.hidden) return;
    if (!small || (frame++ & 1) === 0) {
      pAct += ((px > -999 ? 1 : 0) - pAct) * 0.08;
      if (t > autoNext) { var ru = (Math.floor(Math.random() * N * 1.2) - Math.floor(N * 0.6)) * S, rv = (Math.floor(Math.random() * N * 1.2) - Math.floor(N * 0.6)) * S; var pr = proj(ru, rv); if (pr && pr[0] > 0 && pr[0] < W && pr[1] > 0 && pr[1] < H) spawn(ru, rv, false); autoNext = t + (small ? 900 : 1300) + Math.random() * 1500; }
      render(t);
    }
    requestAnimationFrame(loop);
  }
  size(); prep(); window.addEventListener('resize', function () { size(); render(performance.now()); });
  if (reduce) { rx = trx = floor ? 1.18 : -0.2; prep(); render(0); return; }
  hero.addEventListener('pointermove', function (e) {
    var r = cv.getBoundingClientRect(); px = e.clientX - r.left; py = e.clientY - r.top;
    if (e.pointerType !== 'touch') tryy = ((e.clientX - r.left) / r.width - 0.5) * 0.22;
    var now = performance.now(); if (now - lastSpawn > (e.pointerType === 'touch' ? 140 : 90)) { lastSpawn = now; var n = nearestNode(px, py); if (n) spawn(n[0], n[1], true); }
  }, { passive: true });
  hero.addEventListener('pointerleave', function () { px = py = -9999; tryy = 0; });
  hero.addEventListener('touchstart', function (e) {
    var r = cv.getBoundingClientRect(), tt = e.touches[0]; px = tt.clientX - r.left; py = tt.clientY - r.top;
    var n = nearestNode(px, py); if (n) { spawn(n[0], n[1], true); spawn(n[0], n[1], true); }
    setTimeout(function () { px = py = -9999; }, 900);
  }, { passive: true });
  function start() {   // after the page has painted, so the grid never delays the first screen
    new IntersectionObserver(function (en) { visible = en[0].isIntersecting; if (visible) requestAnimationFrame(loop); }).observe(hero);
    document.addEventListener('visibilitychange', function () { if (!document.hidden && visible) requestAnimationFrame(loop); });
    requestAnimationFrame(loop);
  }
  if (document.readyState === 'complete') setTimeout(start, 300); else window.addEventListener('load', function () { setTimeout(start, 300); });
})();

// Hero scene (2026-10-24): a North Georgia night behind the hero. Stars, Blue Ridge ridges, pine hills with
// Lake Lanier, near pines. Layers move like a camera: with the pointer on desktop, with scroll on phones
// (and with tilt on Android). Static and calm with prefers-reduced-motion.
(function () {
  var hero = document.querySelector('.hero');
  if (!hero || hero.querySelector('.hs')) return;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var small = window.matchMedia('(max-width: 760px)').matches;
  var NS = 'http://www.w3.org/2000/svg';
  var seed = 7; function rnd() { seed |= 0; seed = seed + 0x6D2B79F5 | 0; var t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }
  function ridge(base, amp, step) {
    var p1 = rnd() * 6, p2 = rnd() * 6, p3 = rnd() * 6, d = 'M-120,700 L-120,' + base;
    for (var x = -120; x <= 1720; x += step) {
      var y = base - amp * (0.55 * Math.sin(x * 0.0041 + p1) + 0.3 * Math.sin(x * 0.011 + p2) + 0.15 * Math.sin(x * 0.029 + p3));
      d += ' L' + x + ',' + y.toFixed(1);
    }
    return d + ' L1720,700 Z';
  }
  function pine(x, base, h) {
    var w = h * 0.44, d = 'M' + (x - w * 0.04).toFixed(1) + ',' + base + 'h' + (w * 0.08).toFixed(1) + 'v' + (-h * 0.12).toFixed(1) + 'h' + (-w * 0.08).toFixed(1) + 'Z';
    for (var i = 0; i < 4; i++) {
      var top = base - h + i * h * 0.2, bot = top + h * 0.34 + i * h * 0.04, hw = w * (0.2 + i * 0.1);
      d += 'M' + x.toFixed(1) + ',' + top.toFixed(1) + 'L' + (x + hw).toFixed(1) + ',' + bot.toFixed(1) + 'L' + (x - hw).toFixed(1) + ',' + bot.toFixed(1) + 'Z';
    }
    return d;
  }
  function layer(cls, inner) {
    var s = document.createElementNS(NS, 'svg');
    s.setAttribute('viewBox', '0 0 1600 700'); s.setAttribute('preserveAspectRatio', 'xMidYMax slice'); s.setAttribute('class', 'hs-layer ' + cls); s.setAttribute('aria-hidden', 'true');
    s.innerHTML = inner; return s;
  }
  var far = layer('hs-far', '<defs><linearGradient id="hsFar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a4a42"/><stop offset="1" stop-color="#152620"/></linearGradient>' +
    '<linearGradient id="hsFar2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1f3830"/><stop offset="1" stop-color="#11201b"/></linearGradient></defs>' +
    '<path d="' + ridge(400, 80, 16) + '" fill="url(#hsFar)"/><path d="' + ridge(462, 60, 14) + '" fill="url(#hsFar2)"/>');
  var pines = '', i, x;
  for (i = 0; i < 70; i++) { x = -100 + i * 26 + rnd() * 14; pines += pine(x, 566 + rnd() * 8, 34 + rnd() * 34); }
  var mid = layer('hs-mid', '<defs><linearGradient id="hsLake" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4FB0BE" stop-opacity=".38"/><stop offset=".25" stop-color="#173430" stop-opacity=".95"/><stop offset="1" stop-color="#0a1311"/></linearGradient></defs>' +
    '<path d="' + ridge(540, 22, 20) + '" fill="#10201a"/><path d="' + pines + '" fill="#10201a"/>' +
    '<rect x="-120" y="572" width="1840" height="140" fill="url(#hsLake)"/>' +
    '<g class="hs-shimmer" stroke="#A6EA66" stroke-linecap="round">' +
    [[180, 590, 60], [420, 604, 90], [690, 594, 50], [930, 612, 110], [1210, 598, 70], [1420, 608, 60], [560, 624, 40], [1080, 628, 50]].map(function (a, k) {
      return '<line x1="' + a[0] + '" y1="' + a[1] + '" x2="' + (a[0] + a[2]) + '" y2="' + a[1] + '" stroke-width="1.6" style="animation-delay:' + (k * 0.7).toFixed(1) + 's"/>'; }).join('') + '</g>');
  var near = '';
  for (i = 0; i < 16; i++) { x = -60 + i * 30 + rnd() * 18; near += pine(x, 712, 150 + rnd() * 170 - i * 6); }
  for (i = 0; i < 16; i++) { x = 1660 - i * 30 - rnd() * 18; near += pine(x, 712, 150 + rnd() * 170 - i * 6); }
  for (i = 0; i < 18; i++) { x = 480 + i * 36 + rnd() * 20; near += pine(x, 712, 46 + rnd() * 40); }
  var nearL = layer('hs-near', '<path d="' + near + '" fill="#070c0a"/><rect x="-120" y="690" width="1840" height="30" fill="#070c0a"/>');
  var box = document.createElement('div'); box.className = 'hs'; box.setAttribute('aria-hidden', 'true');
  var stars = document.createElement('canvas'); stars.className = 'hs-layer hs-stars';
  var glow = document.createElement('div'); glow.className = 'hs-layer hs-glow';
  var shoot = document.createElement('i'); shoot.className = 'hs-shoot';
  var scrim = document.createElement('div'); scrim.className = 'hs-scrim';
  [stars, shoot, glow, far, mid, nearL, scrim].forEach(function (n) { box.appendChild(n); });
  hero.insertBefore(box, hero.firstChild);
  hero.classList.add('has-scene');

  // stars
  var ctx = stars.getContext('2d'), list = [], dpr = Math.min(window.devicePixelRatio || 1, 2), sw = 0, sh = 0;
  function sizeStars() {
    sw = stars.clientWidth; sh = stars.clientHeight; if (!sw || !sh) return;
    stars.width = sw * dpr; stars.height = sh * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    list = []; var n = Math.round(sw * sh / (small ? 7000 : 5200));
    for (var k = 0; k < n; k++) list.push({ x: Math.random() * sw, y: Math.random() * sh * 0.72, r: Math.random() * 1.1 + 0.25, p: Math.random() * 6.28, s: 0.4 + Math.random() * 1.1, g: Math.random() < 0.12 });
    drawStars(0);
  }
  function drawStars(t) {
    ctx.clearRect(0, 0, sw, sh);
    for (var k = 0; k < list.length; k++) {
      var s = list[k], a = reduce ? 0.55 : 0.2 + 0.6 * (0.5 + 0.5 * Math.sin(t / 1000 * s.s + s.p));
      ctx.fillStyle = s.g ? 'rgba(166,234,102,' + (a * 0.9).toFixed(3) + ')' : 'rgba(234,240,236,' + a.toFixed(3) + ')';
      ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, 6.283); ctx.fill();
    }
  }
  sizeStars(); window.addEventListener('resize', sizeStars);
  if (reduce) return;

  // shooting star now and then
  function fly() {
    shoot.style.top = (6 + Math.random() * 26) + '%'; shoot.style.left = (20 + Math.random() * 55) + '%';
    shoot.classList.remove('go'); void shoot.offsetWidth; shoot.classList.add('go');
    setTimeout(fly, 7000 + Math.random() * 9000);
  }
  setTimeout(fly, 2500);

  // camera: pointer (desktop), scroll (all), tilt (Android)
  var L = [[stars, 8, 0.5], [glow, 12, 0.38], [far, 18, 0.3], [mid, 34, 0.16], [nearL, 58, 0.05]];
  var tx = 0, ty = 0, cx = 0, cy = 0, visible = true, frame = 0;
  hero.addEventListener('pointermove', function (e) {
    if (e.pointerType === 'touch') return;
    var r = hero.getBoundingClientRect(); tx = ((e.clientX - r.left) / r.width - 0.5) * 2; ty = ((e.clientY - r.top) / r.height - 0.5) * 2;
  }, { passive: true });
  hero.addEventListener('pointerleave', function () { tx = 0; ty = 0; });
  if (window.DeviceOrientationEvent && typeof DeviceOrientationEvent.requestPermission !== 'function' && small) {
    var base = null;
    window.addEventListener('deviceorientation', function (e) {
      if (e.gamma == null) return; if (base === null) base = e.beta;
      tx = Math.max(-1, Math.min(1, e.gamma / 25)); ty = Math.max(-1, Math.min(1, (e.beta - base) / 25));
    }, { passive: true });
  }
  new IntersectionObserver(function (en) { visible = en[0].isIntersecting; if (visible) requestAnimationFrame(loop); }).observe(hero);
  function loop(t) {
    if (!visible || document.hidden) return;
    cx += (tx - cx) * 0.06; cy += (ty - cy) * 0.06;
    var sy = Math.max(0, Math.min(window.scrollY - (hero.offsetTop || 0) + 80, hero.offsetHeight));
    for (var k = 0; k < L.length; k++) {
      var d = L[k][1], f = L[k][2];
      L[k][0].style.transform = 'translate3d(' + (-cx * d).toFixed(2) + 'px,' + (-cy * d * 0.45 + sy * f).toFixed(2) + 'px,0)';
    }
    if ((frame++ & 1) === 0) drawStars(t);
    requestAnimationFrame(loop);
  }
  document.addEventListener('visibilitychange', function () { if (!document.hidden && visible) requestAnimationFrame(loop); });
  requestAnimationFrame(loop);
})();
