"""Builds the Spanish pages (/es/ and /es/precios/) from the English ones.

Run from the site root after changing the English home or pricing page:
    python3 -I tools/es_build.py
Every English string that must be translated is listed below; the script fails loudly if one is missing,
so an English edit never silently leaves English text on a Spanish page.
Form values (radio value="All keys lost" etc.) stay English on purpose: the bot and Make parse them.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOBE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/>'
         '<path d="M3 12h18M12 3c2.5 2.5 3.8 5.5 3.8 9s-1.3 6.5-3.8 9c-2.5-2.5-3.8-5.5-3.8-9S9.5 5.5 12 3Z" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>')

# Blocks shared by the home and pricing pages
COMMON = [
    ('<a class="skip" href="#home">Skip to content</a>', '<a class="skip" href="#home">Saltar al contenido</a>'),
    ('aria-label="LocksMitch home"', 'aria-label="LocksMitch inicio"'),
    ('alt="LocksMitch mobile auto locksmith"', 'alt="LocksMitch cerrajero de autos a domicilio"'),
    ('<nav class="nav" aria-label="Sections">\n      <a href="#services">Services</a>\n      <a href="/pricing/">Prices</a>\n      <a href="#how">How it works</a>\n      <a href="#area">Service area</a>\n      <a href="#faq">Questions</a>\n    </nav>',
     '<nav class="nav" aria-label="Secciones">\n      <a href="#services">Servicios</a>\n      <a href="/es/precios/">Precios</a>\n      <a href="#how">Cómo funciona</a>\n      <a href="#area">Zona</a>\n      <a href="#faq">Preguntas</a>\n    </nav>\n    <a class="lang" href="{EN}" hreflang="en" lang="en" aria-label="English version">' + GLOBE + 'EN</a>'),
    ('aria-label="Call (770) 270-3333"', 'aria-label="Llamar al (770) 270-3333"'),
    ('<p class="direct"><span><strong>Answered 24/7.</strong> No call center. Every request goes straight to the locksmith who does the job.</span></p>',
     '<p class="direct"><span><strong>Atendemos 24/7.</strong> Sin centro de llamadas. Cada solicitud va directo al cerrajero que hace el trabajo.</span></p>'),
    ('<a class="btn btn-call" href="tel:7702703333"><svg><use href="#i-phone"/></svg>Call (770) 270-3333</a>\n            <a class="btn btn-ghost" href="sms:+17702703333"><svg><use href="#i-sms"/></svg>Text us</a>\n            <a class="btn btn-ghost" href="/book/"><svg><use href="#i-cal"/></svg>Book online</a>',
     '<a class="btn btn-call" href="tel:7702703333"><svg><use href="#i-phone"/></svg>Llame al (770) 270-3333</a>\n            <a class="btn btn-ghost" href="sms:+17702703333"><svg><use href="#i-sms"/></svg>Envíenos un texto</a>\n            <a class="btn btn-ghost" href="/book/"><svg><use href="#i-cal"/></svg>Reservar en línea</a>'),
    ('<span><svg><use href="#i-van"/></svg>Fully mobile</span>', '<span><svg><use href="#i-van"/></svg>Servicio a domicilio</span>'),
    ('<span><svg><use href="#i-shield"/></svg>NASTF certified</span>', '<span><svg><use href="#i-shield"/></svg>Certificado NASTF</span>'),
    ('<span><svg><use href="#i-check"/></svg>Insured</span>', '<span><svg><use href="#i-check"/></svg>Asegurado</span>'),
    ('<span><svg><use href="#i-pay"/></svg>Cards, Zelle, Apple Pay</span>', '<span><svg><use href="#i-pay"/></svg>Tarjetas, Zelle, Apple Pay</span>'),
    ('<h2 id="est-h">Free estimate</h2>\n            <p>Tell us the car and what happened. We’ll text you a price.</p>',
     '<h2 id="est-h">Cotización gratis</h2>\n            <p>Díganos qué carro tiene y qué pasó. Le enviamos el precio por texto.</p>'),
    ('<legend>What do you need?</legend>', '<legend>¿Qué necesita?</legend>'),
    ('<label for="s1">All keys lost</label>', '<label for="s1">Perdí todas las llaves</label>'),
    ('<label for="s2">Spare key</label>', '<label for="s2">Llave extra</label>'),
    ('<label for="s3">Locked out of car</label>', '<label for="s3">Llaves dentro del carro</label>'),
    ('<label for="s4">Key programming</label>', '<label for="s4">Programar una llave</label>'),
    ('<b>Add a second key, 50% off</b><small>For the same car, made in the same visit.</small>', '<b>Segunda llave con 50% de descuento</b><small>Para el mismo carro, en la misma visita.</small>'),
    ('<label for="f-vehicle">Vehicle year, make and model</label>', '<label for="f-vehicle">Año, marca y modelo del carro</label>'),
    ('<label for="f-name">Your name</label><input id="f-name" name="name" placeholder="First name is fine"', '<label for="f-name">Su nombre</label><input id="f-name" name="name" placeholder="Solo el nombre está bien"'),
    ('<label for="f-phone">Phone number</label>', '<label for="f-phone">Número de teléfono</label>'),
    ('<label for="f-company">Company</label>', '<label for="f-company">Empresa</label>'),
    ('type="submit" id="sendBtn">Get my free estimate</button>', 'type="submit" id="sendBtn">Quiero mi cotización gratis</button>'),
    ('<p class="fine">Locked out right now? Call <a href="tel:7702703333">(770) 270-3333</a>, it’s faster.</p>', '<p class="fine">¿Se quedó afuera ahora mismo? Llame al <a href="tel:7702703333">(770) 270-3333</a>, es más rápido.</p>'),
    ('<p class="fine privacy-note">We use your number only to text or call you about this request. <a href="/privacy/">Privacy policy</a></p>',
     '<p class="fine privacy-note">Usamos su número solo para escribirle o llamarle sobre esta solicitud. <a href="/privacy/">Política de privacidad</a> (en inglés)</p>'),
    ('<h2>Request received</h2>\n            <p>We’re looking up your vehicle and will text you an estimate shortly. Need help right now? Call us:</p>',
     '<h2>Solicitud recibida</h2>\n            <p>Estamos revisando su carro y le enviaremos la cotización por texto. ¿Necesita ayuda ahora mismo? Llámenos:</p>'),
    ('id="estAgain" style="border-color:rgba(233,238,234,.5);color:var(--on-fob)">Send another request</button>', 'id="estAgain" style="border-color:rgba(233,238,234,.5);color:var(--on-fob)">Enviar otra solicitud</button>'),
    ('<h2>What we do</h2>\n        <p class="lede">Four jobs, all done at your car. Most are done within about an hour once we arrive.</p>',
     '<h2>Lo que hacemos</h2>\n        <p class="lede">Cuatro servicios, todos en su carro. La mayoría toma más o menos una hora desde que llegamos.</p>'),
    ('<h3>All keys lost <span class="tag offer-tag">2nd key 50% off</span></h3><p class="when">You have no working key at all.</p>', '<h3>Perdió todas las llaves <span class="tag offer-tag">2.ª llave a mitad de precio</span></h3><p class="when">No le queda ninguna llave que funcione.</p>'),
    ('<p class="what">We cut a new key from your vehicle’s code, program the transponder or smart key to the immobilizer, and leave you with a working key. Most makes and models, including push-to-start.</p>',
     '<p class="what">Cortamos una llave nueva con el código de su carro, programamos el chip o la llave inteligente al inmovilizador y le dejamos una llave que funciona. La mayoría de marcas y modelos, incluso los de encendido por botón.</p>'),
    ('<h3>Spare key</h3><p class="when">You have one key and want a backup.</p>', '<h3>Llave extra</h3><p class="when">Tiene una llave y quiere otra de repuesto.</p>'),
    ('<p class="what">The cheapest moment to get a second key is while you still have the first. We clone or add a new key or fob so both work.</p>',
     '<p class="what">El momento más barato para hacer una segunda llave es mientras todavía tiene la primera. Copiamos o agregamos una llave o control nuevo para que las dos funcionen.</p>'),
    ('<h3>Locked out of car</h3><p class="when">Keys are inside, or the lock won’t open.</p>', '<h3>Llaves dentro del carro</h3><p class="when">Las llaves quedaron adentro o la cerradura no abre.</p>'),
    ('<p class="what">We open the door without damage to paint, glass or weatherstripping. Call rather than filling the form so we can head out right away.</p>',
     '<p class="what">Abrimos la puerta sin dañar la pintura, los vidrios ni los empaques. Mejor llame en vez de llenar el formulario, así salimos enseguida.</p>'),
    ('<h3>Key programming only</h3><p class="when">You bought a key or fob and it doesn’t start the car.</p>', '<h3>Solo programación</h3><p class="when">Compró una llave o un control y no arranca el carro.</p>'),
    ('<p class="what">We program keys and remotes you already own, as long as the hardware matches your vehicle. Tell us the part number and we’ll confirm before we come.</p>',
     '<p class="what">Programamos llaves y controles que usted ya tiene, siempre que sean compatibles con su carro. Envíenos el número de pieza y lo confirmamos antes de ir.</p>'),
    ('>More about this service</a>', '>Más información (en inglés)</a>'),
    ('<h3>Bought a car with only one key?</h3>\n          <p>A second key costs far less while you still have a working one. Lose that last key and it turns into an all-keys-lost job.</p>',
     '<h3>¿Compró un carro con una sola llave?</h3>\n          <p>Una segunda llave cuesta mucho menos mientras todavía tiene una que funciona. Si pierde esa última llave, el trabajo es más caro.</p>'),
    ('data-svc="s2">Get a spare key quote</a>\n          <a class="btn btn-ghost" href="sms:+17702703333"><svg><use href="#i-sms"/></svg>Text us</a>',
     'data-svc="s2">Precio de una llave extra</a>\n          <a class="btn btn-ghost" href="sms:+17702703333"><svg><use href="#i-sms"/></svg>Envíenos un texto</a>'),
    ('<h3>Makes we work on</h3>', '<h3>Marcas con las que trabajamos <small style="font-weight:500">(páginas en inglés)</small></h3>'),
    ('>Chevrolet and GMC<', '>Chevrolet y GMC<'), ('>Jeep, Dodge and RAM<', '>Jeep, Dodge y RAM<'),
    ('>Volkswagen and Audi<', '>Volkswagen y Audi<'), ('>Land Rover and Jaguar<', '>Land Rover y Jaguar<'),
    ('<h2>Recent jobs</h2><p class="lede">Keys we’ve cut and programmed around North Atlanta.</p>', '<h2>Trabajos recientes</h2><p class="lede">Llaves que hemos cortado y programado en North Atlanta.</p>'),
    ('<h2>How a visit works</h2>', '<h2>Cómo funciona la visita</h2>'),
    ('<li><h3>Send the car</h3><p>Call, text or use the form. Year, make, model and what happened.</p></li>', '<li><h3>Envíe los datos del carro</h3><p>Llame, escriba o use el formulario. Año, marca, modelo y qué pasó.</p></li>'),
    ('<li><h3>Get a price</h3><p>We check your vehicle’s key system and quote before anyone drives out.</p></li>', '<li><h3>Reciba el precio</h3><p>Revisamos el sistema de llaves de su carro y le damos el precio antes de salir.</p></li>'),
    ('<li><h3>We come to you</h3><p>The locksmith arrives with the blanks, cutter and programmer for your car.</p></li>', '<li><h3>Vamos hasta usted</h3><p>El cerrajero llega con las llaves, la máquina de corte y el programador para su carro.</p></li>'),
    ('<li><h3>Drive away</h3><p>Key cut, programmed and tested in the ignition before we leave.</p></li>', '<li><h3>Listo para manejar</h3><p>La llave queda cortada, programada y probada en su carro antes de irnos.</p></li>'),
    ('<h2>Where we work</h2>\n        <p class="lede">We serve North Atlanta, from Cumming and Lake Lanier down to the Perimeter. Here are the cities we cover most.</p>',
     '<h2>Dónde trabajamos</h2>\n        <p class="lede">Trabajamos en North Atlanta, desde Cumming y Lake Lanier hasta el Perimeter. Estas son las ciudades donde más trabajamos.</p>'),
    ('<p class="area-note">Not on the list? Call anyway. If you’re near one of these cities, we can usually reach you. At the lake? See our <a href="/lake-lanier/">Lake Lanier page</a>.</p>',
     '<p class="area-note">¿Su ciudad no está en la lista? Llame de todas formas. Si está cerca de una de estas ciudades, casi siempre podemos llegar. ¿Está en el lago? Vea nuestra <a href="/lake-lanier/">página de Lake Lanier</a> (en inglés).</p>'),
    ('alt="NASTF and NASTF Vehicle Security Professional badges"', 'alt="Insignias de NASTF y NASTF Vehicle Security Professional"'),
    ('<h2 style="font-size:20px; line-height:1.3">Certified to access manufacturer key data</h2>\n          <p class="lede" style="margin-top:6px; font-size:15px; max-width:none">Modern keys need security codes from the car maker. NASTF’s Vehicle Security Professional registry is how locksmiths get them legally.</p>',
     '<h2 style="font-size:20px; line-height:1.3">Certificado para acceder a los códigos del fabricante</h2>\n          <p class="lede" style="margin-top:6px; font-size:15px; max-width:none">Las llaves modernas necesitan códigos de seguridad del fabricante. El registro Vehicle Security Professional de NASTF es la forma legal en que los cerrajeros los obtienen.</p>'),
    ('<div><b>NASTF certified</b><span>Vehicle Security Professional</span></div>\n            <div><b>Insured</b><span>Covered on every job</span></div>\n            <div><b>Registered business</b><span>LocksMitch is a DBA of TPVision LLC</span></div>',
     '<div><b>Certificado NASTF</b><span>Vehicle Security Professional</span></div>\n            <div><b>Asegurado</b><span>En cada trabajo</span></div>\n            <div><b>Negocio registrado</b><span>LocksMitch es un DBA de TPVision LLC</span></div>'),
    ('<h2 class="col-h">Contact us</h2>', '<h2 class="col-h">Contáctenos</h2>'),
    ('<button class="copy" type="button" id="copyBtn">Copy number</button>', '<button class="copy" type="button" id="copyBtn">Copiar número</button>'),
    ('<p class="hours-line"><svg><use href="#i-check"/></svg>Open 24/7, including nights, weekends and holidays</p>\n        <p class="hours-line pay-line"><svg><use href="#i-pay"/></svg>We accept cash, credit and debit cards, Apple Pay, Zelle, Venmo and Cash App</p>',
     '<p class="hours-line"><svg><use href="#i-check"/></svg>Abierto 24/7, también de noche, fines de semana y días festivos</p>\n        <p class="hours-line pay-line"><svg><use href="#i-pay"/></svg>Aceptamos efectivo, tarjetas de crédito y débito, Apple Pay, Zelle, Venmo y Cash App</p>'),
    ('<span class="ch-name">Text message</span>', '<span class="ch-name">Mensaje de texto</span>'),
    ('<span class="ch-val">Message us</span>', '<span class="ch-val">Escríbanos</span>'),
    ('<span class="ch-name">Email</span>', '<span class="ch-name">Correo</span>'),
    ('<span class="ch-name">Save contact</span><span class="ch-val">Add to your phone</span>', '<span class="ch-name">Guardar contacto</span><span class="ch-val">En su teléfono</span>'),
    ('<nav class="foot-links" aria-label="Services">\n      <a href="/all-keys-lost/">All keys lost</a><a href="/spare-key/">Spare key</a><a href="/car-lockout/">Car lockout</a><a href="/key-programming/">Key programming</a><a href="/pricing/">Prices</a><a href="/guides/">Guides</a><a href="/#area">Service area</a><a href="/privacy/">Privacy</a>\n    </nav>',
     '<nav class="foot-links" aria-label="Servicios">\n      <a href="/es/">Inicio</a><a href="/es/precios/">Precios</a><a href="/es/#area">Zona de servicio</a><a href="{EN}" hreflang="en" lang="en">English</a><a href="/all-keys-lost/" lang="en">All keys lost</a><a href="/spare-key/" lang="en">Spare key</a><a href="/car-lockout/" lang="en">Car lockout</a><a href="/key-programming/" lang="en">Key programming</a><a href="/privacy/">Privacidad</a>\n    </nav>'),
    ('aria-label="City pages"', 'aria-label="Ciudades"'),
    ('<span>© 2026 LocksMitch, a registered DBA of TPVision LLC</span>\n    <span>Mobile auto locksmith serving North Atlanta, GA</span>\n    <span>We accept cash, cards, Apple Pay, Zelle, Venmo and Cash App</span>',
     '<span>© 2026 LocksMitch, un DBA registrado de TPVision LLC</span>\n    <span>Cerrajero de autos a domicilio en North Atlanta, GA</span>\n    <span>Aceptamos efectivo, tarjetas, Apple Pay, Zelle, Venmo y Cash App</span>'),
    ('<a class="btn btn-call" href="tel:7702703333"><svg><use href="#i-phone"/></svg>Call now</a>\n  <a class="btn btn-ghost" href="sms:+17702703333"><svg><use href="#i-sms"/></svg>Text</a>\n  <a class="btn btn-ghost" href="#estimate">Estimate</a>',
     '<a class="btn btn-call" href="tel:7702703333"><svg><use href="#i-phone"/></svg>Llamar</a>\n  <a class="btn btn-ghost" href="sms:+17702703333"><svg><use href="#i-sms"/></svg>Texto</a>\n  <a class="btn btn-ghost" href="#estimate">Cotizar</a>'),
    ('href="assets/', 'href="/assets/'), ('src="assets/', 'src="/assets/'), ('href="favicon.ico', 'href="/favicon.ico'), ('href="site.webmanifest', 'href="/site.webmanifest'),
]

HOME = [
    ('<html lang="en">', '<html lang="es" data-page="Home ES">'),
    ('<title>Mobile Auto Locksmith in North Atlanta | LocksMitch</title>', '<title>Cerrajero de Autos a Domicilio en North Atlanta | LocksMitch</title>'),
    ('<meta name="description" content="Lost car keys, spare keys, lockouts and key programming. LocksMitch comes to you across North Atlanta. Call (770) 270-3333.">',
     '<meta name="description" content="Llaves de carro perdidas, llaves extra, apertura de carros y programación de llaves. LocksMitch va a donde está su carro en North Atlanta. Llame al (770) 270-3333.">'),
    ('<meta property="og:title" content="LocksMitch | Mobile Auto Locksmith in North Atlanta">', '<meta property="og:title" content="LocksMitch | Cerrajero de Autos a Domicilio en North Atlanta">'),
    ('<meta property="og:description" content="Lost car keys, spare keys, lockouts and key programming. We come to you across North Atlanta. Call (770) 270-3333.">',
     '<meta property="og:description" content="Llaves de carro perdidas, llaves extra, apertura de carros y programación de llaves. Vamos a donde está usted en North Atlanta. Llame al (770) 270-3333.">'),
    ('<h1>Lost your car keys?<span class="l2">We cut and program new ones where you’re parked.</span></h1>', '<h1>¿Perdió las llaves de su carro?<span class="l2">Cortamos y programamos llaves nuevas donde esté su carro.</span></h1>'),
    ('<p class="lede">LocksMitch is a mobile auto locksmith for North Atlanta. We bring dealership-level key cutting and programming equipment to your driveway, office lot or the side of the road. No tow, no dealer wait.</p>',
     '<p class="lede">LocksMitch es un cerrajero de autos a domicilio en North Atlanta. Llevamos equipo de corte y programación de llaves, igual al del dealer, hasta su casa, su trabajo o la orilla de la carretera. Sin grúa y sin esperar en el dealer.</p>'),
    ('<p class="book-note"><span class="tag">$15 off</span>&nbsp; <strong>when you book online.</strong> Locked out right now? Call instead, it’s faster.</p>',
     '<p class="book-note"><span class="tag">$15 de descuento</span>&nbsp; <strong>al reservar en línea.</strong> ¿Se quedó afuera de su carro ahora mismo? Mejor llame, es más rápido.</p>'),
    ('<span><strong>Upfront price.</strong> Quoted before we drive out, and it doesn’t change at your car. Coming to you is included. <a href="/pricing/">See prices&nbsp;→</a></span>',
     '<span><strong>Precio por adelantado.</strong> Se lo damos antes de salir y no cambia al llegar a su carro. La visita está incluida. <a href="/es/precios/">Ver precios&nbsp;→</a></span>'),
    ('alt="Mitch, owner of LocksMitch"', 'alt="Mitch, dueño de LocksMitch"'),
    ('<h2>Meet Mitch</h2>\n        <p>Hi, I’m Mitch, the owner of LocksMitch and the locksmith who shows up at your car. Forsyth County is home for me, and I cover Cumming and the rest of North Atlanta.</p>\n        <p>LocksMitch is just me. There’s no call center and no dispatcher: when you call or text, you reach the person who will cut and program your key. I tell you the price before I drive out, and it doesn’t change at your car.</p>\n        <p>Look for the Tesla Model Y with the LocksMitch logo. That’s me pulling up.</p>',
     '<h2>Conozca a Mitch</h2>\n        <p>Hola, soy Mitch, el dueño de LocksMitch y el cerrajero que llega a su carro. Vivo en el condado de Forsyth y trabajo en Cumming y todo North Atlanta.</p>\n        <p>LocksMitch soy yo. No hay centro de llamadas ni operadora: cuando llama o escribe, habla con la persona que va a cortar y programar su llave. Le digo el precio antes de salir y no cambia al llegar a su carro.</p>\n        <p>Busque el Tesla Model Y con el logo de LocksMitch. Ese soy yo.</p>'),
    ('<span>Call Mitch</span></a>\n          <a class="btn btn-ghost" href="sms:+17702703333"><svg><use href="#i-sms"/></svg><span>Text Mitch</span></a>', '<span>Llamar a Mitch</span></a>\n          <a class="btn btn-ghost" href="sms:+17702703333"><svg><use href="#i-sms"/></svg><span>Escribir a Mitch</span></a>'),
    ('<h2 class="col-h">Common questions</h2>', '<h2 class="col-h">Preguntas frecuentes</h2>'),
    ('<details open><summary>Is it cheaper than the dealership?</summary><p>Usually, and you skip the tow. The dealer needs the car on their lot; we do the same programming in your driveway. Send the vehicle details and we’ll quote it.</p></details>',
     '<details open><summary>¿Es más barato que el dealer?</summary><p>Por lo general sí, y no necesita grúa. El dealer necesita el carro en su lote; nosotros hacemos la misma programación en la entrada de su casa. Envíenos los datos del carro y le damos el precio.</p></details>'),
    ('<details><summary>Can you make a key if I’ve lost every one?</summary><p>Yes. That’s the “all keys lost” job. We cut the key from your vehicle’s code and program it on site.</p></details>',
     '<details><summary>¿Pueden hacer una llave si perdí todas?</summary><p>Sí. Cortamos la llave con el código de su carro y la programamos ahí mismo.</p></details>'),
    ('<details><summary>Do you work on push-to-start and smart keys?</summary><p>Yes, for most makes. Some newer models need extra steps or parts. Tell us the year, make and model and we’ll confirm before coming out.</p></details>',
     '<details><summary>¿Trabajan con llaves inteligentes y encendido por botón?</summary><p>Sí, en la mayoría de marcas. Algunos modelos nuevos necesitan pasos o piezas extra. Díganos el año, la marca y el modelo y lo confirmamos antes de salir.</p></details>'),
    ('<details><summary>Do I need to tow my car to you?</summary><p>No. We bring the key machine, blanks and programmer to wherever the car is: home, work, a parking lot or the side of the road.</p></details>',
     '<details><summary>¿Tengo que llevar mi carro en grúa?</summary><p>No. Llevamos la máquina de llaves, las llaves y el programador a donde esté el carro: casa, trabajo, un estacionamiento o la orilla de la carretera.</p></details>'),
    ('<details><summary>Can this damage my car?</summary><p>We take care not to. We open doors with automotive lockout tools, not by force, and program keys with dealer-level equipment, usually through the car’s diagnostic port.</p></details>',
     '<details><summary>¿Esto puede dañar mi carro?</summary><p>Tenemos mucho cuidado. Abrimos las puertas con herramientas especiales, no a la fuerza, y programamos las llaves con el mismo equipo que usa el dealer, normalmente por el puerto de diagnóstico.</p></details>'),
    ('<details><summary>What are your hours?</summary><p>We take calls and go out 24/7, including nights, weekends and holidays.</p></details>',
     '<details><summary>¿Cuál es su horario?</summary><p>Contestamos y salimos 24/7, también de noche, fines de semana y días festivos.</p></details>'),
    ('<details><summary>How can I pay?</summary><p>Cash, credit and debit cards, Apple Pay, Zelle, Venmo or Cash App, whichever is easiest for you.</p></details>',
     '<details><summary>¿Cómo puedo pagar?</summary><p>Efectivo, tarjetas de crédito y débito, Apple Pay, Zelle, Venmo o Cash App, lo que le sea más fácil.</p></details>'),
    ('<details><summary>Can I text instead of calling?</summary><p>Yes. Text <a href="sms:+17702703333">(770) 270-3333</a> with the year, make and model and what happened. You’ll get a reply from the locksmith, not a call center.</p></details>',
     '<details><summary>¿Puedo escribir en vez de llamar?</summary><p>Sí. Envíe un texto al <a href="sms:+17702703333">(770) 270-3333</a> con el año, la marca, el modelo y qué pasó. Le contesta el cerrajero, no un centro de llamadas. Mitch no habla español, pero puede escribirle en español: él usa un traductor y le contesta con gusto.</p></details>'),
    ('<details><summary>Is there a discount on a second key?</summary><p>Yes. When we make a new key because all keys are lost, a second key for the same car is 50% off. Same car, same key type, made during the same visit. Combines with $15 off for online booking.</p></details>',
     '<details><summary>¿Hay descuento en una segunda llave?</summary><p>Sí. Cuando hacemos una llave nueva porque se perdieron todas, la segunda llave para el mismo carro tiene 50% de descuento. Mismo carro, mismo tipo de llave y en la misma visita. Se suma a los $15 de descuento por reservar en línea.</p></details>'),
    ('<details><summary>How do I get the $15 discount?</summary><p>Book your appointment through the online booking page. The discount is applied to online bookings. Valid on spare keys and all-keys-lost jobs only.</p></details>',
     '<details><summary>¿Cómo obtengo el descuento de $15?</summary><p>Reserve su cita en la página de reservas en línea. El descuento se aplica a las reservas en línea. Válido solo para llaves extra y para llaves nuevas cuando se perdieron todas.</p></details>'),
]

PRICING = [
    ('<html lang="en" data-page="Spare key">', '<html lang="es" data-page="Prices ES">'),
    ('<title>Car Locksmith Prices in Cumming &amp; North Atlanta | LocksMitch</title>', '<title>Precios de Cerrajero de Autos en Cumming y North Atlanta | LocksMitch</title>'),
    ('<meta property="og:title" content="Car Locksmith Prices in Cumming &amp; North Atlanta | LocksMitch">', '<meta property="og:title" content="Precios de Cerrajero de Autos en Cumming y North Atlanta | LocksMitch">'),
    ('<meta property="og:description" content="Lockout from $75, spare chip key from $140, smart key from $180, all keys lost from $190. Honest starting prices, no trip fee in our area.">',
     '<meta property="og:description" content="Apertura de carro desde $75, llave extra con chip desde $140, llave inteligente desde $180, todas las llaves perdidas desde $190. Precios honestos, sin cargo por visita en nuestra zona.">'),
    ('<a class="brand" href="/" aria-label=', '<a class="brand" href="/es/" aria-label='),
    ('<nav class="crumbs" aria-label="Breadcrumb"><a href="/">LocksMitch</a> › Prices</nav>', '<nav class="crumbs" aria-label="Ruta"><a href="/es/">LocksMitch</a> › Precios</nav>'),
    ('<h1>What it costs<span class="l2">Honest starting prices, the same on the phone and at your car.</span></h1>', '<h1>Cuánto cuesta<span class="l2">Precios iniciales honestos, los mismos por teléfono y en su carro.</span></h1>'),
    ('<p class="lede">Every price below includes coming to you, the work and testing it. No separate trip fee, no dealer, no tow. Lockouts are flat rate. For keys, Mitch quotes the exact price before he drives out, and it doesn’t change at your car.</p>',
     '<p class="lede">Cada precio incluye la visita, el trabajo y la prueba. Sin cargo aparte por la visita, sin dealer y sin grúa. La apertura de carros tiene precio fijo. Para las llaves, Mitch le da el precio exacto antes de salir y no cambia al llegar a su carro.</p>'),
    ('<p class="book-note"><span class="tag">$15 off</span>&nbsp; <strong>when you book online.</strong> Questions about your key? Call or text, we reply fast.</p>',
     '<p class="book-note"><span class="tag">$15 de descuento</span>&nbsp; <strong>al reservar en línea.</strong> ¿Preguntas sobre su llave? Llame o escriba, contestamos rápido.</p>'),
    ('<h2>Starting prices</h2>\n      <p class="lede">These are the lowest prices for each job. The exact price depends on the make, model year and key type, and Mitch confirms it by text before he drives out.</p>',
     '<h2>Precios iniciales</h2>\n      <p class="lede">Estos son los precios más bajos de cada trabajo. El precio exacto depende de la marca, el año del modelo y el tipo de llave, y Mitch lo confirma por texto antes de salir.</p>'),
    ('<h3 class="pg-h">Lockout and new keys</h3>', '<h3 class="pg-h">Apertura y llaves nuevas</h3>'),
    ('alt="Open padlock"', 'alt="Candado abierto"'),
    ('<h4>Car lockout, flat rate</h4><p>Opening the car with lockout tools, no damage. $75 in Cumming and Forsyth, $100 up to 25 miles, $125 up to 40 miles</p>',
     '<h4>Apertura de carro, precio fijo</h4><p>Abrimos el carro con herramientas especiales, sin daños. $75 en Cumming y Forsyth, $100 hasta 25 millas, $125 hasta 40 millas</p>'),
    ('<span>from</span>', '<span>desde</span>'),
    ('alt="Plain metal key"', 'alt="Llave de metal sencilla"'),
    ('<h4>Key cut, no chip</h4><p>Plain metal key for older cars, doors and trunks, cut by code, by lock or from your working key</p>',
     '<h4>Llave sin chip</h4><p>Llave de metal sencilla para carros más antiguos, puertas y cajuelas, cortada por código, por la cerradura o copiando su llave</p>'),
    ('alt="Key with a chip in the head"', 'alt="Llave con chip en la cabeza"'),
    ('<h4>Spare key with chip</h4><p>Transponder key cut and programmed, most makes</p>', '<h4>Llave extra con chip</h4><p>Llave con chip cortada y programada, la mayoría de marcas</p>'),
    ('alt="Key with lock and unlock buttons"', 'alt="Llave con botones para cerrar y abrir"'),
    ('<h4>Key with remote (flip key)</h4><p>Remote head or flip key, cut and programmed</p>', '<h4>Llave con control (llave navaja)</h4><p>Llave con botones o llave navaja, cortada y programada</p>'),
    ('alt="Push-to-start smart key fob"', 'alt="Llave inteligente de encendido por botón"'),
    ('<h4>Push-to-start smart key</h4><p>Proximity key programmed. 2020 and newer from $200</p>', '<h4>Llave inteligente (encendido por botón)</h4><p>Llave de proximidad programada. Modelos 2020 y más nuevos desde $200</p>'),
    ('alt="New key with a plus sign"', 'alt="Llave nueva con un signo de más"'),
    ('<h4>All keys lost</h4><p>New key made from the vehicle code when no key is left. Toyota, Honda, Ford, GM, Hyundai, Kia, Nissan, Jeep and most other makes. Subaru and European makes quoted by model</p>',
     '<h4>Perdió todas las llaves</h4><p>Llave nueva hecha con el código del carro cuando no queda ninguna. Toyota, Honda, Ford, GM, Hyundai, Kia, Nissan, Jeep y la mayoría de marcas. Subaru y marcas europeas, precio según el modelo</p>'),
    ('<h3 class="pg-h">Programming and remotes</h3>', '<h3 class="pg-h">Programación y controles</h3>'),
    ('alt="Key fob being programmed"', 'alt="Control de llave en programación"'),
    ('<h4>Programming only, a key you bought</h4><p>We cut and program a key or fob you already have. Push-to-start smart key $129. No working key at all: all-keys-lost pricing applies. European makes quoted by model</p>',
     '<h4>Solo programación, una llave que usted compró</h4><p>Cortamos y programamos una llave o control que usted ya tiene. Llave inteligente de encendido por botón $129. Si no tiene ninguna llave que funcione, aplica el precio de todas las llaves perdidas. Marcas europeas, precio según el modelo</p>'),
    ('alt="Remote without a key blade"', 'alt="Control sin llave"'),
    ('<h4>Remote you bought, buttons only</h4><p>Programming a remote without a key blade</p>', '<h4>Control que usted compró, solo botones</h4><p>Programación de un control sin llave</p>'),
    ('<h4>Replacement remote</h4><p>New remote supplied and programmed</p>', '<h4>Control de reemplazo</h4><p>Control nuevo incluido y programado</p>'),
    ('<h3 class="pg-h">European makes</h3>', '<h3 class="pg-h">Marcas europeas</h3>'),
    ('alt="Flip key"', 'alt="Llave navaja"'),
    ('<h4>European: BMW, Mini, VW, Audi</h4><p>Cut and programmed, model years we cover</p>', '<h4>Europeas: BMW, Mini, VW, Audi</h4><p>Cortada y programada, en los años de modelo que trabajamos</p>'),
    ('alt="Smart key fob"', 'alt="Llave inteligente"'),
    ('<h4>Mercedes-Benz, Porsche, Volvo</h4><p>Complex key systems, quoted by model</p>', '<h4>Mercedes-Benz, Porsche, Volvo</h4><p>Sistemas de llave complejos, precio según el modelo</p>'),
    ('<h3 class="sub">Distance and time</h3>', '<h3 class="sub">Distancia y horario</h3>'),
    ('<li><b>Cumming, Forsyth County and Sugar Hill</b> (up to 12 miles by road): prices as listed, no trip fee</li>',
     '<li><b>Cumming, el condado de Forsyth y Sugar Hill</b> (hasta 12 millas por carretera): precios de la lista, sin cargo por visita</li>'),
    ('<li><b>12 to 25 miles</b> (Buford, Suwanee, Alpharetta, Johns Creek, Duluth, Flowery Branch, Milton, Dawsonville, Roswell, Gainesville, Lawrenceville, Canton, Dunwoody): lockout and no-chip key $100, key jobs as listed</li>',
     '<li><b>De 12 a 25 millas</b> (Buford, Suwanee, Alpharetta, Johns Creek, Duluth, Flowery Branch, Milton, Dawsonville, Roswell, Gainesville, Lawrenceville, Canton, Dunwoody): apertura y llave sin chip $100, llaves con los precios de la lista</li>'),
    ('<li><b>25 to 40 miles</b> (Peachtree Corners, Sandy Springs, Norcross, Braselton, Woodstock, Doraville, Smyrna): lockout and no-chip key $125, key jobs +$50</li>',
     '<li><b>De 25 a 40 millas</b> (Peachtree Corners, Sandy Springs, Norcross, Braselton, Woodstock, Doraville, Smyrna): apertura y llave sin chip $125, llaves +$50</li>'),
    ('<li><b>Beyond 40 miles</b> (Marietta, Kennesaw and further): quoted by Mitch</li>', '<li><b>Más de 40 millas</b> (Marietta, Kennesaw y más lejos): Mitch le da el precio</li>'),
    ('<li><b>Nights</b>, 9 pm to 7 am: +$50</li>', '<li><b>De noche</b>, de 9 pm a 7 am: +$50</li>'),
    ('<li><b>Parts you bought</b>: if a key or remote you bought online can’t be programmed to your car (wrong type, used or locked), the trip and check is $75</li>',
     '<li><b>Piezas que usted compró</b>: si una llave o control que compró en línea no se puede programar a su carro (tipo equivocado, usada o bloqueada), la visita y la revisión cuestan $75</li>'),
    ('<li><b>Second key</b> for the same car in the same visit: 50% off. <b>Online booking</b>: $15 off <small>(spare keys and all keys lost only)</small></li>', '<li><b>Segunda llave</b> para el mismo carro en la misma visita: 50% de descuento. <b>Reserva en línea</b>: $15 de descuento <small>(solo llaves extra y pérdida de todas las llaves)</small></li>'),
    ('<p class="svc-tip">Watch out for "$19" and "$29" locksmith ads: that is a dispatch fee for a call center, the work is priced separately when the van arrives. We quote the whole job before anyone drives out.</p>',
     '<p class="svc-tip">Cuidado con los anuncios de cerrajeros de "$19" o "$29": es solo el cargo de un centro de llamadas, y el trabajo se cobra aparte cuando llega la camioneta. Nosotros le damos el precio de todo el trabajo antes de salir.</p>'),
    ('<aside class="nearby">\n        <h3>Services</h3>', '<aside class="nearby">\n        <h3>Servicios <small style="font-weight:500">(en inglés)</small></h3>'),
    ('<li><a href="/all-keys-lost/">All keys lost</a></li><li><a href="/spare-key/">Spare key</a></li><li><a href="/car-lockout/">Locked out of car</a></li><li><a href="/key-programming/">Key programming only</a></li>',
     '<li><a href="/all-keys-lost/">Perdió todas las llaves</a></li><li><a href="/spare-key/">Llave extra</a></li><li><a href="/car-lockout/">Llaves dentro del carro</a></li><li><a href="/key-programming/">Solo programación</a></li>'),
    ('<h3 style="margin-top:20px">By make</h3>', '<h3 style="margin-top:20px">Por marca</h3>'),
    ('<a href="/#services" style="padding:0;color:var(--muted);font-weight:500">All makes and services →</a>', '<a href="/es/#services" style="padding:0;color:var(--muted);font-weight:500">Todas las marcas y servicios →</a>'),
    ('<h2 class="col-h">Price questions</h2>', '<h2 class="col-h">Preguntas sobre precios</h2>'),
    ('<details open><summary>Why is the dealer more expensive?</summary><p>The dealer needs the car on their lot, so you pay for a tow or a second trip, and dealer parts are priced at retail. We do the same cutting and programming at your car with the same manufacturer key data.</p></details>',
     '<details open><summary>¿Por qué el dealer cobra más?</summary><p>El dealer necesita el carro en su lote, así que usted paga una grúa o un segundo viaje, y sus piezas tienen precio de tienda. Nosotros hacemos el mismo corte y la misma programación en su carro, con los mismos datos del fabricante.</p></details>'),
    ('<details><summary>Is the starting price what I will pay?</summary><p>For most cars, yes. The price goes up only for a newer model year, a rarer key, all keys lost or a long drive, and Mitch tells you the exact number by text before he leaves.</p></details>',
     '<details><summary>¿El precio inicial es lo que voy a pagar?</summary><p>En la mayoría de los carros, sí. El precio sube solo con un modelo más nuevo, una llave menos común, si se perdieron todas las llaves o si la distancia es larga, y Mitch le dice el número exacto por texto antes de salir.</p></details>'),
    ('<details><summary>Do you charge a trip fee?</summary><p>No. In Cumming and Forsyth County the price includes coming to you. Further out, the lockout and no-chip key prices step up as shown above; key jobs add $50 only beyond 25 miles.</p></details>',
     '<details><summary>¿Cobran por la visita?</summary><p>No. En Cumming y el condado de Forsyth el precio incluye la visita. Más lejos, la apertura y la llave sin chip suben como se muestra arriba; las llaves suman $50 solo a más de 25 millas.</p></details>'),
    ('<details><summary>What if the key turns out to be a different type?</summary><p>Mitch checks the key at the car. If it is a different type than you thought, he tells you the new price before doing anything.</p></details>',
     '<details><summary>¿Y si la llave resulta ser de otro tipo?</summary><p>Mitch revisa la llave en el carro. Si es de otro tipo del que pensaba, le dice el precio nuevo antes de hacer cualquier trabajo.</p></details>'),
    ('<details><summary>Do you really charge $75 for a lockout?</summary><p>Yes, in Cumming and Forsyth County, day rate. Nights add $50. That is the whole price: coming out, opening the car, no damage.</p></details>',
     '<details><summary>¿De verdad cobran $75 por abrir un carro?</summary><p>Sí, en Cumming y el condado de Forsyth, de día. De noche son $50 más. Ese es el precio completo: la visita y abrir el carro, sin daños.</p></details>'),
    ('<details><summary>What if the key I bought online doesn’t work?</summary><p>Tell us the part number or send a photo before the visit and Mitch checks it. If it still can’t be programmed to your car (wrong type, already used or locked), you pay $75 for the trip and the check, and Mitch can supply a key that works.</p></details>',
     '<details><summary>¿Y si la llave que compré en línea no funciona?</summary><p>Envíenos el número de pieza o una foto antes de la visita y Mitch la revisa. Si aun así no se puede programar a su carro (tipo equivocado, ya usada o bloqueada), usted paga $75 por la visita y la revisión, y Mitch le puede conseguir una llave que funcione.</p></details>'),
    ('<details><summary>How can I pay?</summary><p>Cash, credit and debit cards, Apple Pay, Zelle, Venmo or Cash App.</p></details>',
     '<details><summary>¿Cómo puedo pagar?</summary><p>Efectivo, tarjetas de crédito y débito, Apple Pay, Zelle, Venmo o Cash App.</p></details>'),
]

PAGES = [
    # (English source, Spanish target, English URL, Spanish URL, page pairs, meta description)
    ('index.html', 'es/index.html', 'https://locksmitch.com/', 'https://locksmitch.com/es/', HOME, None),
    ('pricing/index.html', 'es/precios/index.html', 'https://locksmitch.com/pricing/', 'https://locksmitch.com/es/precios/', PRICING,
     'Cuánto cuesta un cerrajero de autos a domicilio en Cumming, el condado de Forsyth y North Atlanta: apertura desde $75, llave extra con chip desde $140, llave inteligente desde $180, todas las llaves perdidas desde $190. Sin cargo por visita en nuestra zona.'),
]


def hreflang(en, es):
    return ('<link rel="alternate" hreflang="en" href="%s">\n<link rel="alternate" hreflang="es" href="%s">\n'
            '<link rel="alternate" hreflang="x-default" href="%s">' % (en, es, en))


def faq_ld(s):
    qa = re.findall(r'<details(?: open)?><summary>(.*?)</summary><p>(.*?)</p></details>', s, flags=re.S)
    strip = lambda t: re.sub(r'<[^>]+>', '', t).strip()
    return {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "es",
            "mainEntity": [{"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qa]}


def build(src, dst, en_url, es_url, pairs, desc):
    s = open(os.path.join(ROOT, src), encoding='utf-8').read()
    # the English page links to its Spanish twin (globe ES + hreflang); the Spanish page gets its own versions below
    s = re.sub(r'\n    <a class="lang"[^\n]*?ES</a>', '', s)
    s = re.sub(r'\n<link rel="alternate" hreflang="[^"]*" href="[^"]*">', '', s)
    for a, b in pairs:
        if a not in s:
            sys.exit('MISSING in %s: %s' % (src, a[:90]))
        s = s.replace(a, b)
    for a, b in COMMON:
        s = s.replace(a, b.replace('{EN}', en_url.replace('https://locksmitch.com', '')))
    s = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="%s">\n%s' % (es_url, hreflang(en_url, es_url)), s, count=1)
    s = re.sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="%s">\n<meta property="og:locale" content="es_US">' % es_url, s, count=1)
    if desc:
        s = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % desc, s, count=1)
    # JSON-LD: the business itself is described on the English pages; here a Spanish WebPage that points to it (+ Spanish FAQ)
    s = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', s, flags=re.S)
    title = re.search(r'<title>(.*?)</title>', s).group(1)
    ld = [{"@context": "https://schema.org", "@type": "WebPage", "url": es_url, "inLanguage": "es", "name": title,
           "about": {"@id": "https://locksmitch.com/#locksmith"}, "isPartOf": {"@type": "WebSite", "url": "https://locksmitch.com/"}}, faq_ld(s)]
    tags = ''.join('<script type="application/ld+json">%s</script>\n' % json.dumps(x, ensure_ascii=False) for x in ld)
    s = s.replace('<link rel="preconnect" href="https://fonts.googleapis.com">', tags + '<link rel="preconnect" href="https://fonts.googleapis.com">', 1)
    # anything English left in visible text?
    body = s[s.index('<main'):s.index('</footer>')]
    t = re.sub(r'<script.*?</script>|<svg.*?</svg>|<a [^>]*lang="en"[^>]*>.*?</a>', '', body, flags=re.S)
    left = [l.strip() for l in re.sub(r'<[^>]+>', '\n', t).split('\n') if re.search(r"\b(the|and|your|you|we|our|with|for|from)\b", l, re.I)]
    if left:
        sys.exit('English left in %s: %s' % (dst, left[:8]))
    os.makedirs(os.path.dirname(os.path.join(ROOT, dst)), exist_ok=True)
    open(os.path.join(ROOT, dst), 'w', encoding='utf-8').write(s)
    print('built', dst)


for p in PAGES:
    build(*p)
