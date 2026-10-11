import os
import sys
import re
import json
import time
import argparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))
from db import get_db_connection, init_db, slugify_manager_name

SEASON_LEAGUE_MAP = {
    2014: '368009',
    2015: '109669',
    2016: '397496',
    2017: '225679',
    2018: '200481',
    2019: '210691',
    2020: '23086',
    2021: '52365',
    2022: '669580',
    2023: '239527',
    2024: '161462',
    2025: '580187'
}

SESSION_PATH = os.path.join(os.path.dirname(__file__), "session.json")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

POS_MAP = {
    'patrick mahomes': 'QB', 'josh allen': 'QB', 'jalen hurts': 'QB', 'lamar jackson': 'QB', 'joe burrow': 'QB',
    'dak prescott': 'QB', 'cj stroud': 'QB', 'c.j. stroud': 'QB', 'kyler murray': 'QB', 'anthony richardson': 'QB',
    'anthony richardson sr.': 'QB', 'justin herbert': 'QB', 'jordan love': 'QB', 'tua tagovailoa': 'QB',
    'brock purdy': 'QB', 'jayden daniels': 'QB', 'caleb williams': 'QB', 'aaron rodgers': 'QB', 'tom brady': 'QB',
    'drew brees': 'QB', 'russell wilson': 'QB', 'cam newton': 'QB', 'andrew luck': 'QB', 'matt ryan': 'QB',
    'matthew stafford': 'QB', 'philip rivers': 'QB', 'deshaun watson': 'QB', 'kirk cousins': 'QB', 'baker mayfield': 'QB',
    'trevor lawrence': 'QB', 'geno smith': 'QB', 'jared goff': 'QB', 'justin fields': 'QB',
    'christian mccaffrey': 'RB', 'bijan robinson': 'RB', 'breece hall': 'RB', 'jahmyr gibbs': 'RB', 'saquon barkley': 'RB',
    'jonathan taylor': 'RB', 'derrick henry': 'RB', 'kyren williams': 'RB', 'travis etienne': 'RB', 'travis etienne jr.': 'RB',
    'de\'von achane': 'RB', 'devon achane': 'RB', 'isiah pacheco': 'RB', 'james cook': 'RB', 'josh jacobs': 'RB',
    'rachaad white': 'RB', 'alvin kamara': 'RB', 'kenneth walker': 'RB', 'kenneth walker iii': 'RB', 'joe mixon': 'RB',
    'd\'andre swift': 'RB', 'david montgomery': 'RB', 'james conner': 'RB', 'tony pollard': 'RB', 'raheem mostert': 'RB',
    'austin ekeler': 'RB', 'nick chubb': 'RB', 'dalvin cook': 'RB', 'ezekiel elliott': 'RB', 'todd gurley': 'RB',
    'todd gurley ii': 'RB', 'le\'veon bell': 'RB', 'david johnson': 'RB', 'adrian peterson': 'RB', 'lesean mccoy': 'RB',
    'jamaal charles': 'RB', 'marshawn lynch': 'RB', 'matt forte': 'RB', 'eddie lacy': 'RB', 'demarco murray': 'RB',
    'melvin gordon': 'RB', 'devonta freeman': 'RB', 'aaron jones': 'RB', 'najee harris': 'RB', 'chuba hubbard': 'RB',
    'ceedee lamb': 'WR', 'tyreek hill': 'WR', 'justin jefferson': 'WR', 'ja\'marr chase': 'WR', 'amon-ra st. brown': 'WR',
    'a.j. brown': 'WR', 'aj brown': 'WR', 'garrett wilson': 'WR', 'puka nacua': 'WR', 'marvin harrison jr.': 'WR',
    'chris olave': 'WR', 'drake london': 'WR', 'mike evans': 'WR', 'davante adams': 'WR', 'nico collins': 'WR',
    'brandon aiyuk': 'WR', 'deebo samuel': 'WR', 'deebo samuel sr.': 'WR', 'michael pittman jr.': 'WR', 'dk metcalf': 'WR',
    'd.k. metcalf': 'WR', 'devonta smith': 'WR', 'dj moore': 'WR', 'd.j. moore': 'WR', 'malik nabers': 'WR', 'jaylen waddle': 'WR',
    'stefon diggs': 'WR', 'cooper kupp': 'WR', 'george pickens': 'WR', 'tee higgins': 'WR', 'amari cooper': 'WR',
    'zay flowers': 'WR', 'tank dell': 'WR', 'christian kirk': 'WR', 'rashee rice': 'WR', 'terry mclaurin': 'WR',
    'antonio brown': 'WR', 'julio jones': 'WR', 'odell beckham jr.': 'WR', 'demaryius thomas': 'WR', 'dez bryant': 'WR',
    'calvin johnson': 'WR', 'a.j. green': 'WR', 'jordy nelson': 'WR', 'deandre hopkins': 'WR', 'michael thomas': 'WR',
    'travis kelce': 'TE', 'sam laporta': 'TE', 'trey mcbride': 'TE', 'mark andrews': 'TE', 'dalton kincaid': 'TE',
    'george kittle': 'TE', 'kyle pitts': 'TE', 'evan engram': 'TE', 'brock bowers': 'TE', 'david njoku': 'TE',
    'rob gronkowski': 'TE', 'jimmy graham': 'TE', 'greg olsen': 'TE', 'zach ertz': 'TE', 'darren waller': 'TE',
    'justin tucker': 'K', 'brandon aubrey': 'K', 'harrison butker': 'K', 'jake elliott': 'K'
}

def infer_position(name, round_num=10):
    clean = name.strip().lower()
    if clean in POS_MAP: return POS_MAP[clean]
    for k, v in POS_MAP.items():
        if k in clean or clean in k: return v
    if 'def' in clean or 'defense' in clean: return 'DEF'
    if round_num >= 15: return 'K'
    if round_num >= 14: return 'DEF'
    if round_num <= 2: return 'RB'
    if round_num <= 6: return 'WR'
    return 'FLEX'

class YahooHistoryScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):
        if not os.path.exists(SESSION_PATH):
            print(f"Error: {SESSION_PATH} not found. Run auth_setup.py first!")
            return False
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.context = self.browser.new_context(
            storage_state=SESSION_PATH,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        self.page = self.context.new_page()
        return True

    def close(self):
        if self.browser: self.browser.close()
        if self.playwright: self.playwright.stop()

    def get_html(self, url, cache_file):
        cache_path = os.path.join(CACHE_DIR, cache_file)
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = f.read()
                if "Request denied" not in cached and len(cached) >= 500:
                    return cached
                else:
                    print(f"  [Invalid Cache] {cache_file} contains error ({len(cached)} bytes). Refetching...")

        for attempt in range(1, 4):
            print(f"  [Scraping Attempt {attempt}] {url}")
            try:
                self.page.goto(url, wait_until="domcontentloaded", timeout=25000)
                time.sleep(1.2 + (attempt * 0.5))
                content = self.page.content()
                if "Request denied" not in content and len(content) >= 500:
                    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                    with open(cache_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    return content
                else:
                    print(f"  [Rate Limited] Attempt {attempt} returned {len(content)} bytes. Pausing {attempt * 6}s before retry...")
                    time.sleep(attempt * 6)
            except Exception as e:
                print(f"  Attempt {attempt} failed for {url}: {e}")
                time.sleep(attempt * 5)
        return ""

KNOWN_GUID_MAP = {
    "26TG3YXEN5547IBHY2XRF4V23Q": {"mid": "m_harrison", "name": "Harrison", "active": 1},
    "GO76MXXPJMC7E7QLTLGUVD4T6M": {"mid": "m_jeremy", "name": "Jeremy", "active": 1},
    "BRAGIZ6G55FAW64FLAWOI3HFZU": {"mid": "m_harris", "name": "Harris", "active": 1},
    "I26SK4KBBFKWKOXSKWB56LJS7Q": {"mid": "m_ross", "name": "Ross Senter", "active": 1},
    "KEBE3WKGE35GXREW4MKCJIRASI": {"mid": "m_evan", "name": "Evan", "active": 1},
    "F2TAYSNBO5HGCC7CXEH3GJ4RTA": {"mid": "m_johnny_n", "name": "Johnny N", "active": 1},
    "GGJ2G7O7K2SCYYQQMZZWESZI4M": {"mid": "m_salomon", "name": "Salomon", "active": 1},
    "PI3BW63YIVO77TMBI5XW5GUBH4": {"mid": "m_michael", "name": "Michael", "active": 1},
    "D2SDCSSKQOZCUHUMFBMTMP5TUI": {"mid": "m_michael", "name": "Michael", "active": 1},
    "7IDZST64UCFTCNJNVVNSWAVX2M": {"mid": "m_bryan", "name": "Bryan", "active": 1},
    "VWDXZTFTMWH3VM3WCA3Z57K2UI": {"mid": "m_bryan", "name": "Bryan", "active": 1},
    "KYVJTN2QTVOSZA6U6MEG7NKKVA": {"mid": "m_neil", "name": "Neil", "active": 1},
    "ZYEZVYNVXHYF2AJFKPKSTNCU7E": {"mid": "m_steven", "name": "Steven", "active": 1},
    "RGAS7VHBN2SBAXC3EAAGW53LOE": {"mid": "m_ryan", "name": "Ryan Blaustein", "active": 1},
    "3TJZOKBERXSLJDW2RORZDOPHF4": {"mid": "m_jeremy_gilstein", "name": "Jeremy Gilstein", "active": 0},
    "76KXFKZ5RBLEFTPE4KYM7SZHBY": {"mid": "m_scott", "name": "Scott", "active": 0},
    "7643BC3URB47YWZMZ2QKEZRZAA": {"mid": "m_andrew", "name": "Andrew", "active": 0},
}

KNOWN_EMAIL_MAP = {
    "hakatz6@gmail.com": ("m_harrison", "Harrison", 1),
    "kreitmaster@gmail.com": ("m_jeremy", "Jeremy", 1),
    "hdschatz@gmail.com": ("m_harris", "Harris", 1),
    "rsenter11@gmail.com": ("m_ross", "Ross Senter", 1),
    "ecrothman@gmail.com": ("m_evan", "Evan", 1),
    "snahon21@gmail.com": ("m_salomon", "Salomon", 1),
    "mmarcus09@gmail.com": ("m_michael", "Michael", 1),
    "bkatz720@gmail.com": ("m_bryan", "Bryan", 1),
    "nhmendy@gmail.com": ("m_neil", "Neil", 1),
    "sml71389@yahoo.com": ("m_steven", "Steven", 1),
    "jgilstein@gmail.com": ("m_jeremy_gilstein", "Jeremy Gilstein", 0),
    "sternberg.scott@gmail.com": ("m_scott", "Scott", 0),
    "lilzv2@yahoo.com": ("m_andrew", "Andrew", 0),
}

def normalize_manager_name(name):
    clean = re.sub(r'Commissioner|Co-Manager', '', name, flags=re.I).strip()
    return clean if clean else "Unknown Manager"

def run_etl(years_to_scrape=None, clear_db=True):
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()

    if clear_db:
        print("Clearing database tables for clean historical ingestion...")
        cur.execute("DELETE FROM transactions")
        cur.execute("DELETE FROM rosters")
        cur.execute("DELETE FROM draft_picks")
        cur.execute("DELETE FROM matchups")
        cur.execute("DELETE FROM teams")
        cur.execute("DELETE FROM seasons")
        cur.execute("DELETE FROM managers")
        conn.commit()

    scraper = YahooHistoryScraper(headless=True)
    if not scraper.start():
        print("Cannot start scraper. Aborting.")
        return

    years = sorted([y for y in (years_to_scrape or SEASON_LEAGUE_MAP.keys()) if y in SEASON_LEAGUE_MAP])
    print(f"Starting full historical ETL for seasons: {years}")

    manager_registry = {}
    season_team_meta = {}

    try:
        # Step 1: Collect manager identities & team stats across all seasons
        print("\n--- Step 1: Indexing Managers, Waiver Moves & Historical Team Names ---")
        for yr in years:
            lid = SEASON_LEAGUE_MAP[yr]
            teams_url = f"https://football.fantasysports.yahoo.com/{yr}/f1/{lid}/teams"
            html = scraper.get_html(teams_url, f"{yr}/teams.html")
            soup = BeautifulSoup(html, "lxml")

            tbl = soup.find("table")
            if not tbl:
                continue

            for row in tbl.find_all("tr")[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) < 3:
                    continue

                # Skip Co-Manager rows entirely
                if "co-manager" in cells[0].text.lower() or "co-manager" in cells[1].text.lower():
                    continue

                team_link = cells[0].find("a", href=True)
                team_name = cells[0].text.strip()
                raw_tid = "1"
                if team_link:
                    m = re.search(r"/(\d+)$", team_link["href"])
                    if m: raw_tid = m.group(1)

                manager_raw = cells[1].text.strip()
                manager_clean = normalize_manager_name(manager_raw)
                email = cells[2].text.strip().lower() if len(cells) > 2 else ""

                # Extract Yahoo profile GUID & link
                m_link = cells[1].find("a", href=True)
                profile_url = ""
                yahoo_guid = ""
                if m_link and "href" in m_link.attrs:
                    href = m_link["href"]
                    if href.startswith("/"):
                        profile_url = f"https://profiles.sports.yahoo.com{href}"
                    elif href.startswith("http"):
                        profile_url = href
                    guid_m = re.search(r"/user/([A-Z0-9]+)", href)
                    if guid_m:
                        yahoo_guid = guid_m.group(1)

                # Moves, Trades, Waiver Budget
                budget_str = cells[3].text.strip().replace("$", "") if len(cells) > 3 else "0"
                moves_str = cells[5].text.strip() if len(cells) > 5 else "0"
                trades_str = cells[6].text.strip() if len(cells) > 6 else "0"
                try: budget = float(budget_str)
                except: budget = 0.0
                try: moves = int(moves_str)
                except: moves = 0
                try: trades = int(trades_str)
                except: trades = 0

                # Resolve Manager Identity
                assigned_mid = None
                display_name = manager_clean
                is_active = 1

                # Check Jamie / Bungs Anonymous
                if "bungs anonymous" in team_name.lower() or "bungs" in team_name.lower():
                    assigned_mid = "m_jamie"
                    display_name = "Jamie"
                    is_active = 0
                elif yahoo_guid and yahoo_guid in KNOWN_GUID_MAP:
                    k_info = KNOWN_GUID_MAP[yahoo_guid]
                    assigned_mid = k_info["mid"]
                    display_name = k_info["name"]
                    is_active = k_info["active"]
                elif email and email in KNOWN_EMAIL_MAP:
                    mid, name, act = KNOWN_EMAIL_MAP[email]
                    assigned_mid = mid
                    display_name = name
                    is_active = act
                elif "johnny" in manager_clean.lower():
                    assigned_mid = "m_johnny_n"
                    display_name = "Johnny N"
                    is_active = 1
                elif yahoo_guid:
                    assigned_mid = f"m_{yahoo_guid.lower()}"
                    display_name = manager_clean
                    is_active = 1
                elif email and "@" in email:
                    assigned_mid = slugify_manager_name(email.split("@")[0])
                    display_name = manager_clean
                    is_active = 1
                else:
                    assigned_mid = slugify_manager_name(manager_clean)
                    display_name = manager_clean
                    is_active = 1

                if assigned_mid not in manager_registry:
                    manager_registry[assigned_mid] = {
                        "manager_id": assigned_mid,
                        "display_name": display_name,
                        "yahoo_guid": yahoo_guid or assigned_mid.replace("m_", ""),
                        "yahoo_profile_url": profile_url or (f"https://profiles.sports.yahoo.com/user/{yahoo_guid}" if yahoo_guid else None),
                        "is_active": is_active,
                        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
                    }
                else:
                    if profile_url and not manager_registry[assigned_mid]["yahoo_profile_url"]:
                        manager_registry[assigned_mid]["yahoo_profile_url"] = profile_url
                    if yahoo_guid and not manager_registry[assigned_mid]["yahoo_guid"]:
                        manager_registry[assigned_mid]["yahoo_guid"] = yahoo_guid

                t_key = (yr, raw_tid)
                meta = {
                    "team_id": f"t_{yr}_{raw_tid}",
                    "raw_tid": raw_tid,
                    "manager_id": assigned_mid,
                    "team_name": team_name,
                    "moves": moves,
                    "trades": trades,
                    "budget": budget
                }
                season_team_meta[t_key] = meta
                season_team_meta[(yr, team_name.lower())] = meta

        print(f"Unified {len(manager_registry)} unique managers:")
        for mid, minfo in manager_registry.items():
            print(f"  [{'Active' if minfo['is_active'] else 'Inactive'}] {minfo['display_name']} ({mid}) -> {minfo['yahoo_profile_url']}")
            cur.execute(
                "INSERT OR REPLACE INTO managers (manager_id, display_name, yahoo_guid_or_slug, yahoo_profile_url, avatar_url, is_active) VALUES (?, ?, ?, ?, ?, ?)",
                (mid, minfo["display_name"], minfo["yahoo_guid"], minfo["yahoo_profile_url"], minfo["avatar_url"], minfo["is_active"])
            )
        conn.commit()

        # Step 2: Standings, Podiums, Rosters, Transactions, Drafts & Matchups
        print("\n--- Step 2: Extracting Standings, Podiums, Rosters, Drafts & Matchups ---")
        for yr in years:
            lid = SEASON_LEAGUE_MAP[yr]
            print(f"\nProcessing Season {yr} (League {lid})...")

            # Standings & Podium
            stand_url = f"https://football.fantasysports.yahoo.com/{yr}/f1/{lid}?lhst=stand#leaguehomestandings"
            stand_html = scraper.get_html(stand_url, f"{yr}/standings.html")
            soup_stand = BeautifulSoup(stand_html, "lxml")

            champ_tid = None
            ru_tid = None

            podium = soup_stand.find("table", class_=re.compile(r"Mbot-xl", re.I))
            if podium:
                p_rows = podium.find_all("tr")
                if len(p_rows) > 1:
                    champ_cell = p_rows[1].find_all(["td", "th"])[0]
                    champ_a = champ_cell.find("a", href=True)
                    if champ_a:
                        m_c = re.search(r"/(\d+)$", champ_a["href"])
                        if m_c and (yr, m_c.group(1)) in season_team_meta:
                            champ_tid = season_team_meta[(yr, m_c.group(1))]["team_id"]
                    if not champ_tid:
                        champ_name = champ_cell.text.strip()
                        if (yr, champ_name.lower()) in season_team_meta:
                            champ_tid = season_team_meta[(yr, champ_name.lower())]["team_id"]

                    if len(p_rows[1].find_all(["td", "th"])) > 1:
                        ru_cell = p_rows[1].find_all(["td", "th"])[1]
                        ru_a = ru_cell.find("a", href=True)
                        if ru_a:
                            m_r = re.search(r"/(\d+)$", ru_a["href"])
                            if m_r and (yr, m_r.group(1)) in season_team_meta:
                                ru_tid = season_team_meta[(yr, m_r.group(1))]["team_id"]
                        if not ru_tid:
                            ru_name = ru_cell.text.strip()
                            if (yr, ru_name.lower()) in season_team_meta:
                                ru_tid = season_team_meta[(yr, ru_name.lower())]["team_id"]

            cur.execute(
                "INSERT OR REPLACE INTO seasons (year, league_name, num_teams, regular_season_weeks, playoff_weeks, champion_team_id, runner_up_team_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (yr, f"Concrete Gridiron ({yr})", 12, 14, 3, champ_tid, ru_tid)
            )

            # Standings rows
            stand_tbl = soup_stand.find("table", class_=re.compile(r"Table-interactive", re.I)) or soup_stand.find("table", class_=re.compile(r"Table-underline", re.I))
            season_teams = {}
            if stand_tbl:
                for row in stand_tbl.find_all("tr")[1:]:
                    cells = row.find_all(["td", "th"])
                    if len(cells) < 5:
                        continue
                    rank_txt = re.sub(r"[^\d]", "", cells[0].text.strip())
                    rank = int(rank_txt) if rank_txt else 0
                    t_name = re.sub(r"[^\x00-\x7F]+", "", cells[1].text).strip()
                    wlt = cells[2].text.strip()
                    wlt_m = re.match(r"(\d+)-(\d+)(?:-(\d+))?", wlt)
                    wins = int(wlt_m.group(1)) if wlt_m else 0
                    losses = int(wlt_m.group(2)) if wlt_m else 0
                    ties = int(wlt_m.group(3)) if (wlt_m and wlt_m.group(3)) else 0
                    pf_txt = cells[3].text.strip().replace(",", "")
                    pa_txt = cells[4].text.strip().replace(",", "")
                    pf = float(pf_txt) if pf_txt else 0.0
                    pa = float(pa_txt) if pa_txt else 0.0

                    t_a = cells[1].find("a", href=True)
                    t_num = None
                    if t_a:
                        m_tnum = re.search(r"/(\d+)$", t_a["href"])
                        if m_tnum:
                            t_num = m_tnum.group(1)

                    t_meta = None
                    if t_num and (yr, t_num) in season_team_meta:
                        t_meta = season_team_meta[(yr, t_num)]
                    if not t_meta:
                        t_meta = season_team_meta.get((yr, t_name.lower()))
                    if not t_meta:
                        # Fuzzy match
                        for (s_yr, s_tname), s_m in season_team_meta.items():
                            if s_yr == yr and isinstance(s_tname, str) and (s_tname in t_name.lower() or t_name.lower() in s_tname):
                                t_meta = s_m
                                break

                    if not t_meta:
                        tid = f"t_{yr}_{len(season_teams)+1}"
                        mid = list(manager_registry.keys())[0] if manager_registry else "m_unknown"
                        moves, trades, budget = 0, 0, 0.0
                    else:
                        tid = t_meta["team_id"]
                        mid = t_meta["manager_id"]
                        moves = t_meta["moves"]
                        trades = t_meta["trades"]
                        budget = t_meta["budget"]

                    season_teams[tid] = {
                        "team_id": tid, "season_year": yr, "manager_id": mid,
                        "team_name": t_name, "final_rank": rank, "wins": wins, "losses": losses, "ties": ties,
                        "points_for": pf, "points_against": pa, "moves": moves, "trades": trades, "faab_remaining": budget
                    }
                    cur.execute(
                        "INSERT OR REPLACE INTO teams (team_id, season_year, manager_id, team_name, final_rank, wins, losses, ties, points_for, points_against, moves, trades, faab_remaining) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (tid, yr, mid, t_name, rank, wins, losses, ties, pf, pa, moves, trades, budget)
                    )

            # Rosters per team (1 to 12)
            for t_num in range(1, 13):
                roster_url = f"https://football.fantasysports.yahoo.com/{yr}/f1/{lid}/{t_num}"
                r_html = scraper.get_html(roster_url, f"{yr}/team_{t_num}_roster.html")
                soup_r = BeautifulSoup(r_html, "lxml")
                tid = f"t_{yr}_{t_num}"

                for tbl in soup_r.find_all("table", id=re.compile(r"statTable\d+")):
                    for tr in tbl.find_all("tr"):
                        cells = tr.find_all(["td", "th"])
                        if len(cells) < 4:
                            continue
                        slot = cells[0].text.strip()
                        p_link = cells[1].find("a", class_=re.compile(r"name|player", re.I))
                        if p_link:
                            p_name = p_link.text.strip()
                            pos = infer_position(p_name)
                            try: pts = float(cells[3].text.strip())
                            except: pts = 0.0
                            r_id = f"r_{yr}_{t_num}_{p_name.lower().replace(' ', '_')}"
                            cur.execute(
                                "INSERT OR REPLACE INTO rosters (roster_id, season_year, team_id, player_name, position, roster_slot, fan_pts) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (r_id, yr, tid, p_name, pos, slot, pts)
                            )

            # Transactions (Waiver / Free Agency moves log)
            tx_url = f"https://football.fantasysports.yahoo.com/{yr}/f1/{lid}/transactions"
            tx_html = scraper.get_html(tx_url, f"{yr}/transactions.html")
            soup_tx = BeautifulSoup(tx_html, "lxml")
            tx_tbl = soup_tx.find("table", class_=re.compile(r"transaction", re.I))
            if tx_tbl:
                for tx_idx, tr in enumerate(tx_tbl.find_all("tr")[1:]):
                    cells = tr.find_all(["td", "th"])
                    if len(cells) < 3:
                        continue
                    action_txt = cells[1].text.strip().replace("\n", " ")
                    team_meta_cell = cells[2].text.strip()
                    tx_id = f"tx_{yr}_{tx_idx}"
                    cur.execute(
                        "INSERT OR REPLACE INTO transactions (tx_id, season_year, team_id, tx_type, player_name, position, date_str) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (tx_id, yr, None, "FA/Waiver", action_txt[:100], "FLEX", team_meta_cell)
                    )

            # Draft Results
            draft_url = f"https://football.fantasysports.yahoo.com/{yr}/f1/{lid}/draftresults"
            draft_html = scraper.get_html(draft_url, f"{yr}/draftresults.html")
            soup_draft = BeautifulSoup(draft_html, "lxml")
            draft_tables = soup_draft.find_all("table")

            pick_overall = 1
            for rnd_idx, d_tbl in enumerate(draft_tables, start=1):
                for row in d_tbl.find_all("tr"):
                    cells = row.find_all(["td", "th"])
                    if len(cells) < 3:
                        continue
                    p_num = cells[0].text.strip().replace(".", "")
                    if not p_num.isdigit():
                        continue
                    p_name_raw = cells[1].text.strip()
                    p_name = re.sub(r"\(.*?\)", "", p_name_raw).strip()
                    pos = infer_position(p_name, rnd_idx)

                    drafted_team_name = cells[2].text.strip()
                    team_a = cells[2].find("a", href=True)
                    tid = None
                    if team_a:
                        m_tid = re.search(r"/(\d+)$", team_a["href"])
                        if m_tid and (yr, m_tid.group(1)) in season_team_meta:
                            tid = season_team_meta[(yr, m_tid.group(1))]["team_id"]
                    if not tid:
                        t_meta = season_team_meta.get((yr, drafted_team_name.lower()))
                        if not t_meta:
                            # Fuzzy match team name in season_team_meta
                            for (s_yr, s_tname), s_meta in season_team_meta.items():
                                if s_yr == yr and isinstance(s_tname, str) and (s_tname in drafted_team_name.lower() or drafted_team_name.lower() in s_tname):
                                    t_meta = s_meta
                                    break
                        tid = t_meta["team_id"] if t_meta else f"t_{yr}_1"

                    cur.execute(
                        "INSERT OR REPLACE INTO draft_picks (pick_id, season_year, round, pick_overall, team_id, player_name, position, nfl_team, is_keeper, keeper_cost, projected_rank) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (f"dp_{yr}_{pick_overall}", yr, rnd_idx, pick_overall, tid, p_name, pos, "NFL", 0, None, pick_overall)
                    )
                    pick_overall += 1

            # Matchups (Weeks 1 through 16)
            for w in range(1, 17):
                m_url = f"https://football.fantasysports.yahoo.com/{yr}/f1/{lid}?matchup_week={w}&module=matchups&lhst=matchups"
                m_html = scraper.get_html(m_url, f"{yr}/matchup_w{w}.html")
                soup_m = BeautifulSoup(m_html, "lxml")
                mod = soup_m.find(id="matchupweek")
                if not mod:
                    continue

                for li in mod.find_all("li"):
                    m_link = li.find("a", href=re.compile(r"mid1=(\d+)&mid2=(\d+)"))
                    if not m_link:
                        continue
                    m_params = re.search(r"mid1=(\d+)&mid2=(\d+)", m_link["href"])
                    tid1_num = m_params.group(1)
                    tid2_num = m_params.group(2)
                    tid1 = f"t_{yr}_{tid1_num}"
                    tid2 = f"t_{yr}_{tid2_num}"

                    scores = re.findall(r"\b\d{1,3}\.\d{2}\b", li.text)
                    if len(scores) >= 2:
                        s1 = float(scores[0])
                        s2 = float(scores[1])
                    else:
                        continue

                    is_playoff = 1 if w >= 15 else 0
                    is_champ = 1 if (w == 16 and (tid1 == champ_tid or tid2 == champ_tid)) else 0

                    mid_key = f"m_{yr}_w{w}_{tid1_num}_vs_{tid2_num}"
                    cur.execute(
                        "INSERT OR REPLACE INTO matchups (matchup_id, season_year, week, team1_id, team1_score, team2_id, team2_score, is_playoffs, is_championship) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (mid_key, yr, w, tid1, s1, tid2, s2, is_playoff, is_champ)
                    )

            conn.commit()
            print(f"Season {yr} complete: Standings, Rosters, Transactions, Draft & Matchups ingested.")

    finally:
        scraper.close()
        conn.commit()
        conn.close()
        print("\nFull historical ETL completed successfully!")

    # Step 3: Run analytics engine
    import analytics
    analytics.generate_analytics()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", nargs="+", type=int, help="Years to run")
    parser.add_argument("--no-clear", action="store_true", help="Do not clear DB")
    args = parser.parse_args()
    run_etl(args.years, clear_db=not args.no_clear)
