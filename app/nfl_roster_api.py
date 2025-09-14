# NFL Roster API Backend - Python Flask Server
# For deployment to Railway, Render, or similar cloud platforms

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
import os
from datetime import datetime, timedelta
import json
from functools import wraps
from typing import Dict, List, Optional

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# NFL Teams with ESPN IDs
NFL_TEAMS = {
    'Arizona Cardinals': {'id': 22, 'abbr': 'ARI'},
    'Atlanta Falcons': {'id': 1, 'abbr': 'ATL'},
    'Baltimore Ravens': {'id': 33, 'abbr': 'BAL'},
    'Buffalo Bills': {'id': 2, 'abbr': 'BUF'},
    'Carolina Panthers': {'id': 29, 'abbr': 'CAR'},
    'Chicago Bears': {'id': 3, 'abbr': 'CHI'},
    'Cincinnati Bengals': {'id': 4, 'abbr': 'CIN'},
    'Cleveland Browns': {'id': 5, 'abbr': 'CLE'},
    'Dallas Cowboys': {'id': 6, 'abbr': 'DAL'},
    'Denver Broncos': {'id': 7, 'abbr': 'DEN'},
    'Detroit Lions': {'id': 8, 'abbr': 'DET'},
    'Green Bay Packers': {'id': 9, 'abbr': 'GB'},
    'Houston Texans': {'id': 34, 'abbr': 'HOU'},
    'Indianapolis Colts': {'id': 11, 'abbr': 'IND'},
    'Jacksonville Jaguars': {'id': 30, 'abbr': 'JAX'},
    'Kansas City Chiefs': {'id': 12, 'abbr': 'KC'},
    'Las Vegas Raiders': {'id': 13, 'abbr': 'LV'},
    'Los Angeles Chargers': {'id': 24, 'abbr': 'LAC'},
    'Los Angeles Rams': {'id': 14, 'abbr': 'LAR'},
    'Miami Dolphins': {'id': 15, 'abbr': 'MIA'},
    'Minnesota Vikings': {'id': 16, 'abbr': 'MIN'},
    'New England Patriots': {'id': 17, 'abbr': 'NE'},
    'New Orleans Saints': {'id': 18, 'abbr': 'NO'},
    'New York Giants': {'id': 19, 'abbr': 'NYG'},
    'New York Jets': {'id': 20, 'abbr': 'NYJ'},
    'Philadelphia Eagles': {'id': 21, 'abbr': 'PHI'},
    'Pittsburgh Steelers': {'id': 23, 'abbr': 'PIT'},
    'San Francisco 49ers': {'id': 25, 'abbr': 'SF'},
    'Seattle Seahawks': {'id': 26, 'abbr': 'SEA'},
    'Tampa Bay Buccaneers': {'id': 27, 'abbr': 'TB'},
    'Tennessee Titans': {'id': 10, 'abbr': 'TEN'},
    'Washington Commanders': {'id': 28, 'abbr': 'WAS'}
}

# Cache system
roster_cache = {}
CACHE_DURATION = 1800  # 30 minutes

def calculate_strategic_value(position: str) -> int:
    """Calculate strategic value for GRIT platform"""
    position_values = {
        'QB': 95, 'RB': 75, 'WR': 80, 'TE': 70,
        'OT': 85, 'OG': 75, 'C': 80,
        'DE': 85, 'DT': 75, 'LB': 80, 'CB': 85, 'S': 78,
        'K': 50, 'P': 45
    }
    return position_values.get(position, 60)

def calculate_game_impact(position: str, experience: int) -> int:
    """Calculate game impact combining strategic value and experience"""
    base_impact = calculate_strategic_value(position)
    experience_bonus = min(experience * 2, 15)
    return min(base_impact + experience_bonus, 100)

def generate_fantasy_stats(position: str, experience: int, strategic_value: int) -> Dict:
    """Generate fantasy football statistics"""
    import random
    
    base_stats_templates = {
        'QB': {
            'passingYards': (2500, 4500),
            'passingTDs': (15, 35),
            'interceptions': (4, 15),
            'rushingYards': (100, 600),
            'rushingTDs': (1, 8)
        },
        'RB': {
            'rushingYards': (400, 1200),
            'rushingTDs': (2, 12),
            'receptions': (15, 70),
            'receivingYards': (150, 500),
            'receivingTDs': (0, 5)
        },
        'WR': {
            'receptions': (25, 100),
            'receivingYards': (400, 1400),
            'receivingTDs': (2, 15),
            'rushingYards': (0, 100),
            'rushingTDs': (0, 3)
        },
        'TE': {
            'receptions': (20, 80),
            'receivingYards': (250, 1000),
            'receivingTDs': (2, 12)
        },
        'K': {
            'fieldGoalsMade': (15, 35),
            'fieldGoalsAttempted': (20, 40),
            'extraPointsMade': (20, 50)
        }
    }
    
    template = base_stats_templates.get(position, {})
    stats = {}
    
    multiplier = (strategic_value / 100) * (1 + experience * 0.03)
    
    for stat, (min_val, max_val) in template.items():
        adjusted_max = int(max_val * multiplier)
        adjusted_min = max(int(min_val * multiplier), min_val // 2)
        stats[stat] = random.randint(adjusted_min, adjusted_max)
    
    # Calculate fantasy points
    fantasy_points = 0
    
    if position == 'QB':
        fantasy_points = (
            stats.get('passingYards', 0) * 0.04 +
            stats.get('passingTDs', 0) * 4 -
            stats.get('interceptions', 0) * 2 +
            stats.get('rushingYards', 0) * 0.1 +
            stats.get('rushingTDs', 0) * 6
        )
    elif position == 'RB':
        fantasy_points = (
            stats.get('rushingYards', 0) * 0.1 +
            stats.get('rushingTDs', 0) * 6 +
            stats.get('receptions', 0) * 0.5 +
            stats.get('receivingYards', 0) * 0.1 +
            stats.get('receivingTDs', 0) * 6
        )
    elif position in ['WR', 'TE']:
        fantasy_points = (
            stats.get('receptions', 0) * 0.5 +
            stats.get('receivingYards', 0) * 0.1 +
            stats.get('receivingTDs', 0) * 6 +
            stats.get('rushingYards', 0) * 0.1 +
            stats.get('rushingTDs', 0) * 6
        )
    elif position == 'K':
        fantasy_points = (
            stats.get('fieldGoalsMade', 0) * 3 +
            stats.get('extraPointsMade', 0) * 1
        )
    
    stats['fantasyPoints'] = int(fantasy_points)
    stats['projectedPoints'] = int(fantasy_points * (0.85 + random.random() * 0.3))
    
    return stats

def determine_starter_status(position: str, roster_index: int, strategic_value: int) -> bool:
    """Determine if player is likely a starter"""
    starter_limits = {
        'QB': 1, 'RB': 2, 'WR': 3, 'TE': 2,
        'OT': 2, 'OG': 2, 'C': 1,
        'DE': 2, 'DT': 2, 'LB': 3, 'CB': 2, 'S': 2,
        'K': 1, 'P': 1
    }
    
    max_starters = starter_limits.get(position, 1)
    return (roster_index < max_starters) or (strategic_value > 85)

def get_position_order(position: str) -> int:
    """Get position order for depth chart"""
    position_order = {
        'QB': 1, 'RB': 2, 'WR': 3, 'TE': 4,
        'OT': 5, 'OG': 6, 'C': 7,
        'DE': 8, 'DT': 9, 'LB': 10, 'CB': 11, 'S': 12,
        'K': 13, 'P': 14
    }
    return position_order.get(position, 15)

def sort_roster_by_depth_chart(roster: List[Dict]) -> List[Dict]:
    """Sort roster by depth chart"""
    return sorted(roster, key=lambda player: (
        get_position_order(player['position']),
        -player['strategicValue']
    ))

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'NFL Roster API for GRIT Platform',
        'version': '1.0.0',
        'endpoints': [
            'GET /api/teams - List all teams',
            'GET /api/roster/<team_name> - Get team roster',
            'GET /api/matchup?team1=<n>&team2=<n> - Get matchup data',
            'GET /api/health - Health check'
        ]
    })

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Get list of all NFL teams"""
    return jsonify({
        'teams': list(NFL_TEAMS.keys()),
        'team_data': NFL_TEAMS
    })

@app.route('/api/roster/<team_name>', methods=['GET'])
def get_team_roster(team_name: str):
    """Get roster for specific team"""
    
    # Check cache first
    cache_key = f"roster_{team_name}"
    if cache_key in roster_cache:
        cached_data, cached_time = roster_cache[cache_key]
        if datetime.now() - cached_time < timedelta(seconds=CACHE_DURATION):
            print(f"Returning cached data for {team_name}")
            return jsonify(cached_data)
    
    # Get team info
    team_info = NFL_TEAMS.get(team_name)
    if not team_info:
        return jsonify({'error': f'Team {team_name} not found'}), 404
    
    try:
        # Fetch from ESPN API
        espn_url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_info['id']}/roster"
        
        print(f"Fetching roster for {team_name} from ESPN: {espn_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        response = requests.get(espn_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"ESPN API error: {response.status_code}")
            return jsonify({
                'error': f'ESPN API returned {response.status_code}',
                'message': 'Failed to fetch roster data'
            }), 500
        
        data = response.json()
        
        if 'athletes' not in data or not data['athletes']:
            return jsonify({
                'error': 'No roster data found',
                'message': f'ESPN returned empty roster for {team_name}'
            }), 404
        
        # Process roster data
        processed_roster = []
        
        for index, athlete in enumerate(data['athletes']):
            position = athlete.get('position', {}).get('abbreviation', 'N/A')
            experience = athlete.get('experience', {}).get('years', 0)
            strategic_value = calculate_strategic_value(position)
            
            player = {
                'id': athlete.get('id', f"{team_info['id']}-{index}"),
                'name': athlete.get('displayName') or athlete.get('name', f'Player {index + 1}'),
                'position': position,
                'jersey': athlete.get('jersey', index + 1),
                'age': athlete.get('age', 'N/A'),
                'height': athlete.get('height', 'N/A'),
                'weight': athlete.get('weight', 'N/A'),
                'experience': experience,
                'college': athlete.get('college', {}).get('name', 'N/A'),
                'strategicValue': strategic_value,
                'injuryStatus': athlete.get('status', 'Healthy'),
                'gameImpact': calculate_game_impact(position, experience),
                'isStarter': determine_starter_status(position, index, strategic_value),
                'depthChartOrder': index + 1,
                'fantasyStats': generate_fantasy_stats(position, experience, strategic_value)
            }
            
            processed_roster.append(player)
        
        # Sort by depth chart
        sorted_roster = sort_roster_by_depth_chart(processed_roster)
        
        # Create response
        result = {
            'team': team_name,
            'teamId': team_info['id'],
            'abbreviation': team_info['abbr'],
            'roster': sorted_roster,
            'totalPlayers': len(sorted_roster),
            'starters': len([p for p in sorted_roster if p['isStarter']]),
            'lastUpdated': datetime.now().isoformat(),
            'dataSource': 'ESPN API'
        }
        
        # Cache the result
        roster_cache[cache_key] = (result, datetime.now())
        
        print(f"Successfully processed {len(sorted_roster)} players for {team_name}")
        return jsonify(result)
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'ESPN API timeout', 'message': 'Request timed out'}), 500
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Network error', 'message': str(e)}), 500
    except Exception as e:
        print(f"Error processing roster for {team_name}: {str(e)}")
        return jsonify({'error': 'Processing error', 'message': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_size': len(roster_cache),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # For local development
    print("Starting NFL Roster API Server...")
    print("Server starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # For production deployment
    print("NFL Roster API Server ready for production")
