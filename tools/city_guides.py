"""Links the 24 city pages to the guides: one city-specific "Lost all your car keys in <City>?" question at the top of the
FAQ (mirrored into the FAQPage JSON-LD, plain text there) and a "Guides" list in the side column.

Rerun is safe: an existing question and list are replaced.
    python3 -I tools/city_guides.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# slug: (city name, drive minutes from Cumming, zone)
# zone 1: Cumming and Forsyth, prices as listed; 2: up to 25 miles, key jobs as listed; 3: 25 to 40 miles, key jobs +$50; 4: quoted
CITIES = {
    'cumming': ('Cumming', 0, 1), 'sugarhill': ('Sugar Hill', 20, 1),
    'alpharetta': ('Alpharetta', 20, 2), 'milton': ('Milton', 20, 2), 'johnscreek': ('Johns Creek', 25, 2),
    'buford': ('Buford', 25, 2), 'suwanee': ('Suwanee', 25, 2), 'duluth': ('Duluth', 25, 2), 'roswell': ('Roswell', 30, 2),
    'dawsonville': ('Dawsonville', 30, 2), 'gainesville': ('Gainesville', 35, 2), 'flowerybranch': ('Flowery Branch', 35, 2),
    'dunwoody': ('Dunwoody', 35, 2), 'lawrenceville': ('Lawrenceville', 40, 2), 'canton': ('Canton', 40, 2),
    'peachtreecorners': ('Peachtree Corners', 30, 3), 'sandysprings': ('Sandy Springs', 35, 3), 'norcross': ('Norcross', 35, 3),
    'doraville': ('Doraville', 40, 3), 'braselton': ('Braselton', 45, 3), 'woodstock': ('Woodstock', 50, 3), 'smyrna': ('Smyrna', 50, 3),
    'marietta': ('Marietta', 55, 4), 'kennesaw': ('Kennesaw', 60, 4),
}
GUIDES = [
    ('lost-all-car-keys', 'Lost all your car keys?'),
    ('keys-locked-in-car', 'Keys locked in the car?'),
    ('key-fob-not-working', 'Key fob not working?'),
    ('dealer-vs-locksmith-car-key', 'Dealer or locksmith?'),
]


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def answer(name, mins, zone):
    if mins == 0:
        drive = 'Mitch starts his day in Cumming, so the drive is usually minutes'
    else:
        drive = 'Mitch reaches %s in about %d minutes' % (name, mins)
    price = {
        1: 'All keys lost starts at $190 for most makes, with no trip fee in %s.' % name,
        2: 'All keys lost starts at $190 for most makes, with no trip fee for key jobs in %s.' % name,
        3: 'All keys lost starts at $190 for most makes, plus $50 for the drive to %s.' % name,
        4: 'All keys lost starts at $190 for most makes; for %s Mitch quotes the job and the drive by text first.' % name,
    }[zone]
    return ("Don't tow it to a dealer. Find the VIN, have the registration or title and a photo ID ready, and call or text us. "
            "%s and makes a new key at the car, usually within an hour on site. %s" % (drive, price))


def main():
    for slug, (name, mins, zone) in CITIES.items():
        p = os.path.join(ROOT, slug, 'index.html')
        s = open(p, encoding='utf-8').read()
        q = 'Lost all your car keys in %s?' % name
        a = answer(name, mins, zone)
        # 1) FAQ question, first in the list
        s = re.sub(r'<details data-guide-faq-city="1">.*?</details>\n\s*', '', s, flags=re.S)
        html = ('<details data-guide-faq-city="1"><summary>' + esc(q) + '</summary><p>' + esc(a) +
                ' <a href="/guides/lost-all-car-keys/">Step by step: what to do when all keys are lost</a>.</p></details>\n        ')
        m = re.search(r'<div class="faq" id="faq">\n\s*', s)
        if not m:
            raise SystemExit('no faq in ' + slug)
        s = s[:m.end()] + html + s[m.end():]
        # 2) FAQPage JSON-LD, plain text
        def fix_ld(mm):
            d = json.loads(mm.group(1))
            if d.get('@type') != 'FAQPage':
                return mm.group(0)
            ents = [e for e in d['mainEntity'] if e['name'] != q]
            d['mainEntity'] = [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}}] + ents
            return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'
        s = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_ld, s, flags=re.S)
        # 3) Guides list in the side column
        s = re.sub(r'<h3 style="margin-top:20px" data-guides="1">Guides</h3>\n\s*<ul[^>]*>.*?</ul>\n\s*', '', s, flags=re.S)
        m = re.search(r'<aside class="nearby"[^>]*>.*?</aside>', s, re.S)
        if not m:
            raise SystemExit('no aside in ' + slug)
        items = ''.join('<li><a href="/guides/%s/">%s</a></li>' % (g, esc(t)) for g, t in GUIDES)
        block = '<h3 style="margin-top:20px" data-guides="1">Guides</h3>\n        <ul style="grid-template-columns:1fr">' + items + '</ul>\n        '
        aside = m.group(0)
        anchor = '<p style="margin-top:14px"><a href="/#area"'
        new = aside.replace(anchor, block + anchor, 1) if anchor in aside else aside.replace('</aside>', block + '</aside>', 1)
        s = s[:m.start()] + new + s[m.end():]
        open(p, 'w', encoding='utf-8').write(s)
        print(slug, 'ok')


main()
