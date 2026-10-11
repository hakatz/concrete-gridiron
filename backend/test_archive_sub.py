import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('backend')
from scrape_history import YahooScraper
from bs4 import BeautifulSoup

s = YahooScraper(headless=True)
s.start()

base = 'https://football.fantasysports.yahoo.com/league/concretegridiron/2024'
for sub in ['', '/standings', '/draftresults', '/matchup?week=1', '/matchup?week=16']:
    url = f'{base}{sub}'
    cache_name = '2024_arch_' + sub.replace('/', '_').replace('?', '_') + '.html'
    html = s.fetch_page(url, cache_name)
    soup = BeautifulSoup(html, 'lxml')
    tbls = soup.find_all('table')
    print('URL:', url)
    print('Title:', s.page.title())
    print('Tables:', len(tbls))
    for idx, t in enumerate(tbls[:2]):
        first_row = t.find('tr')
        if first_row:
            print(f'  Tbl {idx} row 0:', [c.text.strip().replace('\n', ' ') for c in first_row.find_all(['th', 'td'])])

s.close()
