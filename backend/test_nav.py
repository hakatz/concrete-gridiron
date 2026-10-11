import sys
import time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('backend')
from scrape_history import YahooScraper
from bs4 import BeautifulSoup

s = YahooScraper(headless=True)
s.start()

s.page.goto('https://football.fantasysports.yahoo.com/f1/503435', wait_until='domcontentloaded')

print('Submitting gotoseason for 2024...')
with s.page.expect_navigation(wait_until='domcontentloaded'):
    s.page.select_option('#seasonspec', '2024_concretegridiron')
    s.page.evaluate('document.querySelector("#seasonspec").form.submit()')

time.sleep(3)
print('Final URL after gotoseason:', s.page.url)
print('Final Page Title:', s.page.title())

soup = BeautifulSoup(s.page.content(), 'lxml')
tbls = soup.find_all('table')
print(f'Total tables found: {len(tbls)}')
for idx, tbl in enumerate(tbls):
    print('Table', idx, 'class:', tbl.get('class'))
    for r in tbl.find_all('tr')[:4]:
        print('  ', [c.text.strip() for c in r.find_all(['th', 'td'])])

s.close()
