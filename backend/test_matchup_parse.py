import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('backend')
from scrape_history import YahooScraper
from bs4 import BeautifulSoup
import re

s = YahooScraper(headless=True)
s.start()

s.page.goto('https://football.fantasysports.yahoo.com/2024/f1/161462/matchup?week=1', wait_until='domcontentloaded')
soup = BeautifulSoup(s.page.content(), 'lxml')

# Look for matchups in page
matchup_blocks = soup.find_all('section', class_=re.compile(r'matchup', re.I)) or soup.find_all('div', class_=re.compile(r'matchup', re.I))
print('Matchup blocks found:', len(matchup_blocks))

# Also check links with /matchup?week=1&mid1= or similar
links = set()
for a in soup.find_all('a', href=True):
    if 'mid' in a['href'] or 'matchup' in a['href']:
        links.add(a['href'])

print('Sample matchup links:')
for l in list(links)[:10]:
    print(' ', l)

# Let's check the scoreboard or matchup tables
tables = soup.find_all('table', class_=re.compile(r'scoreboard|matchup|Table', re.I))
print('Tables count:', len(tables))
for idx, tbl in enumerate(tables[:4]):
    rows = tbl.find_all('tr')
    print(f'Table {idx} rows: {len(rows)}')
    for r in rows[:3]:
        print('  ', [c.text.strip().replace('\n', ' ') for c in r.find_all(['th', 'td'])])

s.close()
