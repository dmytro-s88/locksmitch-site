"""Make-specific answers for the four make questions in the FAQ of each make page.

Every make page has four questions that used to carry the same answer on all makes:
    lost  : "Can you make a <make> key if I lost all of them?"
    smart : "Do you program <make> smart keys and push-to-start fobs?"
    orig  : "Original or aftermarket <make> key?"
    new   : "Do you work on the newest <make> models?"
This script puts the answer from ANSWERS into the page and into the FAQPage JSON-LD. A key left out keeps the
answer that is already on the page (Mercedes and Land Rover have hand-written ones). The questions stay as they are.
Two home page questions that repeat the make questions (DROP) are removed from the make pages.

Rules for the texts: only what the page already promises (prices, year limits, "quoted by model") and what was
really done (tools/jobs.json, tools/job_pages.json). No "cut from the key code": the key is made from the car itself.
No customer names, addresses, prices of a job or lead numbers. No long dashes. Rerun changes nothing.
    python3 -I tools/make_faq.py
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KINDS = [
    ('lost', re.compile(r'^Can you make .* if I lost all of them\?$')),
    ('smart', re.compile(r'^Do you program .* smart keys and push-to-start fobs\?$')),
    ('orig', re.compile(r'^Original or aftermarket .* key\?$')),
    ('new', re.compile(r'^Do you work on the newest .* models\?$')),
]

ANSWERS = {
    'toyota': {
        'lost': "Yes. We did it on a 2010 Corolla and a 2011 Camry in Cumming: no key at all, and the new keys were made from the car itself, with no tow. On a Toyota, all keys lost adds $50 to $150 to the price of the key. Ask for two keys while we are there: the second one is 50% off.",
        'smart': "Yes. Push-to-start models like the RAV4, Highlander, Camry and Sienna use a smart key, from $200. Two Toyota smart keys can look the same and be different inside, so we match yours by the number on its circuit board. We added spare smart keys to a 2017 and a 2019 Highlander on a car lot in Cumming.",
        'orig': "Your choice. An original Toyota key costs more, a quality aftermarket key does the same job for less, and we carry both. What matters is the match: the G or H chip on older keys, the board number on smart keys. You get the price of each by text first.",
        'new': "Most of them. A spare for a newer Toyota is a regular visit while one key still works. With every key lost, some of the newest models take extra steps, so send the year and model and we confirm your exact car before anyone drives out.",
    },
    'lexus': {
        'lost': "Yes. Almost every Lexus uses a smart key, so we program a new one to the car on site and cut the small emergency blade inside it for your door. All keys lost adds $50 to $200 on a Lexus. Tell us the year and model and whether the car is locked.",
        'smart': "Yes, that is most of our Lexus work. A Lexus smart key starts from $220. On a 2021 RX in Cumming the new key started the car right away, and the lock and unlock buttons came alive after the remote sync step was run a second time.",
        'orig': "Your choice, and we carry both. If you buy a Lexus key online, match the part number and the number on the circuit board inside, not only the look of the case. Send a photo of both sides of your key and we tell you which one fits before you pay for it.",
        'new': "Most of them. A spare while one key still works is the easy case. With every key lost, a few of the very newest Lexus models need parts or steps we confirm first. Send the year and model and you get a clear answer before anyone drives out.",
    },
    'honda': {
        'lost': "Yes, for Honda and Acura. The new key is cut and programmed at the car, and all keys lost adds $50 to $150. If you are down to a valet key, don't wait: on a 2007 Ridgeline in Cumming we cut two full remote keys from the valet key, which costs less than starting with no key at all.",
        'smart': "Yes. Push-to-start Civic, Accord, CR-V, Pilot and Odyssey models use a smart key, from $180. We match the button layout too: on a 2017 Odyssey in Cumming the new key had to have the power sliding door buttons. A 2019 Accord got its spare smart key on a car lot the same way.",
        'orig': "Your choice. An original Honda key and a quality aftermarket key both work when the chip and the buttons match your car, and we carry both. A hardware store copy of the metal part alone may open the door but will not start the engine.",
        'new': "Most of them. A few of the newest Honda and Acura models need steps or a key we confirm first, so send the year and model and whether it is a turn key or push-to-start. You get a yes or no and a price by text before anyone drives out.",
    },
    'ford': {
        'lost': "Yes. On a 2019 Ranger in Johns Creek with no key we read the door lock, cut two flip keys and programmed them at the truck. On a 2012 Explorer in Flowery Branch we made four keys the same day. All keys lost adds $50 to $250 on a Ford, and the car's own security wait is why the job takes about an hour.",
        'smart': "Yes. Ford calls its push-to-start key Intelligent Access, and Lincoln uses the same kind. A smart key starts from $180 and is programmed at the car. Tell us whether your Ford starts with a button or a key, because one model, like the F-150, comes with different keys depending on the trim.",
        'orig': "Your choice. We carry original Ford keys and quality aftermarket ones that cost less. Either way, every key we make is tested in the door, in the ignition and on the remote buttons before you pay.",
        'new': "Many of them. Ford 2021 and newer is confirmed per car before we quote, because the newer systems vary by model. Send the year and model and you get a straight yes or no first.",
    },
    'chevrolet-gmc': {
        'lost': "Yes. After a house fire took every key to a 2024 Silverado 2500HD in Cumming, we read the door lock, cut the emergency blade and programmed a new smart key in the driveway. Many GM vehicles make us wait during the security relearn, ten to thirty minutes. All keys lost adds $50 to $250.",
        'smart': "Yes. Push-to-start Tahoe, Suburban, Yukon and Escalade models and many newer Silverado and Sierra trims use a smart key, from $180. Tell us the year and trim, since the key depends on whether the truck starts with a button.",
        'orig': "Your choice on most models, and we carry both. If your flip key still starts the truck and only the case or the blade is worn out, a new case that keeps your programmed chip can cost less than either.",
        'new': "Many of them. The newest GM trucks and SUVs use a newer system that needs GM's own dealer software, and that is how we did a 2024 Silverado 2500HD in Cumming. Send the year and model and we confirm your exact vehicle before anyone drives out.",
    },
    'jeep-dodge-ram': {
        'lost': "Yes. A recent one was a 2020 Dodge Challenger in Cumming with every key gone. How long it takes depends on the year: an older fobik car is quick, and a 2018 or newer one has a security gateway we connect through first. All keys lost adds $50 to $200.",
        'smart': "Yes. The newer Grand Cherokee, Wrangler, Durango, Charger, Challenger and Pacifica use a push-to-start smart key, from $180. Many cars from about 2008 to 2018 use a fobik that plugs into the dash instead, and we program those too.",
        'orig': "Your choice. We carry original keys and quality aftermarket ones that cost less. Tell us whether your key plugs into the dash or stays in your pocket, and we text you the price of each before we come out.",
        'new': "Most of them. Newer Jeep, Dodge, Chrysler and RAM models have a security gateway in front of the diagnostic port, and we come with the connection for it. A few of the very newest need parts or steps we confirm first, so send the year and model.",
    },
    'hyundai': {
        'lost': "Yes. On a 2025 Santa Fe Hybrid in Cumming with no key at all, we programmed a temporary key first so the car could be driven, then the genuine Hyundai key when it arrived. All keys lost adds $50 to $100, and 2022 and newer models add $150 to $250 for the newer immobilizer.",
        'smart': "Yes. Santa Fe, Palisade, Tucson and Genesis models with push-to-start use a smart key, from $180. On new models the key has to match the exact part number for your VIN. On a 2026 Tucson in Gainesville the second fob that came with the car was the wrong one, and a genuine key with the right number fixed it.",
        'orig': "On new Hyundai and Genesis models the key has to match the exact part number for your VIN, so we often use a genuine Hyundai key. On older Elantra, Sonata and Tucson models a quality aftermarket key costs less. We tell you the options for your car and the price of each first.",
        'new': "Yes. We have done a 2025 Santa Fe and a 2026 Tucson. Hyundai models from 2022 on use a newer immobilizer, which adds $150 to $250, and the genuine key sometimes has to be ordered. Send the VIN or the year and model and we check the exact key.",
    },
    'kia': {
        'lost': "Yes. One night a bag was stolen with the only key to a 2020 Forte in downtown Atlanta. We opened the door, quieted the alarm, got the car's PIN and programmed a new smart key right in the parking lot. All keys lost adds $50 to $100, and 2022 and newer models add $150 to $250.",
        'smart': "Yes. Telluride, Sorento, Sportage and K5 models with push-to-start use a smart key, from $180. A 2021 Forte in Cumming got its second smart key one evening at the owner's home: emergency blade cut, key programmed, door and start button tested.",
        'orig': "Both exist for most Kia models. What matters more is the part number: a Kia key has to match your car by VIN, not just by its look. Send the VIN or the year and model before you buy anything online, and we tell you which key fits and what each option costs.",
        'new': "Most of them. Kia models from 2022 on use a newer immobilizer, which adds $150 to $250. Tell us the exact year, since the Optima became the K5 in 2021 and the key changed with it. We confirm your car before anyone drives out.",
    },
    'nissan': {
        'lost': "Yes, for Nissan and Infiniti. The car needs a security code to accept a new key, and we read or retrieve it for your car. All keys lost adds $50 to $200. A 2008 Infiniti G35 in Sugar Hill had forgotten every key after sitting for years with a dead battery, and we programmed a new one on the spot.",
        'smart': "Yes. Nissan calls it the Intelligent Key, and it is on most Altima, Rogue, Maxima, Murano and Pathfinder models, from $180. On a 2015 Altima in Lawrenceville the owner's fob was alive but the car refused it; a new smart key programmed at the car brought the push-to-start back.",
        'orig': "Your choice on most models, and we carry both. Before you buy a fob, make sure the key is the problem: an \"I-Key System Error\" on the dash can come from a fault in the car, not from the key. Ask us to read the codes first, so you don't pay for a fob you don't need.",
        'new': "Most of them. Some Rogue and Sentra years take extra steps or are not a fit for on-site work, so send the year and model first. You get a clear yes or no and a price by text before anyone drives out.",
    },
    'mitsubishi': {
        'lost': "Yes. Many Mitsubishi keys need a security code for programming, and we handle that on our side. The new key is cut and programmed at your car, so it does not have to go to one of the few Mitsubishi dealers around Atlanta. All keys lost adds $50 to $200.",
        'smart': "Yes. Push-to-start Outlander, Outlander Sport and Eclipse Cross models use a smart key, from $180. Mirage, Lancer, Galant and older Outlanders use a chip key or a remote head key instead. Tell us whether your car starts with a button or a key.",
        'orig': "Your choice on most models. An aftermarket key costs less and works the same when it matches your year and model; an original Mitsubishi key costs more. We text you the price of each before we come out.",
        'new': "Most of them. A few of the very newest models need parts or steps we confirm first. Send the exact year, the model and whether it starts with a button, and we tell you before anyone drives out.",
    },
    'subaru': {
        'lost': "Yes, and it costs more than on most Japanese cars: all keys lost adds $200 to $350 on a Subaru. On many years the car needs a longer procedure when no working key is left. If you still have one key, a spare now is the cheaper route.",
        'smart': "Yes. Newer Outback, Forester, Crosstrek and Ascent trims with push-to-start use a smart key, from $300. Older ones use a chip key or a remote head key. If you still have a working key, adding a second smart key is a normal visit.",
        'orig': "Your choice on most models. An original Subaru key costs more; a quality aftermarket key costs less and works the same when it matches your year and trim. We text you the price of each before we come out.",
        'new': "Most of them. A few of the very newest Subaru models need parts or steps we confirm first. Send the year, the model and whether it is push-to-start. If you are at a trailhead, tell us which one too.",
    },
    'mazda': {
        'lost': "Yes. The new key is cut and programmed at your car, with no tow. All keys lost adds $50 to $100 on a Mazda, and 2022 and newer models add $150 to $250 because of the newer key system.",
        'smart': "Yes. Most newer Mazdas with push-to-start, like the CX-5, CX-30, CX-50 and Mazda3, use a smart key, from $190. Many older Mazda3, Mazda6 and CX-5 models use a flip key with the remote built in, from $170.",
        'orig': "Your choice. Original and quality aftermarket keys both work when they match your year and model. If your flip key still starts the car and only the case broke, ask about a new case first: it can cost much less than a new key.",
        'new': "Most of them. Mazda models from 2022 on use a newer key system that adds $150 to $250 to the price. Send the year and model and we confirm your car and the exact price by text before anyone drives out.",
    },
    'bmw': {
        'smart': "Yes. Comfort Access smart keys and regular remote keys are coded to the module in your car (CAS, FEM or BDC), at the car. On the newest G-series we add a spare while one key still works. Send the year and model, or the VIN, and we confirm what your car needs.",
        'orig': "On most BMW and Mini models up to about 2019 you can choose: an original key, or a quality aftermarket key that costs less. On some of the newest G-series models only an original BMW key can be added. We tell you which applies and the price before we come out.",
        'new': "Partly. On G-series models such as the G20 3 Series, G30 5 Series, G01 X3 and G05 X5 we add a spare key when you still have one that works. If every key is lost, BDC2 models (about 2015 to 2021) are checked case by case by VIN, and 2020 and newer BDC3 models go to the dealer. We tell you which on the phone, for free.",
    },
    'mercedes': {
        'orig': "For the years we cover, up to 2014, we tell you which keys are available for your car, original or aftermarket, and the price of each before we come out. For 2015 and newer the key comes from the dealer.",
    },
    'volkswagen-audi': {
        'lost': "Often, yes. It depends on the year and model: older Jetta, Passat, Golf and Tiguan cars are simpler, newer ones like the Atlas use a newer immobilizer that takes more steps, and Audi differs a lot from model to model. Send the details and we confirm before anyone drives out.",
        'smart': "Yes, on many models. A Volkswagen keyless smart key starts from $300, and Audi smart keys are quoted per car. These systems change a lot by year, so we check your exact car first and tell you upfront what is possible.",
        'orig': "It depends on the car. For many Volkswagen flip keys a quality aftermarket key works well and costs less. On some newer Volkswagen and Audi models only certain keys can be programmed. We tell you the options for your car and the price of each before we come out.",
        'new': "Some of them. Newer models like the Atlas and the latest Tiguan and Jetta use a newer immobilizer generation, and those are confirmed case by case. Send the year and model and you get a clear yes or no before anyone drives out.",
    },
    'land-rover-jaguar': {
        'lost': "Often, yes. All keys lost on a Land Rover or Jaguar is quoted by model, because the key systems differ between generations. Send the year and model and we tell you what is possible and the price before anyone drives out.",
        'smart': "Yes. Range Rover, Range Rover Sport, Evoque, Discovery, F-Pace, XF and F-Type all use smart keys, and a spare from us starts from $350 for 2011 and newer models. It is programmed at your car, without a dealer visit.",
        'orig': "It depends on the model and year. These keys are expensive at the dealer, so where a quality aftermarket key works for your car, we offer it as the cheaper option. We tell you what is available and the price of each before we come out.",
    },
    'volvo': {
        'lost': "On many models, yes, but every Volvo is quoted by model and some keys have to be ordered for your car first. Send the year and model and we tell you what is possible, the timeline and the price before booking.",
        'smart': "Yes, on the models we cover; the newer XC90, XC60 and XC40 are keyless. Volvo keys start from $450 and are quoted by model. Some have to be ordered for your car before we can come out, so ask early if your only key still works.",
        'orig': "It depends on the model. Many Volvo keys are made for a specific car, so often the choice is simply the key that fits your car, ordered ahead. Where a cheaper aftermarket key exists, we tell you, with the price of each.",
        'new': "Some of them. Volvo changed its key systems several times, so we check the newest models one by one. Send the year and model and whether the car is keyless, and we tell you what is possible before anyone drives out.",
    },
    'porsche': {
        'lost': "It depends on the model and year. Porsche keys are quoted by model, and for many cars only an original key works and has to be ordered first. Send the year and model and we tell you honestly what is possible before anyone drives out.",
        'smart': "On many models, yes. The Cayenne, Macan and Panamera use the car-shaped key, with keyless entry on many trims. Porsche keys start from $450 and are quoted by model. We tell you whether your key can be programmed right away or has to be ordered first.",
        'orig': "For many Porsches only an original key works, and it often has to be ordered for your car. Where a quality aftermarket key exists for your model and year, we offer it too. You get the options and the price before we come out.",
        'new': "Some of them. The newest Porsche models are checked one by one, because the key and the work vary a lot by year. Send the year and model and whether you still have a working key.",
    },
    'ferrari': {
        'lost': "Sometimes. It depends on the model and year, and every Ferrari key job is checked and quoted per car. Many keys have to be ordered first. Send the year and model and Mitch tells you what is possible before anything else happens.",
        'smart': "On the models we can do, yes, and at your garage, so the car does not need a trailer. Which models is checked per car, because the key and the steps differ between the 458, 488, F8, Roma and Portofino.",
        'orig': "For most Ferrari keys only the original works, and it usually has to be ordered for your car. Where another option exists, Mitch tells you, with the price of each, before anything is ordered.",
        'new': "Each one is checked on its own. The newest models such as the 296, SF90 and Purosangue may only be possible through the dealer. Send the year and model and you get a straight answer by text.",
    },
    'maserati': {
        'lost': "It depends on the model and year. Maserati jobs are quoted per car, and many keys have to be ordered first. Send the year and model and Mitch tells you what is possible and the price by text.",
        'smart': "On many models, yes. Ghibli, Levante and Quattroporte use keyless smart keys, and we program them where the car is parked. Many used Maseratis are sold with a single key, and adding the second one while the first still works is the easy version of the job.",
        'orig': "It depends on the model and year. For many Maserati keys only the original fits, and some have to be ordered ahead. Where a quality aftermarket key exists for your car, we offer it and tell you both prices.",
        'new': "Each one is checked on its own. The Grecale and MC20 are newer cars, and their keys may need to be ordered or may have to come from the dealer. Send the year and model and Mitch gives you a straight answer by text.",
    },
}


# Two questions from the home page FAQ repeat the make questions above and answered a flat "Yes" on every make,
# also where the make answer says "it depends". They are dropped from the make pages (text and FAQPage).
DROP = ['Can you make a key if I’ve lost every one?', 'Do you work on push-to-start and smart keys?']


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def typo(t):
    # curly apostrophes and quotes, to match the rest of the site
    t = re.sub(r'"([^"]*)"', '“\\1”', t)
    return t.replace("'", '’')


def kind_of(q):
    for k, pat in KINDS:
        if pat.match(q):
            return k
    return None


def main():
    changed = 0
    for slug, ans in ANSWERS.items():
        for k, t in ans.items():
            if '—' in t or '–' in t:
                raise SystemExit('long dash in %s/%s' % (slug, k))
            if 'key code' in t:
                raise SystemExit('"key code" in %s/%s' % (slug, k))
        p = os.path.join(ROOT, slug + '-key-replacement', 'index.html')
        old = s = open(p, encoding='utf-8').read()
        done, by_q = set(), {}

        def fix_item(m):
            q = html.unescape(re.sub(r'<[^>]+>', '', m.group(2))).strip()
            k = kind_of(q)
            if k not in ans:
                return m.group(0)
            done.add(k)
            a = typo(ans[k])
            by_q[q] = a
            return m.group(1) + m.group(2) + '</summary><p>' + esc(a) + '</p></details>'
        # only the template questions: the two make_content.py questions carry data-local="1"
        s = re.sub(r'(<details(?: open)?><summary>)(.*?)</summary><p>.*?</p></details>', fix_item, s, flags=re.S)
        for q in DROP:
            s = re.sub(r'[ \t]*<details><summary>' + re.escape(esc(q)) + r'</summary>.*?</details>\n', '', s, flags=re.S)
        if done != set(ans):
            raise SystemExit('%s: questions not found: %s' % (slug, sorted(set(ans) - done)))

        def fix_ld(mm):
            d = json.loads(mm.group(1))
            if d.get('@type') != 'FAQPage':
                return mm.group(0)
            d['mainEntity'] = [e for e in d['mainEntity'] if e['name'] not in DROP]
            seen = set()
            for e in d['mainEntity']:
                if e['name'] in by_q:
                    e['acceptedAnswer']['text'] = by_q[e['name']]
                    seen.add(e['name'])
            if seen != set(by_q):
                raise SystemExit('%s: not in FAQPage: %s' % (slug, sorted(set(by_q) - seen)))
            return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'
        s = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_ld, s, flags=re.S)
        if s != old:
            open(p, 'w', encoding='utf-8').write(s)
            changed += 1
        print(slug, 'ok,', len(ans), 'answers,', sum(len(t.split()) for t in ans.values()), 'words')
    print('pages changed:', changed, 'of', len(ANSWERS))


if __name__ == '__main__':
    main()
