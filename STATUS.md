# locksmitch-site - статус (2026-10-22)

Записка для новой сессии Claude и для Димы. Что это за проект, где что лежит, что сделано и что осталось. Обновлять, когда что-то меняется.

## Что это

Сайт locksmitch.com (мобильный автомобильный locksmith, Северная Атланта). Статический HTML, публикуется через GitHub Pages из репозитория github.com/dmytro-s88/locksmitch-site. DNS на Porkbun: 4 A-записи GitHub на корне, 24 городских поддомена (cumming.locksmitch.com и т.д.) делают 301 на locksmitch.com/<город>/. Carrd больше не используется.

## Структура

| Что | Где |
|---|---|
| Главная | `index.html` |
| 24 городских страницы | `cumming/`, `alpharetta/`, ... (папка = URL) |
| 4 сервисных | `spare-key/`, `all-keys-lost/`, `car-lockout/`, `key-programming/` |
| 19 страниц по маркам | `bmw-key-replacement/`, `toyota-key-replacement/`, ... |
| Онлайн-запись | `book/index.html` (свои CSS/JS, отправляет в веб-приложение бота, не в form-backend) |
| Прочее | `lake-lanier/`, `privacy/`, `404.html` |
| Общие стили и скрипты | `assets/site.css`, `assets/site.js` (подключены на 49 страницах с `?v=20261022b`) |
| Логотип, og-картинка, иконки | `assets/` (logo.webp для img, PNG для schema/og, og.png 1200x630) |
| Форма заявки (бэкенд) | `form-backend/` - Apps Script "LocksMitch Site Form", scriptId `1DE2XXZ4KPqsc5j-O1-AjMp7psQRMmbH9owOBRz-Mo9s-aVG5r3abRn-3`; doPost шлёт письмо на info@locksmitch.com, doGet ?feed=instagram отдаёт галерею @locksmitch.ga |
| sitemap, robots, manifest | в корне; sitemap lastmod берётся из git |

Всего 52 html-файла. Генератора страниц нет (шаблон и скрипты сборки потеряны в октябре): правки общих частей (футер, форма, шапка) делаются скриптом сразу по всем `*/index.html`.

## Как работать

- Правка: редактируем HTML в репозитории напрямую. После правки `assets/site.css` или `site.js` поднять `?v=` на всех страницах.
- Локальный просмотр: `python3 -m http.server 8765` в папке сайта, открыть http://localhost:8765.
- Публикация: `git push` в main = сайт обновился через 1-2 минуты. Пушить по команде Димы ("Push сайт").
- Бэкенд формы деплоится из соседнего проекта: `python3 ~/Projects/LocksMitch-bot/gas.py push 1DE2XXZ4KPqsc5j-O1-AjMp7psQRMmbH9owOBRz-Mo9s-aVG5r3abRn-3 ~/Projects/locksmitch-site/form-backend`.
- DNS и форварды на Porkbun: через MCP Porkbun, не через браузер. MX и SMTP2GO-записи не трогать.

## Правила по тексту и дизайну (решения Димы)

- Никаких длинных тире в тексте сайта, только короткий дефис. Диапазоны цен: "$350-400".
- "Insured" и "Registered business", не "Licensed": в Джорджии нет лицензии locksmith. Страховка и бизнес-лицензия есть (подтверждено 2026-10-22).
- Не перечислять документы, которые клиент должен приготовить (ID, VIN, title). Дима говорит это сам после контакта.
- Шрифт Open Sans, тёмная графитовая тема, зелёный логотипа #6CC655. Никаких "растянутых" шрифтов и декоративных трюков.
- Везде одинаковые NAP: LocksMitch, (770) 270-3333, locksmitch.com. Часы 24/7, ночью дороже.
- Отзывы только настоящие. Любые платные рекламные предложения отклонять.
- Оплата: Cash, карты, Apple Pay, Zelle, Venmo, Cash App (на всех страницах и в schema).

## Сделано (хронология, последнее сверху)

- 2026-10-22: тех. долг закрыт. Общие CSS/JS вынесены в assets (index.html 57 КБ -> 25 КБ), футер с 24 городами, BreadcrumbList и Locksmith @id в JSON-LD, og:image 1200x630, короткие meta description, skip-link, aria-label на кнопке звонка, logo.webp, 404.html, favicon.ico, иконки манифеста 192/512, robots Disallow /form-backend/.
- 2026-10-22: смягчены формулировки ("Insured", "The locksmith arrives", "within about an hour", честный ответ про повреждения, наличие ключей для Ferrari/Maserati/Porsche зависит от модели).
- 2026-10-22: онлайн-запись /book/ заменила Square на всех 49 кнопках "Book online". Запись закрыта до 2026-11-05 (BK_FIRST_DAY в боте, дни показаны как "Full"). Google Calendar к записи пока не подключён.
- 2026-10-20: блок способов оплаты; страницы марок: мягкие ответы, "уточним по году и модели".
- 2026-10-18: городские поддомены перенаправлены на /<город>/, Carrd отключён.
- 2026-10-17: 50 страниц, privacy, GA4 (единственная cookie _ga).
- 2026-10-09: первый коммит, переезд с Carrd на GitHub Pages.

## Осталось

Для Димы:
- Google Business Profile ещё не создан (нужна видеоверификация дома). Это главный источник звонков.
- Подтвердить, что есть именно liability insurance (на сайте написано "Insured").
- Yelp: переписать и пересдать Specialties (отклонили 2026-10-14). Bing Places: ввести PIN с открытки, потом скрыть адрес и загрузить 11 фото из `~/Projects/locksmitch-bing-photos`.

Для Claude (по команде Димы):
- Генератор страниц (один шаблон + данные) вместо ручной правки 52 файлов.
- Городские страницы на 92-97% одинаковые: добавить по 2-3 реальных работы на город.
- Страница цен ("from" цены, нужны цифры Димы) и страница "About / Meet Mitch".
- Блок отзывов и aggregateRating, когда появятся реальные отзывы.
- 11 реальных фото работ пока не используются, галерея зависит от Instagram.
- 3D-модель брелока в hero: прототип есть (Three.js, артефакт v3), на сайт не выложен, ждёт одобрения.
- Перед Google Ads: GA4 key events -> конверсии, страницы марок исключить из рекламы до проверки покрытия.

## Связанные проекты

- `~/Projects/LocksMitch-bot` - Telegram-бот, принимает заявки с формы, с телефона и из онлайн-записи. Его STATUS.md описывает ассистента ElevenLabs, Make и Twilio.
- Память Claude по сайту и бизнесу лежит в основном в проекте бота (`~/.claude/projects/-Users-dima-Projects-LocksMitch-bot/memory`).
