import json
import os
import requests

from cs50 import SQL
from flask import redirect, render_template, session, url_for
from tenacity import retry, stop_after_attempt, wait_fixed


TEAM_LOGO_MAP = {
    "ATL": "hawks",
    "BOS": "celtics",
    "CHI": "bulls",
    "CHO": "hornets",
    "BRK": "nets",
    "CLE": "cavaliers",
    "MIA": "heat",
    "NYK": "knicks",
    "TOR": "raptors",
    "DET": "pistons",
    "ORL": "magic",
    "PHI": "76ers",
    "IND": "pacers",
    "WAS": "wizards",
    "MIL": "bucks",
    "LAC": "clippers",
    "LAL": "lakers",
    "DAL": "mavericks",
    "DEN": "nuggets",
    "MIN": "timberwolves",
    "MEM": "grizzlies",
    "OKC": "thunder",
    "NOP": "pelicans",
    "POR": "traiblazers",
    "PHO": "suns",
    "SAS": "spurs",
    "UTA": "jazz",
    "SAC": "kings",
    "GSW": "warriors",
    "HOU": "rockets",
}

def get_team_logo_url(team_abbr):
    """
    Given a 3-letter NBA team abbreviation, return the corresponding SVG logo path.
    """
    slug = TEAM_LOGO_MAP.get(team_abbr)
    if not slug:
        return None
    return url_for("static", filename=f"logos/{slug}_logo.svg")

# -------------------------------------------------------
# 🛠️ Initialize Local SQLite Cache – One-Time Table Setup
# -------------------------------------------------------
def initialize_db():
    if not os.path.exists("nba_cache.db"):
        open("nba_cache.db", "w").close()

    db = SQL("sqlite:///nba_cache.db")
    
    # Regular Season Totals Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS player_totals (
            playerId TEXT,
            season INTEGER,
            team TEXT,
            stats_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (playerId, season, team)
        )
    """)
    # Regular Season Advanced Stats Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS player_advanced (
            playerId TEXT,
            season INTEGER,
            team TEXT,
            stats_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (playerId, season, team)
        )
    """)
    # Playoff Advanced Stats Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS player_advanced_playoffs (
            playerId TEXT,
            season INTEGER,
            team TEXT,
            stats_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (playerId, season, team)
        )
    """)
    # Playoff Totals Table
    db.execute("""
        CREATE TABLE IF NOT EXISTS player_totals_playoffs (
            playerId TEXT,
            season INTEGER,
            team TEXT,
            stats_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (playerId, season, team)
        )
    """)
    return db


# ---------------------------------------------------
# 📊 Fetch Regular Season Totals Stats for a Player
# ---------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def fetch_player_totals(player_name, season, db=None):
    if db is None:
        db = initialize_db()

    try:
        # 🔗 Query NBA Stats API
        response = requests.get(
            "http://rest.nbaapi.com/api/PlayerDataTotals/query",
            params={
                "playerName": player_name,
                "season": season,
                "sortBy": "PlayerName",
                "ascending": True,
                "pageNumber": 1,
                "pageSize": 10
            }
        )

        if response.status_code != 200:
            return {"error": "API request failed".format(response.status_code)}

        data = response.json()
        if not data:
            return {"error": "Player not found"}

        
        player_id = data[0]["playerId"]

        # 🔍 Look for cached combined stats (TOT/2TM)
        cached = db.execute(
            '''
            SELECT stats_json FROM player_totals
            WHERE playerId = ? AND season = ?
              AND team IN ('TOT', '2TM')
              AND timestamp > datetime('now', '-1 day')
            ''',
            player_id, season
        )

        if cached:
            combined_entry = json.loads(cached[0]["stats_json"])
            rows = db.execute(
                '''
                SELECT stats_json FROM player_totals
                WHERE playerId = ? AND season = ?
                ''',
                player_id, season
            )
            entries = [json.loads(r["stats_json"]) for r in rows]
            return {"combined": combined_entry, "entries": entries}

        # 💾 Cache all entries (individual + combined)
        for entry in data:
            db.execute('''
                INSERT OR REPLACE INTO player_totals
                (playerId, season, team, stats_json)
                VALUES (?, ?, ?, ?)
            ''', entry["playerId"], season, entry["team"], json.dumps(entry))

        # 🔢 Prioritize combined stats if available
        combined = next((e for e in data if e["team"] in ("TOT","2TM")), data[0])

        return {
        "combined": combined,
        "entries": data
        }

    except Exception as e:
        return {"error": str(e)}


# ------------------------------------------------------
# 📊 Fetch Regular Season Advanced Stats for a Player
# ------------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def fetch_player_advanced(player_name, season, db=None):
    if db is None:
        db = initialize_db()

    try:
        response = requests.get(
            "http://rest.nbaapi.com/api/PlayerDataAdvanced/query",
            params={
                "playerName": player_name,
                "season": season,
                "sortBy": "PlayerName",
                "ascending": True,
                "pageNumber": 1,
                "pageSize": 10
            }
        )

        if response.status_code != 200:
            return {"error": "API request failed".format(response.status_code)}

        data = response.json()
        if not data:
            return {"error": "Player not found"}

        player_id = data[0]["playerId"]

        # Cache check for advanced stats
        cached = db.execute(
            '''
            SELECT stats_json FROM player_advanced
            WHERE playerId = ? AND season = ?
              AND team IN ('TOT', '2TM')
              AND timestamp > datetime('now', '-1 day')
            ''',
            player_id, season
        )

        if cached:
            combined_entry = json.loads(cached[0]["stats_json"])
            rows = db.execute(
                '''
                SELECT stats_json FROM player_advanced
                WHERE playerId = ? AND season = ?
                ''',
                player_id, season
            )
            entries = [json.loads(r["stats_json"]) for r in rows]
            return {"combined": combined_entry, "entries": entries}

        for entry in data:
            db.execute('''
                INSERT OR REPLACE INTO player_advanced
                (playerId, season, team, stats_json)
                VALUES (?, ?, ?, ?)
            ''', entry["playerId"], season, entry["team"], json.dumps(entry))

        combined = next((e for e in data if e["team"] in ("TOT","2TM")), data[0])

        return {
        "combined": combined,
        "entries": data
        }

    except Exception as e:
        return {"error": str(e)}


# ----------------------------------------------------------
# 📊 Fetch Advanced Playoff Stats for a Player + Caching
# ----------------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def fetch_advanced_playoffs(player_name, season, db=None):
    if db is None:
        db = initialize_db()

    try:

        response = requests.get(
            "http://rest.nbaapi.com/api/PlayerDataAdvancedPlayoffs/query",
            params={
                "playerName": player_name,
                "season": season,
                "sortBy": "PlayerName",
                "ascending": True,
                "pageNumber": 1,
                "pageSize": 10
            }
        )

        if response.status_code != 200:
            return {"error": "API request failed"}

        data = response.json()
        if not data:
            return {"error": "Player not found"}


        player_id = data[0]["playerId"]

        # Cache check
        cached = db.execute('''
            SELECT stats_json FROM player_advanced_playoffs
            WHERE playerId = ? AND season = ?
            AND timestamp > datetime('now', '-1 day')
        ''', player_id, season)

        if cached:
            return json.loads(cached[0]["stats_json"])

        # Store to cache
        for entry in data:
            db.execute('''
                INSERT OR REPLACE INTO player_advanced_playoffs
                (playerId, season, team, stats_json)
                VALUES (?, ?, ?, ?)
            ''', entry["playerId"], season, entry["team"], json.dumps(entry))


        return entry

    except Exception as e:
        return {"error": str(e)}


# ------------------------------------------------------
# 📊 Fetch Totals Playoff Stats for a Player + Caching
# ------------------------------------------------------
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def fetch_playoff_totals(player_name, season, db=None):
    if db is None:
        db = initialize_db()

    try:
        response = requests.get(
            "http://rest.nbaapi.com/api/PlayerDataTotalsPlayoffs/query",
            params={
                "playerName": player_name,
                "season": season,
                "sortBy": "PlayerName",
                "ascending": True,
                "pageNumber": 1,
                "pageSize": 10
            }
        )

        if response.status_code != 200:
            return {"error": "API request failed"}

        data = response.json()
        if not data:
            return {"error": "Player not found"}

        player_id = data[0]["playerId"]

        cached = db.execute('''
            SELECT stats_json FROM player_totals_playoffs
            WHERE playerId = ? AND season = ?
            AND timestamp > datetime('now', '-1 day')
        ''', player_id, season)

        if cached:
            return json.loads(cached[0]["stats_json"])

        for entry in data:
            db.execute('''
                INSERT OR REPLACE INTO player_totals_playoffs
                (playerId, season, team, stats_json)
                VALUES (?, ?, ?, ?)
            ''', entry["playerId"], season, entry["team"], json.dumps(entry))

        return entry

    except Exception as e:
        return {"error": str(e)}


# --------------------------------------
# ❗ Render Error Template for Front-End
# --------------------------------------
def error(message, code=400):
    """Render error message with your custom image."""
    def escape(s):
        for old, new in [
            ("-", "--"), (" ", "-"), ("_", "__"),
            ("?", "~q"), ("%", "~p"), ("#", "~h"),
            ("/", "~s"), ('"', "''")
        ]:
            s = s.replace(old, new)
        return s

    return render_template(
        "error.html",
        top="_",  # leave top blank so it doesn't cover the image
        bottom=escape(f"{code}: {message}")
    ), code


def summarize_player_totals(stats):
    """
    Generate a short summary sentence based on a player's combined regular season stats.
    """
    if not stats or "combined" not in stats:
        return "Sorry, no stats available to generate a summary."

    player = stats["combined"]

    # Safely get values with defaults
    name = player.get("playerName", "Unknown Player")
    season = player.get("season", "unknown season")
    points = player.get("points", 0)
    rebounds = player.get("totalRb", 0)
    assists = player.get("assists", 0)
    games = player.get("games", 0)
    steals = player.get("steals", 0)
    blocks = player.get("blocks", 0)
    fg = player.get("fieldPercent", 0)
    three = player.get("threePercent", 0)
    ft = player.get("ftPercent", 0)
    

    if games == 0:
        return f"{name} did not play any games in the {season} season."

    ppg = round(points / games, 1)
    rpg = round(rebounds / games, 1)
    apg = round(assists / games, 1)
    stl = round(steals / games, 1)
    blk = round(blocks / games, 1)

    return (
        f"In the {season} season, {name} played {games} games, "
        f"averaging {ppg} points, {rpg} rebounds, and {apg} assists per game. "
        f"{name} also had {stl} steals and {blk} blocks per game. "
        f"He shot {fg:.1%} from the field, {three:.1%} from three-point range, " 
        f"and {ft:.1%} from the free-throw line."
    )

#f"In the {season} season, {name} played {games} games, "
#f"averaging {ppg} points, {rpg} rebounds, and {apg} assists per game."

#def summarize_player_totals(stats):
    """Generate a rule-based summary of a player's season stats."""
    name = stats["playerName"]
    season = stats["season"]
    pts = stats["points"]
    ast = stats["assists"]
    trb = stats["totalRb"]
    stl = stats["steals"]
    blk = stats["blocks"]
    fg = stats["fieldPercent"]
    three = stats["threePercent"]
    ft = stats["ftPercent"]

    summary = (
        f"In the {season} season, {name} scored {pts} points, grabbed {trb} rebounds, "
        f"and dished out {ast} assists. He also recorded {stl} steals and {blk} blocks. "
        f"{name} shot {fg:.1%} from the field, {three:.1%} from three-point range, and {ft:.1%} from the free-throw line."
    )

    return summary



