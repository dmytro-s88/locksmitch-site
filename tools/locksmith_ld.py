"""One Locksmith node in the JSON-LD of every page that has it, and the page's own facts in a Service node.

The business is described once: the Locksmith node of the home page (index.html), @id https://locksmitch.com/#locksmith,
plus the postal address below (city, state and ZIP only: a mobile service-area business, the street is never published).
Edit the business facts (services, prices, hours, payment, profiles) in index.html, then run from the site root:
    python3 -I tools/locksmith_ld.py
Rerun is safe: nothing changes when the home node did not change.

What it writes:
  - index.html: adds "address" to the Locksmith node;
  - every other page with a top-level Locksmith node (cities, counties, Lake Lanier): that node becomes a copy of the home
    one (same url, description, areaServed, offers); what the page said about itself (its url, description, areaServed)
    moves once into a Service node with @id <page url>#service and provider {"@id": ".../#locksmith"}.
"aggregateRating" and "review" belong to tools/reviews_build.py: they are kept as found on each page and never copied
from the home page. The Spanish pages and the Service pages (provider with a short Locksmith reference) are not touched.
"""
import glob, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIZ_ID = 'https://locksmitch.com/#locksmith'
ADDRESS = {'@type': 'PostalAddress', 'addressLocality': 'Cumming', 'addressRegion': 'GA', 'postalCode': '30041', 'addressCountry': 'US'}
REVIEW_KEYS = ('aggregateRating', 'review')   # owned by tools/reviews_build.py
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def dump(node):
    return '<script type="application/ld+json">' + json.dumps(node, ensure_ascii=False) + '</script>'


def with_address(node):
    """The node with "address" right after "email" (or at its old place when it is already there)."""
    out = {}
    for k, v in node.items():
        if k == 'address':
            continue
        out[k] = v
        if k == 'email':
            out['address'] = dict(ADDRESS)
    if 'address' not in out:
        out['address'] = dict(ADDRESS)
    return out


def home_node():
    s = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    for m in LD_RE.finditer(s):
        d = json.loads(m.group(1))
        if d.get('@type') == 'Locksmith' and d.get('@id') == BIZ_ID:
            return with_address({k: v for k, v in d.items() if k not in REVIEW_KEYS})
    raise SystemExit('no Locksmith node in index.html')


def h1_name(s, rel):
    m = re.search(r'<h1>(.*?)(?:<span class="l2">|</h1>)', s, re.S)
    if not m:
        raise SystemExit('no h1 in ' + rel)
    return html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()


def fix_page(rel, base):
    path = os.path.join(ROOT, rel)
    old = open(path, encoding='utf-8').read()
    blocks = [(m, json.loads(m.group(1))) for m in LD_RE.finditer(old)]
    biz = [(m, d) for m, d in blocks if isinstance(d, dict) and d.get('@type') == 'Locksmith' and d.get('@id') == BIZ_ID]
    if not biz:
        return False
    m, d = biz[0]
    node = dict(base)
    for k in REVIEW_KEYS:
        if k in d:
            node[k] = d[k]
    new = dump(node)
    if rel != 'index.html':
        canon = re.search(r'<link rel="canonical" href="([^"]+)"', old)
        if not canon:
            raise SystemExit('no canonical in ' + rel)
        sid = canon.group(1) + '#service'
        if not any(isinstance(x, dict) and x.get('@id') == sid for _, x in blocks):
            name = h1_name(old, rel)
            service = {'@context': 'https://schema.org', '@type': 'Service', '@id': sid, 'name': name,
                       'serviceType': 'Mobile car locksmith', 'description': d['description'], 'url': canon.group(1),
                       'areaServed': d['areaServed'], 'provider': {'@id': BIZ_ID}}
            new += '\n' + dump(service)
    s = old[:m.start()] + new + old[m.end():]
    if s != old:
        open(path, 'w', encoding='utf-8').write(s)
    return s != old


def main():
    base = home_node()
    pages = sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True))
    pages = [p for p in pages if not p.startswith('es' + os.sep)]
    changed = [p for p in pages if fix_page(p, base)]
    print('locksmith node: pages changed: %d' % len(changed))


main()
