"""Adds a "Guides" list to the side column of the service pages and every make page.

Rerun is safe: an existing list is replaced.
    python3 -I tools/related_guides.py
"""
import glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDES = {
    'lost-all-car-keys': 'Lost all your car keys?',
    'dealer-vs-locksmith-car-key': 'Dealer or locksmith?',
    'bought-car-key-online': 'Bought a key online?',
    'key-fob-not-working': 'Key fob not working?',
    'keys-locked-in-car': 'Keys locked in the car?',
    'smart-key-not-detected': '“Key not detected”?',
}
SERVICES = {
    'all-keys-lost': ['lost-all-car-keys', 'dealer-vs-locksmith-car-key', 'bought-car-key-online'],
    'spare-key': ['bought-car-key-online', 'dealer-vs-locksmith-car-key', 'key-fob-not-working'],
    'car-lockout': ['keys-locked-in-car', 'smart-key-not-detected', 'key-fob-not-working'],
    'key-programming': ['bought-car-key-online', 'smart-key-not-detected', 'key-fob-not-working'],
}
MAKE_GUIDES = ['lost-all-car-keys', 'dealer-vs-locksmith-car-key', 'key-fob-not-working']


def block(slugs):
    items = ''.join('<li><a href="/guides/%s/">%s</a></li>' % (g, GUIDES[g]) for g in slugs)
    return '<h3 style="margin-top:20px" data-guides="1">Guides</h3>\n        <ul style="grid-template-columns:1fr">' + items + '</ul>\n        '


def main():
    pages = {os.path.join(ROOT, k, 'index.html'): v for k, v in SERVICES.items()}
    for p in glob.glob(os.path.join(ROOT, '*-key-replacement', 'index.html')):
        pages[p] = MAKE_GUIDES
    n = 0
    for p, slugs in pages.items():
        s = open(p, encoding='utf-8').read()
        s = re.sub(r'<h3 style="margin-top:20px" data-guides="1">Guides</h3>\n\s*<ul[^>]*>.*?</ul>\n\s*', '', s, flags=re.S)
        m = re.search(r'<aside class="nearby">.*?</aside>', s, re.S)
        if not m:
            raise SystemExit('no aside in ' + p)
        aside = m.group(0)
        anchor = '<p style="margin-top:14px"><a href="/#area"'
        if anchor in aside:
            new = aside.replace(anchor, block(slugs) + anchor, 1)
        else:
            new = aside.replace('</aside>', block(slugs) + '</aside>', 1)
        s = s[:m.start()] + new + s[m.end():]
        open(p, 'w', encoding='utf-8').write(s)
        n += 1
    print('pages updated:', n)


main()
