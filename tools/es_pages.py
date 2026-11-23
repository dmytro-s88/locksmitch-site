"""Spanish landing pages built on es/precios/index.html:
/es/llaves-de-carro/, /es/abrir-carro/, /es/cerrajero-gainesville/, /es/cerrajero-lawrenceville/.

Run from the site root after tools/es_build.py (rerun is safe):
    python3 -I tools/es_pages.py
then tools/sitemap_lastmod.py.

The template keeps the header, estimate form, services, "Cómo funciona", area and contact blocks. Head, hero, the
#local section and the FAQ are replaced. Prices must match /es/precios/. Mitch does not speak Spanish: every page says
customers can write in Spanish and he answers with a translator.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, 'es', 'precios', 'index.html')
SITE = 'https://locksmitch.com'
CALL = '<a href="tel:7702703333">(770) 270-3333</a>'
TEXT = '<a href="sms:+17702703333">(770) 270-3333</a>'
SPANISH = ('Mitch no habla español, pero puede escribirle en español por texto o WhatsApp: él usa un traductor y le contesta con gusto.')
HOURS = ('Aperturas y pérdida de todas las llaves: 24/7, también de noche, domingos y días festivos. Llaves de repuesto, programación '
         'y otros trabajos: de lunes a sábado. De 9 pm a 7 am hay un cargo de noche de $50.')
STYLE = ('<style>.guide-body .price-rows{list-style:none;padding:0;margin:0 0 26px;display:grid;gap:8px}'
         '.guide-body .price-rows li{margin:0;display:flex;justify-content:space-between;gap:16px;padding:10px 14px;border:1px solid var(--line);border-radius:10px}'
         '.guide-body .price-rows b{white-space:nowrap}</style>')


def sub1(pat, repl, s, flags=0):
    new, n = re.subn(pat, lambda m: repl, s, count=1, flags=flags)
    if not n:
        raise SystemExit('template changed, not found: ' + pat[:60])
    return new


def esc(t):
    return html.escape(t, quote=True)


def plain(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', t))).strip()


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'


def prices(rows):
    return '<ul class="price-rows">%s</ul>\n' % ''.join('<li><span>%s</span><b>%s</b></li>' % (a, b) for a, b in rows)


KEY_PRICES = prices([('Llave sin chip', 'desde $75'), ('Llave extra con chip', 'desde $140'), ('Llave con control o llave navaja', 'desde $150'),
                     ('Llave inteligente (encendido por botón)', 'desde $180'), ('Llave inteligente, 2020 y más nuevos', 'desde $200'),
                     ('Perdió todas las llaves', 'desde $190'), ('Programar una llave inteligente que usted compró', '$129'),
                     ('Segunda llave del mismo carro, misma visita', '50% menos')])

PAGES = [
    dict(slug='llaves-de-carro', en='/car-key-replacement/', crumb='Llaves de carro',
         title='Llaves de Carro a Domicilio en Cumming, GA | LocksMitch',
         desc='Llaves de carro a domicilio en Cumming y North Atlanta: llave extra desde $140, llave inteligente desde $180, todas las llaves perdidas desde $190. (770) 270-3333.',
         h1='Llaves de carro a domicilio', l2='Llave extra, llave inteligente o todas las llaves perdidas, hechas en su carro.',
         lede='Cortamos y programamos la llave donde está su carro: en su casa, su trabajo o un estacionamiento. Sin grúa y sin dealer. Le damos el precio antes de salir.',
         article=(
             '<h2>Respuesta rápida</h2>\n<p>Una llave extra con chip cuesta <strong>desde $140</strong>, una llave inteligente <strong>desde $180</strong> '
             'y si perdió todas las llaves, <strong>desde $190</strong>. La visita está incluida. La segunda llave del mismo carro en la misma visita es a mitad de precio.</p>\n'
             '<h2>Qué tipo de llave tiene</h2>\n<ul><li><strong>Llave con chip</strong>: llave de metal con un chip en la cabeza. El carro no arranca sin el chip programado.</li>'
             '<li><strong>Llave con control o llave navaja</strong>: la llave y los botones en una sola pieza.</li>'
             '<li><strong>Llave inteligente</strong>: el carro arranca con un botón y la llave en el bolsillo.</li></ul>\n'
             '<h2>Precios</h2>\n' + KEY_PRICES +
             '<p>El precio exacto depende de la marca, el año y el tipo de llave. Vea todos los <a href="/es/precios/">precios</a>.</p>\n'
             '<h2>Si perdió todas las llaves</h2>\n<p>No necesita la llave original. Hacemos la llave nueva con el código del carro, la cortamos y la programamos ahí mismo. '
             'Para eso necesitamos ver que el carro es suyo: una identificación con foto y el registro, el título o la tarjeta del seguro.</p>\n'
             '<h2>Le robaron la llave</h2>\n<p>Al programar la llave nueva podemos borrar la llave robada de la memoria del carro, para que ya no lo arranque. '
             'Con una llave nueva nuestra es gratis; solo borrar, desde $89.</p>\n'
             '<h2>Cuándo llamar</h2>\n<p>' + HOURS + '</p>\n'
             '<h2>¿Habla español?</h2>\n<p>' + SPANISH + '</p>\n'),
         faq=[('¿Cuánto cuesta una llave de carro nueva?', 'Una llave extra con chip desde $140, una llave con control desde $150, una llave inteligente desde $180 y todas las llaves perdidas desde $190. La visita está incluida.'),
              ('¿Pueden hacer una llave sin la original?', 'Sí. Es el trabajo de todas las llaves perdidas: hacemos la llave con el código del carro y la programamos en su carro.'),
              ('¿Necesito llevar el carro al dealer?', 'No. Vamos hasta su carro con la máquina de corte y el programador.'),
              ('¿Trabajan el domingo?', 'El domingo solo atendemos aperturas y todas las llaves perdidas. Las llaves de repuesto se hacen de lunes a sábado.'),
              ('¿Puedo escribir en español?', SPANISH)]),
    dict(slug='abrir-carro', en='/car-lockout/', crumb='Abrir carro',
         title='Abrir Carro con Llaves Adentro en Cumming, GA | LocksMitch',
         desc='¿Dejó las llaves dentro del carro? Abrimos su carro sin daños en Cumming y North Atlanta, 24/7. Desde $75 en Cumming y Forsyth. (770) 270-3333.',
         h1='Abrir carro con las llaves adentro', l2='Precio fijo, sin daños, 24/7 también el domingo.',
         lede='Si dejó las llaves dentro del carro, vamos a donde esté y lo abrimos con herramientas especiales, sin romper nada. Llame y le decimos cuánto tardamos.',
         article=(
             '<h2>Respuesta rápida</h2>\n<p><strong>Si hay un niño o una mascota adentro y hace calor, llame primero al 911.</strong> '
             'Abrir el carro cuesta <strong>$75</strong> en Cumming y el condado de Forsyth, <strong>$100</strong> hasta 25 millas y <strong>$125</strong> hasta 40 millas. '
             'De noche, de 9 pm a 7 am, hay un cargo de $50. Si hay un niño o una mascota encerrados, lo abrimos gratis.</p>\n'
             '<h2>Precios</h2>\n' + prices([('Cumming, Forsyth y Sugar Hill', '$75'), ('Hasta 25 millas', '$100'), ('Hasta 40 millas', '$125'),
                                           ('De noche, de 9 pm a 7 am', '+$50'), ('Niño o mascota encerrados', 'gratis')]) +
             '<h2>Qué no hacer</h2>\n<ul><li>No meta ganchos de ropa ni alambres por la ventana: dañan el hule y los cables de la puerta.</li>'
             '<li>No rompa una ventana si no es una emergencia: cuesta mucho más que abrir el carro.</li></ul>\n'
             '<h2>Cómo lo abrimos</h2>\n<p>Con herramientas para carros, como las del dealer: abrimos la cerradura o la puerta sin forzarla y sin dañar la pintura.</p>\n'
             '<h2>¿Perdió la llave en vez de dejarla adentro?</h2>\n<p>Entonces necesita una llave nueva: vea <a href="/es/llaves-de-carro/">llaves de carro</a>.</p>\n'
             '<h2>¿Habla español?</h2>\n<p>' + SPANISH + '</p>\n'),
         faq=[('¿Cuánto cuesta abrir un carro?', 'Precio fijo: $75 en Cumming y Forsyth, $100 hasta 25 millas y $125 hasta 40 millas. De noche, de 9 pm a 7 am, hay un cargo de $50.'),
              ('¿Abrir el carro lo daña?', 'No, con las herramientas correctas. Los daños vienen de ganchos, alambres y de forzar la puerta.'),
              ('¿Vienen de noche y el domingo?', 'Sí. Las aperturas se atienden 24/7, también de noche, domingos y días festivos.'),
              ('¿Puedo escribir en español?', SPANISH)]),
    dict(slug='cerrajero-gainesville', en='/gainesville/', crumb='Cerrajero en Gainesville',
         title='Cerrajero de Autos en Gainesville, GA | LocksMitch',
         desc='Cerrajero de autos a domicilio en Gainesville, GA: llaves nuevas, llaves inteligentes, todas las llaves perdidas y apertura de carros. (770) 270-3333.',
         h1='Cerrajero de autos en Gainesville, GA', l2='Llaves nuevas y apertura de carros, en su casa o su trabajo.',
         lede='Vamos a Gainesville y a todo el condado de Hall: cortamos y programamos llaves en su carro y abrimos carros con las llaves adentro. Sin grúa y sin dealer.',
         article=(
             '<h2>Respuesta rápida</h2>\n<p>En Gainesville las llaves tienen el mismo precio que en Cumming: llave extra con chip <strong>desde $140</strong>, '
             'llave inteligente <strong>desde $180</strong>, todas las llaves perdidas <strong>desde $190</strong>. Abrir un carro en Gainesville cuesta <strong>$100</strong>.</p>\n'
             '<h2>Precios en Gainesville</h2>\n' + KEY_PRICES.replace('<li><span>Llave sin chip</span><b>desde $75</b></li>', '<li><span>Llave sin chip</span><b>$100</b></li>')
             .replace('<ul class="price-rows">', '<ul class="price-rows"><li><span>Abrir el carro</span><b>$100</b></li>') +
             '<p>Vea todos los <a href="/es/precios/">precios</a>.</p>\n'
             '<h2>Un trabajo real en Gainesville</h2>\n<p>Una Hyundai Tucson 2026: los dueños tenían una sola llave. Pedimos la llave original de Hyundai por el VIN '
             'y la programamos en el garaje. Fotos y detalles (en inglés): <a href="/jobs/2026-hyundai-tucson-spare-smart-key-gainesville/">2026 Hyundai Tucson en Gainesville</a>.</p>\n'
             '<h2>Dónde trabajamos</h2>\n<p>Gainesville, Oakwood, Flowery Branch, Buford y los alrededores del lago Lanier. Página en inglés: <a href="/gainesville/">Gainesville</a>.</p>\n'
             '<h2>Cuándo llamar</h2>\n<p>' + HOURS + '</p>\n'
             '<h2>¿Habla español?</h2>\n<p>' + SPANISH + '</p>\n'),
         faq=[('¿Cuánto cuesta una llave de carro en Gainesville?', 'Igual que en Cumming: llave extra con chip desde $140, llave inteligente desde $180, todas las llaves perdidas desde $190. La visita está incluida.'),
              ('¿Cuánto cuesta abrir un carro en Gainesville?', '$100, precio fijo. De noche, de 9 pm a 7 am, hay un cargo de $50.'),
              ('¿Puedo escribir en español?', SPANISH)]),
    dict(slug='cerrajero-lawrenceville', en='/lawrenceville/', crumb='Cerrajero en Lawrenceville',
         title='Cerrajero de Autos en Lawrenceville, GA | LocksMitch',
         desc='Cerrajero de autos a domicilio en Lawrenceville, GA: llaves nuevas, llaves inteligentes, todas las llaves perdidas y apertura de carros. (770) 270-3333.',
         h1='Cerrajero de autos en Lawrenceville, GA', l2='Llaves nuevas y apertura de carros, en su casa o su trabajo.',
         lede='Vamos a Lawrenceville y al condado de Gwinnett: cortamos y programamos llaves en su carro y abrimos carros con las llaves adentro. Sin grúa y sin dealer.',
         article=(
             '<h2>Respuesta rápida</h2>\n<p>En Lawrenceville las llaves tienen el mismo precio que en Cumming: llave extra con chip <strong>desde $140</strong>, '
             'llave inteligente <strong>desde $180</strong>, todas las llaves perdidas <strong>desde $190</strong>. Abrir un carro en Lawrenceville cuesta <strong>$100</strong>.</p>\n'
             '<h2>Precios en Lawrenceville</h2>\n' + KEY_PRICES.replace('<li><span>Llave sin chip</span><b>desde $75</b></li>', '<li><span>Llave sin chip</span><b>$100</b></li>')
             .replace('<ul class="price-rows">', '<ul class="price-rows"><li><span>Abrir el carro</span><b>$100</b></li>') +
             '<p>Vea todos los <a href="/es/precios/">precios</a>.</p>\n'
             '<h2>Un trabajo real en Lawrenceville</h2>\n<p>Un Nissan Altima 2015: el carro ya no aceptaba la llave inteligente, aunque la llave funcionaba. '
             'Programamos una llave nueva en el carro. Fotos y detalles (en inglés): <a href="/jobs/2015-nissan-altima-smart-key-lawrenceville/">2015 Nissan Altima en Lawrenceville</a>.</p>\n'
             '<h2>Dónde trabajamos</h2>\n<p>Lawrenceville, Duluth, Suwanee, Buford y el resto de Gwinnett. Página en inglés: <a href="/lawrenceville/">Lawrenceville</a>.</p>\n'
             '<h2>Cuándo llamar</h2>\n<p>' + HOURS + '</p>\n'
             '<h2>¿Habla español?</h2>\n<p>' + SPANISH + '</p>\n'),
         faq=[('¿Cuánto cuesta una llave de carro en Lawrenceville?', 'Igual que en Cumming: llave extra con chip desde $140, llave inteligente desde $180, todas las llaves perdidas desde $190. La visita está incluida.'),
              ('¿Cuánto cuesta abrir un carro en Lawrenceville?', '$100, precio fijo. De noche, de 9 pm a 7 am, hay un cargo de $50.'),
              ('¿Puedo escribir en español?', SPANISH)]),
]


def build(tpl, p):
    url = '%s/es/%s/' % (SITE, p['slug'])
    en = SITE + p['en']
    s = tpl
    s = sub1(r'<html lang="es" data-page="[^"]*">', '<html lang="es" data-page="ES %s">' % esc(p['crumb']), s)
    s = sub1(r'<title>.*?</title>', '<title>%s</title>' % esc(p['title']), s)
    s = sub1(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % esc(p['desc']), s)
    s = sub1(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">' % url, s)
    s = sub1(r'<link rel="alternate" hreflang="en" href="[^"]*">', '<link rel="alternate" hreflang="en" href="%s">' % en, s)
    s = sub1(r'<link rel="alternate" hreflang="es" href="[^"]*">', '<link rel="alternate" hreflang="es" href="%s">' % url, s)
    s = sub1(r'<link rel="alternate" hreflang="x-default" href="[^"]*">', '<link rel="alternate" hreflang="x-default" href="%s">' % en, s)
    s = sub1(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s">' % url, s)
    s = sub1(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % esc(p['title']), s)
    s = sub1(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % esc(p['desc']), s)
    s = s.replace('<a class="lang" href="/pricing/"', '<a class="lang" href="%s"' % p['en'], 1)
    lds = [ld({'@context': 'https://schema.org', '@type': 'WebPage', 'url': url, 'name': p['title'], 'inLanguage': 'es',
               'about': {'@id': SITE + '/#locksmith'}}),
           ld({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
               {'@type': 'ListItem', 'position': 1, 'name': 'LocksMitch', 'item': SITE + '/es/'},
               {'@type': 'ListItem', 'position': 2, 'name': p['crumb'], 'item': url}]}),
           ld({'@context': 'https://schema.org', '@type': 'FAQPage', 'inLanguage': 'es', 'mainEntity': [
               {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in p['faq']]})]
    head, body = s.split('</head>', 1)
    head = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', head, flags=re.S)
    head = head + '\n'.join(lds) + '\n' + STYLE + '\n'
    s = head + '</head>' + body
    s = sub1(r'<nav class="crumbs" aria-label="Ruta">.*?</nav>', '<nav class="crumbs" aria-label="Ruta"><a href="/es/">LocksMitch</a> › %s</nav>' % esc(p['crumb']), s)
    s = sub1(r'<h1>.*?</h1>', '<h1>%s<span class="l2">%s</span></h1>' % (esc(p['h1']), esc(p['l2'])), s)
    s = sub1(r'<p class="lede">.*?</p>', '<p class="lede">%s</p>' % esc(p['lede']), s)
    article = p['article'] + '<h2>Pida su precio</h2>\n<p>Llame o envíe un texto al ' + TEXT + ' con el año, la marca y el modelo. Le damos el precio antes de salir.</p>'
    aside = ('<aside class="nearby guide-side"><h3>En español</h3><ul style="grid-template-columns:1fr"><li><a href="/es/">Inicio</a></li>'
             '<li><a href="/es/llaves-de-carro/">Llaves de carro</a></li><li><a href="/es/abrir-carro/">Abrir carro</a></li>'
             '<li><a href="/es/cerrajero-gainesville/">Cerrajero en Gainesville</a></li><li><a href="/es/cerrajero-lawrenceville/">Cerrajero en Lawrenceville</a></li>'
             '<li><a href="/es/precios/">Precios</a></li></ul></aside>')
    local = ('<section class="local guide" id="local">\n    <div class="wrap local-grid">\n      <article class="guide-body">\n%s\n      </article>\n      %s\n'
             '    </div>\n  </section>\n\n  ') % (article, aside)
    s = sub1(r'<section class="local pricing" id="local">.*?</section>\n\s*', local, s, flags=re.S)
    faq = ''.join('<details%s><summary>%s</summary><p>%s</p></details>' % (' open' if i == 0 else '', esc(q), a) for i, (q, a) in enumerate(p['faq']))
    s = sub1(r'<div class="faq" id="faq">\s*<h2 class="col-h">Preguntas sobre precios</h2>.*?</div>\n', '<div class="faq" id="faq">\n        <h2 class="col-h">Preguntas frecuentes</h2>\n        %s\n      </div>\n' % faq, s, flags=re.S)
    return s


def main():
    tpl = open(TEMPLATE, encoding='utf-8').read()
    changed = []
    for p in PAGES:
        s = build(tpl, p)
        path = os.path.join(ROOT, 'es', p['slug'], 'index.html')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
        if s != old:
            open(path, 'w', encoding='utf-8').write(s)
            changed.append(p['slug'])
    print('es pages: %d; changed: %s' % (len(PAGES), ', '.join(changed) or 'none'))


main()
