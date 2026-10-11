import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "fantasy_league.db")

def get_db_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=DB_PATH):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS managers (
        manager_id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        yahoo_guid_or_slug TEXT,
        yahoo_profile_url TEXT,
        avatar_url TEXT,
        is_active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS seasons (
        year INTEGER PRIMARY KEY,
        league_name TEXT,
        num_teams INTEGER,
        regular_season_weeks INTEGER DEFAULT 14,
        playoff_weeks INTEGER DEFAULT 3,
        champion_team_id TEXT,
        runner_up_team_id TEXT,
        scoring_type TEXT DEFAULT 'Half-PPR'
    );

    CREATE TABLE IF NOT EXISTS teams (
        team_id TEXT PRIMARY KEY,
        season_year INTEGER NOT NULL,
        manager_id TEXT NOT NULL,
        team_name TEXT NOT NULL,
        final_rank INTEGER,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        ties INTEGER DEFAULT 0,
        points_for REAL DEFAULT 0.0,
        points_against REAL DEFAULT 0.0,
        moves INTEGER DEFAULT 0,
        trades INTEGER DEFAULT 0,
        faab_remaining REAL,
        FOREIGN KEY (season_year) REFERENCES seasons(year),
        FOREIGN KEY (manager_id) REFERENCES managers(manager_id)
    );

    CREATE TABLE IF NOT EXISTS matchups (
        matchup_id TEXT PRIMARY KEY,
        season_year INTEGER NOT NULL,
        week INTEGER NOT NULL,
        team1_id TEXT NOT NULL,
        team1_score REAL NOT NULL,
        team2_id TEXT NOT NULL,
        team2_score REAL NOT NULL,
        is_playoffs INTEGER DEFAULT 0,
        is_championship INTEGER DEFAULT 0,
        FOREIGN KEY (season_year) REFERENCES seasons(year),
        FOREIGN KEY (team1_id) REFERENCES teams(team_id),
        FOREIGN KEY (team2_id) REFERENCES teams(team_id)
    );

    CREATE TABLE IF NOT EXISTS draft_picks (
        pick_id TEXT PRIMARY KEY,
        season_year INTEGER NOT NULL,
        round INTEGER NOT NULL,
        pick_overall INTEGER NOT NULL,
        team_id TEXT NOT NULL,
        player_name TEXT NOT NULL,
        position TEXT NOT NULL,
        nfl_team TEXT,
        is_keeper INTEGER DEFAULT 0,
        keeper_cost REAL,
        projected_rank INTEGER,
        FOREIGN KEY (season_year) REFERENCES seasons(year),
        FOREIGN KEY (team_id) REFERENCES teams(team_id)
    );

    CREATE TABLE IF NOT EXISTS rosters (
        roster_id TEXT PRIMARY KEY,
        season_year INTEGER NOT NULL,
        team_id TEXT NOT NULL,
        player_name TEXT NOT NULL,
        position TEXT NOT NULL,
        roster_slot TEXT,
        fan_pts REAL,
        FOREIGN KEY (season_year) REFERENCES seasons(year),
        FOREIGN KEY (team_id) REFERENCES teams(team_id)
    );

    CREATE TABLE IF NOT EXISTS transactions (
        tx_id TEXT PRIMARY KEY,
        season_year INTEGER NOT NULL,
        team_id TEXT,
        tx_type TEXT,
        player_name TEXT,
        position TEXT,
        date_str TEXT,
        FOREIGN KEY (season_year) REFERENCES seasons(year),
        FOREIGN KEY (team_id) REFERENCES teams(team_id)
    );

    CREATE INDEX IF NOT EXISTS idx_teams_season ON teams(season_year);
    CREATE INDEX IF NOT EXISTS idx_teams_manager ON teams(manager_id);
    CREATE INDEX IF NOT EXISTS idx_matchups_season_week ON matchups(season_year, week);
    CREATE INDEX IF NOT EXISTS idx_draft_picks_season ON draft_picks(season_year);
    CREATE INDEX IF NOT EXISTS idx_rosters_season_team ON rosters(season_year, team_id);
    CREATE INDEX IF NOT EXISTS idx_transactions_season ON transactions(season_year);
    ''')

    conn.commit()
    conn.close()
    print(f"Database schema initialized at {db_path}")

def slugify_manager_name(name):
    clean = re.sub(r'[^a-zA-Z0-9]+', '_', name.strip().lower()).strip('_')
    return f"m_{clean}" if clean else "m_unknown"

if __name__ == "__main__":
    init_db()
