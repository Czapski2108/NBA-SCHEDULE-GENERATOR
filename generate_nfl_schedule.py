import os
import requests
from playwright.sync_api import sync_playwright

NFL_TEAM_ASSETS = {
    "Arizona Cardinals": {"color": "#97233F", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/ari.png"},
    "Atlanta Falcons": {"color": "#A71930", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png"},
    "Baltimore Ravens": {"color": "#241773", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/bal.png"},
    "Buffalo Bills": {"color": "#00338D", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/buf.png"},
    "Carolina Panthers": {"color": "#0085CA", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/car.png"},
    "Chicago Bears": {"color": "#0B162A", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/chi.png"},
    "Cincinnati Bengals": {"color": "#FB4F14", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/cin.png"},
    "Cleveland Browns": {"color": "#311D00", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/cle.png"},
    "Dallas Cowboys": {"color": "#041E42", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png"},
    "Denver Broncos": {"color": "#FB4F14", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/den.png"},
    "Detroit Lions": {"color": "#0076B6", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/det.png"},
    "Green Bay Packers": {"color": "#203731", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/gb.png"},
    "Houston Texans": {"color": "#03202F", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/hou.png"},
    "Indianapolis Colts": {"color": "#002C5F", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/ind.png"},
    "Jacksonville Jaguars": {"color": "#006778", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/jax.png"},
    "Kansas City Chiefs": {"color": "#E31837", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/kc.png"},
    "Las Vegas Raiders": {"color": "#101820", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/lv.png"},
    "Los Angeles Chargers": {"color": "#0080C6", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/lac.png"},
    "Los Angeles Rams": {"color": "#003594", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/lar.png"},
    "Miami Dolphins": {"color": "#008E97", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/mia.png"},
    "Minnesota Vikings": {"color": "#4F2683", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/min.png"},
    "New England Patriots": {"color": "#002244", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/ne.png"},
    "New Orleans Saints": {"color": "#D3BC8D", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/no.png"},
    "New York Giants": {"color": "#0B2265", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png"},
    "New York Jets": {"color": "#125740", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png"},
    "Philadelphia Eagles": {"color": "#004C54", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/phi.png"},
    "Pittsburgh Steelers": {"color": "#FFB612", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/pit.png"},
    "San Francisco 49ers": {"color": "#AA0000", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/sf.png"},
    "Seattle Seahawks": {"color": "#002244", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/sea.png"},
    "Tampa Bay Buccaneers": {"color": "#D50A0A", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/tb.png"},
    "Tennessee Titans": {"color": "#0C2340", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/ten.png"},
    "Washington Commanders": {"color": "#5A1414", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/wsh.png"},
}


def get_nfl_asset(team_name):
    if team_name in NFL_TEAM_ASSETS:
        return NFL_TEAM_ASSETS[team_name]
    for key, data in NFL_TEAM_ASSETS.items():
        if team_name.lower() in key.lower() or key.lower() in team_name.lower():
            return data
    return {"color": "#14532d", "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/nfl.png"}


def get_sample_nfl_games():
    return [
        {"away": "Detroit Lions", "away_spread": "-3.5", "total": "51.5", "home": "Green Bay Packers", "home_spread": "+3.5", "book": "Circa"},
        {"away": "Buffalo Bills", "away_spread": "-6.5", "total": "48.0", "home": "Miami Dolphins", "home_spread": "+6.5", "book": "Circa"},
        {"away": "Baltimore Ravens", "away_spread": "-2.5", "total": "49.5", "home": "Cincinnati Bengals", "home_spread": "+2.5", "book": "Circa"},
        {"away": "Kansas City Chiefs", "away_spread": "-4.5", "total": "46.5", "home": "Denver Broncos", "home_spread": "+4.5", "book": "Circa"},
    ]


def fetch_nfl_odds():
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        print("Warning: No ODDS_API_KEY found. Using sample NFL games.")
        return get_sample_nfl_games()

    url = (
        f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/"
        f"?apiKey={api_key}&regions=us&markets=spreads,totals&oddsFormat=american"
    )
    response = requests.get(url)

    if response.status_code != 200:
        print(f"API Error: {response.status_code} - {response.text}")
        return get_sample_nfl_games()

    data = response.json()
    games = []

    for event in data:
        home_team = event.get("home_team")
        away_team = event.get("away_team")
        bookmakers = event.get("bookmakers", [])

        if not bookmakers:
            continue

        # Primary: Circa -> Fallback: FanDuel -> Fallback: first available book
        book = next((b for b in bookmakers if b.get("key") == "circa"), None)
        if not book:
            book = next((b for b in bookmakers if b.get("key") == "fanduel"), None)
        if not book:
            book = bookmakers[0]

        away_spread, home_spread, total = "N/A", "N/A", "N/A"

        for market in book.get("markets", []):
            if market.get("key") == "spreads":
                for outcome in market.get("outcomes", []):
                    point = outcome.get("point")
                    if point is None:
                        continue
                    formatted_point = f"+{point:g}" if point > 0 else f"{point:g}"
                    if outcome.get("name") == home_team:
                        home_spread = formatted_point
                    elif outcome.get("name") == away_team:
                        away_spread = formatted_point
            elif market.get("key") == "totals":
                for outcome in market.get("outcomes", []):
                    if outcome.get("name") == "Over" and outcome.get("point") is not None:
                        total = f"{outcome.get('point'):g}"

        print(f"Pulled {away_team} @ {home_team} from: {book.get('title', 'Unknown')}")
        games.append({
            "away": away_team,
            "away_spread": away_spread,
            "total": total,
            "home": home_team,
            "home_spread": home_spread,
            "book": book.get("title", ""),
        })

    return games[:16] if games else get_sample_nfl_games()


def generate_html(games):
    cards_html = ""
    for g in games[:16]:
        away_data = get_nfl_asset(g["away"])
        home_data = get_nfl_asset(g["home"])

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
                background: radial-gradient(circle at 50% 8%, #15803d 0%, #064e3b 52%, #022c22 100%);
                color: white;
                font-family: 'Oswald', sans-serif;
                width: 1080px;
                height: 1350px;
                margin: 0;
                padding: 32px 48px;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
                align-items: center;
                overflow: hidden;
            }}
            h1 {{
                font-family: 'Anton', sans-serif;
                font-size: 72px;
                letter-spacing: 2.5px;
                margin: 0 0 12px 0;
                text-transform: uppercase;
                text-shadow: 0 6px 18px rgba(0, 0, 0, 0.55);
            }}
            .column-headers {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 38px;
                width: 100%;
                margin-bottom: 6px;
            }}
            .header-labels {{
                display: flex;
                justify-content: space-around;
                font-size: 19px;
                font-weight: 700;
                letter-spacing: 1px;
                color: #dcfce7;
            }}
            .grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 11px 38px;
                width: 100%;
            }}
            .card {{
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.55);
                border: 2px solid rgba(255, 255, 255, 0.22);
                background: #052e16;
                border-radius: 4px;
                overflow: hidden;
            }}
            .logo-banner {{
                display: flex;
                height: 64px;
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
                box-shadow: inset 0 0 18px rgba(0, 0, 0, 0.42);
            }}
            .team-logo {{
                width: 82px;
                height: 82px;
                object-fit: contain;
                filter: drop-shadow(0 3px 6px rgba(0, 0, 0, 0.5));
                z-index: 2;
            }}
            .divider {{
                width: 2px;
                background: rgba(255, 255, 255, 0.35);
                z-index: 3;
            }}
            .odds-bar {{
                background: linear-gradient(180deg, #f8fafc 0%, #cbd5e1 100%);
                color: #052e16;
                height: 34px;
                display: flex;
                justify-content: space-around;
                align-items: center;
                font-size: 20px;
                font-weight: 700;
                border-top: 1px solid #94a3b8;
            }}
            .footer {{
                margin-top: auto;
                font-family: Arial, sans-serif;
                font-size: 12px;
                color: #bbf7d0;
                text-align: center;
                opacity: 0.85;
            }}
        </style>
    </head>
    <body>
        <h1>NFL SLATE ({len(games)})</h1>
        <div class="column-headers">
            <div class="header-labels"><span>AWAY</span><span>O/U</span><span>HOME</span></div>
            <div class="header-labels"><span>AWAY</span><span>O/U</span><span>HOME</span></div>
        </div>
        <div class="grid">
            {cards_html}
        </div>
        <div class="footer">
            Lines prioritize Circa (FanDuel fallback). Gambling Problem? Call 1-800-GAMBLER. Odds subject to change.
        </div>
    </body>
    </html>
    """


def main():
    os.makedirs("output", exist_ok=True)
    games = fetch_nfl_odds()
    html_content = generate_html(games)

    html_path = "output/nfl_temp.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        page.goto(f"file://{os.path.abspath(html_path)}")
        page.screenshot(path="output/nfl_schedule_week.png")
        browser.close()

    print(f"Successfully generated NFL graphic with {len(games)} games!")


if __name__ == "__main__":
    main()
