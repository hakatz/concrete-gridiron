import os
import random
import sqlite3
from db import get_db_connection, init_db

# Deterministic seed for reproducible league stats
random.seed(42)

MANAGERS = [
    {"id": "m_harrison", "name": "Harrison", "slug": "harrison_c", "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"},
    {"id": "m_dave", "name": "Dave Miller", "slug": "dave_m", "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80"},
    {"id": "m_marcus", "name": "Marcus Vance", "slug": "marcus_v", "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80"},
    {"id": "m_sarah", "name": "Sarah Jenkins", "slug": "sarah_j", "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80"},
    {"id": "m_kevin", "name": "Kevin Chen", "slug": "kevin_c", "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80"},
    {"id": "m_alex", "name": "Alex Rivera", "slug": "alex_r", "avatar": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=150&auto=format&fit=crop&q=80"},
    {"id": "m_brandon", "name": "Brandon O'Connor", "slug": "brandon_o", "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80"},
    {"id": "m_tyler", "name": "Tyler Ross", "slug": "tyler_r", "avatar": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80"},
    {"id": "m_chris", "name": "Chris Taylor", "slug": "chris_t", "avatar": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&auto=format&fit=crop&q=80"},
    {"id": "m_jordan", "name": "Jordan Smith", "slug": "jordan_s", "avatar": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=150&auto=format&fit=crop&q=80"},
    {"id": "m_sam", "name": "Sam Patel", "slug": "sam_p", "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&auto=format&fit=crop&q=80"},
    {"id": "m_nick", "name": "Nick Kowalski", "slug": "nick_k", "avatar": "https://images.unsplash.com/photo-1463453091185-61582044d556?w=150&auto=format&fit=crop&q=80"}
]

TEAM_NAME_POOLS = {
    "m_harrison": ["The Gridiron Architects", "Brady's Believers", "Harrison's Heroes", "Fourth & Inches", "Red Zone Raiders"],
    "m_dave": ["Miller Time TD", "Dave's Dynasty", "Blitzkrieg Bop", "Gridiron Grinders"],
    "m_marcus": ["Vance Refrigeration", "Marcus's Monsters", "Touchdown Treason", "Hail Mary Kings"],
    "m_sarah": ["Jenkins Juggernauts", "Sarah's Squad", "Endzone Angels", "Pigskin Perfection"],
    "m_kevin": ["Chen Dynasty", "Kevin's Kicking Game", "Turnover Machine", "Sack City"],
    "m_alex": ["Rivera Renegades", "Alex's Aces", "Goal Line Gang", "Fumble Recoveries"],
    "m_brandon": ["Shamrock Shockers", "Brandon's Badgers", "O'Connor Offense", "Sunday Funday"],
    "m_tyler": ["Ross Thunder", "Tyler's Trenches", "Pocket Passers", "Waiver Wire Kings"],
    "m_chris": ["Chris's Crusaders", "Taylor Made TD", "Fantasy Gods", "Pick Six Patrol"],
    "m_jordan": ["Air Jordan", "Smith's Steamrollers", "No Punt Intended", "Field Goal Freaks"],
    "m_sam": ["Patel Power", "Sam's Sliders", "Curry in the Clutch", "Run CMC Fanatics"],
    "m_nick": ["Kowalski Chaos", "Nick's Nightmares", "Gridiron Glitches", "The Underdogs"]
}

SEASONS = list(range(2013, 2026))

HISTORICAL_COHORTS = {
    2013: [("Adrian Peterson", "RB"), ("Arian Foster", "RB"), ("Doug Martin", "RB"), ("Marshawn Lynch", "RB"), ("Jamaal Charles", "RB"), ("Calvin Johnson", "WR"), ("LeSean McCoy", "RB"), ("Ray Rice", "RB"), ("C.J. Spiller", "RB"), ("Trent Richardson", "RB"), ("Drew Brees", "QB"), ("Aaron Rodgers", "QB"), ("Jimmy Graham", "TE"), ("Dez Bryant", "WR"), ("A.J. Green", "WR"), ("Peyton Manning", "QB")],
    2014: [("LeSean McCoy", "RB"), ("Jamaal Charles", "RB"), ("Adrian Peterson", "RB"), ("Matt Forte", "RB"), ("Eddie Lacy", "RB"), ("Calvin Johnson", "WR"), ("Marshawn Lynch", "RB"), ("Jimmy Graham", "TE"), ("Demaryius Thomas", "WR"), ("Dez Bryant", "WR"), ("Peyton Manning", "QB"), ("DeMarco Murray", "RB"), ("Antonio Brown", "WR"), ("Jordy Nelson", "WR"), ("Rob Gronkowski", "TE"), ("Aaron Rodgers", "QB")],
    2015: [("Adrian Peterson", "RB"), ("Eddie Lacy", "RB"), ("Jamaal Charles", "RB"), ("Marshawn Lynch", "RB"), ("Antonio Brown", "WR"), ("Le'Veon Bell", "RB"), ("Rob Gronkowski", "TE"), ("Julio Jones", "WR"), ("Demaryius Thomas", "WR"), ("Dez Bryant", "WR"), ("Odell Beckham Jr.", "WR"), ("C.J. Anderson", "RB"), ("Andrew Luck", "QB"), ("Aaron Rodgers", "QB"), ("DeAndre Hopkins", "WR"), ("Devonta Freeman", "RB")],
    2016: [("Antonio Brown", "WR"), ("Julio Jones", "WR"), ("Odell Beckham Jr.", "WR"), ("Todd Gurley", "RB"), ("David Johnson", "RB"), ("Adrian Peterson", "RB"), ("Ezekiel Elliott", "RB"), ("DeAndre Hopkins", "WR"), ("A.J. Green", "WR"), ("Lamar Miller", "RB"), ("Rob Gronkowski", "TE"), ("Allen Robinson", "WR"), ("Aaron Rodgers", "QB"), ("Cam Newton", "QB"), ("Mike Evans", "WR"), ("Melvin Gordon", "RB")],
    2017: [("David Johnson", "RB"), ("Le'Veon Bell", "RB"), ("Antonio Brown", "WR"), ("Odell Beckham Jr.", "WR"), ("Julio Jones", "WR"), ("Melvin Gordon", "RB"), ("Mike Evans", "WR"), ("Devonta Freeman", "RB"), ("LeSean McCoy", "RB"), ("Jordy Nelson", "WR"), ("A.J. Green", "WR"), ("Michael Thomas", "WR"), ("Rob Gronkowski", "TE"), ("Tom Brady", "QB"), ("Aaron Rodgers", "QB"), ("Todd Gurley", "RB")],
    2018: [("Todd Gurley", "RB"), ("Le'Veon Bell", "RB"), ("David Johnson", "RB"), ("Ezekiel Elliott", "RB"), ("Antonio Brown", "WR"), ("Alvin Kamara", "RB"), ("Saquon Barkley", "RB"), ("DeAndre Hopkins", "WR"), ("Julio Jones", "WR"), ("Melvin Gordon", "RB"), ("Michael Thomas", "WR"), ("Odell Beckham Jr.", "WR"), ("Rob Gronkowski", "TE"), ("Travis Kelce", "TE"), ("Aaron Rodgers", "QB"), ("Patrick Mahomes", "QB")],
    2019: [("Saquon Barkley", "RB"), ("Christian McCaffrey", "RB"), ("Alvin Kamara", "RB"), ("Ezekiel Elliott", "RB"), ("David Johnson", "RB"), ("DeAndre Hopkins", "WR"), ("Davante Adams", "WR"), ("Julio Jones", "WR"), ("Michael Thomas", "WR"), ("Nick Chubb", "RB"), ("Travis Kelce", "TE"), ("Odell Beckham Jr.", "WR"), ("Patrick Mahomes", "QB"), ("George Kittle", "TE"), ("Dalvin Cook", "RB"), ("Deshaun Watson", "QB")],
    2020: [("Christian McCaffrey", "RB"), ("Saquon Barkley", "RB"), ("Ezekiel Elliott", "RB"), ("Alvin Kamara", "RB"), ("Dalvin Cook", "RB"), ("Michael Thomas", "WR"), ("Derrick Henry", "RB"), ("Davante Adams", "WR"), ("Clyde Edwards-Helaire", "RB"), ("Travis Kelce", "TE"), ("Tyreek Hill", "WR"), ("Julio Jones", "WR"), ("Patrick Mahomes", "QB"), ("Lamar Jackson", "QB"), ("George Kittle", "TE"), ("Josh Jacobs", "RB")],
    2021: [("Christian McCaffrey", "RB"), ("Dalvin Cook", "RB"), ("Derrick Henry", "RB"), ("Alvin Kamara", "RB"), ("Ezekiel Elliott", "RB"), ("Davante Adams", "WR"), ("Travis Kelce", "TE"), ("Tyreek Hill", "WR"), ("Jonathan Taylor", "RB"), ("Nick Chubb", "RB"), ("Aaron Jones", "RB"), ("Stefon Diggs", "WR"), ("Patrick Mahomes", "QB"), ("Josh Allen", "QB"), ("Justin Jefferson", "WR"), ("Darren Waller", "TE")],
    2022: [("Jonathan Taylor", "RB"), ("Christian McCaffrey", "RB"), ("Austin Ekeler", "RB"), ("Cooper Kupp", "WR"), ("Justin Jefferson", "WR"), ("Derrick Henry", "RB"), ("Dalvin Cook", "RB"), ("Ja'Marr Chase", "WR"), ("Najee Harris", "RB"), ("Stefon Diggs", "WR"), ("Travis Kelce", "TE"), ("Joe Mixon", "RB"), ("Josh Allen", "QB"), ("Patrick Mahomes", "QB"), ("Davante Adams", "WR"), ("CeeDee Lamb", "WR")],
    2023: [("Justin Jefferson", "WR"), ("Christian McCaffrey", "RB"), ("Ja'Marr Chase", "WR"), ("Austin Ekeler", "RB"), ("Travis Kelce", "TE"), ("Tyreek Hill", "WR"), ("Nick Chubb", "RB"), ("Bijan Robinson", "RB"), ("Saquon Barkley", "RB"), ("Stefon Diggs", "WR"), ("CeeDee Lamb", "WR"), ("Amon-Ra St. Brown", "WR"), ("Patrick Mahomes", "QB"), ("Josh Allen", "QB"), ("Jalen Hurts", "QB"), ("Tony Pollard", "RB")],
    2024: [("Christian McCaffrey", "RB"), ("CeeDee Lamb", "WR"), ("Tyreek Hill", "WR"), ("Justin Jefferson", "WR"), ("Ja'Marr Chase", "WR"), ("Amon-Ra St. Brown", "WR"), ("Breece Hall", "RB"), ("Bijan Robinson", "RB"), ("A.J. Brown", "WR"), ("Garrett Wilson", "WR"), ("Puka Nacua", "WR"), ("Jahmyr Gibbs", "RB"), ("Travis Kelce", "TE"), ("Josh Allen", "QB"), ("Patrick Mahomes", "QB"), ("Sam LaPorta", "TE")],
    2025: [("Bijan Robinson", "RB"), ("CeeDee Lamb", "WR"), ("Ja'Marr Chase", "WR"), ("Justin Jefferson", "WR"), ("Jahmyr Gibbs", "RB"), ("Amon-Ra St. Brown", "WR"), ("Breece Hall", "RB"), ("Malik Nabers", "WR"), ("Marvin Harrison Jr.", "WR"), ("Nico Collins", "WR"), ("Jayden Daniels", "QB"), ("Brock Bowers", "TE"), ("Josh Allen", "QB"), ("Lamar Jackson", "QB"), ("Kyren Williams", "RB"), ("Trey McBride", "TE")]
}

def seed_database():
    init_db()
    conn = get_db_connection()
    cur = conn.cursor()

    # Clear existing
    cur.execute("DELETE FROM draft_picks")
    cur.execute("DELETE FROM matchups")
    cur.execute("DELETE FROM teams")
    cur.execute("DELETE FROM seasons")
    cur.execute("DELETE FROM managers")

    # 1. Insert Managers
    for m in MANAGERS:
        cur.execute(
            "INSERT INTO managers (manager_id, display_name, yahoo_guid_or_slug, avatar_url) VALUES (?, ?, ?, ?)",
            (m["id"], m["name"], m["slug"], m["avatar"])
        )

    # Manager skill / strength rating (determines long-term win% tendency with variance)
    manager_weights = {
        "m_harrison": 1.25, # Consistent contender
        "m_dave": 1.15,
        "m_sarah": 1.10,
        "m_marcus": 1.05,
        "m_kevin": 0.95,
        "m_alex": 1.00,
        "m_brandon": 0.90,
        "m_tyler": 1.08,
        "m_chris": 0.88,
        "m_jordan": 0.96,
        "m_sam": 1.02,
        "m_nick": 0.85
    }

    # Draft style tendency:
    # 'early_qb' (Alex, Kevin), 'zero_rb' (Harrison, Sarah), 'hero_rb' (Dave, Tyler), 'heavy_wr' (Sam, Jordan), 'balanced' (Marcus, Brandon, Nick, Chris)
    draft_styles = {
        "m_harrison": "zero_rb",
        "m_dave": "hero_rb",
        "m_marcus": "balanced",
        "m_sarah": "heavy_wr",
        "m_kevin": "early_qb",
        "m_alex": "early_qb",
        "m_brandon": "balanced",
        "m_tyler": "hero_rb",
        "m_chris": "balanced",
        "m_jordan": "heavy_wr",
        "m_sam": "zero_rb",
        "m_nick": "balanced"
    }

    for year in SEASONS:
        league_name = f"The Concrete Gridiron League ({year})"
        cur.execute(
            "INSERT INTO seasons (year, league_name, num_teams, regular_season_weeks, playoff_weeks) VALUES (?, ?, ?, ?, ?)",
            (year, league_name, len(MANAGERS), 14, 3)
        )

        season_teams = {}
        for m in MANAGERS:
            team_id = f"t_{m['id']}_{year}"
            name_candidates = TEAM_NAME_POOLS.get(m["id"], ["The Gridiron Club"])
            team_name = name_candidates[year % len(name_candidates)]
            season_teams[m["id"]] = {
                "team_id": team_id,
                "manager_id": m["id"],
                "team_name": team_name,
                "wins": 0,
                "losses": 0,
                "ties": 0,
                "points_for": 0.0,
                "points_against": 0.0,
                "final_rank": 0
            }

        # Generate 14 Regular Season Weeks
        # Round-robin scheduling simulation
        manager_ids = [m["id"] for m in MANAGERS]
        for week in range(1, 15):
            # Shuffle pairings per week
            round_ids = list(manager_ids)
            random.shuffle(round_ids)
            while len(round_ids) >= 2:
                m1 = round_ids.pop()
                m2 = round_ids.pop()
                t1 = season_teams[m1]
                t2 = season_teams[m2]

                base1 = 110.0 * manager_weights[m1] + random.gauss(0, 16)
                base2 = 110.0 * manager_weights[m2] + random.gauss(0, 16)
                score1 = round(max(55.0, base1), 2)
                score2 = round(max(55.0, base2), 2)
                if score1 == score2:
                    score1 += 0.5

                matchup_id = f"m_{year}_w{week}_{m1}_vs_{m2}"
                cur.execute(
                    "INSERT INTO matchups (matchup_id, season_year, week, team1_id, team1_score, team2_id, team2_score, is_playoffs, is_championship) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (matchup_id, year, week, t1["team_id"], score1, t2["team_id"], score2, 0, 0)
                )

                t1["points_for"] += score1
                t1["points_against"] += score2
                t2["points_for"] += score2
                t2["points_against"] += score1

                if score1 > score2:
                    t1["wins"] += 1
                    t2["losses"] += 1
                else:
                    t2["wins"] += 1
                    t1["losses"] += 1

        # Regular Season Standings
        ranked_teams = sorted(
            season_teams.values(),
            key=lambda x: (x["wins"], x["points_for"]),
            reverse=True
        )

        # Playoffs (Top 6 teams)
        # Week 15: Semis (top 2 byes or seeds 1-4)
        top4 = ranked_teams[:4]
        # Semi 1: Seed 1 vs Seed 4
        s1_score = round(105 + random.gauss(0, 15) * manager_weights[top4[0]["manager_id"]], 2)
        s4_score = round(105 + random.gauss(0, 15) * manager_weights[top4[3]["manager_id"]], 2)
        semi1_winner = top4[0] if s1_score >= s4_score else top4[3]
        semi1_loser = top4[3] if s1_score >= s4_score else top4[0]

        cur.execute(
            "INSERT INTO matchups (matchup_id, season_year, week, team1_id, team1_score, team2_id, team2_score, is_playoffs, is_championship) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"m_{year}_w15_semi1", year, 15, top4[0]["team_id"], s1_score, top4[3]["team_id"], s4_score, 1, 0)
        )

        # Semi 2: Seed 2 vs Seed 3
        s2_score = round(105 + random.gauss(0, 15) * manager_weights[top4[1]["manager_id"]], 2)
        s3_score = round(105 + random.gauss(0, 15) * manager_weights[top4[2]["manager_id"]], 2)
        semi2_winner = top4[1] if s2_score >= s3_score else top4[2]
        semi2_loser = top4[2] if s2_score >= s3_score else top4[1]

        cur.execute(
            "INSERT INTO matchups (matchup_id, season_year, week, team1_id, team1_score, team2_id, team2_score, is_playoffs, is_championship) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"m_{year}_w15_semi2", year, 15, top4[1]["team_id"], s2_score, top4[2]["team_id"], s3_score, 1, 0)
        )

        # Week 16: Championship
        c1_score = round(112 + random.gauss(0, 18) * manager_weights[semi1_winner["manager_id"]], 2)
        c2_score = round(112 + random.gauss(0, 18) * manager_weights[semi2_winner["manager_id"]], 2)
        if c1_score == c2_score: c1_score += 0.5
        champ = semi1_winner if c1_score > c2_score else semi2_winner
        runner_up = semi2_winner if c1_score > c2_score else semi1_winner

        cur.execute(
            "INSERT INTO matchups (matchup_id, season_year, week, team1_id, team1_score, team2_id, team2_score, is_playoffs, is_championship) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"m_{year}_w16_champ", year, 16, semi1_winner["team_id"], c1_score, semi2_winner["team_id"], c2_score, 1, 1)
        )

        # Update season champion & runner up
        cur.execute(
            "UPDATE seasons SET champion_team_id = ?, runner_up_team_id = ? WHERE year = ?",
            (champ["team_id"], runner_up["team_id"], year)
        )

        # Assign ranks
        champ["final_rank"] = 1
        runner_up["final_rank"] = 2
        semi_losers = sorted([semi1_loser, semi2_loser], key=lambda x: x["points_for"], reverse=True)
        semi_losers[0]["final_rank"] = 3
        semi_losers[1]["final_rank"] = 4
        rank_counter = 5
        for t in ranked_teams:
            if t["final_rank"] == 0:
                t["final_rank"] = rank_counter
                rank_counter += 1

        for t in season_teams.values():
            cur.execute(
                """INSERT INTO teams (team_id, season_year, manager_id, team_name, final_rank, wins, losses, ties, points_for, points_against)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (t["team_id"], year, t["manager_id"], t["team_name"], t["final_rank"], t["wins"], t["losses"], t["ties"], round(t["points_for"], 2), round(t["points_against"], 2))
            )

        # Generate Draft for Year
        cohort = HISTORICAL_COHORTS.get(year, HISTORICAL_COHORTS[2024])
        # Generate 15 rounds of 12 picks = 180 picks
        pick_counter = 1
        draft_order = list(MANAGERS)
        random.shuffle(draft_order)

        for round_num in range(1, 16):
            round_managers = list(draft_order) if round_num % 2 == 1 else list(reversed(draft_order))
            for m in round_managers:
                team_id = season_teams[m["id"]]["team_id"]
                style = draft_styles[m["id"]]

                # Determine position by round & manager style
                pos = "RB"
                if round_num <= 3:
                    if style == "zero_rb":
                        pos = "WR" if random.random() < 0.75 else "TE"
                    elif style == "early_qb" and round_num in (2, 3) and random.random() < 0.6:
                        pos = "QB"
                    elif style == "hero_rb":
                        pos = "RB" if round_num == 1 else "WR"
                    else:
                        pos = random.choice(["RB", "WR", "RB"])
                elif round_num <= 7:
                    if style == "zero_rb":
                        pos = random.choice(["WR", "RB", "QB", "TE"])
                    elif style == "early_qb":
                        pos = random.choice(["RB", "WR", "WR"])
                    else:
                        pos = random.choice(["RB", "WR", "TE", "QB"])
                elif round_num >= 14:
                    pos = "DEF" if round_num == 14 else "K"
                else:
                    pos = random.choice(["WR", "RB", "QB", "TE"])

                # Pick player name
                player_name = f"Player {year} R{round_num}P{pick_counter} ({pos})"
                if pick_counter <= len(cohort):
                    c_name, c_pos = cohort[pick_counter - 1]
                    player_name = c_name
                    pos = c_pos

                projected_rank = pick_counter + random.randint(-8, 8)
                projected_rank = max(1, projected_rank)

                is_keeper = 1 if (round_num >= 5 and random.random() < 0.08) else 0
                keeper_cost = round_num if is_keeper else None

                cur.execute(
                    """INSERT INTO draft_picks (pick_id, season_year, round, pick_overall, team_id, player_name, position, nfl_team, is_keeper, keeper_cost, projected_rank)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (f"dp_{year}_{pick_counter}", year, round_num, pick_counter, team_id, player_name, pos, "NFL", is_keeper, keeper_cost, projected_rank)
                )
                pick_counter += 1

    conn.commit()
    conn.close()
    print("Successfully seeded 13 seasons (2013-2025) of full historical league data!")

if __name__ == "__main__":
    seed_database()
