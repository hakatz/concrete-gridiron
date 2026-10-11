import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('backend')
from scrape_history import YahooScraper
from bs4 import BeautifulSoup
import re

s = YahooScraper(headless=True)
s.start()

s.page.goto('https://football.fantasysports.yahoo.com/2024/f1/161462?matchup_week=1&module=matchups&lhst=matchups', wait_until='domcontentloaded')
soup = BeautifulSoup(s.page.content(), 'lxml')

matchup_list = soup.find(id=re.compile(r'matchupweek|matchups|scoreboard', re.I))
if matchup_list:
    print('Found matchup module by ID:', matchup_list.get('id'))
    for tr in matchup_list.find_all('tr'):
        cells = [c.text.strip().replace('\n', ' ') for c in tr.find_all(['th', 'td'])]
        if cells:
            print(' ', cells)
    for a in matchup_list.find_all('a', href=True):
        if 'mid' in a['href']:
            print('  Matchup link:', a.text.strip(), '->', a['href'])
else:
    print('No matchup module found by ID. Checking all tables...')
    for idx, tbl in enumerate(soup.find_all('table')):
        print('Table', idx, 'class:', tbl.get('class'))
        for tr in tbl.find_all('tr')[:3]:
            print(' ', [c.text.strip().replace('\n', ' ') for c in tr.find_all(['th', 'td'])])

s.close()
