"""One page per real job: /jobs/<slug>/ plus the hub /jobs/. Data: tools/job_pages.json (texts) + tools/jobs.json (date, vehicle,
service, city; the job is matched by "slug"). Photos: assets/jobs/<slug>.webp.

Run from the site root (rerun is safe):
    python3 -I tools/job_pages.py
then tools/jobs_build.py (links the job lists to these pages) and tools/sitemap_lastmod.py.

Template: guides/keys-locked-in-car/index.html (header, estimate form, "How a visit works", footer). Only the head, the hero
text and the article/aside are replaced, so shared parts stay in sync with the guides.
The repo is public: no customer names, addresses, phones, prices or lead numbers in the data.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, 'guides', 'keys-locked-in-car', 'index.html')
SITE = 'https://locksmitch.com'
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
SVC = {'all-keys-lost': ('akl', 's1'), 'spare-key': ('spare', 's2'), 'car-lockout': ('lockout', 's3'), 'key-programming': ('program', 's4')}
STYLE = ('<style>.job-photo{margin:0 0 26px;border-radius:16px;overflow:hidden;max-width:520px;background:var(--surface)}'
         '.job-photo img{display:block;width:100%;height:auto}'
         '.job-facts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 18px;margin:0 0 26px;padding:16px 18px;border:1px solid var(--line);border-radius:14px}'
         '.job-facts dt{font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}.job-facts dd{margin:2px 0 0;font-weight:700}'
         '.job-cards{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px}'
         '.job-cards a{display:block;text-decoration:none;color:inherit;border:1px solid var(--line);border-radius:14px;overflow:hidden;height:100%}'
         '.job-cards img{display:block;width:100%;height:auto;aspect-ratio:4/5;object-fit:cover}.job-cards b{display:block;padding:12px 14px 4px}'
         '.job-cards span{display:block;padding:0 14px 14px;color:var(--muted);font-size:15px;line-height:1.45}</style>')


def sub1(pat, repl, s, flags=0):
    """re.sub once with a literal replacement (text may contain backslashes)."""
    return re.sub(pat, lambda m: repl, s, count=1, flags=flags)


def esc(t):
    return html.escape(t, quote=True)


def month(date):
    y, m = date.split('-')[:2]
    return MONTHS[int(m) - 1] + ' ' + y


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'


PHONE = ' Call (770) 270-3333.'


def with_phone(text):
    """Meta description with the phone at the end when it still fits in a search snippet (160 characters)."""
    return text + PHONE if len(text + PHONE) <= 160 else text


def set_head(s, title, desc, url, image, page_name, og_type, lds):
    s = sub1(r'<html lang="en" data-page="[^"]*">', '<html lang="en" data-page="%s">' % esc(page_name), s)
    s = sub1(r'<title>.*?</title>', '<title>%s</title>' % esc(title), s)
    s = sub1(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % esc(desc), s)
    s = sub1(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">' % url, s)
    s = sub1(r'<meta property="og:type" content="[^"]*">', '<meta property="og:type" content="%s">' % og_type, s)
    s = sub1(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s">' % url, s)
    s = sub1(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % esc(title), s)
    s = sub1(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % esc(desc), s)
    if image:
        s = sub1(r'<meta property="og:image" content="[^"]*">\n<meta property="og:image:width" content="\d+">\n<meta property="og:image:height" content="\d+">',
                   '<meta property="og:image" content="%s">\n<meta property="og:image:width" content="960">\n<meta property="og:image:height" content="1200">' % image, s)
    s = sub1(r'(<script type="application/ld\+json">.*?</script>\n)+</head>', '\n'.join(lds) + '\n' + STYLE + '\n</head>', s, flags=re.S)
    return s


def set_hero(s, crumbs, h1, l2, lede, byline, svc):
    s = sub1(r'<nav class="crumbs" aria-label="Breadcrumb">.*?</nav>', '<nav class="crumbs" aria-label="Breadcrumb">%s</nav>' % crumbs, s)
    s = sub1(r'<h1>.*?</h1>', '<h1>%s<span class="l2">%s</span></h1>' % (esc(h1), esc(l2)), s)
    s = sub1(r'<p class="lede">.*?</p>', '<p class="lede">%s</p>' % esc(lede), s)
    s = sub1(r'<p class="byline">.*?</p>', '<p class="byline">%s</p>' % esc(byline), s)
    book, radio = SVC.get(svc, ('spare', 's2'))
    s = s.replace('/book/?svc=lockout', '/book/?svc=' + book, 1)
    s = s.replace('value="Locked out" checked>', 'value="Locked out">', 1)
    s = re.sub(r'(id="%s" value="[^"]*")>' % radio, r'\1 checked>', s, count=1)
    return s


def set_body(s, article, aside):
    s = sub1(r'<article class="guide-body">.*?</article>', '<article class="guide-body">\n' + article + '\n      </article>', s, flags=re.S)
    s = sub1(r'<aside class="nearby guide-side">.*?</aside>', aside, s, flags=re.S)
    return s


def write(rel, s):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    old = open(path, encoding='utf-8').read() if os.path.exists(path) else None
    if s != old:
        open(path, 'w', encoding='utf-8').write(s)
    return s != old


def main():
    tpl = open(TEMPLATE, encoding='utf-8').read()
    pages = json.load(open(os.path.join(ROOT, 'tools', 'job_pages.json'), encoding='utf-8'))['pages']
    jobs = {j['slug']: j for j in json.load(open(os.path.join(ROOT, 'tools', 'jobs.json'), encoding='utf-8'))['jobs'] if j.get('slug')}
    for p in pages:
        if p['slug'] not in jobs:
            raise SystemExit('no job with slug %s in tools/jobs.json' % p['slug'])
        if not os.path.exists(os.path.join(ROOT, 'assets', 'jobs', p['slug'] + '.webp')):
            raise SystemExit('no photo assets/jobs/%s.webp' % p['slug'])
    order = [j['slug'] for j in json.load(open(os.path.join(ROOT, 'tools', 'jobs.json'), encoding='utf-8'))['jobs'] if j.get('slug')]
    pages.sort(key=lambda p: order.index(p['slug']))
    changed = []

    for p in pages:
        j = jobs[p['slug']]
        url = '%s/jobs/%s/' % (SITE, p['slug'])
        img = '/assets/jobs/%s.webp' % p['slug']
        when = month(j['date'])
        svc_slug = p['service_page'].strip('/')
        lds = [
            ld({'@context': 'https://schema.org', '@type': 'Article', 'headline': p['title'], 'description': p['summary'],
                'image': SITE + img, 'datePublished': j['date'] + '-01', 'dateModified': j['date'] + '-01',
                'author': {'@type': 'Person', 'name': 'Mitch', 'url': SITE + '/'},
                'publisher': {'@id': SITE + '/#locksmith'}, 'about': {'@type': 'Service', 'name': j['service'], 'provider': {'@id': SITE + '/#locksmith'},
                'areaServed': {'@type': 'City', 'name': j['city'] + ', GA'}}, 'mainEntityOfPage': url}),
            ld({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'LocksMitch', 'item': SITE + '/'},
                {'@type': 'ListItem', 'position': 2, 'name': 'Recent jobs', 'item': SITE + '/jobs/'},
                {'@type': 'ListItem', 'position': 3, 'name': p['title'], 'item': url}]}),
        ]
        s = set_head(tpl, p['title'] + ' | LocksMitch', with_phone(p['summary']), url, SITE + img, 'Job: ' + p['title'], 'article', lds)
        s = set_hero(s, '<a href="/">LocksMitch</a> › <a href="/jobs/">Recent jobs</a> › %s' % esc(j['vehicle']),
                     p['title'], 'Recent job · %s' % when, p['summary'], 'By Mitch, owner of LocksMitch · Job done %s' % when, svc_slug)
        did = ''.join('<li>%s</li>' % esc(x) for x in p['did'])
        city_name = j['city']
        article = (
            '<figure class="job-photo"><img src="%s" alt="%s" width="960" height="1200" loading="eager"></figure>\n'
            '<dl class="job-facts"><div><dt>Vehicle</dt><dd>%s</dd></div><div><dt>Service</dt><dd>%s</dd></div>'
            '<div><dt>Area</dt><dd>%s, GA</dd></div><div><dt>Date</dt><dd>%s</dd></div></dl>\n'
            '<h2>The problem</h2>\n<p>%s</p>\n'
            '<h2>What I did</h2>\n<ol>%s</ol>\n'
            '<h2>The result</h2>\n<p>%s</p>\n'
            '<h2>Good to know</h2>\n<p>%s</p>\n'
            '<h2>Need this in %s?</h2>\n<p>Call or text <a href="tel:7702703333">(770) 270-3333</a> with the year, make and model. '
            'You get the price before I drive out. More: <a href="%s">%s keys</a>, <a href="%s">%s</a>, <a href="%s">car locksmith in %s</a>, '
            '<a href="/pricing/">prices</a>.</p>'
        ) % (img, esc(p['alt']), esc(j['vehicle']), esc(j['service']), esc(city_name), when, esc(p['problem']), did,
             esc(p['result']), esc(p['tip']), esc(city_name), p['make_page'], esc(p['make']), p['service_page'], esc(j['service'].lower()),
             p['city_page'], esc(city_name))
        others = [o for o in pages if o['slug'] != p['slug']][:6]
        aside = ('<aside class="nearby guide-side"><h3>More recent jobs</h3><ul style="grid-template-columns:1fr">%s<li><a href="/jobs/">All recent jobs</a></li></ul>'
                 '<h3 style="margin-top:20px">Services</h3><ul style="grid-template-columns:1fr"><li><a href="/all-keys-lost/">All keys lost</a></li>'
                 '<li><a href="/spare-key/">Spare key</a></li><li><a href="/car-lockout/">Car lockout</a></li><li><a href="/key-programming/">Key programming</a></li>'
                 '<li><a href="/pricing/">Prices</a></li></ul></aside>') % ''.join(
            '<li><a href="/jobs/%s/">%s, %s</a></li>' % (o['slug'], esc(jobs[o['slug']]['vehicle']), esc(jobs[o['slug']]['city'])) for o in others)
        s = set_body(s, article, aside)
        if write('jobs/%s/index.html' % p['slug'], s):
            changed.append(p['slug'])

    # hub
    url = SITE + '/jobs/'
    title = 'Recent Car Key Jobs in North Atlanta, GA'
    desc = 'Real car key jobs done by LocksMitch around Cumming and North Atlanta: the car, the problem, what was done, with a photo from each job.'
    items = [{'@type': 'ListItem', 'position': i + 1, 'url': '%s/jobs/%s/' % (SITE, p['slug']), 'name': p['title']} for i, p in enumerate(pages)]
    lds = [ld({'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': title, 'description': desc, 'url': url,
               'mainEntity': {'@type': 'ItemList', 'itemListElement': items}}),
           ld({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
               {'@type': 'ListItem', 'position': 1, 'name': 'LocksMitch', 'item': SITE + '/'},
               {'@type': 'ListItem', 'position': 2, 'name': 'Recent jobs', 'item': url}]})]
    s = set_head(tpl, title + ' | LocksMitch', 'Real car key jobs by LocksMitch around Cumming and North Atlanta: the car, the problem and the fix, with a photo.' + PHONE, url, None, 'Recent jobs', 'website', lds)
    s = set_hero(s, '<a href="/">LocksMitch</a> › Recent jobs', 'Recent jobs', 'Real cars, real keys, around North Atlanta.',
                 'Every job here is a real one: the car, what went wrong and what I did, with a photo from the job. No customer names.',
                 'By Mitch, owner of LocksMitch · Updated %s' % month(jobs[pages[0]['slug']]['date']), 'spare-key')
    cards = ''.join('<li><a href="/jobs/%s/"><img src="/assets/jobs/%s.webp" alt="%s" width="960" height="1200" loading="lazy">'
                    '<b>%s</b><span>%s · %s, GA · %s</span></a></li>' % (
                        p['slug'], p['slug'], esc(p['alt']), esc(jobs[p['slug']]['vehicle']), esc(p['result_short']),
                        esc(jobs[p['slug']]['city']), month(jobs[p['slug']]['date'])) for p in pages)
    article = ('<p>These are jobs from the last weeks, newest first. Each page tells what the problem was, what I did at the car and how it ended.</p>\n'
               '<ul class="job-cards">%s</ul>\n'
               '<h2>Have a car like one of these?</h2>\n<p>Call or text <a href="tel:7702703333">(770) 270-3333</a> with the year, make and model, '
               'or see <a href="/pricing/">prices</a>.</p>') % cards
    aside = ('<aside class="nearby guide-side"><h3>Services</h3><ul style="grid-template-columns:1fr"><li><a href="/all-keys-lost/">All keys lost</a></li>'
             '<li><a href="/spare-key/">Spare key</a></li><li><a href="/car-lockout/">Car lockout</a></li><li><a href="/key-programming/">Key programming</a></li>'
             '<li><a href="/pricing/">Prices</a></li><li><a href="/guides/">Guides</a></li></ul></aside>')
    s = set_body(s, article, aside)
    if write('jobs/index.html', s):
        changed.append('(hub)')
    print('job pages: %d; changed: %s' % (len(pages), ', '.join(changed) or 'none'))


main()
