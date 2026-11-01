"""Builds the county pages (/forsyth-county/, /gwinnett-county/, /north-fulton/) from the Alpharetta page as a shell,
links them from the home page and the city pages, and adds city links to the make pages.

Drive times and prices in the city lists are read from each city page, so they can't drift from it.
Rerun is safe: pages are rebuilt, existing links are replaced.
    python3 -I tools/county_pages.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEL = '<a href="tel:7702703333">(770) 270-3333</a>'

COUNTIES = {
    'forsyth-county': {
        'name': 'Forsyth County',
        'area': 'Forsyth County, GA',
        'title': 'Car Locksmith in Forsyth County, GA | LocksMitch',
        'desc': 'Car locksmith based in Forsyth County, GA. Lockouts flat $75, spare and lost keys made at your car. Answered 24/7. Call (770) 270-3333.',
        'h1': 'Mobile car locksmith in Forsyth County, GA',
        'lede': 'Lost your keys? Need a spare? Locked out? LocksMitch is based right here in Forsyth County, so Cumming, Big Creek or Coal Mountain is a short drive for us. We cut and program the key at your car, with no tow and no dealer wait.',
        'cities': ['cumming'],
        'nearby': ['cumming', 'suwanee', 'johnscreek', 'alpharetta', 'sugarhill', 'dawsonville', 'buford', 'gainesville'],
        'nearby_h': 'Cities nearby',
        'h2': 'Vehicle lockouts and car keys across Forsyth County',
        'intro': 'This is home ground for us, and the part of our area we reach fastest. A daytime lockout in the county is a flat $75, and key jobs are at the listed price with no trip fee.',
        'spots_h': 'We come to you anywhere in Forsyth County, including:',
        'spots': ['Downtown Cumming', 'Vickery Village', 'The Collection at Forsyth', 'Halcyon', 'Northside Hospital Forsyth', '<a href="/lake-lanier/">Lake Lanier</a>', 'Big Creek', 'Coal Mountain', 'Sawnee Mountain', 'GA-400 corridor'],
        'facts_h': 'What it costs in Forsyth County',
        'more_h': 'Where we come in Forsyth County',
        'more': [
            'South Forsyth runs from the Johns Creek line up through Big Creek: Halcyon, Vickery Village and the shops along Peachtree Parkway (GA-141). A lot of homes here have a Suwanee or Alpharetta mailing address. That’s fine, just send us the address and you get the exact price before we drive out.',
            'Around Cumming we cover the GA-400 corridor, The Collection at Forsyth, Northside Hospital Forsyth and the subdivisions off Post Road, Bethelview Road and Pilgrim Mill Road. Further north and west, on the long roads toward Coal Mountain, Matt and Silver City, a gate code or a landmark in your text saves a few minutes.',
            'On the east side of the county the lake takes over: Bald Ridge, Mary Alice Park and the ramps off Buford Dam Road. If your key is at the bottom of the lake or you’re locked out at a ramp, see our <a href="/lake-lanier/">Lake Lanier page</a>. We make the new key in the lot, so the car doesn’t need a tow.',
        ],
        'faq': [
            ('How much is a car lockout in Forsyth County?', 'A daytime lockout is a flat $75 and a plain key without a chip is $75. Key jobs are at the listed price with no trip fee. Nights from 9 pm to 7 am add $50. You get the price before we drive out.'),
            ('My address says Suwanee or Alpharetta, but I’m in Forsyth County. What do I pay?', 'Send us the address by call or text. We go by where the car actually is, and you get the exact price before we drive out.'),
            ('How fast can you get to me in Forsyth County?', 'We’re based in the county, so this is our shortest drive. Mitch texts you the arrival time when he confirms the job.'),
            ('Can you make a new key if I lost mine at Lake Lanier?', 'Yes. We make the key at the marina or ramp lot, so the car doesn’t need a tow to a dealer. Tell us which park or ramp you’re at, or text a pin from your map app.'),
        ],
    },
    'gwinnett-county': {
        'name': 'Gwinnett County',
        'area': 'Gwinnett County, GA',
        'title': 'Car Locksmith in Gwinnett County, GA | LocksMitch',
        'desc': 'Vehicle lockout service and car keys made at your car across Gwinnett County, GA: Buford, Suwanee, Duluth, Lawrenceville. Call (770) 270-3333.',
        'h1': 'Mobile car locksmith in Gwinnett County, GA',
        'lede': 'Locked out at the Mall of Georgia? Lost your only key in Duluth? We come to you across Gwinnett County from our base next door in Forsyth County, and we cut and program the key where you’re parked. No tow and no dealer wait.',
        'cities': ['sugarhill', 'buford', 'suwanee', 'duluth', 'lawrenceville', 'peachtreecorners', 'norcross'],
        'nearby': ['sugarhill', 'buford', 'suwanee', 'duluth', 'lawrenceville', 'peachtreecorners', 'norcross', 'braselton'],
        'nearby_h': 'Gwinnett cities we serve',
        'h2': 'Vehicle lockout service in Gwinnett County',
        'intro': 'The price depends on how far the city is from our base. It’s quoted before we drive out and doesn’t change at your car.',
        'spots_h': 'We come to you anywhere in our Gwinnett area, including:',
        'spots': ['Mall of Georgia', 'Suwanee Town Center', 'Gas South District', 'The Bowl at Sugar Hill', 'The Forum on Peachtree Parkway', 'Georgia Gwinnett College', 'Northside Hospital Gwinnett', 'Coolray Field', 'I-85 corridor'],
        'facts_h': 'Drive time and price by city',
        'more_h': 'Where we come in Gwinnett County',
        'more': [
            'North Gwinnett is the closest part for us. Sugar Hill is right next to our base, and Buford and Suwanee are about 25 minutes from Cumming. We come to the lots at the Mall of Georgia, Suwanee Town Center on event nights and the homes along Peachtree Industrial Boulevard.',
            'Along I-85 we cover Duluth, from the Gas South District to the apartments off Pleasant Hill Road, then the tech parks of Peachtree Corners and Jimmy Carter Boulevard in Norcross. Those last two are a longer drive for us, so a lockout is $125 and key jobs add $50.',
            'Lawrenceville, the county seat, is about 40 minutes from Cumming, so we confirm the price and timing by text before heading down. For Lilburn, Snellville, Dacula or Grayson, call or text the address and we tell you whether we can reach you and what it costs before anyone drives out. Prefer Spanish? <a href="/es/">Text us in Spanish</a> and you get the price and the confirmation in Spanish.',
        ],
        'faq': [
            ('How much is a vehicle lockout in Gwinnett County?', 'In the daytime it’s a flat $75 in Sugar Hill, $100 in Buford, Suwanee, Duluth and Lawrenceville, and $125 in Peachtree Corners and Norcross. Nights from 9 pm to 7 am add $50. You get the price before we drive out.'),
            ('Do you cover all of Gwinnett County?', 'We cover the cities listed on this page. For Lilburn, Snellville, Dacula or Grayson, call or text the address and we tell you whether we can reach you and what it costs.'),
            ('Can you come to a parking lot at the mall or an office park?', 'Yes. Tell us the lot and the car and we come straight to it. Most key jobs take about an hour once we arrive.'),
            ('Can I text you in Spanish?', 'Yes. Text us in Spanish at (770) 270-3333 and you get the price and the confirmation in Spanish.'),
        ],
    },
    'north-fulton': {
        'name': 'North Fulton',
        'area': 'North Fulton, GA',
        'title': 'Car Locksmith in North Fulton, GA | LocksMitch',
        'desc': 'Mobile car locksmith for North Fulton: Alpharetta, Milton, Roswell, Johns Creek and Sandy Springs. Keys made at your car. Call (770) 270-3333.',
        'h1': 'Mobile car locksmith in North Fulton, GA',
        'lede': 'Lost your keys? Need a spare? Locked out? We come down GA-400 to Alpharetta, Milton, Roswell, Johns Creek and Sandy Springs, and we cut and program the key at your car. No tow and no dealer wait.',
        'cities': ['alpharetta', 'milton', 'johnscreek', 'roswell', 'sandysprings'],
        'nearby': ['alpharetta', 'milton', 'johnscreek', 'roswell', 'sandysprings', 'cumming', 'dunwoody', 'peachtreecorners'],
        'nearby_h': 'North Fulton and nearby',
        'h2': 'Car keys and lockouts across North Fulton',
        'intro': 'North Fulton is the easy part of our area: straight down GA-400 from our base in Forsyth County. There’s no trip fee for key jobs in Alpharetta, Milton, Johns Creek or Roswell.',
        'spots_h': 'We come to you anywhere in North Fulton, including:',
        'spots': ['Avalon', 'North Point Mall', 'Windward Parkway', 'Crabapple', 'Canton Street', 'Emory Johns Creek Hospital', 'Technology Park', 'City Springs', 'Perimeter Center', 'GA-400 corridor'],
        'facts_h': 'Drive time and price by city',
        'more_h': 'Where we come in North Fulton',
        'more': [
            'Alpharetta and Milton are closest, about 20 minutes from Cumming. We drive into the parking decks at Avalon and the lots at North Point Mall, the office parks along Windward Parkway, and the long driveways off Birmingham Highway in Milton. Tell us the level and the row, or send a gate code or a landmark.',
            'Johns Creek is mostly driveways: the subdivisions off Medlock Bridge and State Bridge, often with two or three cars, which is where a spare key makes the most sense. We also come to Technology Park and Emory Johns Creek Hospital. In Roswell we cover Canton Street, the Roswell Mill area, Holcomb Bridge Road and the lots at the Chattahoochee river parks.',
            'Sandy Springs is near the edge of our area, about 35 minutes from Cumming: City Springs, Perimeter Center, Northside Hospital Atlanta and the homes off Roswell Road. A lockout there is $125 and key jobs add $50 for the drive. Elsewhere in North Fulton a daytime lockout is a flat $100.',
        ],
        'faq': [
            ('How much is a car lockout in North Fulton?', 'In the daytime it’s a flat $100 in Alpharetta, Milton, Johns Creek and Roswell, and $125 in Sandy Springs. Nights from 9 pm to 7 am add $50. You get the price before we drive out.'),
            ('Is there a trip fee in North Fulton?', 'Not for key jobs in Alpharetta, Milton, Johns Creek or Roswell: they’re at the listed price. Sandy Springs key jobs add $50 for the drive. Every price includes coming to you.'),
            ('Can you get into a parking deck at Avalon or Perimeter Center?', 'Yes. We drive in like any visitor. Text us the level, the row and the car, and we come straight to it.'),
            ('Can you make spare keys for several family cars in one visit?', 'Yes. List the cars when you text us and we bring blanks for each one, so nobody has to drive to a dealer and wait.'),
        ],
    },
}

CITY_NAMES = {'cumming': 'Cumming', 'sugarhill': 'Sugar Hill', 'buford': 'Buford', 'suwanee': 'Suwanee', 'duluth': 'Duluth', 'lawrenceville': 'Lawrenceville',
              'peachtreecorners': 'Peachtree Corners', 'norcross': 'Norcross', 'braselton': 'Braselton', 'alpharetta': 'Alpharetta', 'milton': 'Milton',
              'johnscreek': 'Johns Creek', 'roswell': 'Roswell', 'sandysprings': 'Sandy Springs', 'dawsonville': 'Dawsonville', 'gainesville': 'Gainesville',
              'dunwoody': 'Dunwoody'}

# Make pages: which cities to name, rotated so the pages don't all carry the same list
MAKE_CITIES = ['cumming', 'alpharetta', 'johnscreek', 'roswell', 'suwanee', 'buford', 'milton', 'duluth', 'sugarhill', 'gainesville']


def read(*path):
    return open(os.path.join(ROOT, *path), encoding='utf-8').read()


def write(text, *path):
    os.makedirs(os.path.dirname(os.path.join(ROOT, *path)), exist_ok=True)
    open(os.path.join(ROOT, *path), 'w', encoding='utf-8').write(text)


def plain(t):
    return re.sub(r'<[^>]+>', '', t)


def city_line(slug):
    """One list row built from the facts on the city page itself."""
    facts = plain(re.search(r'id="local-facts".*?</ul></div>', read(slug, 'index.html'), re.S).group(0))
    lockout = re.search(r'Car lockout: flat (\$\d+)', facts).group(1)
    keys = re.search(r'Key jobs: ([^.]+)', facts).group(1).strip()
    keys = 'key jobs +$50 for the drive' if '+$50' in keys else 'key jobs at the listed price'
    m = re.search(r'about (\d+) minutes', facts)
    drive = 'about ' + m.group(1) + ' minutes from Cumming' if m else 'our home base'
    return '<li><a href="/' + slug + '/"><b>' + CITY_NAMES[slug] + '</b></a>: ' + drive + ', lockout ' + lockout + ', ' + keys + '.</li>'


def local_section(c):
    rows = ''.join(city_line(s) for s in c['cities'])
    if c['name'] == 'Forsyth County':
        rows += '<li><b>The rest of the county:</b> lockout $75, key jobs at the listed price.</li>'
    rows += '<li><b>Nights</b>, 9 pm to 7 am: +$50.</li>'
    near = ''.join('<li><a href="/' + s + '/">' + CITY_NAMES[s] + '</a></li>' for s in c['nearby'])
    return ('<section class="local" id="local">\n    <div class="wrap local-grid">\n      <div>\n'
            '        <h2>' + c['h2'] + '</h2>\n'
            '        <p class="lede">' + c['intro'] + '</p><p class="lede">Locked out right now? Call ' + TEL + ' and we’ll head your way.</p>\n'
            '        <p class="spots-h" style="margin-top:22px;font-weight:600">' + c['spots_h'] + '</p>\n'
            '        <ul class="spots">' + ''.join('<li>' + s + '</li>' for s in c['spots']) + '</ul>\n'
            '        <div id="local-facts" class="local-facts"><h3 class="sub">' + c['facts_h'] + '</h3><ul class="price-list">' + rows + '</ul><p>Key job prices are on the <a href="/pricing/">price list</a>.</p></div>\n'
            '        <div class="local-more"><h3 class="sub">' + c['more_h'] + '</h3>' + ''.join('<p>' + p + '</p>' for p in c['more']) + '</div>\n'
            '      </div>\n'
            '      <aside class="nearby" aria-labelledby="nearby-h">\n'
            '        <h3 id="nearby-h">' + c['nearby_h'] + '</h3>\n'
            '        <ul>' + near + '</ul>\n'
            '        <p style="margin-top:14px"><a href="/#area" style="padding:0;color:var(--muted);font-weight:500">All 24 cities →</a></p>\n'
            '      </aside>\n    </div>\n  </section>')


def build(slug, c):
    s = read('alpharetta', 'index.html')
    url = 'https://locksmitch.com/' + slug + '/'
    s = s.replace('<html lang="en" data-city="Alpharetta">', '<html lang="en" data-page="' + c['name'] + '">')
    s = re.sub(r'<title>.*?</title>', '<title>' + c['title'] + '</title>', s)
    s = re.sub(r'<meta name="description" content=".*?">', '<meta name="description" content="' + c['desc'] + '">', s)
    s = re.sub(r'<meta property="og:title" content=".*?">', '<meta property="og:title" content="' + c['title'] + '">', s)
    s = re.sub(r'<meta property="og:description" content=".*?">', '<meta property="og:description" content="' + c['desc'] + '">', s)
    s = s.replace('https://locksmitch.com/alpharetta/"', url + '"')

    def fix_ld(m):
        d = json.loads(m.group(1))
        t = d.get('@type')
        if t == 'Locksmith':
            d['description'] = c['desc']
            d['areaServed'] = [{'@type': 'AdministrativeArea', 'name': c['area']}] + [{'@type': 'City', 'name': CITY_NAMES[x] + ', GA'} for x in c['cities']]
        elif t == 'BreadcrumbList':
            d['itemListElement'][1]['name'] = c['area']
        elif t == 'FAQPage':
            d['mainEntity'] = [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in c['faq']]
        return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'
    s = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_ld, s, flags=re.S)

    s = s.replace('› Alpharetta, GA</nav>', '› ' + c['area'] + '</nav>')
    s = re.sub(r'<h1>.*?<span class="l2">', '<h1>' + c['h1'] + '<span class="l2">', s, flags=re.S)
    s = re.sub(r'(<nav class="crumbs".*?</h1>\s*<p class="lede">).*?</p>', lambda m: m.group(1) + c['lede'] + '</p>', s, count=1, flags=re.S)
    s = s.replace('Locked out in the Alpharetta area right now?', 'Locked out in ' + c['name'] + ' right now?')
    s = re.sub(r'<section class="local" id="local">.*?</section>', lambda m: local_section(c), s, count=1, flags=re.S)

    # FAQ: the county questions replace the ones that name Alpharetta, the general ones stay
    faq_html = ''.join('<details data-local="1"><summary>' + q + '</summary><p>' + a + '</p></details>\n        ' for q, a in c['faq'])
    s = re.sub(r'<details(?: open)?(?: data-local="1")?><summary>[^<]*Alpharetta.*?</details>\n\s*', '', s, flags=re.S)
    s = re.sub(r'<details data-local="1">.*?</details>\n\s*', '', s, flags=re.S)
    s = s.replace('<h2 class="col-h">Common questions</h2>\n        ', '<h2 class="col-h">Common questions</h2>\n        ' + faq_html, 1)

    body = s[s.find('</head>'):]
    body = re.sub(r'<(footer|aside class="nearby").*?</(footer|aside)>', '', body, flags=re.S)
    if 'Alpharetta' in body and c['name'] != 'North Fulton':
        left = [x for x in re.findall(r'.{30}Alpharetta.{20}', plain(body)) if 'Suwanee or Alpharetta' not in x]
        if left:
            raise SystemExit('leftover Alpharetta in ' + slug + ': ' + str(left))
    if len(c['title']) > 60 or len(c['desc']) > 155:
        raise SystemExit('title or description too long in ' + slug + ': ' + str((len(c['title']), len(c['desc']))))
    if '—' in s[s.find('<body'):] or '–' in s[s.find('<body'):]:
        raise SystemExit('long dash in ' + slug)
    write(s, slug, 'index.html')
    print(slug, 'ok')


def link_cities():
    """City pages point up to their county, in the side list."""
    for slug, c in COUNTIES.items():
        for city in c['cities']:
            s = read(city, 'index.html')
            s = re.sub(r'<p class="county-link".*?</p>\n\s*', '', s, flags=re.S)
            line = '<p class="county-link" style="margin-top:14px"><a href="/' + slug + '/" style="padding:0;color:var(--muted);font-weight:500">All of ' + c['name'] + ' →</a></p>\n        '
            i = s.index('<p style="margin-top:14px"><a href="/#area"')
            write(s[:i] + line + s[i:], city, 'index.html')


def link_home():
    s = read('index.html')
    s = re.sub(r' By county: <a href="/forsyth-county/">.*?</a>\.', '', s)
    note = ' By county: <a href="/forsyth-county/">Forsyth</a>, <a href="/gwinnett-county/">Gwinnett</a> and <a href="/north-fulton/">North Fulton</a>.'
    s = s.replace('<a href="/lake-lanier/">Lake Lanier page</a>.', '<a href="/lake-lanier/">Lake Lanier page</a>.' + note, 1)
    write(s, 'index.html')


def link_makes():
    """Make pages had no links to cities outside the footer."""
    dirs = sorted(d for d in os.listdir(ROOT) if d.endswith('-key-replacement'))
    for n, d in enumerate(dirs):
        s = read(d, 'index.html')
        s = re.sub(r'\s*<p class="make-cities".*?</p>', '', s, flags=re.S)
        make = re.search(r'<nav class="crumbs".*?› ([^<]+)</nav>', s, re.S).group(1).split('›')[-1].strip()
        picks = [MAKE_CITIES[(n + i) % len(MAKE_CITIES)] for i in range(6)]
        links = ', '.join('<a href="/' + x + '/">' + CITY_NAMES[x] + '</a>' for x in picks[:-1]) + ' and <a href="/' + picks[-1] + '/">' + CITY_NAMES[picks[-1]] + '</a>'
        line = ('\n        <p class="make-cities" style="margin:0 0 12px;color:var(--muted);max-width:70ch">We come to you for ' + make + ' keys in ' + links +
                ', and across <a href="/forsyth-county/">Forsyth County</a>, <a href="/gwinnett-county/">Gwinnett County</a> and <a href="/north-fulton/">North Fulton</a>.</p>')
        m = re.search(r'<div class="local-more">.*?</div>(?=\n)', s, re.S)
        write(s[:m.end()] + line + s[m.end():], d, 'index.html')
        print(d, '->', make)


def extras():
    sm = read('sitemap.xml')
    for slug in COUNTIES:
        if '/' + slug + '/<' not in sm:
            sm = sm.replace('  <url><loc>https://locksmitch.com/lake-lanier/', '  <url><loc>https://locksmitch.com/' + slug + '/</loc><lastmod>2026-11-01</lastmod><changefreq>weekly</changefreq></url>\n  <url><loc>https://locksmitch.com/lake-lanier/', 1)
    write(sm, 'sitemap.xml')
    ll = read('llms.txt')
    if '/forsyth-county/' not in ll:
        ll = ll.replace('- [Cumming, GA](https://locksmitch.com/cumming/)\n', '- [Cumming, GA](https://locksmitch.com/cumming/)\n' + ''.join('- [' + c['area'] + '](https://locksmitch.com/' + slug + '/)\n' for slug, c in COUNTIES.items()), 1)
    write(ll, 'llms.txt')


for slug, c in COUNTIES.items():
    build(slug, c)
link_cities()
link_home()
link_makes()
extras()
