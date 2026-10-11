import sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('backend')
from scrape_history import YahooScraper
from bs4 import BeautifulSoup

s = YahooScraper(headless=True)
s.start()

season_mappings = {}

for yr in range(2013, 2026):
    url = f'https://football.fantasysports.yahoo.com/league/concretegridiron/{yr}'
    try:
        s.page.goto(url, wait_until='domcontentloaded', timeout=15000)
        html = s.page.content()
        soup = BeautifulSoup(html, 'lxml')
        # find link with /<yr>/f1/<id>
        match = None
        for a in soup.find_all('a', href=True):
            m = re.search(rf'/{yr}/f1/(\d+)', a['href'])
            if m:
                match = m.group(1)
                break
        if match:
            season_mappings[yr] = match
            print(f'Year {yr} -> League ID {match}')
        else:
            print(f'Year {yr} -> No historical league ID found on vanity page')
    except Exception as e:
        print(f'Year {yr} error: {e}')

print('All Mappings:', season_mappings)
s.close()
