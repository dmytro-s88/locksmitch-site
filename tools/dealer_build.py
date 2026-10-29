"""Builds the "Why call us instead of the dealer" comparison and puts it before "How a visit works"
on the home page, the key service pages and every make page. Rerun after editing ROWS, then rebuild the Spanish pages:
    python3 -I tools/dealer_build.py
    python3 -I tools/es_build.py
"""
import glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ['index.html', 'all-keys-lost/index.html', 'spare-key/index.html', 'key-programming/index.html', 'guides/dealer-vs-locksmith-car-key/index.html'] + sorted(
    os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, '*-key-replacement', 'index.html')))

# (row, LocksMitch, dealer); each answer is (mark, text) with mark yes / no / mid
ROWS = [
    ('We come to your car', ('yes', 'Yes'), ('no', 'You bring the car in')),
    ('No tow when all keys are lost', ('yes', 'Yes'), ('no', 'Often needs a tow')),
    ('Usually costs less', ('yes', 'No tow fee'), ('no', 'Key + programming + tow')),
    ('Often same day, 24/7 for urgent calls', ('yes', 'Yes'), ('mid', 'Usually by appointment')),
    ('Dealer-level programming equipment', ('yes', 'NASTF certified'), ('yes', 'Yes')),
    ('Keys + electrical diagnostics in one visit', ('yes', 'Yes'), ('mid', 'Varies')),
    ('Talk directly to the locksmith', ('yes', 'Yes'), ('no', 'Service desk')),
    ('Price before anyone drives out', ('yes', 'By text'), ('mid', 'Varies')),
    ('Original or aftermarket key, your choice', ('yes', 'Yes'), ('no', 'Original only')),
    ('1-year warranty on keys we supply', ('yes', 'Yes'), ('mid', 'Varies')),
]
MARK = {
    'yes': '<svg viewBox="0 0 24 24"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>',
    'no': '<svg viewBox="0 0 24 24"><path d="M7 7l10 10M17 7 7 17"/></svg>',
    'mid': '<svg viewBox="0 0 24 24"><path d="M5 13c2.5-3 4.5-3 7 0s4.5 3 7 0"/></svg>',
}


def cell(ans, cls):
    mark, text = ans
    return f'<td class="{cls}"><span class="mk mk-{mark}">{MARK[mark]}{text}</span></td>'


def block():
    rows = ''.join(f'\n            <tr><th scope="row">{r}</th>{cell(us, "us")}{cell(them, "them")}</tr>' for r, us, them in ROWS)
    return ('<section class="vs-sec" id="dealer">\n    <div class="wrap">\n      <div class="sec-head">\n'
            '        <h2>Why call us instead of the dealer</h2>\n'
            '        <p class="lede">The same dealer-level programming, done in your driveway instead of their service bay.</p>\n'
            '      </div>\n      <div class="vs-wrap">\n        <table class="vs">\n'
            '          <thead><tr><td></td><th scope="col" class="us">LocksMitch</th><th scope="col" class="them">Dealership</th></tr></thead>\n'
            '          <tbody>' + rows + '\n          </tbody>\n        </table>\n      </div>\n    </div>\n  </section>\n\n  ')


def main():
    new, n = block(), 0
    for rel in PAGES:
        p = os.path.join(ROOT, rel)
        s = open(p).read()
        s2 = re.sub(r'<section class="vs-sec" id="dealer">.*?</section>\n\n  ', '', s, flags=re.S)
        anchor = '<section class="steps-sec" id="how">'
        if anchor not in s2:
            raise SystemExit('no "How a visit works" section in ' + rel)
        s2 = s2.replace(anchor, new + anchor, 1)
        if s2 != s:
            open(p, 'w').write(s2)
            n += 1
    print('pages updated:', n, 'of', len(PAGES))


main()
