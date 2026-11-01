"""Car-locksmith titles and a unique meta description on all 24 city pages.

Places in the descriptions come from the local text in city_content.py. Rerun is safe.
    python3 -I tools/city_meta.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DESCRIPTIONS = {
    'cumming': 'Lost your car keys or locked out in Cumming? Mitch starts his day here and comes to Halcyon, The Collection, Lake Lanier or your driveway. 24/7.',
    'alpharetta': 'Lost your car keys in Alpharetta? Mitch comes to Avalon, North Point, Windward Parkway or your driveway and makes a new key at your car. 24/7.',
    'johnscreek': 'Need a spare or lost car key in Johns Creek? Mitch comes to your driveway off Medlock Bridge or State Bridge and makes it at your car. 24/7.',
    'milton': 'Lost your car keys in Milton? Mitch comes to Crabapple or up your driveway off Birmingham Highway and makes a new key at your car. 24/7.',
    'roswell': 'Locked out on Canton Street or lost your keys in Roswell? Mitch comes to Historic Roswell, Holcomb Bridge or your driveway. Keys made on site, 24/7.',
    'buford': 'Locked out at the Mall of Georgia or lost your keys in Buford? Mitch comes to your car, at the lot or at the lake, and makes a new key on site. 24/7.',
    'suwanee': 'Locked out at Suwanee Town Center or lost your car keys? Mitch comes to the lot, the office park or your driveway and makes a new key on site. 24/7.',
    'gainesville': 'Lost your car keys in Gainesville? Mitch comes to the downtown square, Northeast Georgia Medical Center, Brenau or your driveway. 24/7.',
    'sugarhill': 'Locked out in Sugar Hill? A daytime lockout is a flat $75. Mitch also makes new car keys at the E Center, the store lot or your driveway. 24/7.',
    'duluth': 'Locked out at Gas South Arena or lost your car keys in Duluth? Mitch comes to your lot and row, or to your driveway. Keys made on site, 24/7.',
    'peachtreecorners': 'Fob died or keys locked in the car in Peachtree Corners? Mitch comes to your office lot on Technology Parkway or your driveway. 24/7.',
    'norcross': 'Car, pickup or work van keys lost in Norcross? Mitch comes to your shop off Jimmy Carter Boulevard or Buford Highway. Keys made on site, 24/7.',
    'lawrenceville': 'Lost your car keys in Lawrenceville? Mitch comes to the hospital decks, the college or your driveway, with no trip fee on key jobs. 24/7.',
    'sandysprings': 'Lost your keys in a Sandy Springs parking deck? Mitch comes to the hospitals on Peachtree Dunwoody, your office or your driveway. 24/7.',
    'flowerybranch': 'Keys lost at Aqualand Marina or in Flowery Branch? Mitch comes to the boat ramp, the lake house or your driveway and makes a new key on site. 24/7.',
    'dawsonville': 'Locked out at the North Georgia Premium Outlets or lost your keys in Dawsonville? Mitch comes to your car and makes a new key on site. 24/7.',
    'canton': 'Locked out at Riverstone or lost your car keys in Canton? Mitch comes to The Mill on Etowah, Northside Cherokee or your driveway. 24/7.',
    'woodstock': 'Locked out in downtown Woodstock or lost your car keys? Mitch confirms the price by text, then comes to your car. New keys made on site, 24/7.',
    'dunwoody': 'Locked out at Perimeter Mall or lost your keys in Dunwoody? Mitch comes to the deck, your office on Ashford Dunwoody or your driveway. 24/7.',
    'doraville': 'Lost your car or van keys in Doraville? Mitch comes to Buford Highway, Assembly or your driveway and makes a new key at your car. 24/7.',
    'braselton': 'Locked out at Road Atlanta or Chateau Elan, or lost your keys in Braselton? Mitch confirms the price by text and comes to your car. 24/7.',
    'marietta': 'Need a spare or new car key in Marietta? Text the car and the address. Mitch quotes the full price with the drive and comes at a set time.',
    'kennesaw': 'Need a car key in Kennesaw or at KSU? Text the car and the address. Mitch quotes the full price and the time before anything is booked.',
    'smyrna': 'Locked out at The Battery or lost your car keys in Smyrna? Mitch confirms the price by text and comes to your car. New keys made on site, 24/7.',
}


def main():
    for city, desc in DESCRIPTIONS.items():
        assert len(desc) <= 155 and '—' not in desc and '–' not in desc, (city, len(desc))
        path = os.path.join(ROOT, city, 'index.html')
        html = open(path, encoding='utf-8').read()
        html = re.sub(r'Mobile Auto Locksmith in ([^|"<]+), GA \| LocksMitch', r'Car Locksmith in \1, GA, 24/7 | LocksMitch', html)
        html, n = re.subn(r'(<meta (?:name="description"|property="og:description") content=")[^"]*', lambda m: m.group(1) + desc, html)
        assert n == 2, (city, n)
        open(path, 'w', encoding='utf-8').write(html)
    print(len(DESCRIPTIONS), 'city pages updated')


if __name__ == '__main__':
    main()
