#some older code that i have needed to remove due to them either not being needed
# or being exchanged for better code or the fact that they were only initially used
# for testing purposes 

import requests
import sqlite3
import json
from tenacity import retry, stop_after_attempt, wait_fixed

# Initialize SQLite cache
conn = sqlite3.connect('nba_cache.db')
db = conn.cursor()
db.execute('''CREATE TABLE IF NOT EXISTS player_stats (
                player_name TEXT,
                season INTEGER,
                stats_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_name, season)
           )''')
conn.commit()

player = input("Player: ")
year = input("Season: ")
year = int(year)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def fetch_player_totals(player_name, season=year):
    try:
        # Check cache first (valid for 24 hours)
        db.execute('''SELECT stats_json FROM player_stats
                    WHERE player_name = ? AND season = ?
                    AND timestamp > datetime('now', '-1 day')''',
                    (player_name, season))
        cached = db.fetchone()
        if cached:
            return json.loads(cached[0])

        # Fetch from API
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
            return {"error": "API request failed"}

        data = response.json()
        if not data:
            return {"error": "Player not found"}

        # Extract first match (most relevant)
        stats = data[0]

        # Cache results
        db.execute('''INSERT OR REPLACE INTO player_stats
                    (player_name, season, stats_json)
                    VALUES (?, ?, ?)''',
                    (player_name, season, json.dumps(stats)))
        conn.commit()

        return stats

    except Exception as e:
        return {"error": str(e)}

# Test

print(fetch_player_totals(player, year))


# older routes from app.py

# Pie‐chart generator route
@app.route("/player_shot_distribution.png")
def player_shot_distribution_plot():
    
    
    
    name = request.args.get("name")
    season = request.args.get("season", type=int)

    # Grab the combined totals for that player-season
    tot = fetch_player_totals(name, season)["combined"]

    # Build the three slices
    three = tot.get("threeAttempts", 0)
    two = tot.get("twoAttempts", 0)
    ft = tot.get("ftAttempts", 0)
    labels = ["3PT Attempts", "2PT Attempts", "FT Attempts"]
    values = [three, two, ft]

    # Create the pie chart
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%")
    ax.set_title(f"{name} Shot Distribution ({season})")
    fig.tight_layout()

    # Send back as PNG
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype="image/png")


@app.route("/test")
def test():
    return error("Player not found", 404)


#the below was from helpers.py
# for testing purposes and creation of database every time i tweak it
if __name__ == "__main__":
    db = initialize_db()
    rows = db.execute("SELECT team FROM player_totals WHERE playerId = ?", "doncilu01")
    #print([row["team"] for row in rows])
    #print(fetch_player_totals("Luka Dončić", 2025, db))
    #print(fetch_player_advanced("Luka Dončić", 2025, db))
    #print(fetch_advanced_playoffs("LeBron James", 2018, db))
    #print(fetch_playoff_totals("LeBron James", 2018, db))