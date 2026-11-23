"""Service and info pages built on the guide template (like tools/job_pages.py):
/push-to-start-smart-key/, /key-fob-replacement/, /broken-key-extraction/, /erase-lost-key/,
/about/, /reviews/, /faq/, /contact/.

Run from the site root (rerun is safe):
    python3 -I tools/extra_pages.py
then tools/sitemap_lastmod.py.

Template: guides/keys-locked-in-car/index.html (header, estimate form, "How a visit works", footer). Only the head, the
hero text and the article/aside are replaced. Prices must match /pricing/. Reviews come from tools/reviews.json.
Rules: short hyphens only, "insured" / "registered", never "licensed"; no review count until 10 reviews.
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, 'guides', 'keys-locked-in-car', 'index.html')
SITE = 'https://locksmitch.com'
SVC = {'all-keys-lost': ('akl', 's1'), 'spare-key': ('spare', 's2'), 'car-lockout': ('lockout', 's3'), 'key-programming': ('program', 's4')}
STYLE = ('<style>.guide-body .contact-list{list-style:none;padding:0;margin:0 0 26px;display:grid;gap:10px}'
         '.guide-body .contact-list li{margin:0;padding:12px 16px;border:1px solid var(--line);border-radius:12px}'
         '.contact-list b{display:block;font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;font-weight:600}'
         '.guide-body .review-list{list-style:none;padding:0;margin:0 0 26px;display:grid;gap:14px}'
         '.guide-body .review-list li{margin:0;padding:16px 18px;border:1px solid var(--line);border-radius:14px}'
         '.review-list .stars{color:#f5b301;letter-spacing:2px}.review-list .who{margin-top:8px;color:var(--muted);font-size:15px}'
         '.guide-body .price-rows{list-style:none;padding:0;margin:0 0 26px;display:grid;gap:8px}'
         '.guide-body .price-rows li{margin:0;display:flex;justify-content:space-between;gap:16px;padding:10px 14px;border:1px solid var(--line);border-radius:10px}'
         '.price-rows b{white-space:nowrap}</style>')

HOURS = ('Lockouts and all keys lost: 24/7, including nights, Sundays and holidays. Spare keys, programming and other jobs: '
         'Monday to Saturday. From 9 pm to 7 am there is a $50 night charge.')
CALL = '<a href="tel:7702703333">(770) 270-3333</a>'


def sub1(pat, repl, s, flags=0):
    return re.sub(pat, lambda m: repl, s, count=1, flags=flags)


def esc(t):
    return html.escape(t, quote=True)


def plain(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', t))).strip()


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'


def set_head(s, title, desc, url, page_name, og_type, lds):
    s = sub1(r'<html lang="en" data-page="[^"]*">', '<html lang="en" data-page="%s">' % esc(page_name), s)
    s = sub1(r'<title>.*?</title>', '<title>%s</title>' % esc(title), s)
    s = sub1(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % esc(desc), s)
    s = sub1(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">' % url, s)
    s = sub1(r'<meta property="og:type" content="[^"]*">', '<meta property="og:type" content="%s">' % og_type, s)
    s = sub1(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s">' % url, s)
    s = sub1(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % esc(title), s)
    s = sub1(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % esc(desc), s)
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


def faq_html(faq):
    return ('<h2 data-guide-faq="1">Common questions</h2>\n<div class="faq guide-faq">%s</div>\n' %
            ''.join('<details><summary>%s</summary><p>%s</p></details>' % (esc(q), a) for q, a in faq))


def faq_ld(faq):
    return ld({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': plain(a)}} for q, a in faq]})


def crumbs_ld(name, url):
    return ld({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'LocksMitch', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': name, 'item': url}]})


def prices(rows):
    return '<ul class="price-rows">%s</ul>\n' % ''.join('<li><span>%s</span><b>%s</b></li>' % (a, b) for a, b in rows)


def jobs_links(slugs):
    pages = {p['slug']: p for p in json.load(open(os.path.join(ROOT, 'tools', 'job_pages.json'), encoding='utf-8'))['pages']}
    return '<ul>%s</ul>\n' % ''.join('<li><a href="/jobs/%s/">%s</a></li>' % (s, esc(pages[s]['title'])) for s in slugs if s in pages)


SERVICES_ASIDE = ('<h3%s>Services</h3><ul style="grid-template-columns:1fr"><li><a href="/all-keys-lost/">All keys lost</a></li>'
                  '<li><a href="/spare-key/">Spare key</a></li><li><a href="/push-to-start-smart-key/">Push-to-start smart key</a></li>'
                  '<li><a href="/key-fob-replacement/">Key fob replacement</a></li><li><a href="/car-lockout/">Car lockout</a></li>'
                  '<li><a href="/key-programming/">Key programming</a></li><li><a href="/broken-key-extraction/">Broken key extraction</a></li>'
                  '<li><a href="/erase-lost-key/">Erase a lost key</a></li><li><a href="/pricing/">Prices</a></li></ul>')
ABOUT_ASIDE = ('<h3 style="margin-top:20px">About LocksMitch</h3><ul style="grid-template-columns:1fr"><li><a href="/about/">About Mitch</a></li>'
               '<li><a href="/reviews/">Reviews</a></li><li><a href="/faq/">Questions</a></li><li><a href="/contact/">Contact</a></li>'
               '<li><a href="/jobs/">Recent jobs</a></li></ul>')


def aside(extra=''):
    return '<aside class="nearby guide-side">%s%s%s</aside>' % (extra, SERVICES_ASIDE % (' style="margin-top:20px"' if extra else ''), ABOUT_ASIDE)


def service_ld(name, desc, url, min_price):
    return ld({'@context': 'https://schema.org', '@type': 'Service', 'name': name, 'serviceType': name, 'description': desc, 'url': url,
               'provider': {'@id': SITE + '/#locksmith'}, 'areaServed': {'@type': 'AdministrativeArea', 'name': 'North Atlanta, GA'},
               'offers': {'@type': 'Offer', 'priceCurrency': 'USD', 'priceSpecification': {
                   '@type': 'PriceSpecification', 'minPrice': min_price, 'priceCurrency': 'USD'}}})


# ---------------------------------------------------------------- pages

PAGES = []

PAGES.append(dict(
    slug='push-to-start-smart-key', svc='spare-key', min_price=180,
    title='Push-to-Start Smart Key Replacement in Cumming, GA',
    h1='Push-to-start smart key in Cumming, GA', l2='Spare or replacement proximity key, programmed at your car.',
    lede='Need a second smart key, or lost the only one? I bring the key and the programmer to your car anywhere in North Atlanta. '
         'No tow, no dealer appointment, and you get the price before I drive out.',
    desc='Push-to-start smart key made and programmed at your car in Cumming and North Atlanta. Spare from $180, all keys lost from $190.',
    article=(
        '<h2>Quick answer</h2>\n<p>A push-to-start (proximity) smart key can be made and programmed at your car, in your driveway or a parking lot. '
        'A spare smart key starts <strong>from $180</strong> (2020 and newer <strong>from $200</strong>). If every key is lost it is an '
        '<a href="/all-keys-lost/">all keys lost</a> job, <strong>from $190</strong>. Bought a smart key yourself? Programming only is <strong>$129</strong>.</p>\n'
        '<h2>What I need from you</h2>\n<ul><li>Year, make and model, or the VIN.</li><li>Whether you still have one working key.</li>'
        '<li>Where the car is.</li></ul>\n<p>Text it to ' + CALL + ' and I text back the price.</p>\n'
        '<h2>How the job goes</h2>\n<ol><li>I pick the right key for your car. On Toyota and Lexus that means matching the board number inside the key, '
        'on Hyundai and Kia the part number for your VIN. A key that only looks the same often will not program.</li>'
        '<li>I cut the emergency blade inside the fob to your locks.</li>'
        '<li>I program the key to the car through the diagnostic port with dealer-level equipment.</li>'
        '<li>We test push-to-start, lock, unlock, trunk and any other buttons before I leave.</li></ol>\n'
        '<h2>Prices</h2>\n' + prices([('Spare smart key, while one key works', 'from $180'), ('Spare smart key, 2020 and newer', 'from $200'),
                                     ('All smart keys lost', 'from $190'), ('Program a smart key you bought', '$129'),
                                     ('Second key for the same car, same visit', '50% off')]) +
        '<p>The exact price depends on the make, year and key. European makes are quoted by model. See all <a href="/pricing/">prices</a>.</p>\n'
        '<h2>Smart key jobs I have done</h2>\n' +
        jobs_links(['2021-lexus-rx-smart-key-programming-cumming', '2024-chevrolet-silverado-2500hd-all-keys-lost-cumming',
                    '2026-hyundai-tucson-spare-smart-key-gainesville', '2025-hyundai-santa-fe-all-keys-lost-cumming',
                    '2017-toyota-highlander-spare-smart-key-cumming', '2019-honda-accord-spare-smart-key-cumming',
                    '2021-kia-forte-spare-smart-key-cumming', '2008-infiniti-g35-spare-smart-key-sugar-hill']) +
        '<h2>When to call</h2>\n<p>' + HOURS + ' If you have lost every key, that counts as an emergency and I come any day.</p>\n'),
    faq=[('How much is a push-to-start key replacement?', 'A spare smart key starts from $180, 2020 and newer from $200. All keys lost starts from $190. '
          'Programming a smart key you already bought is $129. A second key for the same car in the same visit is 50% off.'),
         ('Can you program a smart key without the old one?', 'Yes. That is the all keys lost job: the key is made and programmed from the car itself, at the car.'),
         ('Can I buy the key online and have you program it?', 'Yes, programming only is $129. The key has to match your car exactly. Send me the part number or a photo before you order, and I will tell you if it will work.'),
         ('Do you do push-to-start keys on Sunday?', 'On Sunday I take only lockouts and all keys lost. A spare smart key is done Monday to Saturday.')],
    jobs=True))

PAGES.append(dict(
    slug='key-fob-replacement', svc='key-programming', min_price=89,
    title='Key Fob Replacement and Programming in Cumming, GA',
    h1='Key fob replacement in Cumming, GA', l2='New remote or flip key, programmed at your car.',
    lede='Remote stopped working, buttons dead, or the fob is lost? I bring a new remote and program it to your car anywhere in North Atlanta. '
         'Often it is just the battery, and I check that first.',
    desc='Key fob and remote replacement in Cumming and North Atlanta: new remote programmed from $129, remote you bought from $89, flip key from $150.',
    article=(
        '<h2>Quick answer</h2>\n<p>A new replacement remote, supplied and programmed, starts <strong>from $129</strong>. If you bought the remote yourself, '
        'programming the buttons starts <strong>from $89</strong>. A flip key or remote head key with a cut blade starts <strong>from $150</strong>. '
        'If the fob only stopped working, start with the battery: see <a href="/guides/key-fob-not-working/">key fob not working</a>.</p>\n'
        '<h2>Fob, remote or smart key?</h2>\n<ul><li><strong>Separate remote</strong>: buttons only, the car starts with a metal key. Replacement remote from $129.</li>'
        '<li><strong>Flip key or remote head key</strong>: remote and key in one piece. Cut and programmed from $150.</li>'
        '<li><strong>Push-to-start smart key</strong>: the car starts with the key in your pocket. See <a href="/push-to-start-smart-key/">push-to-start smart key</a>.</li></ul>\n'
        '<h2>How the job goes</h2>\n<ol><li>I check the old fob: battery, buttons and whether the car still sees the chip.</li>'
        '<li>I match the new remote to your car by part number and button layout, so every button works.</li>'
        '<li>I program it at the car and test lock, unlock, trunk and panic, plus sliding doors or remote start if your car has them.</li></ol>\n'
        '<h2>Prices</h2>\n' + prices([('Key fob not working: new battery and a check', 'from $75'), ('Remote you bought, buttons only', 'from $89'),
                                     ('Replacement remote, supplied and programmed', 'from $129'), ('Flip key or remote head key', 'from $150'),
                                     ('Second key for the same car, same visit', '50% off')]) +
        '<p>The battery check is free when I am already there for another job. See all <a href="/pricing/">prices</a>.</p>\n'
        '<h2>Remote jobs I have done</h2>\n' +
        jobs_links(['2021-lexus-rx-smart-key-programming-cumming', '2017-honda-odyssey-spare-smart-key-cumming',
                    '2012-ford-explorer-all-keys-lost-flowery-branch', '2011-toyota-camry-all-keys-lost-cumming',
                    '2019-ford-ranger-all-keys-lost-johns-creek']) +
        '<h2>When to call</h2>\n<p>' + HOURS + '</p>\n'),
    faq=[('How much does it cost to replace a key fob?', 'A replacement remote, supplied and programmed, starts from $129. Programming a remote you bought starts from $89. A flip key with a cut blade starts from $150.'),
         ('My key fob stopped working. Do I need a new one?', 'Not always. A dead battery is the most common cause. If the battery is fine and the car still does not respond, the remote may need to be synced again or replaced.'),
         ('The new key starts the car but the buttons do not work. Why?', 'The chip and the remote are programmed separately on many cars. Usually the remote step was not done, and it does not need a new key.'),
         ('Can you program a remote I bought on Amazon or eBay?', 'Often yes, from $89, if it is the right part for your car. Send me the part number before you order. It is tested before you pay, but a part you bought is not under my warranty.'),
         ('Is there a warranty?', '1 year on keys and remotes I supply. Not covered: physical or water damage, lost keys and batteries.')]))

PAGES.append(dict(
    slug='broken-key-extraction', svc='key-programming', min_price=75,
    title='Broken Key Extraction in Cumming, GA',
    h1='Broken key extraction in Cumming, GA', l2='Key snapped in the ignition or a door lock? I get it out at your car.',
    lede='A broken key piece stuck in the ignition, the door or the trunk lock. I remove it with extraction tools, without damaging the lock, '
         'and make a new key on the spot if you need one.',
    desc='Broken car key removed from the ignition or a door lock at your car in Cumming and North Atlanta, from $75. New key priced separately.',
    article=(
        '<h2>Quick answer</h2>\n<p>Broken key extraction starts <strong>from $75</strong>. I come to the car, take the broken piece out of the ignition or the lock '
        'with extraction tools, and check that the lock still turns. If you need a new key, it is priced separately, and I can usually cut it '
        'from the broken pieces or from the lock right there.</p>\n'
        '<h2>Before I get there</h2>\n<ul><li>Do not push the piece deeper with another key, a pin or tweezers.</li>'
        '<li>Do not spray glue or oil into the lock.</li><li>Keep both broken pieces: they help cut the new key.</li></ul>\n'
        '<h2>How the job goes</h2>\n<ol><li>I look at where the piece sits and how deep it is.</li>'
        '<li>I pull it out with thin extraction tools that hook the cuts on the blade.</li>'
        '<li>I test the lock or ignition with a working key.</li>'
        '<li>If there is no working key left, I make a new one: cut to your locks and, if your car needs it, programmed.</li></ol>\n'
        '<h2>Prices</h2>\n' + prices([('Broken key extraction', 'from $75'), ('Plain metal key, no chip', 'from $75'),
                                     ('Spare key with chip, cut and programmed', 'from $140'), ('Flip key or remote head key', 'from $150')]) +
        '<p>In Cumming, Forsyth County and Sugar Hill the price is as listed. From 12 to 25 miles quick fixes are $100. See <a href="/pricing/">prices</a> for all distances.</p>\n'
        '<h2>Why keys break</h2>\n<p>A worn key, a sticky ignition, or turning the key with a heavy key ring hanging from it. '
        'If your key is bent or the cuts are worn, make a fresh spare before it breaks: see <a href="/spare-key/">spare key</a>.</p>\n'
        '<h2>When to call</h2>\n<p>Monday to Saturday, nights included (from 9 pm to 7 am there is a $50 night charge). '
        'On Sunday I take only lockouts and all keys lost.</p>\n'),
    faq=[('How much does it cost to get a broken key out?', 'From $75 in Cumming, Forsyth County and Sugar Hill, $100 from 12 to 25 miles. A new key, if you need one, is priced separately.'),
         ('Will getting the key out damage the lock?', 'No, not with proper extraction tools. Damage usually comes from trying to dig the piece out with whatever is at hand.'),
         ('Can you make a new key from the broken one?', 'Usually yes. The two pieces show the cuts. If the piece is lost, I can cut a key from the lock or from the vehicle code.'),
         ('The key broke in the ignition. Will my car start after?', 'Once the piece is out and you have a working key, yes. If the car has a chip key, a new key also needs programming, which I do at the car.')]))

PAGES.append(dict(
    slug='erase-lost-key', svc='all-keys-lost', min_price=89,
    title='Erase a Lost or Stolen Car Key in Cumming, GA',
    h1='Erase a lost or stolen car key', l2='Remove the missing key from your car’s memory, so it no longer starts it.',
    lede='If your key was stolen or lost somewhere it could be found with the car, the old key can still open and start it. '
         'I erase it from the car’s memory at your car, anywhere in North Atlanta.',
    desc='Lost or stolen car key erased from the car’s memory at your car in Cumming and North Atlanta, from $89. Free with a new key from LocksMitch.',
    article=(
        '<h2>Quick answer</h2>\n<p>Erasing a lost key starts <strong>from $89</strong>, and it is <strong>free when I make you a new key</strong>. '
        'I connect to the car, clear every key from its memory and program back only the keys you still have, plus any new one. '
        'After that, the missing key can no longer start the car. On many cars its remote stops working too.</p>\n'
        '<h2>When to do it</h2>\n<ul><li>The key was stolen, for example with a bag or a purse.</li>'
        '<li>The key was lost with something that has your address on it.</li>'
        '<li>You bought a used car and do not know who still has a key.</li>'
        '<li>A former employee, tenant or family member kept a key.</li></ul>\n'
        '<h2>How the job goes</h2>\n<ol><li>Bring every key you still have. Any key that is not at the car will stop working.</li>'
        '<li>I clear the key memory and program the keys you have, one by one.</li>'
        '<li>We test each key: start, lock and unlock.</li></ol>\n'
        '<p>Keep in mind: erasing stops the key from starting the car. A plain metal blade can still turn an old door lock. '
        'If that worries you, ask me about the locks too.</p>\n'
        '<h2>Prices</h2>\n' + prices([('Erase a lost key, keys you have reprogrammed', 'from $89'),
                                     ('Erase with a new key from LocksMitch', 'free'), ('All keys lost, new key made', 'from $190')]) +
        '<p>See all <a href="/pricing/">prices</a>.</p>\n'
        '<h2>Stolen key, no key left?</h2>\n<p>Then it is an <a href="/all-keys-lost/">all keys lost</a> job, and erasing the stolen key is part of it at no extra charge. '
        'Read a real case: <a href="/jobs/2020-kia-forte-all-keys-lost-atlanta/">a Kia Forte after a stolen bag</a>.</p>\n'
        '<h2>When to call</h2>\n<p>' + HOURS + ' A stolen key with no key left is an all keys lost job, and I come any day.</p>\n'),
    faq=[('Can a car be started with a key that was erased?', 'No. Once the key is removed from the car’s memory, its chip is no longer accepted, so it will not start the car.'),
         ('How much does it cost to erase a lost key?', 'From $89. It is free when I make you a new key in the same visit.'),
         ('Do I need all my keys there?', 'Yes. Every key that is not at the car during the job will stop working, so bring all the keys you want to keep.'),
         ('Can every car do this?', 'Most cars from the late 1990s on with chip keys can. A few makes need extra steps or are done by the dealer. Send me the year, make and model to confirm.')]))

# ---- about

PAGES.append(dict(
    slug='about', svc='spare-key', kind='about',
    title='About Mitch, Mobile Car Locksmith in Cumming, GA',
    h1='About LocksMitch', l2='One locksmith who comes to your car, across North Atlanta.',
    lede='Hi, I’m Mitch, the owner of LocksMitch and the locksmith who shows up at your car. There is no call center: when you call or text, you reach me.',
    desc='Who is behind LocksMitch: Mitch, a NASTF-registered, insured mobile car locksmith in Cumming, GA. Equipment, area, warranty and how to reach him.',
    article=(
        '<h2>Who I am</h2>\n<p>Forsyth County is home for me, and I cover Cumming and the rest of North Atlanta. LocksMitch is just me. '
        'There is no dispatcher in between: the person who answers the phone is the person who cuts and programs your key. '
        'I tell you the price before I drive out, and it does not change at your car.</p>\n'
        '<h2>Credentials</h2>\n<ul><li><strong>NASTF-registered Vehicle Security Professional.</strong> This gives access to manufacturer key data, the same as dealers.</li>'
        '<li><strong>Insured</strong> on every job.</li><li><strong>Registered business</strong>: LocksMitch is a DBA of TPVision LLC.</li>'
        '<li><strong>1-year warranty</strong> on keys and remotes I supply.</li></ul>\n'
        '<h2>What I bring to your car</h2>\n<p>Key programmers and cutting tools travel with me: key programmers (Autel IM508S with XP400 Pro, Autel KM100, '
        'Xhorse Key Tool Max Pro), the Yanhua ACDP-2 for European cars, an Xhorse Dolphin key cutting machine, Lishi pick-decoders for reading locks, '
        'and blanks and smart keys for most makes. Look for the Tesla Model Y with the LocksMitch logo: that’s me pulling up.</p>\n'
        '<h2>What I do</h2>\n<ul><li><a href="/all-keys-lost/">All keys lost</a>, new key made at the car</li><li><a href="/spare-key/">Spare keys</a> and '
        '<a href="/push-to-start-smart-key/">push-to-start smart keys</a></li><li><a href="/car-lockout/">Car lockouts</a></li>'
        '<li><a href="/key-fob-replacement/">Key fob replacement</a> and <a href="/key-programming/">key programming</a></li>'
        '<li><a href="/broken-key-extraction/">Broken key extraction</a> and <a href="/erase-lost-key/">erasing a lost key</a></li></ul>\n'
        '<p>See real jobs with photos on <a href="/jobs/">recent jobs</a>, and what customers say on <a href="/reviews/">reviews</a>.</p>\n'
        '<h2>Where and when</h2>\n<p>North Atlanta, from Cumming and Lake Lanier down to the Perimeter: Forsyth, Gwinnett, North Fulton, Hall, Dawson and Cherokee. '
        + HOURS + '</p>\n'
        '<h2>Talk to me</h2>\n<p>Call or text ' + CALL + ' with the year, make and model. More ways to reach me on the <a href="/contact/">contact page</a>.</p>\n'),
    faq=[('Does Georgia require a locksmith license?', 'No. Georgia has no state license for locksmiths. LocksMitch is a registered business (a DBA of TPVision LLC), insured, and registered with NASTF as a Vehicle Security Professional.'),
         ('Who will come to my car?', 'Mitch, the owner. LocksMitch is a one-person business, so the person you talk to is the person who does the job.'),
         ('Do you have a shop?', 'No. LocksMitch is fully mobile: I come to your home, work, a parking lot or the roadside.')]))

# ---- reviews

PAGES.append(dict(
    slug='reviews', svc='spare-key', kind='reviews',
    title='LocksMitch Reviews: What Customers Say',
    h1='Reviews', l2='What customers say about LocksMitch on Google.',
    lede='Every review here is a real Google review, word for word. To read them all or leave one, open the LocksMitch profile on Google.',
    desc='Real Google reviews of LocksMitch, mobile car locksmith in Cumming and North Atlanta, word for word.',
    article=None,
    faq=[('Are these reviews real?', 'Yes. They are copied word for word from the LocksMitch profile on Google, with the name the customer uses there.'),
         ('How can I leave a review?', 'Open the LocksMitch profile on Google and tap "Write a review". It takes a minute and helps a small business a lot.')]))

# ---- faq

PAGES.append(dict(
    slug='faq', svc='spare-key', kind='faq',
    title='Car Locksmith Questions: Prices, Hours, Warranty | LocksMitch',
    h1='Questions and answers', l2='Prices, hours, payment, warranty and how a visit works.',
    lede='The questions people ask me most, in one place. Don’t see yours? Text (770) 270-3333 and you get an answer from the locksmith, not a call center.',
    desc='Answers about LocksMitch: prices, hours, Sunday calls, payment, warranty, smart keys, all keys lost and how a mobile locksmith visit works.',
    article=None,
    faq=[('Is it cheaper than the dealership?', 'Usually, and you skip the tow. The dealer needs the car on their lot; I do the same programming in your driveway. Send the vehicle details and I quote it.'),
         ('Can you make a key if I have lost every one?', 'Yes. That is the <a href="/all-keys-lost/">all keys lost</a> job, from $190. I cut the key from your vehicle’s code and program it on site.'),
         ('Do you work on push-to-start and smart keys?', 'Yes, for most makes. See <a href="/push-to-start-smart-key/">push-to-start smart key</a>. Tell me the year, make and model and I confirm before coming out.'),
         ('How much does a car lockout cost?', 'Flat rate: $75 in Cumming and Forsyth County, $100 up to 25 miles, $125 up to 40 miles. See <a href="/car-lockout/">car lockout</a>.'),
         ('What are your hours?', HOURS),
         ('Do you work on Sunday?', 'Yes, for lockouts and all keys lost. Spare keys, programming and other jobs are done Monday to Saturday.'),
         ('Do I need to tow my car to you?', 'No. I bring the key machine, blanks and programmer to wherever the car is: home, work, a parking lot or the side of the road.'),
         ('Can this damage my car?', 'I take care not to. Doors are opened with automotive lockout tools, not by force, and keys are programmed with dealer-level equipment, usually through the diagnostic port.'),
         ('Is there a warranty?', '1 year on keys and remotes I supply. If one stops working within a year, I fix or replace it free. Not covered: physical or water damage, lost keys and batteries. A key you bought elsewhere is tested before you pay but is not under warranty.'),
         ('Can you program a key I bought online?', 'Often yes: a smart key $129, a remote from $89. It has to be the right part for your car, so send me the part number before you order. See <a href="/key-fob-replacement/">key fob replacement</a>.'),
         ('My key is stolen. Can the thief still start my car?', 'Yes, until the key is erased from the car’s memory. See <a href="/erase-lost-key/">erase a lost key</a>: from $89, free with a new key.'),
         ('My key broke in the lock. What now?', 'Don’t push the piece deeper and keep both halves. Extraction is from $75. See <a href="/broken-key-extraction/">broken key extraction</a>.'),
         ('Is there a discount on a second key?', 'Yes. A second key for the same car, made in the same visit, is 50% off, for spare keys and all keys lost.'),
         ('How do I get the $15 discount?', 'Book through the <a href="/book/">online booking page</a>. Valid on spare keys and all-keys-lost jobs.'),
         ('How can I pay?', 'Cash, credit and debit cards, Apple Pay, Google Pay, Zelle, Venmo or Cash App.'),
         ('What do I need to show for a new key?', 'Proof that the car is yours: a photo ID plus the registration, title or insurance card.'),
         ('Can I text instead of calling?', 'Yes. Text (770) 270-3333 with the year, make and model and what happened.')]))

# ---- contact

PAGES.append(dict(
    slug='contact', svc='spare-key', kind='contact',
    title='Contact LocksMitch: Call or Text (770) 270-3333',
    h1='Contact LocksMitch', l2='Call, text or message: you reach the locksmith, not a call center.',
    lede='The fastest way is a call or a text to (770) 270-3333 with the year, make and model of your car and what happened. You get the price before I drive out.',
    desc='Contact LocksMitch, mobile car locksmith in Cumming and North Atlanta: call or text (770) 270-3333, WhatsApp, email, online booking. Hours and area.',
    article=(
        '<h2>Ways to reach me</h2>\n<ul class="contact-list">'
        '<li><b>Call</b>' + CALL + '</li>'
        '<li><b>Text</b><a href="sms:+17702703333">(770) 270-3333</a>: send the year, make and model and a photo of the key if you have one</li>'
        '<li><b>WhatsApp</b><a href="https://wa.me/17702703333" target="_blank" rel="noopener">Message on WhatsApp</a></li>'
        '<li><b>Telegram</b><a href="https://t.me/LocksMitch" target="_blank" rel="noopener">@LocksMitch</a></li>'
        '<li><b>Email</b><a href="mailto:info@locksmitch.com">info@locksmitch.com</a></li>'
        '<li><b>Book online</b><a href="/book/">Pick a time</a>, $15 off spare keys and all keys lost</li>'
        '<li><b>Instagram</b><a href="https://www.instagram.com/locksmitch.ga/" target="_blank" rel="noopener">@locksmitch.ga</a></li>'
        '<li><b>Facebook</b><a href="https://www.facebook.com/profile.php?id=61585047509637" target="_blank" rel="noopener">LocksMitch</a></li></ul>\n'
        '<h2>Hours</h2>\n<p>' + HOURS + '</p>\n'
        '<h2>Where I work</h2>\n<p>LocksMitch is fully mobile, with no shop to drive to: I come to your car. The area is North Atlanta, from Cumming and Lake Lanier down to the Perimeter. '
        'By county: <a href="/forsyth-county/">Forsyth</a>, <a href="/gwinnett-county/">Gwinnett</a> and <a href="/north-fulton/">North Fulton</a>. '
        'Cities: <a href="/cumming/">Cumming</a>, <a href="/alpharetta/">Alpharetta</a>, <a href="/johnscreek/">Johns Creek</a>, <a href="/suwanee/">Suwanee</a>, '
        '<a href="/buford/">Buford</a>, <a href="/gainesville/">Gainesville</a> and <a href="/#area">more</a>.</p>\n'
        '<h2>Locked out right now?</h2>\n<p>Call ' + CALL + '. It’s faster than any form.</p>\n'),
    faq=[('What is the fastest way to get a price?', 'Text (770) 270-3333 with the year, make and model and what happened. You get the price by text before I drive out.'),
         ('Do you have an address I can drive to?', 'No. LocksMitch is fully mobile, with no storefront. I come to your car.')]))


def build_reviews_article():
    data = json.load(open(os.path.join(ROOT, 'tools', 'reviews.json'), encoding='utf-8'))
    revs = sorted(data['reviews'], key=lambda r: r['date'], reverse=True)
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    items = ''.join('<li><div class="stars" aria-label="%d out of 5 stars">%s</div><p>%s</p><div class="who">%s · Google · %s %d, %s</div></li>' % (
        r['rating'], '★' * r['rating'], esc(r['text']), esc(r['name']), months[int(r['date'][5:7]) - 1], int(r['date'][8:10]), r['date'][:4]) for r in revs)
    return ('<p><strong>5.0 on Google.</strong> Newest first.</p>\n<ul class="review-list">%s</ul>\n'
            '<p><a href="%s" target="_blank" rel="noopener">See all reviews on Google</a></p>\n'
            '<h2>Had a job done?</h2>\n<p>A short review on Google helps other drivers find an honest locksmith. '
            'You can also see the work itself on <a href="/jobs/">recent jobs</a>.</p>\n') % (items, data['profile_url'])


def main():
    tpl = open(TEMPLATE, encoding='utf-8').read()
    changed = []
    for p in PAGES:
        url = '%s/%s/' % (SITE, p['slug'])
        kind = p.get('kind', 'service')
        lds = [crumbs_ld(p['h1'], url), faq_ld(p['faq'])]
        if kind == 'service':
            lds.insert(0, service_ld(p['h1'], p['desc'], url, p['min_price']))
        elif kind == 'about':
            lds.insert(0, ld({'@context': 'https://schema.org', '@type': 'AboutPage', 'name': p['title'], 'url': url,
                              'about': {'@id': SITE + '/#locksmith'},
                              'mainEntity': {'@type': 'Person', 'name': 'Mitch', 'jobTitle': 'Owner and locksmith', 'worksFor': {'@id': SITE + '/#locksmith'}}}))
        elif kind == 'contact':
            lds.insert(0, ld({'@context': 'https://schema.org', '@type': 'ContactPage', 'name': p['title'], 'url': url, 'about': {'@id': SITE + '/#locksmith'}}))
        else:
            lds.insert(0, ld({'@context': 'https://schema.org', '@type': 'WebPage', 'name': p['title'], 'url': url, 'about': {'@id': SITE + '/#locksmith'}}))
        title = p['title'] if '|' in p['title'] or kind in ('reviews', 'contact') else p['title'] + ' | LocksMitch'
        s = set_head(tpl, title, p['desc'], url, p['h1'], 'website', lds)
        s = set_hero(s, '<a href="/">LocksMitch</a> › %s' % esc(p['h1']), p['h1'], p['l2'], p['lede'],
                     'By Mitch, owner of LocksMitch · Updated November 2026', p['svc'])
        if kind == 'reviews':
            article = build_reviews_article()
        elif kind == 'faq':
            article = ''
        else:
            article = p['article']
        if kind == 'faq':
            article += '<div class="faq guide-faq">%s</div>\n' % ''.join(
                '<details open><summary>%s</summary><p>%s</p></details>' % (esc(q), a) for q, a in p['faq'])
            article += '<h2>Still have a question?</h2>\n<p>Call or text ' + CALL + '. More on the <a href="/contact/">contact page</a>.</p>'
        else:
            article += faq_html(p['faq'])
            if kind == 'service':
                article += ('<h2>Get a price</h2>\n<p>Call or text ' + CALL + ' with the year, make and model. '
                            'You get the price before I drive out, and coming to you is included.</p>')
        s = set_body(s, article, aside())
        if write('%s/index.html' % p['slug'], s):
            changed.append(p['slug'])
    print('extra pages: %d; changed: %s' % (len(PAGES), ', '.join(changed) or 'none'))


main()
