import os
import datetime
import requests
from playwright.sync_api import sync_playwright

# Complete 30-team dictionary for brand colors and logos
TEAM_ASSETS = {
    "Atlanta Hawks": {"color": "#E03A3E", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/atl.png"},
    "Boston Celtics": {"color": "#007A33", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/bos.png"},
    "Brooklyn Nets": {"color": "#000000", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/bkn.png"},
    "Charlotte Hornets": {"color": "#1D1160", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/cha.png"},
    "Chicago Bulls": {"color": "#CE1141", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/chi.png"},
    "Cleveland Cavaliers": {"color": "#860038", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/cle.png"},
    "Dallas Mavericks": {"color": "#00538C", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/dal.png"},
    "Denver Nuggets": {"color": "#0E2240", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/den.png"},
    "Detroit Pistons": {"color": "#C8102E", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/det.png"},
    "Golden State Warriors": {"color": "#1D428A", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/gs.png"},
    "Houston Rockets": {"color": "#CE1141", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/hou.png"},
    "Indiana Pacers": {"color": "#002D62", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/ind.png"},
    "Los Angeles Clippers": {"color": "#C8102E", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/lac.png"},
    "Los Angeles Lakers": {"color": "#552583", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/lal.png"},
    "Memphis Grizzlies": {"color": "#5D76A9", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/mem.png"},
    "Miami Heat": {"color": "#98002E", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/mia.png"},
    "Milwaukee Bucks": {"color": "#00471B", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/mil.png"},
    "Minnesota Timberwolves": {"color": "#0c2340", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/min.png"},
    "New Orleans Pelicans": {"color": "#0C2340", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/no.png"},
    "New York Knicks": {"color": "#006BB6", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/ny.png"},
    "Oklahoma City Thunder": {"color": "#007AC1", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/okc.png"},
    "Orlando Magic": {"color": "#0077C0", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/orl.png"},
    "Philadelphia 76ers": {"color": "#006BB6", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/phi.png"},
    "Phoenix Suns": {"color": "#1D1160", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/phx.png"},
    "Portland Trail Blazers": {"color": "#E03A3E", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/por.png"},
    "Sacramento Kings": {"color": "#5A2D81", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/sac.png"},
    "San Antonio Spurs": {"color": "#C4CED4", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/sa.png"},
    "Toronto Raptors": {"color": "#CE1141", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/tor.png"},
    "Utah Jazz": {"color": "#002B5C", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/uta.png"},
    "Washington Wizards": {"color": "#002B5C", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/wsh.png"}
}

def get_team_asset(team_name):
    if team_name in TEAM_ASSETS:
        return TEAM_ASSETS[team_name]
    for key, data in TEAM_ASSETS.items():
        if team_name.lower() in key.lower() or key.lower() in team_name.lower():
            return data
    return {"color": "#1e3a8a", "logo": "https://a.espncdn.com/i/teamlogos/nba/500/nba.png"}

def fetch_nba_odds():
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        print("Warning: No ODDS_API_KEY secret found. Using fallback sample games.")
        return get_sample_games()
    
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={api_key}&regions=us&markets=spreads,totals&oddsFormat=american"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"API Error: {response.status_code} - {response.text}")
        return get_sample_games()
    
    data = response.json()
    games = []
    
    for event in data:
        home_team = event.get('home_team')
        away_team = event.get('away_team')
        bookmakers = event.get('bookmakers', [])
        
        if not bookmakers:
            continue
            
        # Grab lines from FanDuel or DraftKings if available, otherwise first bookmaker
        book = next((b for b in bookmakers if b['key'] in ['fanduel', 'draftkings']), bookmakers[0])
        
        away_spread, home_spread, total = "N/A", "N/A", "N/A"
        
        for market in book.get('markets', []):
            if market['key'] == 'spreads':
                for outcome in market.get('outcomes', []):
                    point = outcome.get('point', 0)
                    formatted_point = f"+{point}" if point > 0 else str(point)
                    if outcome['name'] == home_team:
                        home_spread = formatted_point
                    elif outcome['name'] == away_team:
                        away_spread = formatted_point
            elif market['key'] == 'totals':
                for outcome in market.get('outcomes', []):
                    if outcome.get('name') == 'Over':
                        total = str(outcome.get('point', 'N/A'))
                        
        games.append({
            "away": away_team,
            "away_spread": away_spread,
            "total": total,
            "home": home_team,
            "home_spread": home_spread
        })
        
    return games if games else get_sample_games()

def get_sample_games():
    return [
        {"away": "Minnesota Timberwolves", "away_spread": "-3.5", "total": "229.5", "home": "Washington Wizards", "home_spread": "+3.5"},
        {"away": "Dallas Mavericks", "away_spread": "+8.5", "total": "212.5", "home": "Boston Celtics", "home_spread": "-8.5"},
        {"away": "Chicago Bulls", "away_spread": "+9.5", "total": "241.5", "home": "Cleveland Cavaliers", "home_spread": "-9.5"},
        {"away": "Houston Rockets", "away_spread": "-2.5", "total": "230.5", "home": "Miami Heat", "home_spread": "+2.5"},
    ]

def generate_html(games):
    cards_html = ""
    # Limit to 8 games to fit the 1080x1350 vertical layout cleanly
    for g in games[:8]:
        away_data = get_team_asset(g['away'])
        home_data = get_team_asset(g['home'])
        
        cards_html += f"""
        <div class="card">
            <div class="logo-banner">
                <div class="team-half" style="background-color: {away_data['color']};">
                    <img src="{away_data['logo']}" class="team-logo" />
                </div>
                <div class="divider"></div>
                <div class="team-half" style="background-color: {home_data['color']};">
                    <img src="{home_data['logo']}" class="team-logo" />
                </div>
            </div>
            <div class="odds-bar">
                <span>{g['away_spread']}</span>
                <span class="ou-val">{g['total']}</span>
                <span>{g['home_spread']}</span>
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Anton&family=Oswald:wght@600;700&display=swap" rel="stylesheet">
        <style>
            body {{
                background: radial-gradient(circle at 50% 8%, #1b56b8 0%, #071b42 55%, #020817 100%);
                color: white;
                font-family: 'Oswald', sans-serif;
                width: 1080px;
                height: 1350px;
                margin: 0;
                padding: 45px 55px;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            h1 {{
                font-family: 'Anton', sans-serif;
                font-size: 92px;
                letter-spacing: 3px;
                margin: 0 0 25px 0;
                text-transform: uppercase;
                text-shadow: 0 8px 20px rgba(0, 0, 0, 0.55);
            }}
            .column-headers {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 45px;
                width: 100%;
                margin-bottom: 8px;
            }}
            .header-labels {{
                display: flex;
                justify-content: space-around;
                font-size: 22px;
                font-weight: 700;
                letter-spacing: 1.5px;
                color: #e2e8f0;
            }}
            .grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 28px 45px;
                width: 100%;
            }}
            .card {{
                box-shadow: 0 12px 28px rgba(0, 0, 0, 0.65);
                border: 2px solid rgba(255, 255, 255, 0.25);
                background: #0f172a;
                border-radius: 6px;
                overflow: hidden;
            }}
            .logo-banner {{
                display: flex;
                height: 110px;
                position: relative;
                overflow: hidden;
            }}
            .team-half {{
                width: 50%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }}
            .team-half::after {{
                content: '';
                position: absolute;
                inset: 0;
                box-shadow: inset 0 0 25px rgba(0,0,0,0.4);
            }}
            .team-logo {{
                width: 130px;
                height: 130px;
                object-fit: contain;
                filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5));
                z-index: 2;
            }}
            .divider {{
                width: 3px;
                background: rgba(255, 255, 255, 0.4);
                z-index: 3;
            }}
            .odds-bar {{
                background: linear-gradient(180deg, #f8fafc 0%, #cbd5e1 100%);
                color: #0f172a;
                height: 52px;
                display: flex;
                justify-content: space-around;
                align-items: center;
                font-size: 28px;
                font-weight: 700;
                border-top: 2px solid #94a3b8;
            }}
            .footer {{
                margin-top: auto;
                font-family: Arial, sans-serif;
                font-size: 13px;
                color: #94a3b8;
                text-align: center;
                line-height: 1.4;
            }}
        </style>
    </head>
    <body>
        <h1>TODAY'S GAMES</h1>
        <div class="column-headers">
            <div class="header-labels"><span>AWAY</span><span>O/U</span><span>HOME</span></div>
            <div class="header-labels"><span>AWAY</span><span>O/U</span><span>HOME</span></div>
        </div>
        <div class="grid">
            {cards_html}
        </div>
        <div class="footer">
            Gambling Problem? Call 1-800-GAMBLER. Odds subject to change.
        </div>
    </body>
    </html>
    """

def main():
    os.makedirs("output", exist_ok=True)
    games = fetch_nba_odds()
    html_content = generate_html(games)
    
    html_path = "output/temp.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        page.goto(f"file://{os.path.abspath(html_path)}")
        page.screenshot(path="output/nba_schedule_today.png")
        browser.close()
    
    print(f"Successfully generated graphic with {len(games)} games!")

if __name__ == "__main__":
    main()
