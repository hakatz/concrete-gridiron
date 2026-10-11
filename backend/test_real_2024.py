import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('backend')
from scrape_history import YahooScraper
from bs4 import BeautifulSoup

s = YahooScraper(headless=True)
s.start()

test_urls = [
    'https://football.fantasysports.yahoo.com/2024/f1/161462/draftresults',
    'https://football.fantasysports.yahoo.com/2024/f1/161462/teams',
    'https://football.fantasysports.yahoo.com/2024/f1/161462/matchup?week=1',
    'https://football.fantasysports.yahoo.com/2024/f1/161462/matchup?week=16'
]

for url in test_urls:
    s.page.goto(url, wait_until='domcontentloaded')
    soup = BeautifulSoup(s.page.content(), 'lxml')
    tbls = soup.find_all('table')
    print('URL:', url)
    print('Title:', s.page.title())
    print('Tables count:', len(tbls))
    if tbls:
        for r in tbls[0].find_all('tr')[:3]:
            print('  row:', [c.text.strip().replace('\n', ' ') for c in r.find_all(['th', 'td'])])
    print('-' * 40)

s.close()
