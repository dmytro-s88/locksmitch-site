"""Builds the "Makes we work on" logo block and swaps it into every page that has one.

Run from the site root after changing the BRANDS list below, then rebuild the Spanish pages:
    python3 -I tools/brands_build.py
    python3 -I tools/es_build.py
To rebuild the logo sprite (assets/brands.svg) from a Simple Icons checkout (npm pack simple-icons):
    python3 -I tools/brands_build.py --icons /path/to/package/icons
Makes with no Simple Icons logo are shown as a lettered wordmark; Mercedes is drawn here.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITE = '/assets/brands.svg?v=1'

# (name, sprite id or None for a wordmark, page slug or None)
BRANDS = [
    ('Asian', [
        ('Toyota', 'toyota', 'toyota'), ('Lexus', None, 'lexus'), ('Honda', 'honda', 'honda'), ('Acura', 'acura', None),
        ('Nissan', 'nissan', 'nissan'), ('Infiniti', 'infiniti', None), ('Mazda', 'mazda', 'mazda'), ('Subaru', 'subaru', 'subaru'),
        ('Mitsubishi', 'mitsubishi', None), ('Hyundai', 'hyundai', 'hyundai'), ('Kia', 'kia', 'kia'), ('Genesis', None, None),
    ]),
    ('American', [
        ('Ford', 'ford', 'ford'), ('Chevrolet', 'chevrolet', 'chevrolet-gmc'), ('GMC', None, 'chevrolet-gmc'), ('Cadillac', 'cadillac', None),
        ('Buick', None, None), ('Chrysler', 'chrysler', None), ('Dodge', None, 'jeep-dodge-ram'), ('Jeep', 'jeep', 'jeep-dodge-ram'),
        ('RAM', 'ram', 'jeep-dodge-ram'),
    ]),
    ('European', [
        ('BMW', 'bmw', 'bmw'), ('Mercedes', 'mercedes', 'mercedes'), ('Volkswagen', 'volkswagen', 'volkswagen-audi'), ('Audi', 'audi', 'volkswagen-audi'),
        ('Volvo', 'volvo', 'volvo'), ('Porsche', 'porsche', 'porsche'), ('Ferrari', 'ferrari', 'ferrari'), ('Maserati', 'maserati', 'maserati'),
        ('Land Rover', None, 'land-rover-jaguar'), ('Jaguar', None, 'land-rover-jaguar'), ('MINI', 'mini', None),
    ]),
]
# Drawn here: Simple Icons has no Mercedes logo
MERCEDES = ('<symbol id="mercedes" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10.6" fill="none" stroke="currentColor" stroke-width="1.6"/>'
            '<path d="M12 2.4 13.4 11.2 20.3 16.8 12 13.6 3.7 16.8 10.6 11.2Z"/></symbol>')


def tile(name, icon, slug):
    mark = (f'<svg aria-hidden="true"><use href="{SPRITE}#{icon}"/></svg>' if icon
            else f'<b class="wm" aria-hidden="true">{name.upper().replace(" ", "<br>")}</b>')
    inner = f'{mark}<span>{name}</span>'
    return f'<li><a href="/{slug}-key-replacement/">{inner}</a></li>' if slug else f'<li><div>{inner}</div></li>'


def block():
    groups = ''.join(f'\n          <section class="make-group"><h4>{g}</h4><ul class="logos">{"".join(tile(*b) for b in items)}</ul></section>'
                     for g, items in BRANDS)
    return ('<div class="brands" id="brands">\n        <h3>Makes we work on</h3>\n        <div class="makes">' + groups +
            '\n        </div>\n        <p class="makes-more">Don’t see your make? <a href="sms:+17702703333">Text us the year, make and model</a> and we’ll check.</p>\n      </div>')


def sprite(icons_dir):
    out = []
    for _, items in BRANDS:
        for _, icon, _ in items:
            if not icon or icon == 'mercedes':
                continue
            svg = open(os.path.join(icons_dir, icon + '.svg')).read()
            path = re.search(r'<path d="([^"]+)"', svg).group(1)
            out.append(f'<symbol id="{icon}" viewBox="0 0 24 24"><path d="{path}"/></symbol>')
    out.append(MERCEDES)
    with open(os.path.join(ROOT, 'assets', 'brands.svg'), 'w') as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg">\n<!-- Logos from Simple Icons (CC0), simpleicons.org; Mercedes drawn by hand. Built by tools/brands_build.py -->\n'
                + '\n'.join(out) + '\n</svg>\n')
    print('sprite:', len(out), 'logos')


def main():
    if '--icons' in sys.argv:
        sprite(sys.argv[sys.argv.index('--icons') + 1])
    new, n = block(), 0
    pat = re.compile(r'<div class="brands" id="brands">.*?\n      </div>', re.S)
    for d, _, files in os.walk(ROOT):
        if '/.git' in d or d.startswith(os.path.join(ROOT, 'es')):
            continue
        for fn in files:
            if fn != 'index.html':
                continue
            p = os.path.join(d, fn)
            s = open(p).read()
            if 'id="brands"' not in s:
                continue
            s2, k = pat.subn(lambda m: new, s, count=1)
            if not k:
                sys.exit('brands block not found in ' + p)
            if s2 != s:
                open(p, 'w').write(s2)
                n += 1
    print('pages updated:', n)


main()
