"""Sets <lastmod> in sitemap.xml from git: the date of each page's last commit, or today if the file has uncommitted changes.

Run from the site root before committing a content change:
    python3 -I tools/sitemap_lastmod.py
"""
import datetime, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def main():
    dirty = set(line[3:].strip() for line in git('status', '--porcelain').splitlines())
    sm_path = os.path.join(ROOT, 'sitemap.xml')
    sm = open(sm_path, encoding='utf-8').read()
    changed = 0

    def fix(m):
        nonlocal changed
        url, old = m.group(1), m.group(2)
        path = url.replace('https://locksmitch.com/', '').strip('/')
        rel = (path + '/index.html') if path else 'index.html'
        if not os.path.exists(os.path.join(ROOT, rel)):
            return m.group(0)
        new = TODAY if rel in dirty else (git('log', '-1', '--format=%cs', '--', rel) or old)
        if new != old:
            changed += 1
        return m.group(0).replace('<lastmod>' + old + '</lastmod>', '<lastmod>' + new + '</lastmod>')

    sm = re.sub(r'<url><loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>', fix, sm)
    open(sm_path, 'w', encoding='utf-8').write(sm)
    print('lastmod updated on', changed, 'pages')


main()
