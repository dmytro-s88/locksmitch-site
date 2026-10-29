"""Adds the unique local text and two local FAQ questions to all 24 city pages.

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
    'sugarhill': {
        'h3': 'Sugar Hill, next door to our base',
        'paras': [
            'Sugar Hill is the closest town to us after Cumming, about 20 minutes down Peachtree Industrial Boulevard or GA-20. That is why a lockout here is a flat $75 in the daytime, the lowest price in our area. Most calls are quick ones: a car locked at the E Center, a fob that died in a driveway, keys left on the seat at the grocery store.',
            'Downtown Sugar Hill fills up on concert nights at The Bowl, and the lots around the E Center and Broad Street are where the fob ends up inside the car. We also come to Gary Pirkle Park on game days, Sugar Hill Golf Club, and the subdivisions off Level Creek Road, Whitehead Road and Suwanee Dam Road.',
            'Because it is so close, Sugar Hill is the easiest place to get a spare key before you need one. Pick a weekday or Saturday, Mitch comes to the driveway with the blanks and the programmer, and the new key is made and tested next to the one you already have.',
        ],
        'faq': [
            ('Why is a lockout in Sugar Hill only $75?', 'Sugar Hill is next door to our base, so the drive is short. A lockout is a flat $75 in the daytime and $125 after 9 pm with the $50 night charge. Key jobs are at the listed price.'),
            ('Can you make a spare key at my house in Sugar Hill?', 'Yes, Monday to Saturday. Text the year, make and model, get the price, and pick a time. Sunday is for lockouts and emergencies only.'),
        ],
    },
    'duluth': {
        'h3': 'Where we come in Duluth',
        'paras': [
            'Duluth is about 25 minutes from Cumming down Peachtree Industrial Boulevard or I-85. Event nights at Gas South Arena and the convention center in the Gas South District are when the lots fill up and the lockout calls start. Tell us the lot and the row and we come to the car, not to the front door.',
            'Pleasant Hill Road is the other busy stretch: the restaurants, markets and shopping centers between Satellite Boulevard and Buford Highway, and the apartment complexes behind them. For a gated complex, text the gate code or meet us at the entrance, and we drive straight to the parking spot.',
            'We also cover Downtown Duluth and the Town Green on festival weekends, Shorty Howell Park, Rogers Bridge Park on the Chattahoochee, and the homes and offices along Peachtree Industrial and Abbotts Bridge Road. Key jobs in Duluth are at the listed price with no extra trip fee.',
        ],
        'faq': [
            ('Locked out after a game or a concert at Gas South Arena?', 'Call us. A lockout in Duluth is a flat $100, plus $50 after 9 pm. Send the lot name and a photo of the car if you can, and Mitch texts the arrival time.'),
            ('Do you come to gated apartment complexes in Duluth?', 'Yes. Text the gate code, or meet us at the gate, and we come to the car in its spot. Keys get made right there in the lot.'),
        ],
    },
    'peachtreecorners': {
        'h3': 'Where we come in Peachtree Corners',
        'paras': [
            'Peachtree Corners is about 30 minutes from Cumming down Peachtree Parkway (GA-141). Most calls here come during the workday from the office campuses along Technology Parkway, Peachtree Corners Circle and the Curiosity Lab area: a fob that stopped working, a key locked in the car at lunch, a spare for a company car.',
            'In the evening it is The Forum on Peachtree Parkway and Peachtree Corners Town Center, where the restaurant lots are the classic place to lock a smart key inside. We also come to Simpsonwood Park and Jones Bridge Park on the river, and to the homes off Spalding Drive, Holcomb Bridge Road and Medlock Bridge Road.',
            'Peachtree Corners is past our no-fee zone, so a lockout is a flat $125 and key jobs add $50 for the drive. You get the full price by text before Mitch leaves, and nothing changes at the car.',
        ],
        'faq': [
            ('Can you program a fob I bought online while I am at work in Peachtree Corners?', 'Often, yes. Send a photo of the fob and the car’s year, make and model. We check that the fob fits your car, then program it in the office lot while you keep working.'),
            ('Why do key jobs in Peachtree Corners cost $50 more?', 'It covers the longer drive from Cumming. The key itself is the listed price. A lockout is a flat $125, and nights after 9 pm add $50.'),
        ],
    },
    'norcross': {
        'h3': 'Where we come in Norcross',
        'paras': [
            'Norcross is about 35 minutes from us down I-85 or Peachtree Industrial Boulevard. A lot of our Norcross work is with working vehicles: pickups, vans and work trucks for contractors and small shops along Jimmy Carter Boulevard, Buford Highway and the industrial parks off Best Friend Road and Oakbrook Parkway. A truck without a key is a lost workday, so we make the key where the truck is parked.',
            'Historic Downtown Norcross is the other side of town: the restaurants on South Peachtree Street, Thrasher Park and Lillian Webb Park, where weekend lockouts happen. We also cover the apartments and homes off Beaver Ruin Road, Indian Trail and Holcomb Bridge Road.',
            'Prefer Spanish? Text us in Spanish and you get the price and the confirmation in Spanish. In Norcross a lockout is a flat $125 and key jobs add $50 for the drive, with the full price sent by text before we leave.',
        ],
        'faq': [
            ('Do you make keys for work trucks and vans in Norcross?', 'Yes. Ford, Chevrolet, GMC, RAM and the common work vans are everyday jobs for us. If you have several vehicles, send the list and we price each one and do them in one visit.'),
            ('Can I text you in Spanish?', 'Yes. Text us in Spanish and we answer in Spanish, including the price and the arrival time.'),
        ],
    },
    'lawrenceville': {
        'h3': 'Where we come in Lawrenceville',
        'paras': [
            'Lawrenceville is about 40 minutes from Cumming by GA-20 or Sugarloaf Parkway, so we confirm the price and the arrival time by text before heading down. Key jobs here are still at the listed price with no extra trip fee, and a lockout is a flat $100.',
            'The hospital and the college bring a lot of calls: the parking decks at Northside Hospital Gwinnett, where a shift ends and the key is gone, and the Georgia Gwinnett College lots. Around the historic square and the Gwinnett Justice and Administration Center, it is usually a key locked in the car during a long day downtown.',
            'We also come to Coolray Field on Stripers game nights, the shopping along GA-316 and Sugarloaf Parkway, and the subdivisions off GA-20, GA-120 and Hurricane Shoals Road. Text us in Spanish if you prefer, and we answer in Spanish.',
        ],
        'faq': [
            ('Can you come to the Northside Hospital Gwinnett parking deck during my shift?', 'Yes. Send the deck, the level and the car, and leave the key work to us. Most keys take about an hour, and we text you when it is done.'),
            ('Is there an extra charge because Lawrenceville is 40 minutes away?', 'No. Key jobs in Lawrenceville are at the listed price with no trip fee. A lockout is a flat $100, plus $50 after 9 pm.'),
        ],
    },
    'sandysprings': {
        'h3': 'Where we come in Sandy Springs',
        'paras': [
            'Sandy Springs is about 35 minutes from Cumming straight down GA-400. The busiest place for us is the hospital cluster around Peachtree Dunwoody Road and I-285, with Northside Hospital Atlanta and Emory Saint Joseph’s: big parking decks, long shifts and keys that disappear somewhere in between. Tell us the deck and the level and we come to the car.',
            'Perimeter Center office towers and the MARTA park-and-ride lots at North Springs and Sandy Springs stations are the workday calls. In the evening it is City Springs and the restaurants along Roswell Road, and on weekends the river parks: Morgan Falls Overlook Park and the trail lots along the Chattahoochee.',
            'Sandy Springs is near the edge of our area, so a lockout is a flat $125 and key jobs add $50 for the drive. Mitch sends the full price and the arrival time by text before he leaves.',
        ],
        'faq': [
            ('My car is in the MARTA lot at North Springs and I lost the key. Can you help?', 'Yes. We come to the park-and-ride lot and make a new key at the car, so you don’t need a tow. If every key is lost, a second key for the same car is 50% off in the same visit.'),
            ('Can you work inside the hospital parking decks in Sandy Springs?', 'Yes. We drive in like any visitor. Text the deck name, the level and the row, and Mitch comes straight to the car.'),
        ],
    },
    'flowerybranch': {
        'h3': 'Where we come in Flowery Branch',
        'paras': [
            'Flowery Branch is about 35 minutes from us along I-985 or McEver Road. Lake Lanier is a big part of the calls here: Aqualand Marina, the boat ramps and parks along the shore, and the lake houses off McEver Road. A key dropped off the dock or a fob soaked in the lake is a summer weekend classic, and we make the new key right at the marina lot.',
            'Away from the water we come to downtown Flowery Branch along Main Street, the area around the Atlanta Falcons training facility, and the big neighborhoods: Sterling on the Lake and the subdivisions off Spout Springs Road and Atlanta Highway (GA-13).',
            'Key jobs in Flowery Branch are at the listed price with no extra trip fee, and a lockout is a flat $100. For a spare key, pick a weekday or Saturday and we come to the driveway.',
        ],
        'faq': [
            ('My key went in the lake at Aqualand Marina. Can you make one at the marina?', 'Yes. We come to the marina lot with the blanks and the programmer and make the key at the car, about an hour for most cars. No tow needed.'),
            ('Do you come to Sterling on the Lake and the neighborhoods off Spout Springs Road?', 'Yes. Send the address and, if there is a gate, the code. Spare keys are Monday to Saturday; lockouts any day, 24/7.'),
        ],
    },
    'dawsonville': {
        'h3': 'Where we come in Dawsonville',
        'paras': [
            'Dawsonville is about 30 minutes straight up GA-400 from Cumming. The North Georgia Premium Outlets lots are the most common lockout spot: shopping bags in one hand, the key on the seat. We come to the outlet lot and to the shopping and restaurants along GA-400 and GA-53.',
            'Dawson County is also a day-trip county. Hikers lose keys on the trails at Amicalola Falls State Park, boaters at War Hill Park on Lake Lanier, and drivers on track days at Atlanta Motorsports Park. These spots are farther out than town, so call and Mitch gives you a real arrival time.',
            'We also cover downtown Dawsonville around the courthouse and the homes off GA-9 and GA-53. Key jobs in Dawsonville are at the listed price with no extra trip fee, and a lockout is a flat $100.',
        ],
        'faq': [
            ('We lost the key hiking at Amicalola Falls. Can you come out there?', 'Yes. Call with the name of the lot. If cell signal is weak, a text with the lot name and the car is enough. We make the new key at the car, so it does not need a tow down the mountain.'),
            ('Do you come to Atlanta Motorsports Park?', 'Yes, to the parking area. Send the car and where it is parked. Lockouts are a flat $100, and key jobs are at the listed price.'),
        ],
    },
    'canton': {
        'h3': 'Where we come in Canton',
        'paras': [
            'Canton is about 40 minutes from Cumming straight across GA-20, one road the whole way. Riverstone Parkway and Canton Marketplace are where most of the shopping-lot lockouts happen, along with The Mill on Etowah and the restaurants downtown around the square.',
            'Northside Hospital Cherokee is a regular stop: staff and visitors in the parking lots, keys locked in or lost between shifts. We also come to Boling Park and the Etowah River access, and out east to Hickory Flat and the homes along GA-140 and East Cherokee Drive.',
            'Even with the longer drive, key jobs in Canton are at the listed price with no extra trip fee, and a lockout is a flat $100. For a spare key, text the car and pick a weekday or Saturday.',
        ],
        'faq': [
            ('How do you get to Canton from Cumming?', 'Straight across GA-20, about 40 minutes in normal traffic. Mitch texts the real arrival time when he confirms, and for a lockout, calling is faster than texting.'),
            ('Do you cover Hickory Flat and the area off GA-140?', 'Yes. Hickory Flat sits between Cumming and Canton. Send the address and the car, and you get the price by text first.'),
        ],
    },
    'woodstock': {
        'h3': 'Where we come in Woodstock',
        'paras': [
            'Woodstock is one of the longer drives for us, about 50 minutes from Cumming by GA-20 and I-575 or by GA-92. So we always confirm the price and the arrival time by text first. A lockout is a flat $125 and key jobs add $50 for the drive.',
            'Downtown Woodstock along Main Street is where the weekend lockouts come from: restaurant nights, the shops, events downtown. The Outlet Shoppes at Atlanta off I-575 is the other big lot. We also come to Towne Lake and the homes off Towne Lake Parkway, GA-92 and Arnold Mill Road.',
            'Trail lots are a regular call too, like Olde Rope Mill Park on the Little River. If the key is lost and not just locked inside, we make a new one at the car, so the car stays where it is.',
        ],
        'faq': [
            ('Is Woodstock in your service area?', 'Yes. It is about 50 minutes from Cumming, so Mitch confirms the price and timing by text before he leaves. A lockout is a flat $125; key jobs add $50 for the drive.'),
            ('Locked out in downtown Woodstock on a Friday night?', 'Call us. Lockouts are 24/7, and after 9 pm the night charge is $50. Tell us the street or the lot and Mitch texts the arrival time.'),
        ],
    },
    'dunwoody': {
        'h3': 'Where we come in Dunwoody',
        'paras': [
            'Dunwoody is about 35 minutes from Cumming down GA-400 to I-285. Perimeter Mall and the big lots and decks around it are the busiest spot: the key locked in the car at the mall, a fob dead in the deck. The office towers and hotels along Ashford Dunwoody Road and Perimeter Center Parkway are the workday calls.',
            'Dunwoody MARTA station and its parking are another regular stop, along with Dunwoody Village, Brook Run Park and the Georgia State University Perimeter College campus. We also come to the homes off Chamblee Dunwoody Road, Mount Vernon Road and Tilly Mill Road.',
            'Key jobs in Dunwoody are at the listed price with no extra trip fee, and a lockout is a flat $100. Mitch texts the price first, then the arrival time.',
        ],
        'faq': [
            ('Locked out at Perimeter Mall. What should I tell you?', 'The deck or the lot, the level and the nearest store entrance. Send a photo of the car if you can. A lockout is a flat $100, plus $50 after 9 pm.'),
            ('Is there a trip charge to come to Dunwoody?', 'No. Key jobs in Dunwoody are at the listed price with no trip fee, and you get the exact price by text before anyone drives out.'),
        ],
    },
    'doraville': {
        'h3': 'Where we come in Doraville',
        'paras': [
            'Doraville is about 40 minutes from Cumming by I-85 or Peachtree Industrial Boulevard. Buford Highway is the heart of it for us: the restaurant and market lots, the Buford Highway Farmers Market, and the small businesses whose vans and trucks need a spare key before the old one breaks.',
            'The old GM plant site is now Assembly, with film studios and new development around Assembly Yards, and the Doraville MARTA station sits next to it. We come to the public lots and park-and-ride, and to the homes and apartments off New Peachtree Road, Chamblee Tucker Road and Shallowford Road.',
            'Text us in Spanish if you prefer and we answer in Spanish. In Doraville a lockout is a flat $125 and key jobs add $50 for the drive; the full price comes by text before we leave.',
        ],
        'faq': [
            ('Can you come to the Buford Highway Farmers Market lot?', 'Yes. Tell us which side of the lot and send the car. Lockouts are a flat $125; if the key is lost, we make a new one right there at the car.'),
            ('Do you come to the Assembly studio area?', 'Yes, to the public lots and the MARTA park-and-ride. For a lot with security at the gate, put our name on the list and tell us where the car is.'),
        ],
    },
    'braselton': {
        'h3': 'Where we come in Braselton',
        'paras': [
            'Braselton is at the far east edge of our area, about 45 minutes from Cumming by GA-20 and I-85. So we confirm the price and the timing by text before heading out. A lockout is a flat $125 and key jobs add $50 for the drive.',
            'Race weekends at Michelin Raceway Road Atlanta bring crowds and big parking fields, and Chateau Elan brings hotel guests, golfers and wedding parties. A key locked in a car at the resort or lost somewhere in a race lot is exactly the call we take: we come to the car with everything on board.',
            'During the week it is NGMC Braselton hospital, the distribution centers along I-85 and GA-211, downtown Braselton and the neighborhoods off GA-124 and GA-53. Fleet and work vehicles are welcome: several keys in one visit.',
        ],
        'faq': [
            ('Lost a key on a race weekend at Road Atlanta?', 'Call us with the lot and the car. Race weekends mean traffic on GA-53, so Mitch texts a real arrival time. We make the new key at the car, no tow needed.'),
            ('Do you come to guests at Chateau Elan?', 'Yes, to the hotel and resort parking. Text the car and where it is parked; a lockout is a flat $125, plus $50 after 9 pm.'),
        ],
    },
    'marietta': {
        'h3': 'Coming to Marietta',
        'paras': [
            'Marietta is outside our usual 40-mile area, about 55 minutes from Cumming by GA-400 and I-285 or by Roswell Road (GA-120). We still come, but Mitch quotes each job by text first, including the drive, and gives you a time that fits the schedule.',
            'The jobs that make the most sense here are the ones you can plan: a spare key for a car with only one key left, a smart key for a European car, a key for a car you just bought. Marietta Square, Wellstar Kennestone Hospital, Life University and the Kennesaw State Marietta campus are all places we come to.',
            'East Cobb is the closest part of Marietta to us, along Roswell Road, Johnson Ferry Road and Lower Roswell Road. For a lockout anywhere in Marietta, call: Mitch tells you right away if and when he can come.',
        ],
        'faq': [
            ('Do you come to Marietta?', 'Yes, as a quoted trip. Text the year, make and model and the address, and Mitch sends the full price and the time he can be there before anything is booked.'),
            ('Can I schedule a spare key in East Cobb ahead of time?', 'Yes. Pick a weekday or Saturday, get the price by text, and Mitch comes to your driveway. A spare made while you still have one key costs much less than replacing a lost last key.'),
        ],
    },
    'kennesaw': {
        'h3': 'Coming to Kennesaw',
        'paras': [
            'Kennesaw is about an hour from Cumming by I-575 or I-75, outside our usual 40-mile area. We come for quoted jobs: text the car and the address, and Mitch tells you the full price and when he can be there before anything is booked.',
            'Kennesaw State University is a big part of the calls: students with one key for an older car, or no key at all after a weekend. We come to the campus lots and the apartments around Chastain Road and Frey Road. Town Center at Cobb and the shopping along Barrett Parkway are the other regular spots.',
            'Weekend trips bring their own calls: the trail lots at Kennesaw Mountain National Battlefield Park and the Southern Museum in downtown Kennesaw. If you are locked out, call instead of texting, and Mitch tells you right away if he can come.',
        ],
        'faq': [
            ('I am a KSU student and lost my only key. Can you help?', 'Yes. Text the year, make and model and where the car is parked. Mitch quotes the new key and the drive first. If every key is lost, a second key for the same car is 50% off in the same visit.'),
            ('Lost the key on the trail at Kennesaw Mountain?', 'Call us with the trailhead lot and the car. Kennesaw is a long drive for us, so Mitch gives you a real arrival time and the price before he leaves.'),
        ],
    },
    'smyrna': {
        'h3': 'Where we come in Smyrna',
        'paras': [
            'Smyrna is near the edge of our area, about 50 minutes from Cumming by GA-400 and I-285. So a lockout here is a flat $125, key jobs add $50 for the drive, and Mitch confirms the price and the timing by text first.',
            'Game days at The Battery Atlanta next door fill every lot and garage around Cumberland, and Cumberland Mall and the office towers around it are the workday calls. Downtown Smyrna is Smyrna Market Village and the restaurants around it, with Taylor-Brawner Park nearby.',
            'Most home calls come from the neighborhoods off Spring Road, Concord Road, Atlanta Road and South Cobb Drive. A spare key on a weekday or Saturday is the easiest job to plan here: you pick the time, we come to the driveway.',
        ],
        'faq': [
            ('Locked out after a Braves game near The Battery?', 'Call us with the garage or lot and the car. Game-night traffic around I-285 and Cobb Parkway is heavy, so Mitch texts a real arrival time. A lockout is a flat $125, plus $50 after 9 pm.'),
            ('Why do key jobs in Smyrna cost $50 more?', 'Smyrna is about 50 minutes from our base, and the $50 covers the drive. The key itself is the listed price, and you get the total by text before we leave.'),
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
