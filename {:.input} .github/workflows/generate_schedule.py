import os
import json
import requests
from playwright.sync_api import sync_playwright

def fetch_nba_odds():
    # Example using The Odds API (or plug in your preferred sports data source)
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        print("No API key found, using sample fallback data for demo.")
        return get_sample_games()
    
    url = f"https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={api_key}&regions=us&markets=spreads,totals&oddsFormat=american"
    response = requests.get(url)
    if response.status_code == 200:
        return parse_odds_data(response.json())
    return get_sample_games()

def get_sample_games():
    # Fallback structure matching your graphic layout
    return [
        {"away": "Timberwolves", "away_spread": "-3.5", "total": "229.5", "home": "Wizards", "home_spread": "+3.5"},
        {"away": "Mavericks", "away_spread": "+8.5", "total": "212.5", "home": "Celtics", "home_spread": "-8.5"},
        {"away": "Bulls", "away_spread": "+9.5", "total": "241.5", "home": "Cavaliers", "home_spread": "-9.5"},
        {"away": "Rockets", "away_spread": "-2.5", "total": "230.5", "home": "Heat", "home_spread": "+2.5"},
    ]

def parse_odds_data(data):
    # Parse incoming API JSON into clean match objects for your template
    games = []
    for event in data[:8]: # Grab up to 8 games
        home = event.get('home_team')
        away = event.get('away_team')
        # Extract bookmaker spreads & totals logic here...
    return games if games else get_sample_games()

def generate_html(games):
    # Generates the exact visual layout from your reference graphic
    cards_html = ""
    for g in games:
        cards_html += f"""
        <div class="matchup-card">
            <div class="teams-row">
                <span class="team-label">AWAY</span>
                <span class="ou-label">O/U</span>
                <span class="team-label">HOME</span>
            </div>
            <div class="matchup-box">
                <div class="team away">{g['away']}</div>
                <div class="odds">{g['away_spread']}</div>
                <div class="total">{g['total']}</div>
                <div class="odds">{g['home_spread']}</div>
                <div class="team home">{g['home']}</div>
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                background: linear-gradient(135deg, #0b1d3a, #040d1a);
                color: white;
                font-family: Arial, sans-serif;
                width: 1080px;
                height: 1350px;
                margin: 0;
                padding: 40px;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            h1 {{ font-size: 56px; font-weight: 900; letter-spacing: 2px; margin-bottom: 40px; text-transform: uppercase; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; width: 100%; }}
            .matchup-box {{ background: #15294a; border-radius: 12px; padding: 20px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #274472; }}
            .team {{ font-weight: bold; font-size: 20px; width: 30%; }}
            .odds, .total {{ background: white; color: #111; padding: 10px 15px; border-radius: 6px; font-weight: bold; font-size: 22px; }}
            .footer {{ margin-top: auto; font-size: 14px; color: #aaa; text-align: center; }}
        </style>
    </head>
    <body>
        <h1>Today's Games</h1>
        <div class="grid">
            {cards_html}
        </div>
        <div class="footer">
            Gambling Problem? Call 1-800-GAMBLER. FanDuel Sportsbook.
        </div>
    </body>
    </html>
    """

def main():
    os.makedirs("output", exist_ok=True)
    games = fetch_nba_odds()
    html_content = generate_html(games)
    
    html_path = "output/temp.html"
    with open(html_path, "w") as f:
        f.write(html_content)

    # Use Playwright to render the HTML into a sharp PNG image
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        page.goto(f"file://{os.path.abspath(html_path)}")
        page.screenshot(path="output/nba_schedule_today.png")
        browser.close()
    print("Graphic generated successfully: output/nba_schedule_today.png")

if __name__ == "__main__":
    main()
