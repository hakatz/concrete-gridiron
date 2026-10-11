import os
import re
import json
import sqlite3
from collections import defaultdict
from db import get_db_connection

OUTPUT_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "data", "league_analytics.json")

def normalize_pname(name):
    if not name:
        return ""
    n = name.lower().strip()
    n = re.sub(r"[^\w\s]", "", n)
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", n)
    return " ".join(n.split())

def generate_analytics():
    print("Generating comprehensive league analytics, rosters & waiver profiles...")
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Fetch Managers
    cur.execute("SELECT manager_id, display_name, yahoo_guid_or_slug, yahoo_profile_url, avatar_url, is_active FROM managers")
    managers = {row["manager_id"]: dict(row) for row in cur.fetchall()}

    # 2. Fetch Seasons
    cur.execute("SELECT year, league_name, num_teams, regular_season_weeks, playoff_weeks, champion_team_id, runner_up_team_id FROM seasons ORDER BY year ASC")
    seasons = [dict(row) for row in cur.fetchall()]

    # 3. Fetch Teams
    cur.execute("SELECT team_id, season_year, manager_id, team_name, final_rank, wins, losses, ties, points_for, points_against, moves, trades, faab_remaining FROM teams")
    teams = {row["team_id"]: dict(row) for row in cur.fetchall()}

    # 4. Fetch Matchups
    cur.execute("SELECT matchup_id, season_year, week, team1_id, team1_score, team2_id, team2_score, is_playoffs, is_championship FROM matchups")
    matchups = [dict(row) for row in cur.fetchall()]

    # 5. Fetch Draft Picks
    cur.execute("SELECT pick_id, season_year, round, pick_overall, team_id, player_name, position, nfl_team, is_keeper, keeper_cost, projected_rank FROM draft_picks ORDER BY season_year ASC, pick_overall ASC")
    draft_picks = [dict(row) for row in cur.fetchall()]

    # 6. Fetch Rosters
    cur.execute("SELECT roster_id, season_year, team_id, player_name, position, roster_slot, fan_pts FROM rosters")
    roster_rows = [dict(row) for row in cur.fetchall()]

    conn.close()

    # Organize rosters by team
    team_rosters = defaultdict(list)
    for r in roster_rows:
        team_rosters[r["team_id"]].append(r)

    # Organize draft picks by team
    team_drafts = defaultdict(list)
    for dp in draft_picks:
        team_drafts[dp["team_id"]].append(dp)

    # Career aggregates
    career_stats = defaultdict(lambda: {
        "wins": 0, "losses": 0, "ties": 0, "playoff_wins": 0, "playoff_losses": 0,
        "points_for": 0.0, "points_against": 0.0,
        "seasons_played": 0, "championships": 0, "runner_ups": 0, "playoff_appearances": 0,
        "total_moves": 0, "total_trades": 0, "faab_spent": 0.0,
        "drafted_retained_count": 0, "total_drafted_count": 0,
        "historical_teams": [], "high_score": 0.0, "low_score": 9999.0,
        "waiver_gems": []
    })

    # Champion / Runner up counts
    for s in seasons:
        if s["champion_team_id"] and s["champion_team_id"] in teams:
            c_mid = teams[s["champion_team_id"]]["manager_id"]
            career_stats[c_mid]["championships"] += 1
        if s["runner_up_team_id"] and s["runner_up_team_id"] in teams:
            ru_mid = teams[s["runner_up_team_id"]]["manager_id"]
            career_stats[ru_mid]["runner_ups"] += 1

    for t in teams.values():
        mid = t["manager_id"]
        career_stats[mid]["wins"] += t["wins"]
        career_stats[mid]["losses"] += t["losses"]
        career_stats[mid]["ties"] += t["ties"]
        career_stats[mid]["points_for"] += t["points_for"]
        career_stats[mid]["points_against"] += t["points_against"]
        career_stats[mid]["seasons_played"] += 1
        career_stats[mid]["total_moves"] += (t["moves"] or 0)
        career_stats[mid]["total_trades"] += (t["trades"] or 0)
        if t["faab_remaining"] is not None:
            career_stats[mid]["faab_spent"] += max(0.0, 100.0 - t["faab_remaining"])

        if t["final_rank"] and t["final_rank"] <= 4:
            career_stats[mid]["playoff_appearances"] += 1

        # Roster retention & waiver gem analysis
        d_players = {dp["player_name"].lower(): dp for dp in team_drafts[t["team_id"]]}
        r_players = {rp["player_name"].lower(): rp for rp in team_rosters[t["team_id"]]}

        career_stats[mid]["total_drafted_count"] += len(d_players)
        retained = 0
        for p_name, rp in r_players.items():
            if p_name in d_players:
                retained += 1
            else:
                # Potential waiver gem!
                if rp["fan_pts"] and rp["fan_pts"] >= 10.0:
                    career_stats[mid]["waiver_gems"].append({
                        "player": rp["player_name"],
                        "year": t["season_year"],
                        "pos": rp["position"],
                        "slot": rp["roster_slot"],
                        "pts": rp["fan_pts"]
                    })
        career_stats[mid]["drafted_retained_count"] += retained

        career_stats[mid]["historical_teams"].append({
            "year": t["season_year"],
            "name": t["team_name"],
            "rank": t["final_rank"],
            "wins": t["wins"],
            "losses": t["losses"],
            "pf": t["points_for"],
            "pa": t["points_against"],
            "moves": t["moves"] or 0,
            "trades": t["trades"] or 0
        })

    # Head-to-Head Matrix & Single Week Highs/Lows & Luck Index
    h2h_matrix = defaultdict(lambda: defaultdict(lambda: {
        "wins": 0, "losses": 0, "ties": 0, "points_for": 0.0, "points_against": 0.0, "matchups": []
    }))

    weekly_scores = defaultdict(list)
    single_week_records = []

    for m in matchups:
        t1 = teams.get(m["team1_id"])
        t2 = teams.get(m["team2_id"])
        if not t1 or not t2:
            continue

        m1_id = t1["manager_id"]
        m2_id = t2["manager_id"]
        s1 = m["team1_score"]
        s2 = m["team2_score"]

        if not m["is_playoffs"]:
            weekly_scores[(m["season_year"], m["week"])].append((m1_id, s1))
            weekly_scores[(m["season_year"], m["week"])].append((m2_id, s2))

        career_stats[m1_id]["high_score"] = max(career_stats[m1_id]["high_score"], s1)
        career_stats[m1_id]["low_score"] = min(career_stats[m1_id]["low_score"], s1)
        career_stats[m2_id]["high_score"] = max(career_stats[m2_id]["high_score"], s2)
        career_stats[m2_id]["low_score"] = min(career_stats[m2_id]["low_score"], s2)

        single_week_records.append({
            "year": m["season_year"], "week": m["week"], "score": s1,
            "manager_id": m1_id, "manager_name": managers[m1_id]["display_name"],
            "opponent_id": m2_id, "opponent_name": managers[m2_id]["display_name"],
            "opponent_score": s2, "margin": round(abs(s1 - s2), 2),
            "is_playoffs": bool(m["is_playoffs"])
        })
        single_week_records.append({
            "year": m["season_year"], "week": m["week"], "score": s2,
            "manager_id": m2_id, "manager_name": managers[m2_id]["display_name"],
            "opponent_id": m1_id, "opponent_name": managers[m1_id]["display_name"],
            "opponent_score": s1, "margin": round(abs(s2 - s1), 2),
            "is_playoffs": bool(m["is_playoffs"])
        })

        h2h_matrix[m1_id][m2_id]["points_for"] += s1
        h2h_matrix[m1_id][m2_id]["points_against"] += s2
        h2h_matrix[m2_id][m1_id]["points_for"] += s2
        h2h_matrix[m2_id][m1_id]["points_against"] += s1

        matchup_record = {
            "year": m["season_year"], "week": m["week"], "score1": s1, "score2": s2,
            "is_playoffs": bool(m["is_playoffs"]), "is_championship": bool(m["is_championship"])
        }
        h2h_matrix[m1_id][m2_id]["matchups"].append(matchup_record)
        h2h_matrix[m2_id][m1_id]["matchups"].append({**matchup_record, "score1": s2, "score2": s1})

        if s1 > s2:
            h2h_matrix[m1_id][m2_id]["wins"] += 1
            h2h_matrix[m2_id][m1_id]["losses"] += 1
            if m["is_playoffs"]:
                career_stats[m1_id]["playoff_wins"] += 1
                career_stats[m2_id]["playoff_losses"] += 1
        elif s2 > s1:
            h2h_matrix[m2_id][m1_id]["wins"] += 1
            h2h_matrix[m1_id][m2_id]["losses"] += 1
            if m["is_playoffs"]:
                career_stats[m2_id]["playoff_wins"] += 1
                career_stats[m1_id]["playoff_losses"] += 1
        else:
            h2h_matrix[m1_id][m2_id]["ties"] += 1
            h2h_matrix[m2_id][m1_id]["ties"] += 1

    # Luck Index
    expected_wins = defaultdict(float)
    for (yr, wk), scores in weekly_scores.items():
        total_competitors = len(scores) - 1
        if total_competitors <= 0:
            continue
        for i, (mid, sc) in enumerate(scores):
            beat_count = sum(1 for j, (o_mid, o_sc) in enumerate(scores) if i != j and sc > o_sc)
            expected_wins[mid] += (beat_count / total_competitors)

    # Build mapping of (season_year, normalized_name) -> max(fan_pts)
    season_player_points = defaultdict(dict)
    for r in roster_rows:
        p_pts = r["fan_pts"]
        if p_pts is not None:
            p_norm = normalize_pname(r["player_name"])
            if p_norm:
                curr = season_player_points[r["season_year"]].get(p_norm, -1.0)
                if p_pts > curr:
                    season_player_points[r["season_year"]][p_norm] = p_pts

    # Precompute actual rank per season for all drafted players
    season_draft_picks = defaultdict(list)
    for dp in draft_picks:
        season_draft_picks[dp["season_year"]].append(dp)

    draft_pick_actuals = {}
    for yr, picks in season_draft_picks.items():
        pick_pts_list = []
        for dp in picks:
            p_norm = normalize_pname(dp["player_name"])
            pts = season_player_points[yr].get(p_norm)
            if pts is None:
                for r_norm, r_pts in season_player_points[yr].items():
                    if p_norm and (p_norm in r_norm or r_norm in p_norm):
                        pts = r_pts
                        break
            dp_id = dp["pick_id"]
            draft_pick_actuals[dp_id] = {
                "actual_pts": pts,
                "actual_rank": None,
                "value_delta": None
            }
            if pts is not None and pts > 0:
                pick_pts_list.append((dp_id, pts, dp["pick_overall"]))

        pick_pts_list.sort(key=lambda x: x[1], reverse=True)
        for rank_idx, (dp_id, pts, pick_ovr) in enumerate(pick_pts_list, start=1):
            delta = pick_ovr - rank_idx
            draft_pick_actuals[dp_id]["actual_rank"] = rank_idx
            draft_pick_actuals[dp_id]["value_delta"] = delta

    # Draft Tendencies
    manager_drafts = defaultdict(lambda: {
        "picks": [],
        "pos_round_1_3": defaultdict(int),
        "pos_round_4_7": defaultdict(int),
        "pos_round_8_plus": defaultdict(int),
        "total_picks": 0,
        "early_qb_count": 0,
        "early_te_count": 0,
        "steals": [],
        "reaches": []
    })

    for dp in draft_picks:
        team = teams.get(dp["team_id"])
        if not team:
            continue
        mid = team["manager_id"]
        m_draft = manager_drafts[mid]
        m_draft["total_picks"] += 1
        m_draft["picks"].append(dp)

        pos = dp["position"]
        rnd = dp["round"]

        if rnd <= 3:
            m_draft["pos_round_1_3"][pos] += 1
            if pos == "QB": m_draft["early_qb_count"] += 1
            if pos == "TE": m_draft["early_te_count"] += 1
        elif rnd <= 7:
            m_draft["pos_round_4_7"][pos] += 1
        else:
            m_draft["pos_round_8_plus"][pos] += 1

        act_info = draft_pick_actuals.get(dp["pick_id"], {})
        val_delta = act_info.get("value_delta")
        act_pts = act_info.get("actual_pts")
        act_rank = act_info.get("actual_rank")

        item_entry = {
            "player": dp["player_name"], "year": dp["season_year"],
            "round": dp["round"], "pick": dp["pick_overall"],
            "actual_pts": act_pts, "actual_rank": act_rank,
            "projected": dp["projected_rank"], "delta": val_delta or 0
        }
        if val_delta is not None:
            if val_delta >= 15:
                m_draft["steals"].append(item_entry)
            elif val_delta <= -20:
                m_draft["reaches"].append(item_entry)

    manager_dossiers = []
    for mid, m_info in managers.items():
        c_stat = career_stats[mid]
        total_games = c_stat["wins"] + c_stat["losses"] + c_stat["ties"]
        win_pct = round((c_stat["wins"] / total_games * 100) if total_games > 0 else 0.0, 1)

        exp_w = round(expected_wins[mid], 1)
        luck_diff = round(c_stat["wins"] - exp_w, 1)

        # Nemesis & Victim
        h2h_against = h2h_matrix[mid]
        nemesis_id = None
        nemesis_loss_rate = -1.0
        victim_id = None
        victim_win_rate = -1.0

        for opp_id, h_data in h2h_against.items():
            opp_games = h_data["wins"] + h_data["losses"] + h_data["ties"]
            if opp_games >= 3:
                opp_loss_rate = h_data["losses"] / opp_games
                opp_win_rate = h_data["wins"] / opp_games
                if opp_loss_rate > nemesis_loss_rate:
                    nemesis_loss_rate = opp_loss_rate
                    nemesis_id = opp_id
                if opp_win_rate > victim_win_rate:
                    victim_win_rate = opp_win_rate
                    victim_id = opp_id

        nemesis_info = None
        if nemesis_id and nemesis_id in managers:
            n_data = h2h_against[nemesis_id]
            nemesis_info = {
                "manager_id": nemesis_id,
                "name": managers[nemesis_id]["display_name"],
                "record": f"{n_data['wins']}-{n_data['losses']}-{n_data['ties']}",
                "loss_pct": round(nemesis_loss_rate * 100, 1)
            }

        victim_info = None
        if victim_id and victim_id in managers:
            v_data = h2h_against[victim_id]
            victim_info = {
                "manager_id": victim_id,
                "name": managers[victim_id]["display_name"],
                "record": f"{v_data['wins']}-{v_data['losses']}-{v_data['ties']}",
                "win_pct": round(victim_win_rate * 100, 1)
            }

        # Radar Scores
        m_draft = manager_drafts[mid]
        r1_3_total = sum(m_draft["pos_round_1_3"].values()) or 1
        zero_rb_score = min(100, int((m_draft["pos_round_1_3"]["WR"] + m_draft["pos_round_1_3"]["TE"]) / r1_3_total * 120))
        hero_rb_score = min(100, int((m_draft["pos_round_1_3"]["RB"] / r1_3_total) * 110))
        early_qb_score = min(100, int((m_draft["early_qb_count"] / max(1, c_stat["seasons_played"])) * 140))
        late_streamer_score = max(0, 100 - early_qb_score)
        reach_frequency = min(100, int((len(m_draft["reaches"]) / max(1, m_draft["total_picks"])) * 400))
        steal_efficiency = min(100, int((len(m_draft["steals"]) / max(1, m_draft["total_picks"])) * 400))

        # Waiver & Churn Tendency
        seasons_ct = max(1, c_stat["seasons_played"])
        avg_moves_per_season = round(c_stat["total_moves"] / seasons_ct, 1)
        avg_trades_per_season = round(c_stat["total_trades"] / seasons_ct, 1)
        retention_rate = round((c_stat["drafted_retained_count"] / max(1, c_stat["total_drafted_count"])) * 100, 1)

        # Persona & Archetype Tagging
        archetypes = []
        if c_stat["championships"] >= 3:
            archetypes.append("Dynasty Architect")

        if avg_moves_per_season >= 25:
            archetypes.append("Waiver Wire Hawk")
        elif avg_moves_per_season <= 8 and seasons_ct >= 2:
            archetypes.append("Draft-and-Hold Purist")

        if avg_trades_per_season >= 1.5:
            archetypes.append("Blockbuster Trader")

        if retention_rate >= 60:
            archetypes.append("High Roster Loyalty")
        elif retention_rate <= 35 and seasons_ct >= 2:
            archetypes.append("Extreme Roster Churner")

        if zero_rb_score > 65: archetypes.append("Zero-RB Disciple")
        elif hero_rb_score > 65: archetypes.append("Bellcow Heavy")

        if early_qb_score > 55: archetypes.append("Gunslinger QB Priority")
        elif late_streamer_score > 75: archetypes.append("Late QB Streamer")

        if luck_diff >= 4.0: archetypes.append("Favored by Fortune")
        elif luck_diff <= -4.0: archetypes.append("Bad Beat Sufferer")

        if not archetypes:
            archetypes.append("Balanced Tactician")

        manager_dossiers.append({
            "manager_id": mid,
            "name": m_info["display_name"],
            "slug": m_info["yahoo_guid_or_slug"],
            "yahoo_profile_url": m_info.get("yahoo_profile_url"),
            "is_active": bool(m_info.get("is_active", 1)),
            "avatar_url": m_info["avatar_url"],
            "career": {
                "seasons": c_stat["seasons_played"],
                "championships": c_stat["championships"],
                "runner_ups": c_stat["runner_ups"],
                "playoff_appearances": c_stat["playoff_appearances"],
                "wins": c_stat["wins"],
                "losses": c_stat["losses"],
                "ties": c_stat["ties"],
                "win_pct": win_pct,
                "playoff_wins": c_stat["playoff_wins"],
                "playoff_losses": c_stat["playoff_losses"],
                "points_for": round(c_stat["points_for"], 2),
                "points_against": round(c_stat["points_against"], 2),
                "avg_pf_per_game": round(c_stat["points_for"] / max(1, total_games), 1),
                "high_score": c_stat["high_score"] if c_stat["high_score"] > 0 else 0,
                "low_score": c_stat["low_score"] if c_stat["low_score"] < 9000 else 0,
                "expected_wins": exp_w,
                "luck_diff": luck_diff,
                "total_moves": c_stat["total_moves"],
                "avg_moves_per_season": avg_moves_per_season,
                "total_trades": c_stat["total_trades"],
                "avg_trades_per_season": avg_trades_per_season,
                "roster_retention_rate": retention_rate
            },
            "tendencies": {
                "zero_rb": zero_rb_score,
                "hero_rb": hero_rb_score,
                "early_qb": early_qb_score,
                "late_streamer": late_streamer_score,
                "reach_frequency": reach_frequency,
                "steal_efficiency": steal_efficiency,
                "waiver_activity": min(100, int(avg_moves_per_season * 3.3)),
                "pos_allocation_r1_3": dict(m_draft["pos_round_1_3"]),
                "pos_allocation_r4_7": dict(m_draft["pos_round_4_7"]),
                "pos_allocation_r8_plus": dict(m_draft["pos_round_8_plus"])
            },
            "archetypes": archetypes,
            "nemesis": nemesis_info,
            "victim": victim_info,
            "waiver_gems": c_stat["waiver_gems"][:6],
            "recent_draft_steals": sorted(m_draft["steals"], key=lambda x: x["delta"], reverse=True)[:5],
            "recent_draft_reaches": sorted(m_draft["reaches"], key=lambda x: x["delta"])[:5],
            "historical_teams": sorted(c_stat["historical_teams"], key=lambda x: x["year"], reverse=True)
        })

    valid_records = [r for r in single_week_records if r["score"] > 0]
    all_time_high_scores = sorted(valid_records, key=lambda x: x["score"], reverse=True)[:10]
    all_time_low_scores = sorted(valid_records, key=lambda x: x["score"])[:10]
    biggest_blowouts = sorted(valid_records, key=lambda x: x["margin"], reverse=True)[:10]
    closest_games = sorted(valid_records, key=lambda x: x["margin"])[:10]

    hall_of_fame = []
    for s in seasons:
        champ_team = teams.get(s["champion_team_id"])
        ru_team = teams.get(s["runner_up_team_id"])
        if champ_team:
            hall_of_fame.append({
                "year": s["year"],
                "champion": {
                    "manager_id": champ_team["manager_id"],
                    "manager_name": managers[champ_team["manager_id"]]["display_name"],
                    "team_name": champ_team["team_name"],
                    "record": f"{champ_team['wins']}-{champ_team['losses']}"
                },
                "runner_up": {
                    "manager_id": ru_team["manager_id"],
                    "manager_name": managers[ru_team["manager_id"]]["display_name"],
                    "team_name": ru_team["team_name"],
                    "record": f"{ru_team['wins']}-{ru_team['losses']}"
                } if ru_team else None
            })

    h2h_flat = []
    for m1_id, m1 in managers.items():
        if not m1.get("is_active", 1):
            continue
        row = {"manager_id": m1_id, "manager_name": m1["display_name"], "opponents": {}}
        for m2_id, m2 in managers.items():
            if m1_id == m2_id or not m2.get("is_active", 1):
                continue
            data = h2h_matrix[m1_id][m2_id]
            row["opponents"][m2_id] = {
                "wins": data["wins"], "losses": data["losses"], "ties": data["ties"],
                "pf": round(data["points_for"], 1), "pa": round(data["points_against"], 1),
                "total_games": data["wins"] + data["losses"] + data["ties"]
            }
        h2h_flat.append(row)

    analytics_payload = {
        "league_id": "503435",
        "league_name": "Concrete Gridiron",
        "generated_at": "2026-09-26",
        "active_year": 2025,
        "historical_seasons": [s["year"] for s in seasons],
        "managers": sorted([m for m in manager_dossiers if m.get("is_active", True)], key=lambda x: (x["career"]["championships"], x["career"]["win_pct"]), reverse=True),
        "hall_of_fame": sorted(hall_of_fame, key=lambda x: x["year"], reverse=True),
        "records": {
            "all_time_high_scores": all_time_high_scores,
            "all_time_low_scores": all_time_low_scores,
            "biggest_blowouts": biggest_blowouts,
            "closest_games": closest_games
        },
        "h2h_matrix": h2h_flat,
        "draft_archive": [
            {
                "pick_id": dp["pick_id"], "year": dp["season_year"], "round": dp["round"], "pick": dp["pick_overall"],
                "player_name": dp["player_name"], "position": dp["position"],
                "manager_id": teams[dp["team_id"]]["manager_id"] if dp["team_id"] in teams else "unknown",
                "manager_name": managers[teams[dp["team_id"]]["manager_id"]]["display_name"] if (dp["team_id"] in teams and teams[dp["team_id"]]["manager_id"] in managers) else "Manager",
                "team_name": teams[dp["team_id"]]["team_name"] if dp["team_id"] in teams else "Team",
                "is_keeper": bool(dp["is_keeper"]), "projected_rank": dp["projected_rank"],
                "actual_pts": draft_pick_actuals.get(dp["pick_id"], {}).get("actual_pts"),
                "actual_rank": draft_pick_actuals.get(dp["pick_id"], {}).get("actual_rank"),
                "value_delta": draft_pick_actuals.get(dp["pick_id"], {}).get("value_delta"),
                "delta": draft_pick_actuals.get(dp["pick_id"], {}).get("value_delta") or 0
            }
            for dp in draft_picks
        ]
    }

    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(analytics_payload, f, indent=2)

    print(f"Comprehensive analytics successfully written to {OUTPUT_JSON_PATH}!")

if __name__ == "__main__":
    generate_analytics()
