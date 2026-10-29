"""Adds the unique local text and two local FAQ questions to the main city pages.

Each city gets a "local-more" block after the facts list (places we come to, drive notes) and two city-specific
questions at the top of the FAQ, mirrored into the FAQPage JSON-LD. Rerun is safe: an existing block is replaced.
    python3 -I tools/city_content.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CITIES = {
    'cumming': {
        'h3': 'Cumming, street by street',
        'paras': [
            'Cumming is where we start every day, so this is the one place where “on my way” usually means minutes, not an hour. Most calls come from the GA-400 corridor between exits 12 and 17: the parking lots at Halcyon and The Collection at Forsyth, the clinics and offices around Northside Hospital Forsyth, and the shopping strips along Market Place Boulevard and Buford Highway (GA-20).',
            'Lake Lanier is the other half of Cumming for us. Bald Ridge, Habersham and Mary Alice Park marinas, the boat ramps off Buford Dam Road and the rental houses along the water: keys go in the lake, fobs get wet, and a boat day ends with a locked car. We come to the ramp or the marina lot with the blanks and the programmer, so the car doesn’t need a tow to a dealer.',
            'Around town we also cover downtown Cumming and the City Center, Vickery Village, the Cumming Fairgrounds on event days, the Sawnee Mountain and Fowler Park trailheads (a classic place to lose a key on a hike), and the schools and subdivisions off Post Road, Bethelview Road and Pilgrim Mill Road.',
        ],
        'faq': [
            ('Do you come to the Lake Lanier marinas and boat ramps in Cumming?', 'Yes. Bald Ridge, Habersham, Mary Alice Park and the ramps off Buford Dam Road are all a short drive for us. If the key went in the water, we make a new one right at the lot. Most cars take about an hour.'),
            ('I’m locked out at Halcyon or The Collection. How long until you arrive?', 'Both are a few exits from our base, so in normal GA-400 traffic it’s usually 15 to 25 minutes. Mitch texts you the exact arrival time when he confirms the job.'),
        ],
    },
    'alpharetta': {
        'h3': 'Where we come in Alpharetta',
        'paras': [
            'Alpharetta is straight down GA-400 from Cumming, about 20 minutes to exits 9 through 11. The parking decks at Avalon and the lots at North Point Mall are the classic lockout spots: the fob stayed on the restaurant table and the doors locked on their own. We drive into the deck like any visitor; tell us the level and the row.',
            'Office parks are the other regular stop: Windward Parkway, Haynes Bridge Road, Old Milton Parkway and the campuses around Sanctuary Park. A spare key made in the office lot during lunch is the easiest key you will ever get, and you don’t miss an afternoon at the dealer.',
            'We also cover downtown Alpharetta and the City Center, Wills Park, Ameris Bank Amphitheatre on show nights, Big Creek Greenway trailheads, and the subdivisions off Kimball Bridge, Webb Bridge and Rucker Road. Alpharetta has a lot of newer push-to-start cars: send the year and model and we confirm the key type and price before anyone drives out.',
        ],
        'faq': [
            ('Can you get into the Avalon or North Point parking deck?', 'Yes. We drive in like any visitor. Text us the level, the row and the car, and we come straight to it. A lockout in Alpharetta is a flat $100 in the daytime.'),
            ('How long does it take you to reach Alpharetta?', 'About 20 minutes down GA-400 outside rush hour, a bit more at 5 pm. Mitch texts the arrival time when he confirms the job.'),
        ],
    },
    'johnscreek': {
        'h3': 'Where we come in Johns Creek',
        'paras': [
            'Johns Creek is mostly driveways for us: the subdivisions off Medlock Bridge, State Bridge, Abbotts Bridge and Old Alabama Road, often with two or three cars in the garage. That is where a spare key makes the most sense. We bring blanks for every car you list and make them in one visit, so nobody has to drive to a dealer and wait.',
            'Work calls come from Johns Creek Technology Park and the offices along Medlock Bridge Road, and from Emory Johns Creek Hospital. We also cover the shopping centers at State Bridge and Medlock Bridge, Newtown Park, Ocee Park, Cauley Creek Park and the river access at Abbotts Bridge, where keys tend to disappear on a kayak day.',
            'From Cumming we take Peachtree Parkway (GA-141) or McGinnis Ferry Road, about 25 minutes. Evening traffic on 141 can add ten minutes, so Mitch texts the real arrival time, not a guess.',
        ],
        'faq': [
            ('Can you make keys for more than one car in a single visit to Johns Creek?', 'Yes. Send the year, make and model of each car. We price each one before we come, bring the right blanks for all of them and do them back to back in your driveway.'),
            ('What is the fastest way for you to reach Johns Creek?', 'Peachtree Parkway (GA-141) or McGinnis Ferry Road from Cumming, about 25 minutes in normal traffic. If you are locked out, call instead of texting: it is faster.'),
        ],
    },
    'milton': {
        'h3': 'Where we come in Milton',
        'paras': [
            'Milton is right down GA-9 from Cumming, about 20 minutes: Crabapple and its downtown, Bell Memorial Park, and the horse farms and long driveways off Birmingham Highway, Hopewell Road and Freemanville Road. In Milton we usually drive up the driveway rather than meet in a parking lot: a lost key at home, a spare for a new driver before school starts, a truck key out on the farm.',
            'We also cover the offices along Deerfield Parkway, the shopping at Crabapple and along Highway 9, Milton City Park and Preserve, Providence Park, and the schools on Cogburn Road and Bethany Bend. A gate code or a landmark in your text saves a few minutes on the long roads.',
            'Milton families often ask for a second key for a teen driver. A spare made while you still have a working key is the cheap version of this job; losing the last key turns it into an all-keys-lost job at a higher price.',
        ],
        'faq': [
            ('Do you come out to the farms and long driveways in Milton?', 'Yes, anywhere a car can park. Send the address plus a gate code or a landmark, and Mitch comes up the driveway with everything on board.'),
            ('What does a spare key for a teen driver cost in Milton?', 'Spare keys start at $140 with a chip, $150 with a remote and $180 for push-to-start, made in your driveway in about an hour. You get the exact price by text before anyone drives out.'),
        ],
    },
    'roswell': {
        'h3': 'Where we come in Roswell',
        'paras': [
            'Roswell is about 30 minutes from us down GA-400 and Alpharetta Highway (GA-9). Canton Street on a weekend night is where lockout calls come from: the fob stayed on the table, the car locked itself. We also cover Historic Roswell and the Roswell Mill area, Holcomb Bridge Road, and the shopping along Crossville Road and Woodstock Road.',
            'The river parks are the other regular stop: Chattahoochee Nature Center, Riverside Park, the Vickery Creek trail lots and Big Creek Park. Trailhead parking is where keys get lost on a run. Tell us which lot and we come to it. We also reach Wellstar North Fulton Hospital and the offices around Holcomb Bridge and GA-400.',
            'Roswell is at the edge of our regular zone, so the price is the same flat rate as Alpharetta: lockouts $100, keys at the listed price with no trip fee. Mitch texts the arrival time when he confirms.',
        ],
        'faq': [
            ('Locked out on Canton Street at night. Do you still come?', 'Yes, 24/7. After 9 pm the $100 lockout adds $50 for the night call. Call rather than text so we can head out right away, and Mitch texts the ETA.'),
            ('Do you cover the Roswell parks along the Chattahoochee?', 'Yes: the Nature Center, Riverside Park, Vickery Creek and Big Creek trailhead lots. Send the name of the lot and a photo of the car if you can.'),
        ],
    },
    'buford': {
        'h3': 'Where we come in Buford',
        'paras': [
            'Buford is about 25 minutes from Cumming on GA-20 (Buford Drive) across the south end of Lake Lanier. The Mall of Georgia and the shopping around it on Buford Drive and Mall of Georgia Boulevard are the classic lockout spots in Gwinnett. We come to the lot; most lockouts take a few minutes once we are at the car.',
            'The lake is the other half of Buford: Lake Lanier Islands, Buford Dam Park, West Bank Park and the ramps off Buford Dam Road. Keys dropped off a boat or into the water happen every summer weekend. We make a new key at the marina lot, so the car does not need a tow.',
            'We also cover downtown Buford along Main Street, Hamilton Mill and the subdivisions off Hamilton Mill Road and Friendship Road, the warehouses and shops along I-985 exits 4 through 8 and Buford Highway, and Sugar Hill next door.',
        ],
        'faq': [
            ('Do you come to Lake Lanier Islands and the Buford marinas?', 'Yes. Lanier Islands, Buford Dam Park, West Bank Park and the ramps off Buford Dam Road. If the key is in the lake, we make a new one right at the lot, about an hour for most cars.'),
            ('Locked out at the Mall of Georgia. How fast can you get there?', 'About 25 minutes from Cumming in normal traffic. Mitch texts the exact arrival time when he confirms. A lockout in Buford is a flat $100 in the daytime.'),
        ],
    },
    'suwanee': {
        'h3': 'Where we come in Suwanee',
        'paras': [
            'Suwanee is about 25 minutes from Cumming down Peachtree Parkway (GA-141) or Suwanee Dam Road. Suwanee Town Center and Town Center Park on event nights are where the lots fill up and the lockout calls come from. We come to the lot during the event, not after it.',
            'Office parks along Peachtree Industrial Boulevard, Satellite Boulevard and Lawrenceville-Suwanee Road near I-85 exit 111 are a regular stop for spare keys during the workday: you keep working, we make the key in the lot. We also cover Sims Lake Park, George Pierce Park, the Suwanee Creek Greenway trailheads and the subdivisions off Moore Road, Suwanee Dam Road and Old Peachtree Road.',
            'Prefer Spanish? Text us in Spanish and you get the price and the confirmation in Spanish. Prices in Suwanee are the same flat rates as the rest of Gwinnett: lockouts $100, keys at the listed price with no trip fee.',
        ],
        'faq': [
            ('Do you cover events at Suwanee Town Center?', 'Yes, including evenings and festival nights. Text us the car and where it is parked. A lockout is a flat $100, plus $50 after 9 pm.'),
            ('Can I get a spare key made at my office in Suwanee?', 'Yes. The office parks on Peachtree Industrial, Satellite Boulevard and Lawrenceville-Suwanee Road are a regular stop. Most spare keys take about an hour, and you can keep working while we do it.'),
        ],
    },
    'gainesville': {
        'h3': 'Where we come in Gainesville',
        'paras': [
            'Gainesville is the north-east end of our area, about 35 minutes from Cumming on Browns Bridge Road (GA-369) or Dawsonville Highway (GA-53). We come to the downtown square, the garages and clinics around Northeast Georgia Medical Center, Brenau University and the University of North Georgia campus in Oakwood, and the shopping along Dawsonville Highway, Jesse Jewell Parkway and Browns Bridge Road.',
            'Lake Lanier here too: Lake Lanier Olympic Park and Clarks Bridge Park, Gainesville Marina and the ramps off Browns Bridge Road. And the work trucks: Gainesville runs on poultry plants, distribution and the warehouses along I-985 exits 16 through 24. We make keys for work trucks and vans, several vehicles in one visit if you have a small fleet.',
            'Chicopee Woods trail lots and the Atlanta Botanical Garden in Gainesville are where keys get lost on a weekend. Because Gainesville is a longer drive for us, call rather than text when you are locked out, so we can leave right away. Mitch texts the real arrival time.',
        ],
        'faq': [
            ('Do you serve the Northeast Georgia Medical Center area?', 'Yes: the hospital garages and the clinics off Jesse Jewell Parkway, plus Brenau and the UNG campus. Tell us the garage or the lot and we come to the car.'),
            ('How long does it take you to reach Gainesville?', 'About 35 minutes from Cumming by Browns Bridge Road in normal traffic. Mitch texts the exact time when he confirms. For a lockout, calling is faster than the form.'),
        ],
    },
}


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def main():
    for slug, c in CITIES.items():
        p = os.path.join(ROOT, slug, 'index.html')
        s = open(p, encoding='utf-8').read()
        # 1) local-more block after the facts list
        block = ('<div class="local-more"><h3 class="sub">' + esc(c['h3']) + '</h3>' +
                 ''.join('<p>' + esc(t) + '</p>' for t in c['paras']) + '</div>')
        s = re.sub(r'\n?\s*<div class="local-more">.*?</div>(?=\n)', '', s, flags=re.S)
        m = re.search(r'<div id="local-facts" class="local-facts">.*?</ul></div>', s, re.S)
        if not m:
            raise SystemExit('no local-facts in ' + slug)
        s = s[:m.end()] + '\n        ' + block + s[m.end():]
        # 2) FAQ: two local questions before the first shared question (which is the first <details open>)
        s = re.sub(r'<details data-local="1">.*?</details>\n\s*', '', s, flags=re.S)
        faq_html = ''.join('<details data-local="1"><summary>' + esc(q) + '</summary><p>' + esc(a) + '</p></details>\n        ' for q, a in c['faq'])
        i = s.index('<details open>')
        s = s[:i] + faq_html + s[i:]
        # 3) FAQPage JSON-LD
        def fix_ld(mm):
            d = json.loads(mm.group(1))
            if d.get('@type') != 'FAQPage':
                return mm.group(0)
            ents = [e for e in d['mainEntity'] if e['name'] not in {q for q, _ in c['faq']}]
            ents.extend({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in c['faq'])
            d['mainEntity'] = ents
            return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'
        s = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_ld, s, flags=re.S)
        open(p, 'w', encoding='utf-8').write(s)
        words = sum(len(t.split()) for t in c['paras']) + sum(len(q.split()) + len(a.split()) for q, a in c['faq'])
        print(slug, 'ok,', words, 'new words')


main()
