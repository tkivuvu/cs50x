from cs50 import SQL
from datetime import datetime, timedelta, timezone
from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for
from helpers import error, fetch_player_totals, fetch_player_advanced, fetch_advanced_playoffs, fetch_playoff_totals, get_team_logo_url, summarize_player_totals
from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np



app = Flask(__name__)
db = SQL("sqlite:///nba_cache.db")


# ----------------------------
# AI helper tools 
# ----------------------------
# Smart player query assistant 
@app.route("/ai-summary", methods=["GET", "POST"])
def ai_summary():
    summary = None
    if request.method == "POST":
        name = request.form.get("player")
        season = request.form.get("season")
        stats = fetch_player_totals(name, season)
        summary = summarize_player_totals(stats)
    return render_template("ai_summary.html", summary=summary)




# ----------------------------
# 🔁 App-Wide Lifecycle Hooks
# ----------------------------
# Automatically delete old cache entries before every request 
@app.before_request
def cleanup_old_cache():
    cutoff = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    table_names = [
        "player_totals",
        "Player_advanced",
        "player_advanced_playoffs",
        "player_totals_playoffs",
    ]
    for table in table_names:
        query = f"DELETE FROM {table} WHERE timestamp < ?"
        db.execute(query, cutoff)


# ----------------------------
# 🧩 Template Context Injectors
# ----------------------------
# Make the current year available in all templates (for footers, etc.)
@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}


# -----------------------------------
# 🌐 Routes – General Pages
# -----------------------------------
# Homepage
@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------------
# 📊 Routes – Player Statistics Pages (HTML)
# -----------------------------------
# 📝 Form Route – Player Totals (Regular Season)
@app.route("/player_totals_search", methods=["GET", "POST"])
def player_stats_totals():
    if request.method == "POST":
        # --- Get form inputs ---
        name = request.form.get("name")
        season = request.form.get("season", type=int)

        if not name or not season:
            return error("Missing player name or season", 400)

        # --- Fetch player totals ---
        raw = fetch_player_totals(name, season)
        if "error" in raw:
            return error(raw["error"], 400)

        stats = raw["combined"].copy()
        games = stats.get("games") or 1

        # --- Compute per-game and percentage stats ---
        def compute_totals(obj, g):
            return {
                "avg_points":         round(obj.get("points", 0) / g, 1),
                "avg_assists":        round(obj.get("assists", 0) / g, 1),
                "avg_rebounds":       round(obj.get("totalRb", 0) / g, 1),
                "avg_steals":         round(obj.get("steals", 0) / g, 1),
                "avg_blocks":         round(obj.get("blocks", 0) / g, 1),
                "avg_turnovers":      round(obj.get("turnovers", 0) / g, 1),
                "avg_personalfouls":  round(obj.get("personalFouls", 0) / g, 1),
                "avg_ft":             round(obj.get("ft", 0) / g, 1),
                "avg_ftattempts":     round(obj.get("ftAttempts", 0) / g, 1),
                "avg_fieldgoals":     round(obj.get("fieldGoals", 0) / g, 1),
                "avg_fieldattempts":  round(obj.get("fieldAttempts", 0) / g, 1),
                "avg_twofg":          round(obj.get("twoFg", 0) / g, 1),
                "avg_twoattempts":    round(obj.get("twoAttempts", 0) / g, 1),
                "avg_threefg":        round(obj.get("threeFg", 0) / g, 1),
                "avg_threeattempts":  round(obj.get("threeAttempts", 0) / g, 1),
                "ftpercent":          round(obj.get("ftPercent", 0) * 100, 1),
                "fieldpercent":       round(obj.get("fieldPercent", 0) * 100, 1),
                "twopercent":         round(obj.get("twoPercent", 0) * 100, 1),
                "threepercent":       round(obj.get("threePercent", 0) * 100, 1),
            }

        stats.update(compute_totals(stats, games))

        # --- Hall of Fame check ---
        player_name = stats.get("playerName", "")
        stats["is_hof"] = player_name.endswith("*")
        stats["playerName"] = player_name.rstrip("*").strip()

        # --- Team-specific entries (omit "TOT", "2TM") ---    
        team_rows = []
        team_logo_urls = []

        for entry in raw.get("entries", []):
            team = entry.get("team", "")
            if team not in ("TOT", "2TM"):
                g = entry.get("games") or 1
                row = entry.copy()
                row.update(compute_totals(row, g))

                logo_url = get_team_logo_url(team)
                row["logo_url"] = logo_url
                team_logo_urls.append(logo_url)

                team_rows.append(row)

        # --- Team display string ---
        if stats.get("team") in ("TOT", "2TM") and team_rows:
            display_team = ", ".join(row["team"] for row in team_rows)
            team_logo_url = None  # Let HTML handle multi-logo display
        else:
            display_team = stats.get("team", "")
            team_logo_url = get_team_logo_url(display_team)


        

        
        # --- Render output ---
        return render_template(
            "player_totals.html",
            stats=stats,
            team_rows=team_rows,
            display_team=display_team,
            team_logo_url=team_logo_url,
            team_logo_urls=team_logo_urls
        )

    # --- Render search form ---
    return render_template("player_totals_search.html")


# 📝 Form Route – Advanced Player Stats (Regular Season)
@app.route("/player_advanced_search", methods=["GET", "POST"])
def player_stats_advanced(): 
    if request.method == "POST":
        # --- Get form inputs ---
        name = request.form.get("name")
        season = request.form.get("season", type=int)

        if not name or not season:
            return error("Missing player name or season", 400)

        # --- Fetch data ---
        raw = fetch_player_advanced(name, season)
        if "error" in raw:
            return error(raw["error"], 400)

        combined = raw["combined"]
        stats = combined.copy()

        # --- Compute derived stats ---
        games = stats.get("games") or 1
        stats.update({
            "tsPercent":       round(stats.get("tsPercent", 0) * 100, 1),
            "minutespergame":  round(stats.get("minutesPlayed", 0) / games, 1),
            "ftr":             round(stats.get("ftr", 0) * 100, 1)
        })

        # --- Hall of Fame check ---
        player_name = stats.get("playerName", "")
        stats["is_hof"] = player_name.endswith("*")
        stats["playerName"] = player_name.rstrip("*").strip()

        # --- Prepare per-team rows (if player played for multiple teams) ---
        team_rows = []
        team_logo_urls = []

        for entry in raw.get("entries", []):
            team = entry.get("team", "")
            if team not in ("TOT", "2TM"):
                g = entry.get("games") or 1
                logo_url = get_team_logo_url(team)
                team_rows.append({
                    **entry,
                    "tsPercent":      round(entry.get("tsPercent", 0) * 100, 1),
                    "minutespergame": round(entry.get("minutesPlayed", 0) / g, 1),
                    "ftr":            round(entry.get("ftr", 0) * 100, 1),
                    "logo_url":       logo_url
                })
                team_logo_urls.append(logo_url)

        # --- Team display string ---
        if stats.get("team") in ("TOT", "2TM") and team_rows:
            display_team = ", ".join(r["team"] for r in team_rows)
            team_logo_url = None
        else:
            display_team = stats.get("team", "")
            team_logo_url = get_team_logo_url(display_team)

        # --- Render output ---
        return render_template(
            "player_advanced.html",
            stats=stats,
            team_rows=team_rows,
            display_team=display_team,
            team_logo_url=team_logo_url,
            team_logo_urls=team_logo_urls
        )


    # --- Render form page ---
    return render_template("player_advanced_search.html")


# 📝 Form Route – Playoff Totals Stats Search
@app.route("/playoffs_totals_search", methods=["GET", "POST"])
def player_stats_playoffs():
    if request.method == "POST":
        # --- Get form inputs ---
        name = request.form.get("name")
        season = request.form.get("season", type=int)

        if not name or not season:
            return error("Missing player name or season", 400)

        # --- Fetch playoff totals data ---
        raw = fetch_playoff_totals(name, season)
        if "error" in raw:
            return error(raw["error"], 400)

        stats = raw.copy()

        # --- Compute per-game averages ---
        games = stats.get("games") or 1
        stats.update({
            "avg_points":       round(stats["points"] / games, 1),
            "avg_assists":      round(stats["assists"] / games, 1),
            "avg_rebounds":     round(stats["totalRb"] / games, 1),
            "avg_steals":       round(stats["steals"] / games, 1),
            "avg_blocks":       round(stats["blocks"] / games, 1),
            "avg_ft":           round(stats["ft"] / games, 1),
            "avg_ftattempts":   round(stats["ftAttempts"] / games, 1),
            "avg_fieldgoals":   round(stats["fieldGoals"] / games, 1),
            "avg_fieldattempts":round(stats["fieldAttempts"] / games, 1),
            "avg_twofg":        round(stats["twoFg"] / games, 1),
            "avg_twoattempts":  round(stats["twoAttempts"] / games, 1),
            "avg_threefg":      round(stats["threeFg"] / games, 1),
            "avg_threeattempts":round(stats["threeAttempts"] / games, 1),
            "avg_turnovers":    round(stats["turnovers"] / games, 1),
            "avg_personalfouls":round(stats["personalFouls"] / games, 1),
            "ftpercent":        round(stats["ftPercent"] * 100, 1),
            "twopercent":       round(stats["twoPercent"] * 100, 1),
            "threepercent":     round(stats["threePercent"] * 100, 1),
            "fieldpercent":     round(stats["fieldPercent"] * 100, 1),
            "effectfgpercent":  round(stats["effectFgPercent"] * 100, 1)
        })

        # --- Handle Hall of Fame asterisk ---
        player_name = stats.get("playerName", "")
        stats["is_hof"] = player_name.endswith("*")
        stats["playerName"] = player_name.rstrip("*").strip()

        # --- Add team logo ---
        team = stats.get("team", "")
        team_logo_url = get_team_logo_url(team)
        
        # --- Render results page ---
        return render_template(
            "playoffs_totals.html",
            stats=stats,
            team_logo_url=team_logo_url
        )
        
    # --- Render search form ---
    return render_template("playoffs_totals_search.html")


# 📝 Form Route – Advanced Playoff Stats Search
@app.route("/playoffs_advanced_search", methods=["GET", "POST"])
def player_stats_advanced_playoffs():
    if request.method == "POST":
        # --- Retrieve form data ---
        name = request.form.get("name")
        season = request.form.get("season", type=int)

        if not name or not season:
            return error("Missing player name or season", 400)

        # --- Fetch stats from backend ---
        raw = fetch_advanced_playoffs(name, season)
        if "error" in raw:
            return error(raw["error"], 400)

        stats = raw.copy()

        # --- Enhance fields for display ---
        stats["tsPercent"] = round(stats["tsPercent"] * 100, 1)
        stats["minutespergame"] = round(stats["minutesPlayed"] / stats["games"], 1)
        stats["ftr"] = round(stats["ftr"] * 100, 1)

        # --- Handle Hall of Fame asterisk ---
        player_name = stats.get("playerName", "")
        stats["is_hof"] = player_name.endswith("*")
        stats["playerName"] = player_name.rstrip("*").strip()
        
        # --- Add team logo ---
        team = stats.get("team", "")
        team_logo_url = get_team_logo_url(team)


        # --- Render results page ---
        return render_template(
            "playoffs_advanced.html",
            stats=stats,
            team_logo_url=team_logo_url
        )
    # --- Render initial form page ---
    return render_template("playoffs_advanced_search.html")

    
# 📝 Form Route – Quick Access to Player Overview
@app.route("/players", methods=["GET", "POST"])
def players_quick_access():
    if request.method == "POST":
        # --- Retrieve form inputs ---
        name = request.form.get("name")
        season = request.form.get("season", type=int) or datetime.now().year

        if not name:
            return error("Missing player name", 400)

        # --- Render summary page ---
        return render_template(
            "players.html",
            name=name.strip(),
            season=season
        )

    # --- Render initial search form ---
    return render_template("players_search.html")


# 📝 Form Route – Show Player Stat Trends Over Time
@app.route("/player_trends", methods=["GET", "POST"])
def player_trends():
    if request.method == "POST":
        # --- Get form inputs ---
        name = request.form.get("name")
        season = request.form.get("season", type=int)

        if not name or not season:
            return error("Missing player name or season", 400)

        # --- Render trends results ---
        return render_template(
            "player_trends.html",
            name=name,
            season=season
        )

    # --- Render initial form ---
    return render_template("player_trends_search.html")

    
# 📝 Form Route – Compare Two Players' Stats
@app.route("/compare_players", methods=["GET", "POST"])
def compare_players():
    if request.method == "POST":
        # --- Get form inputs ---
        player1 = request.form.get("player1")
        player2 = request.form.get("player2")
        season  = request.form.get("season", type=int)

        if not player1 or not player2 or not season:
            return error("Missing two player names or season", 400)

        # --- Helper: Fetch per-game totals ---
        def get_totals(name):
            raw = fetch_player_totals(name, season)["combined"]
            games = raw.get("games") or 1
            return {
                "PPG": raw.get("points", 0) / games,
                "APG": raw.get("assists", 0) / games,
                "RPG": raw.get("totalRb", 0) / games,
                "BPG": raw.get("blocks", 0) / games,
                "FG%": raw.get("fieldPercent", 0) * 100
            }

        # --- Helper: Fetch advanced metrics ---
        def get_advanced(name):
            raw = fetch_player_advanced(name, season)["combined"]
            return {
                "PER":       raw.get("per", 0),
                "WinShares": raw.get("winShares", 0),
                "Usage%":    raw.get("usagePercent", 0),
                "BPM":       raw.get("box", 0)
            }

        # --- Merge totals + advanced for each player ---
        stats1 = {**get_totals(player1), **get_advanced(player1)}
        stats2 = {**get_totals(player2), **get_advanced(player2)}

        # --- Render comparison results ---
        return render_template(
            "compare_players.html",
            p1=player1, p2=player2,
            season=season,
            stats1=stats1,
            stats2=stats2
        )

    # --- Render initial form ---
    return render_template("compare_players_search.html")


# 📝 Form Route – Display Player Shot Distribution Breakdown
@app.route("/player_shot_distribution", methods=["GET", "POST"])
def player_shot_distribution():
    if request.method == "POST":
        # --- Get form inputs ---
        name = request.form.get("name")
        season = request.form.get("season", type=int)

        if not name or not season:
            return error("Missing player name or season", 400)

        # --- Fetch player data ---
        tot = fetch_player_totals(name, season)["combined"]

        # --- Prepare attempt counts ---
        three_attempts = tot.get("threeAttempts", 0)
        two_attempts = tot.get("twoAttempts", 0)
        ft_attempts = tot.get("ftAttempts", 0)

        # --- Render results page with data ---
        return render_template(
            "player_shot_distribution.html",
            name=name,
            season=season,
            three_attempts=three_attempts,
            two_attempts=two_attempts,
            ft_attempts=ft_attempts
        )

    # --- Render initial form page ---
    return render_template("player_shot_distribution_search.html")



# -----------------------------------
# 📈 Routes – Visual Charts (PNG)
# -----------------------------------
# 📊 Line Chart – Player Trends Over Last 5 Seasons
@app.route("/player_trends.png")
def player_trends_plot():
    name = request.args.get("name")
    season = request.args.get("season", type=int)

    # --- Define the seasons to include (last 5 seasons) ---
    seasons = list(range(season - 4, season + 1))

    # --- Initialize stat trends ---
    ppg, apg, rpg, per = [], [], [], []

    for s in seasons:
        totals = fetch_player_totals(name, s)["combined"]
        advanced = fetch_player_advanced(name, s)["combined"]
        games = totals.get("games") or 1

        ppg.append(round(totals.get("points", 0) / games, 1))
        apg.append(round(totals.get("assists", 0) / games, 1))
        rpg.append(round(totals.get("totalRb", 0) / games, 1))
        per.append(advanced.get("per", 0))

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(6, 4))  
    ax.plot(seasons, ppg, marker='o', label="PPG")
    ax.plot(seasons, apg, marker='o', label="APG")
    ax.plot(seasons, rpg, marker='o', label="RPG")
    ax.plot(seasons, per, marker='o', label="PER")

    ax.set_xlabel("Season", fontsize=10)
    ax.set_ylabel("Value", fontsize=10)
    ax.set_title(f"{name} Trends ({seasons[0]}–{seasons[-1]})", fontsize=12)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()

    # --- Return PNG ---
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype="image/png")


# 📈 Radar Chart – Compare Two Players (Basic + Advanced Stats)
@app.route("/compare_players.png")
def compare_players_plot():
    p1 = request.args["p1"]
    p2 = request.args["p2"]
    season = int(request.args["season"])

    # --- Player Stat Loaders ---
    def get_totals(name):
        raw = fetch_player_totals(name, season)["combined"]
        g = raw.get("games") or 1
        return {
            "PPG": raw["points"] / g,
            "APG": raw["assists"] / g,
            "RPG": raw["totalRb"] / g,
            "BPG": raw["blocks"] / g,
            "FG%": raw["fieldPercent"] * 100
        }

    def get_advanced(name):
        raw = fetch_player_advanced(name, season)["combined"]
        return {
            "PER":       raw.get("per", 0),
            "WinShares": raw.get("winShares", 0),
            "Usage%":    raw.get("usagePercent", 0),
            "BPM":       raw.get("box", 0)
        }

    # --- Fetch data for both players ---
    p1_stats = {**get_totals(p1), **get_advanced(p1)}
    p2_stats = {**get_totals(p2), **get_advanced(p2)}

    labels = list(p1_stats.keys())
    vals1 = list(p1_stats.values()) + [list(p1_stats.values())[0]]  
    vals2 = list(p2_stats.values()) + [list(p2_stats.values())[0]]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    # --- Radar Plot ---
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    max_val = max(vals1 + vals2)
    ax.set_ylim(0, max_val * 1.1)
    ax.set_yticks(np.linspace(0, max_val, 5))
    ax.set_yticklabels([f"{v:.1f}" for v in np.linspace(0, max_val, 5)])

    ax.plot(angles, vals1, marker='o', label=p1)
    ax.fill(angles, vals1, alpha=0.25)
    ax.plot(angles, vals2, marker='o', label=p2)
    ax.fill(angles, vals2, alpha=0.25)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.grid(True)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    fig.tight_layout()

    # --- Output PNG ---
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype="image/png")


# 📊 Pie Chart – Player Shot Distribution
@app.route("/player_shot_distribution.png")
def player_shot_distribution_plot():
    name = request.args.get("name")
    season = request.args.get("season", type=int)
    tot = fetch_player_totals(name, season)["combined"]

    # Shot attempt counts
    values = [
        tot.get("threeAttempts", 0),
        tot.get("twoAttempts", 0),
        tot.get("ftAttempts", 0)
    ]
    labels = ["3PT Attempts", "2PT Attempts", "FT Attempts"]

    # Chart setup: big, colorful, and slightly exploded
    fig, ax = plt.subplots(figsize=(6, 6))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    explode = [0.03, 0.03, 0.03]
    wedges, texts, autotexts = ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        colors=colors,
        explode=explode,
        startangle=90,
        textprops={"fontsize": 11}
    )
    plt.setp(autotexts)
    ax.set_title(f"{name} Shot Distribution ({season})", fontsize=16)
    fig.tight_layout()

    # Return image as response
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype="image/png")










