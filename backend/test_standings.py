import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('backend')
from scrape_history import YahooScraper
from bs4 import BeautifulSoup

s = YahooScraper(headless=True)
s.start()

s.page.goto('https://football.fantasysports.yahoo.com/2024/f1/161462?lhst=stand#leaguehomestandings', wait_until='domcontentloaded')
soup = BeautifulSoup(s.page.content(), 'lxml')

for tbl in soup.find_all('table'):
    print('Table class:', tbl.get('class'))
    for r in tbl.find_all('tr')[:5]:
        print('  ', [c.text.strip().replace('\n', ' ') for c in r.find_all(['th', 'td'])])

s.close()
