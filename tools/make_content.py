"""Adds a make-specific text block and two make-specific FAQ questions to the make pages.

Each make page gets a "local-more" block after the "models we see most often" list (the key systems of that make,
the usual situations, what to text us) and two questions at the top of the FAQ, mirrored into the FAQPage JSON-LD.
Claims stay within what each page already promises (year limits, "quoted by model"). Rerun is safe: an existing
block is replaced.
    python3 -I tools/make_content.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAKES = {
    'toyota': {
        'h3': 'Toyota keys, generation by generation',
        'paras': [
            "Most Toyotas we see use one of three keys. Older Camry, Corolla and Tacoma keys are a metal key with a chip in the black head. From about 2010 the key often has a letter stamped on the blade, G or H, which tells us which chip it needs. Push-to-start models like the newer RAV4, Highlander and Camry use a smart key that stays in your pocket.",
            "The jobs we do most for Toyota owners: a second key for a Tacoma or Tundra that came with only one, a spare for a new driver in the family Corolla, and a smart key for a Sienna or Highlander when one of the two went missing. A spare made while you still have a working key is the quick, cheaper version of the job.",
            "Text us the year and model, whether it starts with a button or a turn of the key, and whether you still have one key that works. On some of the newest Toyota models an all-keys-lost job takes extra steps, so we confirm the exact car before anyone drives out.",
        ],
        'faq': [
            ("My Toyota key has a G or H stamped on the blade. Does that matter?", "Yes, it tells us which chip the key needs. Send a photo of the key or just the year and model, and we bring the right one. A key with the wrong chip will open the doors but won't start the car."),
            ("Can you make a second key for a Tacoma or Tundra that came with only one?", "Yes. That's one of our most common Toyota jobs. We cut and program the new key at the truck, usually in under an hour, and both keys keep working."),
        ],
    },
    'lexus': {
        'h3': 'Lexus smart keys and the hidden blade',
        'paras': [
            "Almost every Lexus from the last fifteen years starts with a smart key: the car senses the key in your pocket and the button starts the engine. Inside each smart key is a small metal blade for the driver's door, which most owners never see until the battery dies. Older RX and ES models still use a remote head key with the buttons on the key itself.",
            "When a Lexus says \"key not detected\", the usual cause is a weak coin battery in the fob. On many models you can still start the car by touching the key to the start button, logo side first. If that works, a new battery may be all you need. If it doesn't, the key itself may need replacing or reprogramming.",
            "We also replace worn smart key cases and broken emergency blades, so a key that still works but falls apart doesn't need a new chip. Text us the year and model, and say whether the problem is the case, the battery or the key not starting the car.",
        ],
        'faq': [
            ("My Lexus smart key case is cracked but the key still works. Do I need a new key?", "Usually not. We can move the working electronics into a new case and fit a new emergency blade, which costs much less than a new programmed key. Send a photo and the year and model first."),
            ("Where is the emergency key in my Lexus smart key?", "There's a small release on the fob; slide it and the metal blade comes out. It opens the driver's door when the battery is dead. If your blade is missing or broken, we can cut a new one to your car."),
        ],
    },
    'honda': {
        'h3': 'Honda and Acura keys we see most',
        'paras': [
            "Most Hondas from the mid-2000s on use a laser-cut blade, the kind with a groove down the middle instead of teeth on the edge. It is cut on a machine to your car's code, not on a hardware store grinder. Civic, Accord and CR-V went from chip keys to remote head keys, and the newer push-to-start models use a smart key.",
            "Honda is the family car of North Atlanta, so many of our Honda calls are a spare: a second key for a teen driving the Civic, a key for the Odyssey when the family is down to one, a smart key for a Pilot or Acura MDX bought used with a single key. Making the spare now costs much less than an all-keys-lost visit later.",
            "Send us the year and model and whether it's a turn key or push-to-start. A few of the newest Honda and Acura models need steps we confirm first, so you get a yes or no and a price by text before anyone drives out.",
        ],
        'faq': [
            ("Can a hardware store copy my Honda key?", "A store can sometimes copy the metal part, but most Honda keys from the mid-2000s on also need a programmed chip to start the car, and many need a laser-cut blade. We cut and program the key at your car, so it opens the doors and starts the engine."),
            ("We bought a used Pilot (or Acura MDX) with only one key. What should we do?", "Get a second key made while the one you have still works. It's a regular spare key job at your driveway, much cheaper than an all-keys-lost visit if the only key goes missing."),
        ],
    },
    'ford': {
        'h3': 'Ford PATS keys, flip keys and Intelligent Access',
        'paras': [
            "Ford's anti-theft system is called PATS: a chip in the key that the car must recognize before the engine runs. Older F-150, Explorer and Escape keys are plain chip keys or remote head keys, then came flip keys on cars like the Fusion and Escape, and push-to-start models use Intelligent Access smart keys.",
            "On many Fords the programming has a built-in security wait of about ten minutes, and some models need it twice. That's normal and part of why an all-keys-lost job takes about an hour. Ford 2021 and newer models are confirmed per car before we quote, because the newer systems vary by model.",
            "Ford trucks are work vehicles here, so we often make keys for a crew: a spare for each driver, or keys for several F-150 and F-250 trucks in one visit. Text us the year, model and how many keys you need, and we bring blanks for all of them.",
        ],
        'faq': [
            ("Can I program a new Ford key myself?", "On many older Fords, yes, but only if you already have two working keys: the car lets you add a third. With one key or none, it takes programming equipment, and that's the job we do at your car."),
            ("Can you make keys for several work trucks in one visit?", "Yes. Send the year and model of each truck. We price each one by text, bring the right blanks for all of them and do them back to back at your yard or job site."),
        ],
    },
    'chevrolet-gmc': {
        'h3': 'GM keys: Silverado to Escalade',
        'paras': [
            "Chevrolet, GMC, Buick and Cadillac use a handful of key types: plain chip keys on older trucks, flip keys with the remote built in on models like the Silverado, Sierra and Equinox, and smart keys on push-to-start models such as the newer Tahoe, Yukon and Escalade.",
            "When all keys are lost, many GM vehicles need a security relearn: the car makes us wait between steps, sometimes ten minutes, sometimes three rounds of ten. It's built into the car, not something we can skip, and it's included in the time we quote. A spare made while you still have a working key is much faster.",
            "Trucks and family SUVs are most of our GM work: keys for a Silverado or Sierra used for work, a spare smart key for a Tahoe or Suburban. Text us the year, model and trim, since the key often depends on whether the truck has push-to-start.",
        ],
        'faq': [
            ("Why does a Silverado or Tahoe key take a while to program?", "Many GM vehicles have a built-in security wait during programming, often ten minutes and sometimes thirty. The car sets that timer, not us. We tell you the expected time when we quote."),
            ("My GM flip key still starts the truck but the blade won't stay open. Do I need a new key?", "Often not. A broken flip mechanism or a worn case can usually be fixed or replaced while keeping your programmed chip and remote. Send a photo and the year and model."),
        ],
    },
    'jeep-dodge-ram': {
        'h3': 'Fobiks, tip keys and Jeep smart keys',
        'paras': [
            "Many Jeep, Dodge, Chrysler and RAM vehicles from about 2008 to 2018 use a fobik: a plastic key that plugs into a slot in the dash, with a metal blade hidden inside. Older Wranglers and RAM trucks use a regular chip key with a remote head, and the newer Grand Cherokee, Wrangler, Durango and Pacifica use push-to-start smart keys.",
            "Newer models from these brands have a security gateway in front of the diagnostic port, so programming goes through it with the right connection. We check the year first and come with what that car needs. That's also why all keys lost on these makes is quoted by year: older cars are quick, newer ones take more steps.",
            "Typical calls: a second fobik for a Grand Cherokee or Durango bought with one key, a key for a work RAM 1500 or 2500, a Charger or Challenger key lost on a night out. Text us the year and model, and whether the key plugs into the dash or stays in your pocket.",
        ],
        'faq': [
            ("What is a fobik and can you make one?", "It's the plastic key that slides into the dash on many Jeep, Dodge, Chrysler and RAM vehicles from about 2008 to 2018. Yes, we cut the hidden blade and program the fobik at your car."),
            ("Does a 2018 or newer Jeep or RAM take longer to program?", "A little. Newer models have a security gateway in front of the diagnostic port, so we connect through it before programming. We confirm your year and model first and quote the full job upfront."),
        ],
    },
    'hyundai': {
        'h3': 'Hyundai and Genesis keys and the PIN code',
        'paras': [
            "To program a key, a Hyundai needs a security PIN that belongs to that car. As a NASTF-certified locksmith, we get it through manufacturer data access. Older Elantra, Sonata and Tucson models use a chip key or a flip key with the remote built in. Newer and higher trims, the Santa Fe, Palisade and Genesis models, use a smart key with push-to-start.",
            "Hyundai models from 2022 and newer use a newer immobilizer, which adds to the price; the exact amount is on the price list above. Older models are a straightforward visit: we cut the key to your car's code, program it with the PIN and test it before you pay.",
            "Text us the year, model and trim, and whether you have a flip key or a smart key. If your car was broken into or the steering column was damaged, send a photo too, so we know what we're looking at before we drive out.",
        ],
        'faq': [
            ("Why do you need a PIN code to program a Hyundai key?", "Hyundai and Genesis lock key programming behind a PIN tied to the car. We retrieve it through our manufacturer data access as a NASTF-certified locksmith, so you don't need to get it from the dealer."),
            ("Do you make keys for Genesis models?", "Yes, the Genesis G70 and GV70 are on our list. They use smart keys; send the year and model and we confirm the key and the price before anyone drives out."),
        ],
    },
    'kia': {
        'h3': 'Kia keys: flip keys to Telluride smart keys',
        'paras': [
            "Kia keys come in three kinds: a plain chip key on older models, a flip key with the remote built in on many Forte, Optima, Soul and Sportage models, and a smart key on push-to-start cars like the Telluride, Sorento and K5. Like Hyundai, a Kia needs its security PIN to program a key, and we retrieve it ourselves.",
            "Kia models from 2022 and newer use a newer immobilizer that costs more to program; the added amount is on the price list above. The Optima became the K5 in 2021, so tell us the exact year, it changes the key.",
            "When we program new keys on most Kia models, any lost key stops starting the car, which matters if a key was stolen with your bag. Text us the year and model and whether you still have a working key.",
        ],
        'faq': [
            ("My Kia key was stolen. Can you make the old one stop working?", "On most Kia models, yes. When we program new keys, the car forgets the old ones, so the stolen key won't start it. Send the year and model and we confirm for your car."),
            ("Is a Telluride smart key different from a Sorento one?", "Often, yes. Kia smart keys differ by model and year, even when they look alike. Send the year and model and we bring the right key, programmed at your car."),
        ],
    },
    'nissan': {
        'h3': 'Nissan Intelligent Key and older chip keys',
        'paras': [
            "Nissan calls its push-to-start smart key the Intelligent Key; you'll find it on most Altima, Rogue, Maxima, Murano and Pathfinder models, and on Infiniti. Older Sentra, Frontier and Altima models use a chip key or a remote head key. Like several makes, Nissan uses a security code for programming, which we read or retrieve for your car.",
            "\"Key not detected\" on a Nissan is often just a weak fob battery. On many models you can still start the car by holding the fob right against the start button while you press it. If that doesn't work, the key may need replacing.",
            "Some Rogue and Sentra years take extra steps or aren't a fit for on-site work, so send us the year and model first. You get a clear yes or no and a price by text before anyone drives out.",
        ],
        'faq': [
            ("My Nissan says key not detected. What can I try first?", "Hold the fob right against the start button and press the button with it. On many Nissans that starts the car even with a weak battery. Then replace the fob battery. If it still isn't recognized, send us the year and model."),
            ("Do you make Infiniti keys?", "Yes, Infiniti uses the same family of Intelligent Keys as Nissan. The Q50 and QX60 are among the ones we see most. Send the year and model and we confirm before we come out."),
        ],
    },
    'mitsubishi': {
        'h3': 'Mitsubishi keys and push-to-start Outlanders',
        'paras': [
            "Mitsubishi keeps it fairly simple: chip keys and remote head keys on the Mirage, Lancer, Galant and older Outlanders, and a smart key on push-to-start Outlander, Outlander Sport and Eclipse Cross models. Many Mitsubishi keys need a security code for programming, which we handle on our side.",
            "A Mirage or an older Lancer is often a commuter or a first car, so a spare key matters more than people think: if the only key is lost, the job turns into all keys lost and costs more. We cut and program the spare at your car in about an hour.",
            "Text us the year and model and whether the car starts with a button or a key. Mitsubishi dealers are few and far between in North Atlanta, so doing it at your car saves a long drive.",
        ],
        'faq': [
            ("Is there a Mitsubishi dealer near me for keys, or can you do it?", "There are only a few Mitsubishi dealers around Atlanta. We cut and program Mitsubishi keys at your car, so you don't have to drive or tow it to one."),
            ("Can you make a spare key for a Mirage?", "Yes. Most Mirage and Mirage G4 cars use a chip key or remote head key. A spare made while you still have a working key is the quickest and cheapest version of the job."),
        ],
    },
    'subaru': {
        'h3': 'Subaru keys and why all keys lost costs more',
        'paras': [
            "Subaru keys went from chip keys to remote head keys, and newer Outback, Forester, Crosstrek and Ascent trims use a smart key with push-to-start. If you still have a working key, adding a spare is a normal visit.",
            "All keys lost costs more on a Subaru than on most Japanese cars, as you can see in the price above. On many years the car needs a longer, more involved programming procedure when no working key is left. That's the main reason we tell every Subaru owner to get a spare made early.",
            "Subarus go where the trails are, and North Georgia trailheads are a classic place to lose a key. Tell us the trailhead or the parking lot, plus the year and model, and whether it's push-to-start. If you're out of cell range, text as soon as you have signal.",
        ],
        'faq': [
            ("Why is all keys lost more expensive on a Subaru?", "On many Subaru years, programming a key with no working key left takes a longer and more involved procedure than a spare. The price above reflects that. A spare made while you have a key avoids it."),
            ("I lost my Subaru key at a trailhead. Can you come out there?", "If a car can park there, yes. Send the trailhead or lot name and the year and model. Some North Georgia trailheads are a long drive, so call and we tell you the arrival time before heading out."),
        ],
    },
    'mazda': {
        'h3': 'Mazda flip keys and keyless entry',
        'paras': [
            "Mazda uses chip keys on older models, flip keys with the remote built in on many Mazda3, Mazda6 and CX-5 models, and smart keys for push-to-start on most newer cars. Mazda models from 2022 and newer use a newer system that adds to the price, as shown above.",
            "The CX-5 and Mazda3 are the Mazdas we see most. A common call is a flip key that still starts the car but the remote stopped working or the case broke. Sometimes a battery or a new case fixes it, sometimes the key needs reprogramming. Send a photo and we'll tell you which.",
            "MX-5 Miata owners: with the top up and the keys inside, it's a normal lockout: we open it with automotive lockout tools, not by force. Text us the year and model, and whether the key is a flip key or a push-to-start fob.",
        ],
        'faq': [
            ("My Mazda flip key still starts the car but the buttons don't work. What now?", "Try a new battery in the fob first. If the buttons still don't work, the remote may need reprogramming or the case may be broken. Send a photo and the year and model and we tell you what it needs before we come out."),
            ("Why does a 2022 or newer Mazda key cost more?", "Newer Mazda models use a newer key system that takes more work to program. The added amount is on the price list above, and we confirm the exact price for your car by text."),
        ],
    },
    'bmw': {
        'h3': 'BMW and Mini keys, 2005 to 2019',
        'paras': [
            "In BMW and Mini cars from our years, the key data lives in a module, not in the key. On older models it's a module called CAS; on many later 3 Series, X-models and Minis it's FEM or BDC. A new key is coded to that module, which is why BMW keys take more work than most cars.",
            "Many BMWs from these years have Comfort Access, where the car unlocks as you touch the handle. Others use a remote key you press. With a working key, adding a spare is fairly quick. With every key lost, we often need to read the module, which can take a couple of hours on some models.",
            "Text us the year, model and whether you have Comfort Access, plus whether you still have a working key. We cover 2005 to 2019 and confirm your exact car before anyone drives out.",
        ],
        'faq': [
            ("Why are BMW keys more expensive than Toyota or Honda keys?", "On a BMW the key is coded to a module in the car (CAS, FEM or BDC), and the key blanks cost more. It takes more equipment and more time than a typical Japanese car. You get the exact price by text before we come out."),
            ("Do you make keys for Mini Cooper and Countryman?", "Yes, Mini uses BMW's key systems and the same price range. We cover 2005 to 2019 model years; send the year and model and we confirm."),
        ],
    },
    'mercedes': {
        'h3': 'Mercedes-Benz SmartKey, 2005 to 2013',
        'paras': [
            "Mercedes-Benz cars from 2005 to 2013 use the SmartKey, the chrome key that slides into the ignition, or Keyless Go on some models. The car checks the key through its ignition module, and a new key is made to match that module. That's why a Mercedes key takes more work and starts at a higher price.",
            "For older C-Class, E-Class and ML models and Sprinter vans from those years, we can usually add a key when you still have one that works. With every key lost, the job depends a lot on the model, and some parts may need to be ordered first. We tell you the timeline upfront.",
            "Text us the year and model, and whether the key goes into the ignition or stays in your pocket. We work on Mercedes-Benz from 2005 to 2013, so we'll tell you right away if your car is outside those years.",
        ],
        'faq': [
            ("Can you make a key for a Sprinter van?", "For Sprinter vans from 2005 to 2013, often yes. Send the year and tell us whether you still have a working key. We confirm the job and the timeline before anyone drives out."),
            ("Why does my Mercedes key slide into the dash instead of turning?", "That's the SmartKey design Mercedes used for years. The car reads the key through its ignition module. If the key stopped being recognized, it may be the key or the module; send the year and model and what happened."),
        ],
    },
    'volkswagen-audi': {
        'h3': 'Volkswagen flip keys and Audi keys',
        'paras': [
            "Most Volkswagens from 2005 to 2016 use a flip key: the blade folds into the remote. Jetta, Passat, Golf, GTI and Tiguan keys from those years are a regular job for us. Inside, the car's immobilizer has gone through several generations, and the newest ones take more steps, so we confirm the exact year first.",
            "The most common VW call is a flip key that broke at the hinge but still starts the car. A new shell or a new flip key often fixes it, and keeping the working chip may save money. Audi keys are quoted per car, because the key system varies a lot between the A3, A4, Q5 and Q7 and across years.",
            "Text us the year and model, and whether you have a flip key or a keyless smart key. You get a clear yes or no and a price before anyone drives out.",
        ],
        'faq': [
            ("My VW flip key broke at the hinge. Do I need a whole new key?", "Not always. If the key still starts the car, a new shell or flip mechanism can often keep your working chip and remote. Send a photo and the year and model and we tell you the cheapest option."),
            ("Why is Audi quoted per car?", "Audi key systems differ a lot by model and year, so one starting price wouldn't be honest. Send the year and model and we text you the exact price."),
        ],
    },
    'land-rover-jaguar': {
        'h3': 'Range Rover and Jaguar smart keys',
        'paras': [
            "Range Rover, Range Rover Sport, Evoque, Discovery and Jaguar models like the F-Pace, XF and F-Type use smart keys: the car unlocks and starts with the key in your pocket. The keys are expensive at the dealer, so a spare is one of the most common jobs we do for these cars.",
            "When the car doesn't detect the key, check the fob battery first. Many Land Rover and Jaguar models also have a backup spot where the car reads the key even with a dead battery; your owner's manual shows where. If the key still isn't recognized, it may need replacing.",
            "Text us the year and model and whether you still have a working key. Key systems differ between generations, so we confirm your exact car before anyone drives out, and all keys lost is quoted by model.",
        ],
        'faq': [
            ("My Range Rover says key not found but the fob is in the car. What can I do?", "Replace the fob battery first. Many models also have a backup spot where the car can read the key with a dead battery; the owner's manual shows where. If that doesn't help, send us the year and model."),
            ("Is a spare Range Rover key cheaper from you than from the dealer?", "Usually, and we make it at your car without a dealer visit. Send the year and model and we text you the exact price first."),
        ],
    },
    'volvo': {
        'h3': 'Volvo keys depend on the model',
        'paras': [
            "Volvo keys changed a lot over the years: remote keys with a blade on older models, keyless smart keys on the newer XC90, XC60 and XC40, and different systems in between. Because the work and the parts differ so much, every Volvo key is quoted by model.",
            "Some Volvo keys have to be ordered for your car before we can come out, so a spare made early is much easier than an emergency. If your Volvo key still works, now is the right time to ask for a second one.",
            "Text us the year and model, whether the car is keyless, and whether you still have a working key. We tell you what's possible for your car and the price before anyone drives out.",
        ],
        'faq': [
            ("Why do Volvo keys sometimes need to be ordered?", "Many Volvo keys are made for a specific car, so the key may need to be ordered ahead. We tell you the timeline and the price before booking."),
            ("Can you open my Volvo if the keys are locked inside?", "Yes. A lockout is a separate, faster job than making a key. We open the car with automotive lockout tools, not by force."),
        ],
    },
    'porsche': {
        'h3': 'Porsche keys are made to order',
        'paras': [
            "Newer Porsche keys are shaped like the car, and the Cayenne, Macan and Panamera use them with keyless entry on many trims. Older 911, Boxster and Cayman models use a remote key with a blade. Porsche keys are quoted by model because the key and the work vary a lot by year.",
            "For many Porsches only an original key works, and it often has to be ordered for your car before we can program it. If you have one working key left, ordering the second one now saves a stressful wait later.",
            "Text us the year and model and whether you still have a working key. We tell you what's possible, whether a key needs ordering, and the price before anyone drives out.",
        ],
        'faq': [
            ("How long does it take to get a Porsche key?", "It depends on the model. Some keys we can program right away, others have to be ordered for your car first. We tell you the timeline and the price before booking."),
            ("My Porsche key battery died. Can I still get in?", "Most Porsche keys hide a small mechanical blade for the driver's door. If the car still doesn't detect the key after a fresh battery, send us the year and model."),
        ],
    },
    'ferrari': {
        'h3': 'Ferrari keys, quoted per car',
        'paras': [
            "Every Ferrari key job is quoted per car. The key and the steps differ between the 458, 488, F8, Roma, Portofino and newer models, and many keys have to be ordered for your car first. Mitch confirms what's possible and the price by text before anything else happens.",
            "Ferraris often sit for weeks between drives, and a weak car battery is a common reason a key suddenly \"stops working\" or the car won't unlock. Tell us if the car has been sitting; it changes what we bring.",
            "We come to your garage or wherever the car is parked, so it doesn't need to be trailered to a dealer. Send the year and model and whether you still have a working key.",
        ],
        'faq': [
            ("My Ferrari won't unlock after sitting in the garage. Is it the key?", "Not always. A weak car battery after weeks of sitting is a common cause. Tell us how long the car has been parked and the year and model, and we tell you what we'll check first."),
            ("Do you come to my garage for a Ferrari key?", "Yes. We work where the car is parked, so it doesn't need to be trailered anywhere. We confirm the key and the price by text first."),
        ],
    },
    'maserati': {
        'h3': 'Maserati keys, quoted per car',
        'paras': [
            "Maserati key jobs are quoted per car, because the key and the work differ between the Ghibli, Levante, Quattroporte, GranTurismo and the newer Grecale and MC20. Many Maserati keys have to be ordered for your car before we can program them. Mitch confirms what's possible and the price by text first.",
            "Many used Maseratis are sold with a single key. If that's you, getting the second key while the first one works is far easier than an all-keys-lost job later, and it's the most common Maserati request we get.",
            "Send us the year and model, and say whether you still have a working key. We come to wherever the car is parked.",
        ],
        'faq': [
            ("I bought a used Maserati with one key. Can you make a second?", "Often, yes. Send the year and model. Some keys have to be ordered for your car first, and we tell you the timeline and the price before booking."),
            ("Does a Ghibli key work for a Levante?", "No. Keys are made for a specific car and differ between models and years. Send your exact year and model so we order or bring the right key."),
        ],
    },
}


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def typo(t):
    # curly apostrophes and quotes, to match the rest of the site
    t = re.sub(r'"([^"]*)"', '“\\1”', t)
    return t.replace("'", '’')


def main():
    for slug, c in MAKES.items():
        p = os.path.join(ROOT, slug + '-key-replacement', 'index.html')
        s = open(p, encoding='utf-8').read()
        paras = [typo(t) for t in c['paras']]
        faq = [(typo(q), typo(a)) for q, a in c['faq']]
        for t in paras + [x for qa in faq for x in qa] + [c['h3']]:
            if '—' in t or '–' in t:
                raise SystemExit('long dash in ' + slug)
        # 1) make block after the "models we see most often" list
        block = ('<div class="local-more"><h3 class="sub">' + esc(c['h3']) + '</h3>' +
                 ''.join('<p>' + esc(t) + '</p>' for t in paras) + '</div>')
        s = re.sub(r'\n?\s*<div class="local-more">.*?</div>(?=\n)', '', s, flags=re.S)
        m = re.search(r'<ul class="spots">.*?</ul>', s, re.S)
        if not m:
            raise SystemExit('no spots list in ' + slug)
        s = s[:m.end()] + '\n        ' + block + s[m.end():]
        # 2) FAQ: two make questions before the first one (the <details open>)
        s = re.sub(r'<details data-local="1">.*?</details>\n\s*', '', s, flags=re.S)
        faq_html = ''.join('<details data-local="1"><summary>' + esc(q) + '</summary><p>' + esc(a) + '</p></details>\n        ' for q, a in faq)
        i = s.index('<details open>')
        s = s[:i] + faq_html + s[i:]
        # 3) FAQPage JSON-LD
        def fix_ld(mm):
            d = json.loads(mm.group(1))
            if d.get('@type') != 'FAQPage':
                return mm.group(0)
            names = {q for q, _ in faq}
            ents = [e for e in d['mainEntity'] if e['name'] not in names]
            ents.extend({'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq)
            d['mainEntity'] = ents
            return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'
        s = re.sub(r'<script type="application/ld\+json">(.*?)</script>', fix_ld, s, flags=re.S)
        open(p, 'w', encoding='utf-8').write(s)
        words = sum(len(t.split()) for t in paras) + sum(len(q.split()) + len(a.split()) for q, a in faq)
        print(slug, 'ok,', words, 'new words')


main()
