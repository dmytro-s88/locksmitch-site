"""Builds the "Makes we work on" logo block and swaps it into every page that has one.

Run from the site root after changing the BRANDS list below, then rebuild the Spanish pages:
    python3 -I tools/brands_build.py
    python3 -I tools/es_build.py
To rebuild the logo sprite (assets/brands.svg) from Simple Icons checkouts (npm pack simple-icons):
    python tools/brands_build.py --icons /path/to/package/icons --icons-old /path/to/simple-icons-11.15.0/package/icons
The sprite build needs svgelements (pip install svgelements) to crop each logo's viewBox tight, so wide logos fill the tile.
Logos come from Simple Icons (CC0); Land Rover, Jaguar, Alfa Romeo and Mercedes from 11.15.0, the last release that had them.
Buick, Dodge and the Lexus emblem are public domain / CC0 files from Wikimedia Commons in assets/makes/, shown as a CSS mask.
Makes with no logo are shown as a lettered wordmark.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITE = '/assets/brands.svg?v=3'
OLD_ICONS = {'landrover', 'jaguar', 'alfaromeo', 'mercedes'}

# (name, sprite id, 'file:<name>' for assets/brands/<name>.svg, or None for a wordmark; page slug or None)
BRANDS = [
    ('Asian', [
        ('Toyota', 'toyota', 'toyota'), ('Lexus', 'file:lexus', 'lexus'), ('Honda', 'honda', 'honda'), ('Acura', 'acura', 'honda'),
        ('Nissan', 'nissan', 'nissan'), ('Infiniti', 'infiniti', 'nissan'), ('Mazda', 'mazda', 'mazda'), ('Subaru', 'subaru', 'subaru'),
        ('Mitsubishi', 'mitsubishi', 'mitsubishi'), ('Hyundai', 'hyundai', 'hyundai'), ('Kia', 'kia', 'kia'), ('Genesis', None, 'hyundai'),
    ]),
    ('American', [
        ('Ford', 'ford', 'ford'), ('Chevrolet', 'chevrolet', 'chevrolet-gmc'), ('GMC', None, 'chevrolet-gmc'), ('Cadillac', 'cadillac', 'chevrolet-gmc'),
        ('Buick', 'file:buick', 'chevrolet-gmc'), ('Chrysler', 'chrysler', 'jeep-dodge-ram'), ('Dodge', 'file:dodge', 'jeep-dodge-ram'), ('Jeep', 'jeep', 'jeep-dodge-ram'),
        ('RAM', 'ram', 'jeep-dodge-ram'),
    ]),
    ('European', [
        ('BMW', 'bmw', 'bmw'), ('Mercedes', 'mercedes', 'mercedes'), ('Volkswagen', 'volkswagen', 'volkswagen-audi'), ('Audi', 'audi', 'volkswagen-audi'),
        ('Volvo', 'volvo', 'volvo'), ('Porsche', 'porsche', 'porsche'), ('Ferrari', 'ferrari', 'ferrari'), ('Maserati', 'maserati', 'maserati'),
        ('Land Rover', 'landrover', 'land-rover-jaguar'), ('Jaguar', 'jaguar', 'land-rover-jaguar'), ('MINI', 'mini', 'bmw'), ('Fiat', 'fiat', None), ('Alfa Romeo', 'alfaromeo', None),
    ]),
]

def tile(name, icon, slug):
    if not icon:
        mark = f'<b class="wm" aria-hidden="true">{name.upper().replace(" ", "<br>")}</b>'
    elif icon.startswith('file:'):
        mark = f'<i class="lgm" style="--m:url(/assets/makes/{icon[5:]}.svg)" aria-hidden="true"></i>'
    else:
        mark = f'<svg aria-hidden="true"><use href="{SPRITE}#{icon}"/></svg>'
    inner = f'{mark}<span>{name}</span>'
    return f'<li><a href="/{slug}-key-replacement/">{inner}</a></li>' if slug else f'<li><div>{inner}</div></li>'


def block():
    groups = ''.join(f'\n          <section class="make-group"><h4>{g}</h4><ul class="logos">{"".join(tile(*b) for b in items)}</ul></section>'
                     for g, items in BRANDS)
    return ('<div class="brands" id="brands">\n        <h3>Makes we work on</h3>\n        <div class="makes">' + groups +
            '\n        </div>\n        <p class="makes-more">Don’t see your make? <a href="sms:+17702703333">Text us the year, make and model</a> and we’ll check.</p>\n      </div>')


def sprite(icons_dir, old_dir):
    from svgelements import Path
    out = []
    for _, items in BRANDS:
        for _, icon, _ in items:
            if not icon or icon.startswith('file:'):
                continue
            svg = open(os.path.join(old_dir if icon in OLD_ICONS else icons_dir, icon + '.svg')).read()
            path = re.search(r'<path d="([^"]+)"', svg).group(1)
            x0, y0, x1, y1 = (float(v) for v in Path(path).bbox())
            out.append(f'<symbol id="{icon}" viewBox="{x0:.2f} {y0:.2f} {x1 - x0:.2f} {y1 - y0:.2f}"><path d="{path}"/></symbol>')
    with open(os.path.join(ROOT, 'assets', 'brands.svg'), 'w') as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg">\n<!-- Logos from Simple Icons (CC0), simpleicons.org. Built by tools/brands_build.py -->\n'
                + '\n'.join(out) + '\n</svg>\n')
    print('sprite:', len(out), 'logos')


def main():
    if '--icons' in sys.argv:
        sprite(sys.argv[sys.argv.index('--icons') + 1], sys.argv[sys.argv.index('--icons-old') + 1])
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
