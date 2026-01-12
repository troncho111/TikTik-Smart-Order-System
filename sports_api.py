"""
Sports API Module
Fetches football team data from TheSportsDB
"""

import requests
import json
import os
from functools import lru_cache

LEAGUES = {
    "מונדיאל 2026": "FIFA World Cup 2026",
    "ליגת האלופות": "UEFA Champions League",
    "ליגה ספרדית": "Spanish La Liga",
    "פרמיירליג": "English Premier League", 
    "סריה A": "Italian Serie A",
    "בונדסליגה": "German Bundesliga",
    "ליג 1": "French Ligue 1"
}

LEAGUE_IDS = {
    "Spanish La Liga": 4335,
    "English Premier League": 4328,
    "Italian Serie A": 4332,
    "German Bundesliga": 4331,
    "French Ligue 1": 4334,
    "UEFA Champions League": 4480
}

OPENFOOTBALL_URLS = {
    "Spanish La Liga": "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/es.1.json",
    "English Premier League": "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/en.1.json",
    "Italian Serie A": "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/it.1.json",
    "German Bundesliga": "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/de.1.json",
    "French Ligue 1": "https://raw.githubusercontent.com/openfootball/football.json/master/2024-25/fr.1.json"
}

TEAM_HEBREW_NAMES = {
    # La Liga (Spain)
    "ברצלונה": "Barcelona",
    "ריאל מדריד": "Real Madrid",
    "אתלטיקו מדריד": "Atletico Madrid",
    "סביליה": "Sevilla",
    "ולנסיה": "Valencia",
    "ריאל בטיס": "Real Betis",
    "ריאל סוסיאדד": "Real Sociedad",
    "אתלטיק בילבאו": "Athletic Bilbao",
    "ויאריאל": "Villarreal",
    "אוסאסונה": "Osasuna",
    "לגאנס": "Leganes",
    "אלאבס": "Alaves",
    "חטאפה": "Getafe",
    "ג'ירונה": "Girona",
    "סלטה ויגו": "Celta Vigo",
    "אספניול": "Espanyol",
    "מיורקה": "Mallorca",
    "ראיו ואייקאנו": "Rayo Vallecano",
    "ויאדוליד": "Valladolid",
    "לאס פלמאס": "Las Palmas",
    
    # Premier League (England)
    "מנצ'סטר יונייטד": "Manchester United",
    "מנצ'סטר סיטי": "Manchester City",
    "ליברפול": "Liverpool",
    "צ'לסי": "Chelsea",
    "ארסנל": "Arsenal",
    "טוטנהאם": "Tottenham",
    "ניוקאסל": "Newcastle",
    "אסטון וילה": "Aston Villa",
    "בורנמות'": "Bournemouth",
    "ברנטפורד": "Brentford",
    "ברייטון": "Brighton",
    "קריסטל פאלאס": "Crystal Palace",
    "אברטון": "Everton",
    "פולהאם": "Fulham",
    "איפסוויץ'": "Ipswich",
    "לסטר": "Leicester",
    "נוטינגהאם פורסט": "Nottingham Forest",
    "סאות'המפטון": "Southampton",
    "ווסטהאם": "West Ham",
    "וולבס": "Wolves",
    
    # Serie A (Italy)
    "יובנטוס": "Juventus",
    "מילאן": "AC Milan",
    "אינטר מילאן": "Inter Milan",
    "אינטר": "Inter",
    "נאפולי": "Napoli",
    "רומא": "Roma",
    "לאציו": "Lazio",
    "אטאלנטה": "Atalanta",
    "פיורנטינה": "Fiorentina",
    "מונזה": "Monza",
    "בולוניה": "Bologna",
    "קליארי": "Cagliari",
    "קומו": "Como",
    "אמפולי": "Empoli",
    "ג'נואה": "Genoa",
    "ורונה": "Verona",
    "פארמה": "Parma",
    "טורינו": "Torino",
    "לצ'ה": "Lecce",
    "אודינזה": "Udinese",
    "ונציה": "Venezia",
    
    # Bundesliga (Germany)
    "באיירן מינכן": "Bayern Munich",
    "באיירן": "Bayern",
    "דורטמונד": "Borussia Dortmund",
    "לייפציג": "RB Leipzig",
    "לברקוזן": "Bayer Leverkusen",
    "היידנהיים": "Heidenheim",
    "אוניון ברלין": "Union Berlin",
    "מיינץ": "Mainz",
    "גלאדבאך": "Gladbach",
    "פרנקפורט": "Frankfurt",
    "אוגסבורג": "Augsburg",
    "סנט פאולי": "St Pauli",
    "הולשטיין קיל": "Holstein Kiel",
    "פרייבורג": "Freiburg",
    "ורדר ברמן": "Werder Bremen",
    "הופנהיים": "Hoffenheim",
    "שטוטגרט": "Stuttgart",
    "בוכום": "Bochum",
    "וולפסבורג": "Wolfsburg",
    
    # Ligue 1 (France)
    "פריז סן ז'רמן": "Paris Saint Germain",
    "פ.ס.ז'": "PSG",
    "מרסיי": "Marseille",
    "ליון": "Lyon",
    "מונקו": "Monaco",
    "אוקסר": "Auxerre",
    "סנט אטיין": "Saint-Etienne",
    "אנז'ה": "Angers",
    "נאנט": "Nantes",
    "לה האבר": "Le Havre",
    "ליל": "Lille",
    "מונפלייה": "Montpellier",
    "ניס": "Nice",
    "סטרסבורג": "Strasbourg",
    "לאנס": "Lens",
    "ברסט": "Brest",
    "רן": "Rennes",
    "ריימס": "Reims",
    "טולוז": "Toulouse",
    
    # World Cup 2026 National Teams
    "מקסיקו": "Mexico",
    "ארה\"ב": "USA",
    "קנדה": "Canada",
    "ברזיל": "Brazil",
    "ארגנטינה": "Argentina",
    "גרמניה": "Germany",
    "צרפת": "France",
    "ספרד": "Spain",
    "אנגליה": "England",
    "פורטוגל": "Portugal",
    "הולנד": "Netherlands",
    "בלגיה": "Belgium",
    "קרואטיה": "Croatia",
    "מרוקו": "Morocco",
    "יפן": "Japan",
    "קוריאה": "Korea Republic",
    "דרום קוריאה": "Korea Republic",
    "אוסטרליה": "Australia",
    "סעודיה": "Saudi Arabia",
    "ערב הסעודית": "Saudi Arabia",
    "קטאר": "Qatar",
    "איראן": "Iran",
    "מצרים": "Egypt",
    "אלג'יריה": "Algeria",
    "סנגל": "Senegal",
    "גאנה": "Ghana",
    "חוף השנהב": "Cote d'Ivoire",
    "קולומביה": "Colombia",
    "אורוגוואי": "Uruguay",
    "אקוודור": "Ecuador",
    "פרגוואי": "Paraguay",
    "שוויץ": "Switzerland",
    "אוסטריה": "Austria",
    "נורבגיה": "Norway",
    "סקוטלנד": "Scotland",
    "פנמה": "Panama",
    "האיטי": "Haiti",
    "דרום אפריקה": "South Africa",
    "טוניסיה": "Tunisia",
    "ניו זילנד": "New Zealand",
    "ירדן": "Jordan",
    "אוזבקיסטן": "Uzbekistan",
    "קאבו ורדה": "Cabo Verde",
    "קוראסאו": "Curacao",
}

def get_hebrew_name(english_name: str) -> str:
    """Get Hebrew name for a team"""
    for heb, eng in TEAM_HEBREW_NAMES.items():
        if eng.lower() == english_name.lower():
            return heb
    return english_name

def get_english_name(hebrew_name: str) -> str:
    """Get English name for a Hebrew team name"""
    return TEAM_HEBREW_NAMES.get(hebrew_name, hebrew_name)

@lru_cache(maxsize=20)
def get_teams_by_league(league_name: str) -> list:
    """Get all teams in a league"""
    try:
        url = f"https://www.thesportsdb.com/api/v1/json/3/search_all_teams.php?l={league_name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        teams = data.get('teams', []) or []
        return [{
            'name': t.get('strTeam', ''),
            'stadium': t.get('strStadium', ''),
            'stadium_location': t.get('strStadiumLocation', ''),
            'badge': t.get('strTeamBadge', ''),
            'capacity': t.get('intStadiumCapacity', '')
        } for t in teams if t.get('strTeam')]
    except Exception as e:
        print(f"Error fetching teams: {e}")
        return []


def search_team(team_name: str) -> dict:
    """Search for a team by name"""
    try:
        url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        teams = data.get('teams', []) or []
        if teams:
            t = teams[0]
            return {
                'name': t.get('strTeam', ''),
                'stadium': t.get('strStadium', ''),
                'stadium_location': t.get('strStadiumLocation', ''),
                'badge': t.get('strTeamBadge', ''),
                'capacity': t.get('intStadiumCapacity', '')
            }
        return {}
    except Exception as e:
        print(f"Error searching team: {e}")
        return {}


def get_all_popular_teams() -> list:
    """Get teams from all major leagues"""
    all_teams = []
    for hebrew_name, english_name in LEAGUES.items():
        teams = get_teams_by_league(english_name)
        for team in teams:
            team['league'] = hebrew_name
        all_teams.extend(teams)
    return all_teams


@lru_cache(maxsize=20)
def get_season_fixtures(league_name: str, season: str = "2024-2025") -> list:
    """Get all fixtures for a league season from openfootball GitHub or local file"""
    try:
        if league_name == "FIFA World Cup 2026":
            local_file = os.path.join(os.path.dirname(__file__), "worldcup2026.json")
            if os.path.exists(local_file):
                with open(local_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                matches = data.get('matches', []) or []
                return [{
                    'id': str(i),
                    'home_team': m.get('team1', ''),
                    'away_team': m.get('team2', ''),
                    'date': m.get('date', ''),
                    'time': m.get('time', ''),
                    'round': m.get('round', ''),
                    'venue': m.get('venue', '')
                } for i, m in enumerate(matches) if m.get('team1')]
            return []
        
        url = OPENFOOTBALL_URLS.get(league_name)
        if not url:
            return []
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        matches = data.get('matches', []) or []
        return [{
            'id': str(i),
            'home_team': m.get('team1', ''),
            'away_team': m.get('team2', ''),
            'date': m.get('date', ''),
            'time': m.get('time', ''),
            'round': m.get('round', '')
        } for i, m in enumerate(matches) if m.get('team1')]
    except Exception as e:
        print(f"Error fetching fixtures: {e}")
        return []


def normalize_team_name(name: str) -> str:
    """Normalize team name for matching"""
    name = name.lower().strip()
    for prefix in ['fc ', 'cf ', 'afc ', 'rcd ', 'real ', 'ac ', 'as ']:
        if name.startswith(prefix):
            name = name[len(prefix):]
    for suffix in [' fc', ' cf', ' afc', ' sc', ' ac', ' fk']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    return name.strip()


TEAM_EXACT_NAMES = {
    # La Liga (Spain)
    'barcelona': 'fc barcelona',
    'real madrid': 'real madrid cf',
    'atletico madrid': 'club atlético de madrid',
    'athletic bilbao': 'athletic club',
    'real betis': 'real betis balompié',
    'real sociedad': 'real sociedad de fútbol',
    'sevilla': 'sevilla fc',
    'valencia': 'valencia cf',
    'villarreal': 'villarreal cf',
    'osasuna': 'ca osasuna',
    'leganes': 'cd leganés',
    'alaves': 'deportivo alavés',
    'getafe': 'getafe cf',
    'girona': 'girona fc',
    'celta vigo': 'rc celta de vigo',
    'espanyol': 'rcd espanyol de barcelona',
    'mallorca': 'rcd mallorca',
    'rayo vallecano': 'rayo vallecano de madrid',
    'valladolid': 'real valladolid cf',
    'las palmas': 'ud las palmas',
    
    # Premier League (England)
    'manchester united': 'manchester united fc',
    'manchester city': 'manchester city fc',
    'liverpool': 'liverpool fc',
    'chelsea': 'chelsea fc',
    'arsenal': 'arsenal fc',
    'tottenham': 'tottenham hotspur fc',
    'newcastle': 'newcastle united fc',
    'aston villa': 'aston villa fc',
    'bournemouth': 'afc bournemouth',
    'brentford': 'brentford fc',
    'brighton': 'brighton & hove albion fc',
    'crystal palace': 'crystal palace fc',
    'everton': 'everton fc',
    'fulham': 'fulham fc',
    'ipswich': 'ipswich town fc',
    'leicester': 'leicester city fc',
    'nottingham forest': 'nottingham forest fc',
    'southampton': 'southampton fc',
    'west ham': 'west ham united fc',
    'wolves': 'wolverhampton wanderers fc',
    'wolverhampton': 'wolverhampton wanderers fc',
    
    # Serie A (Italy)
    'juventus': 'juventus fc',
    'inter milan': 'fc internazionale milano',
    'inter': 'fc internazionale milano',
    'ac milan': 'ac milan',
    'milan': 'ac milan',
    'napoli': 'ssc napoli',
    'roma': 'as roma',
    'lazio': 'ss lazio',
    'atalanta': 'atalanta bc',
    'fiorentina': 'acf fiorentina',
    'monza': 'ac monza',
    'bologna': 'bologna fc 1909',
    'cagliari': 'cagliari calcio',
    'como': 'como 1907',
    'empoli': 'empoli fc',
    'genoa': 'genoa cfc',
    'verona': 'hellas verona fc',
    'parma': 'parma calcio 1913',
    'torino': 'torino fc',
    'lecce': 'us lecce',
    'udinese': 'udinese calcio',
    'venezia': 'venezia fc',
    
    # Bundesliga (Germany)
    'bayern munich': 'fc bayern münchen',
    'bayern': 'fc bayern münchen',
    'borussia dortmund': 'borussia dortmund',
    'dortmund': 'borussia dortmund',
    'bayer leverkusen': 'bayer 04 leverkusen',
    'leverkusen': 'bayer 04 leverkusen',
    'rb leipzig': 'rb leipzig',
    'leipzig': 'rb leipzig',
    'heidenheim': '1. fc heidenheim 1846',
    'union berlin': '1. fc union berlin',
    'mainz': '1. fsv mainz 05',
    'gladbach': 'borussia mönchengladbach',
    'monchengladbach': 'borussia mönchengladbach',
    'eintracht frankfurt': 'eintracht frankfurt',
    'frankfurt': 'eintracht frankfurt',
    'augsburg': 'fc augsburg',
    'st pauli': 'fc st. pauli 1910',
    'holstein kiel': 'holstein kiel',
    'kiel': 'holstein kiel',
    'freiburg': 'sc freiburg',
    'werder bremen': 'sv werder bremen',
    'bremen': 'sv werder bremen',
    'hoffenheim': 'tsg 1899 hoffenheim',
    'stuttgart': 'vfb stuttgart',
    'bochum': 'vfl bochum 1848',
    'wolfsburg': 'vfl wolfsburg',
    
    # Ligue 1 (France)
    'psg': 'paris saint-germain fc',
    'paris saint germain': 'paris saint-germain fc',
    'marseille': 'olympique de marseille',
    'lyon': 'olympique lyonnais',
    'auxerre': 'aj auxerre',
    'monaco': 'as monaco fc',
    'saint-etienne': 'as saint-étienne',
    'angers': 'angers sco',
    'nantes': 'fc nantes',
    'le havre': 'le havre ac',
    'lille': 'lille osc',
    'montpellier': 'montpellier hsc',
    'nice': 'ogc nice',
    'strasbourg': 'rc strasbourg alsace',
    'lens': 'racing club de lens',
    'brest': 'stade brestois 29',
    'rennes': 'stade rennais fc 1901',
    'reims': 'stade de reims',
    'toulouse': 'toulouse fc',
    
    # World Cup 2026 National Teams
    'ivory coast': "cote d'ivoire",
    'south korea': 'korea republic',
    'korea': 'korea republic',
}


def teams_match(search_name: str, fixture_name: str) -> bool:
    """Check if team names match using exact name mappings"""
    search_lower = search_name.lower().strip()
    fix_lower = fixture_name.lower().strip()
    
    if search_lower == fix_lower:
        return True
    
    expected_name = TEAM_EXACT_NAMES.get(search_lower)
    if expected_name:
        return fix_lower == expected_name
    
    return False


def find_fixture(home_team: str, away_team: str, league_name: str, season: str = "2024-2025") -> dict:
    """Find a specific fixture by home and away team"""
    fixtures = get_season_fixtures(league_name, season)
    
    for fixture in fixtures:
        home_match = teams_match(home_team, fixture['home_team'])
        away_match = teams_match(away_team, fixture['away_team'])
        
        if home_match and away_match:
            if fixture.get('date') and fixture.get('time'):
                return fixture
    
    for fixture in fixtures:
        home_match = teams_match(home_team, fixture['home_team'])
        away_match = teams_match(away_team, fixture['away_team'])
        
        if home_match and away_match:
            return fixture
    
    return {}
