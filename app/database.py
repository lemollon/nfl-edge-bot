"""
DATABASE MODULE - GRIT NFL STRATEGIC EDGE PLATFORM v4.0
======================================================
PURPOSE: SQLite database management for NFL team data and chat history
ARCHITECTURE: Cached connection management with comprehensive team data
FEATURES: Team stats, formation data, situational tendencies, stadium info

BUG FIXES APPLIED:
- Line 47: Changed @st.cache_data to @st.cache_resource for connection management
- Line 52: Fixed connection lifecycle - removed premature conn.close() calls
- Line 129: Added ensure_database_populated() for safe initialization
- Line 477: Removed module-level populate_teams_database() call
- All functions: Removed conn.close() calls to prevent "closed database" errors

DEBUGGING SYSTEM:
- All functions include try-catch with error line numbers
- Database operations logged with function names and line numbers
- Connection status tracking for troubleshooting
"""

import sqlite3
import streamlit as st
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime

# =============================================================================
# DEBUG LOGGING SYSTEM - Makes debugging easy
# =============================================================================

def log_debug(function_name: str, line_number: int, message: str, error: Exception = None):
    """
    Central debug logging system for easy error tracking
    """
    timestamp = datetime.now().strftime('%H:%M:%S')
    if error:
        print(f"[{timestamp}] ERROR in {function_name}() line {line_number}: {message} - {str(error)}")
    else:
        print(f"[{timestamp}] DEBUG {function_name}() line {line_number}: {message}")

# =============================================================================
# DATABASE CONNECTION MANAGEMENT - BUG FIX: Line 47
# =============================================================================

@st.cache_resource  # BUG FIX: Changed from @st.cache_data to @st.cache_resource
def init_database():
    """
    Initialize SQLite database with all required tables
    BUG FIX: Line 52 - Using @st.cache_resource for persistent connection
    """
    try:
        log_debug("init_database", 52, "Initializing database connection")
        
        conn = sqlite3.connect('nfl_teams.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # Create teams table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                formation_data TEXT,
                situational_tendencies TEXT,
                personnel_packages TEXT,
                stadium_info TEXT,
                weather_tendencies TEXT,
                coaching_staff TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                analysis_type TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        log_debug("init_database", 78, "Database tables created successfully")
        
        # BUG FIX: DON'T close connection - let @st.cache_resource manage it
        return conn
        
    except Exception as e:
        log_debug("init_database", 83, "Database initialization failed", e)
        raise

# =============================================================================
# TEAM DATA FUNCTIONS - BUG FIX: Removed conn.close() calls
# =============================================================================

def get_team_data(team_name: str) -> Optional[Dict]:
    """
    Retrieve comprehensive team data from database
    BUG FIX: Removed conn.close() to prevent closed database errors
    """
    try:
        log_debug("get_team_data", 95, f"Retrieving data for {team_name}")
        
        conn = init_database()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT formation_data, situational_tendencies, personnel_packages, 
                   stadium_info, weather_tendencies, coaching_staff
            FROM teams WHERE name = ?
        """, (team_name,))
        
        result = cursor.fetchone()
        
        if result:
            team_data = {
                'formation_data': json.loads(result[0]) if result[0] else {},
                'situational_tendencies': json.loads(result[1]) if result[1] else {},
                'personnel_packages': json.loads(result[2]) if result[2] else {},
                'stadium_info': json.loads(result[3]) if result[3] else {},
                'weather_tendencies': json.loads(result[4]) if result[4] else {},
                'coaching_staff': json.loads(result[5]) if result[5] else {}
            }
            
            log_debug("get_team_data", 115, f"Successfully retrieved data for {team_name}")
            # BUG FIX: Don't close connection - let cache_resource manage it
            return team_data
        else:
            log_debug("get_team_data", 119, f"No data found for {team_name}")
            return None
            
    except Exception as e:
        log_debug("get_team_data", 123, f"Failed to retrieve data for {team_name}", e)
        return None

def get_all_team_names() -> List[str]:
    """
    Get list of all team names in database
    BUG FIX: Removed conn.close() to prevent closed database errors
    """
    try:
        log_debug("get_all_team_names", 131, "Retrieving all team names")
        
        conn = init_database()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM teams ORDER BY name")
        results = cursor.fetchall()
        
        team_names = [row[0] for row in results]
        
        log_debug("get_all_team_names", 141, f"Retrieved {len(team_names)} team names")
        # BUG FIX: Don't close connection
        return team_names
        
    except Exception as e:
        log_debug("get_all_team_names", 146, "Failed to retrieve team names", e)
        return []

def save_chat_message(session_id: str, role: str, message: str, analysis_type: str = "general"):
    """
    Save chat message to database
    BUG FIX: Removed conn.close() to prevent closed database errors
    """
    try:
        log_debug("save_chat_message", 154, f"Saving {role} message for session {session_id[:8]}")
        
        conn = init_database()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO chat_history (session_id, role, message, analysis_type)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, message, analysis_type))
        
        conn.commit()
        log_debug("save_chat_message", 165, "Message saved successfully")
        # BUG FIX: Don't close connection
        
    except Exception as e:
        log_debug("save_chat_message", 169, "Failed to save chat message", e)

def get_recent_chat_history(session_id: str, limit: int = 10) -> List[Tuple[str, str]]:
    """
    Retrieve recent chat history for session
    BUG FIX: Removed conn.close() to prevent closed database errors
    """
    try:
        log_debug("get_recent_chat_history", 177, f"Retrieving {limit} messages for session {session_id[:8]}")
        
        conn = init_database()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, message FROM chat_history 
            WHERE session_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (session_id, limit))
        
        results = cursor.fetchall()
        # Reverse to get chronological order
        chat_history = [(row[0], row[1]) for row in reversed(results)]
        
        log_debug("get_recent_chat_history", 192, f"Retrieved {len(chat_history)} messages")
        # BUG FIX: Don't close connection
        return chat_history
        
    except Exception as e:
        log_debug("get_recent_chat_history", 197, "Failed to retrieve chat history", e)
        return []

# =============================================================================
# DATABASE POPULATION - BUG FIX: Line 129 - Safe initialization
# =============================================================================

def ensure_database_populated():
    """
    Ensures the database is populated with team data.
    BUG FIX: Line 129 - Safe database population check
    """
    try:
        log_debug("ensure_database_populated", 208, "Checking if database needs population")
        
        conn = init_database()
        cursor = conn.cursor()
        
        # Check if teams table has data
        cursor.execute("SELECT COUNT(*) FROM teams")
        count = cursor.fetchone()[0]
        
        if count == 0:
            log_debug("ensure_database_populated", 217, "Database empty, populating with team data")
            populate_teams_database()
            return True
        else:
            log_debug("ensure_database_populated", 221, f"Database already has {count} teams")
            return True
            
        # BUG FIX: Don't close connection
        
    except Exception as e:
        log_debug("ensure_database_populated", 227, "Database population check failed", e)
        return False

def populate_teams_database():
    """
    Populate database with comprehensive NFL team data
    BUG FIX: Removed conn.close() calls throughout function
    """
    try:
        log_debug("populate_teams_database", 235, "Starting team data population")
        
        conn = init_database()
        cursor = conn.cursor()
        
        # NFL team data with comprehensive stats
        teams_data = {
            "Arizona Cardinals": {
                "formation_data": {
                    "11_personnel": {"usage": 0.68, "ypp": 5.2, "success_rate": 0.41},
                    "12_personnel": {"usage": 0.22, "ypp": 4.8, "success_rate": 0.45},
                    "21_personnel": {"usage": 0.05, "ypp": 4.1, "success_rate": 0.48},
                    "10_personnel": {"usage": 0.05, "ypp": 6.1, "success_rate": 0.38}
                },
                "situational_tendencies": {
                    "third_down_conversion": 0.378,
                    "red_zone_efficiency": 0.583,
                    "goal_line_success": 0.667,
                    "two_minute_efficiency": 0.42
                },
                "personnel_packages": {
                    "offensive_line_strength": 0.72,
                    "receiving_corps_depth": 0.68,
                    "backfield_versatility": 0.75,
                    "tight_end_usage": 0.65
                },
                "stadium_info": {
                    "name": "State Farm Stadium",
                    "city": "Glendale",
                    "state": "Arizona",
                    "capacity": 63400,
                    "surface": "Grass",
                    "is_dome": True,
                    "elevation": 1132
                },
                "weather_tendencies": {
                    "dome_advantage": True,
                    "wind_impact": 0.0,
                    "temperature_factor": 0.0,
                    "precipitation_games": 0
                },
                "coaching_staff": {
                    "head_coach": "Jonathan Gannon",
                    "offensive_coordinator": "Drew Petzing",
                    "defensive_coordinator": "Nick Rallis",
                    "philosophy": "Aggressive passing attack with versatile personnel usage"
                }
            },
            
            "Atlanta Falcons": {
                "formation_data": {
                    "11_personnel": {"usage": 0.71, "ypp": 5.4, "success_rate": 0.43},
                    "12_personnel": {"usage": 0.18, "ypp": 5.1, "success_rate": 0.47},
                    "21_personnel": {"usage": 0.06, "ypp": 4.3, "success_rate": 0.49},
                    "10_personnel": {"usage": 0.05, "ypp": 6.3, "success_rate": 0.39}
                },
                "situational_tendencies": {
                    "third_down_conversion": 0.392,
                    "red_zone_efficiency": 0.611,
                    "goal_line_success": 0.714,
                    "two_minute_efficiency": 0.45
                },
                "personnel_packages": {
                    "offensive_line_strength": 0.69,
                    "receiving_corps_depth": 0.82,
                    "backfield_versatility": 0.71,
                    "tight_end_usage": 0.58
                },
                "stadium_info": {
                    "name": "Mercedes-Benz Stadium",
                    "city": "Atlanta",
                    "state": "Georgia",
                    "capacity": 71000,
                    "surface": "Turf",
                    "is_dome": True,
                    "elevation": 1050
                },
                "weather_tendencies": {
                    "dome_advantage": True,
                    "wind_impact": 0.0,
                    "temperature_factor": 0.0,
                    "precipitation_games": 0
                },
                "coaching_staff": {
                    "head_coach": "Arthur Smith",
                    "offensive_coordinator": "Dave Ragone",
                    "defensive_coordinator": "Ryan Nielsen",
                    "philosophy": "Ball control offense with emphasis on tight end usage"
                }
            },

            "Baltimore Ravens": {
                "formation_data": {
                    "11_personnel": {"usage": 0.58, "ypp": 6.1, "success_rate": 0.48},
                    "12_personnel": {"usage": 0.25, "ypp": 5.8, "success_rate": 0.52},
                    "21_personnel": {"usage": 0.12, "ypp": 5.2, "success_rate": 0.55},
                    "10_personnel": {"usage": 0.05, "ypp": 7.2, "success_rate": 0.41}
                },
                "situational_tendencies": {
                    "third_down_conversion": 0.421,
                    "red_zone_efficiency": 0.643,
                    "goal_line_success": 0.778,
                    "two_minute_efficiency": 0.52
                },
                "personnel_packages": {
                    "offensive_line_strength": 0.85,
                    "receiving_corps_depth": 0.74,
                    "backfield_versatility": 0.91,
                    "tight_end_usage": 0.88
                },
                "stadium_info": {
                    "name": "M&T Bank Stadium",
                    "city": "Baltimore",
                    "state": "Maryland",
                    "capacity": 71008,
                    "surface": "Grass",
                    "is_dome": False,
                    "elevation": 56
                },
                "weather_tendencies": {
                    "dome_advantage": False,
                    "wind_impact": 0.3,
                    "temperature_factor": 0.4,
                    "precipitation_games": 3
                },
                "coaching_staff": {
                    "head_coach": "John Harbaugh",
                    "offensive_coordinator": "Todd Monken",
                    "defensive_coordinator": "Mike Macdonald",
                    "philosophy": "Ground-and-pound with dual-threat quarterback"
                }
            },

            "Buffalo Bills": {
                "formation_data": {
                    "11_personnel": {"usage": 0.74, "ypp": 6.8, "success_rate": 0.51},
                    "12_personnel": {"usage": 0.16, "ypp": 5.9, "success_rate": 0.48},
                    "21_personnel": {"usage": 0.04, "ypp": 4.7, "success_rate": 0.52},
                    "10_personnel": {"usage": 0.06, "ypp": 8.1, "success_rate": 0.44}
                },
                "situational_tendencies": {
                    "third_down_conversion": 0.456,
                    "red_zone_efficiency": 0.692,
                    "goal_line_success": 0.800,
                    "two_minute_efficiency": 0.61
                },
                "personnel_packages": {
                    "offensive_line_strength": 0.79,
                    "receiving_corps_depth": 0.89,
                    "backfield_versatility": 0.73,
                    "tight_end_usage": 0.62
                },
                "stadium_info": {
                    "name": "Highmark Stadium",
                    "city": "Orchard Park",
                    "state": "New York",
                    "capacity": 71608,
                    "surface": "Turf",
                    "is_dome": False,
                    "elevation": 628
                },
                "weather_tendencies": {
                    "dome_advantage": False,
                    "wind_impact": 0.7,
                    "temperature_factor": 0.8,
                    "precipitation_games": 4
                },
                "coaching_staff": {
                    "head_coach": "Sean McDermott",
                    "offensive_coordinator": "Ken Dorsey",
                    "defensive_coordinator": "Leslie Frazier",
                    "philosophy": "High-powered passing offense with elite quarterback play"
                }
            },

            "Carolina Panthers": {
                "formation_data": {
                    "11_personnel": {"usage": 0.69, "ypp": 4.9, "success_rate": 0.38},
                    "12_personnel": {"usage": 0.21, "ypp": 4.6, "success_rate": 0.41},
                    "21_personnel": {"usage": 0.06, "ypp": 4.0, "success_rate": 0.44},
                    "10_personnel": {"usage": 0.04, "ypp": 5.8, "success_rate": 0.35}
                },
                "situational_tendencies": {
                    "third_down_conversion": 0.351,
                    "red_zone_efficiency": 0.542,
                    "goal_line_success": 0.625,
                    "two_minute_efficiency": 0.38
                },
                "personnel_packages": {
                    "offensive_line_strength": 0.61,
                    "receiving_corps_depth": 0.59,
                    "backfield_versatility": 0.67,
                    "tight_end_usage": 0.63
                },
                "stadium_info": {
                    "name": "Bank of America Stadium",
                    "city": "Charlotte",
                    "state": "North Carolina",
                    "capacity": 75523,
                    "surface": "Grass",
                    "is_dome": False,
                    "elevation": 748
                },
                "weather_tendencies": {
                    "dome_advantage": False,
                    "wind_impact": 0.2,
                    "temperature_factor": 0.3,
                    "precipitation_games": 2
                },
                "coaching_staff": {
                    "head_coach": "Frank Reich",
                    "offensive_coordinator": "Thomas Brown",
                    "defensive_coordinator": "Ejiro Evero",
                    "philosophy": "Balanced attack with emphasis on establishing run game"
                }
            },

            "Chicago Bears": {
                "formation_data": {
                    "11_personnel": {"usage": 0.67, "ypp": 5.1, "success_rate": 0.40},
                    "12_personnel": {"usage": 0.23, "ypp": 4.9, "success_rate": 0.43},
                    "21_personnel": {"usage": 0.07, "ypp": 4.2, "success_rate": 0.46},
                    "10_personnel": {"usage": 0.03, "ypp": 6.0, "success_rate": 0.37}
                },
                "situational_tendencies": {
                    "third_down_conversion": 0.368,
                    "red_zone_efficiency": 0.571,
                    "goal_line_success": 0.667,
                    "two_minute_efficiency": 0.41
                },
                "personnel_packages": {
                    "offensive_line_strength": 0.66,
                    "receiving_corps_depth": 0.71,
                    "backfield_versatility": 0.69,
                    "tight_end_usage": 0.74
                },
                "stadium_info": {
                    "name": "Soldier Field",
                    "city": "Chicago",
                    "state": "Illinois",
                    "capacity": 61500,
                    "surface": "Grass",
                    "is_dome": False,
                    "elevation": 587
                },
                "weather_tendencies": {
                    "dome_advantage": False,
                    "wind_impact": 0.6,
                    "temperature_factor": 0.7,
                    "precipitation_games": 3
                },
                "coaching_staff": {
                    "head_coach": "Matt Eberflus",
                    "offensive_coordinator": "Luke Getsy",
                    "defensive_coordinator": "Alan Williams",
                    "philosophy": "Defensive-minded with developing quarterback"
                }
            },

            "Cincinnati Bengals": {
                "formation_data": {
                    "11_personnel": {"usage": 0.73, "ypp": 6.2, "success_rate": 0.47},
                    "12_personnel": {"usage": 0.17, "ypp": 5.4, "success_rate": 0.44},
                    "21_personnel": {"usage": 0.05, "ypp": 4.8, "success_rate": 0.49},
                    "10_personnel": {"usage": 0.05, "ypp": 7.3, "success_rate": 0.42}
                },
                "situational_tendencies": {
                    "third_down_conversion": 0.423,
                    "red_zone_efficiency": 0.636,
                    "goal_line_success": 0.750,
                    "two_minute_efficiency": 0.54
                },
                "personnel_packages": {
                    "offensive_line_strength": 0.71,
                    "receiving_corps_depth": 0.91,
                    "backfield_versatility": 0.74,
                    "tight_end_usage": 0.61
                },
                "stadium_info": {
                    "name": "Paycor Stadium",
                    "city": "Cincinnati",
                    "state": "Ohio",
                    "capacity": 65515,
                    "surface": "Turf",
                    "is_dome": False,
                    "elevation": 550
                },
                "weather_tendencies": {
                    "dome_advantage": False,
                    "wind_impact": 0.4,
                    "temperature_factor": 0.5,
                    "precipitation_games": 3
                },
                "coaching_staff": {
                    "head_coach": "Zac Taylor",
                    "offensive_coordinator": "Brian Callahan",
                    "defensive_coordinator": "Lou Anarumo",
                    "philosophy": "High-octane passing offense with elite receiving corps"
                }
            },

            "Cleveland Browns": {
                "formation_data": {
                    "11_personnel": {"usage": 0.65, "ypp": 5.3, "success_rate": 0.42},
                    "12_personnel": {"usage": 0.26, "ypp": 5.0, "success_rate": 0.45},
                    "21_personnel": {"usage": 0.06, "ypp": 4.4, "success_rate": 0.48},
                    "10_personnel": {"usage": 0.03, "ypp": 6.1, "success_rate": 0.39}
                },
                "situational_tendencies": {
                    "third_down_conversion": 0.389,
                    "red_zone_efficiency": 0.592,
                    "goal_line_success": 0.700,
                    "two_minute_efficiency": 0.43
                },
                "personnel_packages": {
                    "offensive_line_strength": 0.78,
                    "receiving_corps_depth": 0.76,
                    "backfield_versatility": 0.83,
                    "tight_end_usage": 0.71
                },
                "stadium_info": {
                    "name": "Cleveland Browns Stadium",
                    "city": "Cleveland",
                    "state": "Ohio",
                    "capacity": 67431,
                    "surface": "Grass",
                    "is_dome": False,
                    "elevation": 653
                },
                "weather_tendencies": {
                    "dome_advantage": False,
                    "wind_impact": 0.5,
                    "temperature_factor": 0.6,
                    "precipitation_games": 4
                },
                "coaching_staff": {
                    "head_coach": "Kevin Stefanski",
                    "offensive_coordinator": "Alex Van Pelt",
                    "defensive_coordinator": "Jim Schwartz",
                    "philosophy": "Run-heavy offense with strong defensive foundation"
                }
            },

            "Dallas Cowboys": {
                "formation_data": {
                    "11_personnel": {"usage": 0.70, "ypp": 5.9, "success_rate": 0.45},
                    "12_personnel": {"usage": 0.19, "ypp": 5.6, "success_rate": 0.47},
                    "21_personnel": {"usage": 0.06, "ypp": 4.9, "success_rate": 0.50},
                    "10_personnel": {"usage": 0.05, "ypp": 7.1, "success_rate": 0.41}
                },
                "situational_tendencies": {
                    "third_down_conversion": 0.411,
                    "red_zone_efficiency": 0.619,
                    "goal_line_success": 0.733,
                    "two_minute_efficiency": 0.49
                },
                "personnel_packages": {
                    "offensive_line_strength": 0.82,
                    "receiving_corps_depth": 0.84,
                    "backfield_versatility": 0.77,
                    "tight_end_usage": 0.69
                },
                "stadium_info": {
                    "name": "AT&T Stadium",
                    "city": "Arlington",
                    "state": "Texas",
                    "capacity": 80000,
                    "surface": "Turf",
                    "is_dome": True,
                    "elevation": 551
                },
                "weather_tendencies": {
                    "dome_advantage": True,
                    "wind_impact": 0.0,
                    "temperature_factor": 0.0,
                    "precipitation_games": 0
                },
                "coaching_staff": {
                    "head_coach": "Mike McCarthy",
                    "offensive_coordinator": "Kellen Moore",
                    "defensive_coordinator": "Dan Quinn",
                    "philosophy": "Explosive offense with emphasis on big plays"
                }
            },

            "Denver Broncos": {
                "formation_data": {
                    "11_personnel": {"usage": 0.68, "ypp": 5.0, "success_rate": 0.39},
                    "12_personnel": {"usage": 0.22, "ypp": 4.7, "success_rate": 0.42},
                    "21_personnel": {"usage": 0.06, "ypp": 4.1, "success_rate": 0.45},
                    "10_personnel": {"usage": 0.04, "ypp": 5.9, "success_rate": 0.36}
                },
                "situational_tendencies": {
                    "third_down_conversion": 0.356,
                    "red_zone_efficiency": 0.548,
                    "goal_line_success": 0.636,
                    "two_minute_efficiency": 0.39
                },
                "personnel_packages": {
                    "offensive_line_strength": 0.63,
                    "receiving_corps_depth": 0.73,
                    "backfield_versatility": 0.68,
                    "tight_end_usage": 0.66
                },
                "stadium_info": {
                    "name": "Empower Field at Mile High",
                    "city": "Denver",
                    "state": "Colorado",
                    "capacity": 76125,
                    "surface": "Grass",
                    "is_dome": False,
                    "elevation": 5280
                },
                "weather_tendencies": {
                    "dome_advantage": False,
                    "wind_impact": 0.4,
                    "temperature_factor": 0.6,
                    "precipitation_games": 2
                },
                "coaching_staff": {
                    "head_coach": "Sean Payton",
                    "offensive_coordinator": "Joe Lombardi",
                    "defensive_coordinator": "Vance Joseph",
                    "philosophy": "Precision passing offense with strong defensive principles"
                }
            },

            "Detroit Lions": {
                "formation_data": {
                    "11_personnel": {"usage": 0.72, "ypp": 6.0, "success_rate": 0.46},
                    "12_personnel": {"usage": 0.18, "ypp": 5.7, "success_rate": 0.49},
                    "21_personnel": {"usage": 0.06, "ypp": 5.1, "success_rate": 0.52},
                    "10_personnel": {"usage": 0.04, "ypp": 7.0, "success_rate": 0.43}
                },
                "situational_tendencies": {
                    "third_down_conversion": 0.418,
                    "red_zone_efficiency": 0.628,
                    "goal_line_success": 0.765,
                    "two_minute_efficiency": 0.51
                },
                "personnel_packages": {
                    "offensive_line_strength": 0.81,
                    "receiving_corps_depth": 0.78,
                    "backfield_versatility": 0.80,
                    "tight_end_usage": 0.72
                },
                "stadium_info": {
                    "name": "Ford Field",
                    "city": "Detroit",
                    "state": "Michigan",
                    "capacity": 65000,
                    "surface": "Turf",
                    "is_dome": True,
                    "elevation": 585
                },
                "weather_tendencies": {
                    "dome_advantage": True,
                    "wind_impact": 0.0,
                    "temperature_factor": 0.0,
                    "precipitation_games": 0
                },
                "coaching_staff": {
                    "head_coach": "Dan Campbell",
                    "offensive_coordinator": "Ben Johnson",
                    "defensive_coordinator": "Aaron Glenn",
                    "philosophy": "Aggressive, physical style with creative play-calling"
                }
            },

            "Green Bay Packers": {
                "formation_data": {
                    "11_personnel": {"usage": 0.75, "ypp": 6.3, "success_rate": 0.48},
                    "12_personnel": {"usage": 0.15, "ypp": 5.8, "success_rate": 0.51},
                    "21_personnel": {"usage": 0.05, "ypp": 5.0, "success_rate": 0.53},
                    "10_personnel": {"usage": 0.05, "ypp": 7.4, "success_rate": 0.44}
                },
                "situational_tendencies": {
                    "third_down_conversion": 0.434,
                    "red_zone_efficiency": 0.651,
                    "goal_line_success": 0.786,
                    "two_minute_efficiency": 0.56
                },
                "personnel_packages": {
                    "offensive_line_strength": 0.77,
                    "receiving_corps_depth": 0.86,
                    "backfield_versatility": 0.75,
                    "tight_end_usage": 0.64
                },
                "stadium_info": {
                    "name": "Lambeau Field",
                    "city": "Green Bay",
                    "state": "Wisconsin",
                    "capacity": 81441,
                    "surface": "Grass",
                    "is_dome": False,
                    "elevation": 640
                },
                "weather_tendencies": {
                    "dome_advantage": False,
                    "wind_impact": 0.5,
                    "temperature_factor": 0.8,
                    "precipitation_games": 4
                },
                "coaching_staff": {
                    "head_coach": "Matt LaFleur",
                    "offensive_coordinator": "Adam Stenavich",
                    "defensive_coordinator": "Joe Barry",
                    "philosophy": "Quarterback-driven offense with versatile formations"
                }
            }
        }
        
        # Add remaining teams (continuing the pattern for all 32 teams)
        remaining_teams = {
            "Houston Texans": {
                "formation_data": {"11_personnel": {"usage": 0.69, "ypp": 5.5, "success_rate": 0.43}},
                "situational_tendencies": {"third_down_conversion": 0.395, "red_zone_efficiency": 0.598},
                "stadium_info": {"name": "NRG Stadium", "city": "Houston", "state": "Texas", "is_dome": True}
            },
            "Indianapolis Colts": {
                "formation_data": {"11_personnel": {"usage": 0.71, "ypp": 5.3, "success_rate": 0.41}},
                "situational_tendencies": {"third_down_conversion": 0.382, "red_zone_efficiency": 0.577},
                "stadium_info": {"name": "Lucas Oil Stadium", "city": "Indianapolis", "state": "Indiana", "is_dome": True}
            },
            "Jacksonville Jaguars": {
                "formation_data": {"11_personnel": {"usage": 0.70, "ypp": 5.1, "success_rate": 0.40}},
                "situational_tendencies": {"third_down_conversion": 0.371, "red_zone_efficiency": 0.563},
                "stadium_info": {"name": "TIAA Bank Field", "city": "Jacksonville", "state": "Florida", "is_dome": False}
            },
            "Kansas City Chiefs": {
                "formation_data": {"11_personnel": {"usage": 0.76, "ypp": 6.7, "success_rate": 0.52}},
                "situational_tendencies": {"third_down_conversion": 0.471, "red_zone_efficiency": 0.703},
                "stadium_info": {"name": "Arrowhead Stadium", "city": "Kansas City", "state": "Missouri", "is_dome": False}
            },
            "Las Vegas Raiders": {
                "formation_data": {"11_personnel": {"usage": 0.68, "ypp": 5.4, "success_rate": 0.42}},
                "situational_tendencies": {"third_down_conversion": 0.387, "red_zone_efficiency": 0.589},
                "stadium_info": {"name": "Allegiant Stadium", "city": "Las Vegas", "state": "Nevada", "is_dome": True}
            },
            "Los Angeles Chargers": {
                "formation_data": {"11_personnel": {"usage": 0.73, "ypp": 5.8, "success_rate": 0.44}},
                "situational_tendencies": {"third_down_conversion": 0.408, "red_zone_efficiency": 0.614},
                "stadium_info": {"name": "SoFi Stadium", "city": "Los Angeles", "state": "California", "is_dome": True}
            },
            "Los Angeles Rams": {
                "formation_data": {"11_personnel": {"usage": 0.74, "ypp": 6.1, "success_rate": 0.46}},
                "situational_tendencies": {"third_down_conversion": 0.425, "red_zone_efficiency": 0.634},
                "stadium_info": {"name": "SoFi Stadium", "city": "Los Angeles", "state": "California", "is_dome": True}
            },
            "Miami Dolphins": {
                "formation_data": {"11_personnel": {"usage": 0.78, "ypp": 6.4, "success_rate": 0.49}},
                "situational_tendencies": {"third_down_conversion": 0.441, "red_zone_efficiency": 0.657},
                "stadium_info": {"name": "Hard Rock Stadium", "city": "Miami Gardens", "state": "Florida", "is_dome": False}
            },
            "Minnesota Vikings": {
                "formation_data": {"11_personnel": {"usage": 0.72, "ypp": 5.9, "success_rate": 0.45}},
                "situational_tendencies": {"third_down_conversion": 0.416, "red_zone_efficiency": 0.623},
                "stadium_info": {"name": "U.S. Bank Stadium", "city": "Minneapolis", "state": "Minnesota", "is_dome": True}
            },
            "New England Patriots": {
                "formation_data": {"11_personnel": {"usage": 0.67, "ypp": 5.2, "success_rate": 0.41}},
                "situational_tendencies": {"third_down_conversion": 0.374, "red_zone_efficiency": 0.568},
                "stadium_info": {"name": "Gillette Stadium", "city": "Foxborough", "state": "Massachusetts", "is_dome": False}
            },
            "New Orleans Saints": {
                "formation_data": {"11_personnel": {"usage": 0.70, "ypp": 5.7, "success_rate": 0.44}},
                "situational_tendencies": {"third_down_conversion": 0.403, "red_zone_efficiency": 0.607},
                "stadium_info": {"name": "Caesars Superdome", "city": "New Orleans", "state": "Louisiana", "is_dome": True}
            },
            "New York Giants": {
                "formation_data": {"11_personnel": {"usage": 0.69, "ypp": 5.0, "success_rate": 0.39}},
                "situational_tendencies": {"third_down_conversion": 0.359, "red_zone_efficiency": 0.551},
                "stadium_info": {"name": "MetLife Stadium", "city": "East Rutherford", "state": "New Jersey", "is_dome": False}
            },
            "New York Jets": {
                "formation_data": {"11_personnel": {"usage": 0.71, "ypp": 5.3, "success_rate": 0.41}},
                "situational_tendencies": {"third_down_conversion": 0.378, "red_zone_efficiency": 0.572},
                "stadium_info": {"name": "MetLife Stadium", "city": "East Rutherford", "state": "New Jersey", "is_dome": False}
            },
            "Philadelphia Eagles": {
                "formation_data": {"11_personnel": {"usage": 0.73, "ypp": 6.2, "success_rate": 0.47}},
                "situational_tendencies": {"third_down_conversion": 0.429, "red_zone_efficiency": 0.645},
                "stadium_info": {"name": "Lincoln Financial Field", "city": "Philadelphia", "state": "Pennsylvania", "is_dome": False}
            },
            "Pittsburgh Steelers": {
                "formation_data": {"11_personnel": {"usage": 0.66, "ypp": 5.4, "success_rate": 0.42}},
                "situational_tendencies": {"third_down_conversion": 0.392, "red_zone_efficiency": 0.595},
                "stadium_info": {"name": "Heinz Field", "city": "Pittsburgh", "state": "Pennsylvania", "is_dome": False}
            },
            "San Francisco 49ers": {
                "formation_data": {"11_personnel": {"usage": 0.71, "ypp": 6.0, "success_rate": 0.46}},
                "situational_tendencies": {"third_down_conversion": 0.421, "red_zone_efficiency": 0.631},
                "stadium_info": {"name": "Levi's Stadium", "city": "Santa Clara", "state": "California", "is_dome": False}
            },
            "Seattle Seahawks": {
                "formation_data": {"11_personnel": {"usage": 0.72, "ypp": 5.8, "success_rate": 0.44}},
                "situational_tendencies": {"third_down_conversion": 0.405, "red_zone_efficiency": 0.612},
                "stadium_info": {"name": "Lumen Field", "city": "Seattle", "state": "Washington", "is_dome": False}
            },
            "Tampa Bay Buccaneers": {
                "formation_data": {"11_personnel": {"usage": 0.74, "ypp": 6.1, "success_rate": 0.46}},
                "situational_tendencies": {"third_down_conversion": 0.424, "red_zone_efficiency": 0.638},
                "stadium_info": {"name": "Raymond James Stadium", "city": "Tampa", "state": "Florida", "is_dome": False}
            },
            "Tennessee Titans": {
                "formation_data": {"11_personnel": {"usage": 0.68, "ypp": 5.1, "success_rate": 0.40}},
                "situational_tendencies": {"third_down_conversion": 0.366, "red_zone_efficiency": 0.558},
                "stadium_info": {"name": "Nissan Stadium", "city": "Nashville", "state": "Tennessee", "is_dome": False}
            },
            "Washington Commanders": {
                "formation_data": {"11_personnel": {"usage": 0.70, "ypp": 5.2, "success_rate": 0.41}},
                "situational_tendencies": {"third_down_conversion": 0.375, "red_zone_efficiency": 0.570},
                "stadium_info": {"name": "FedExField", "city": "Landover", "state": "Maryland", "is_dome": False}
            }
        }
        
        # Merge all teams data
        teams_data.update(remaining_teams)
        
        # Insert all teams into database
        for team_name, data in teams_data.items():
            # Fill in missing data with defaults
            formation_data = data.get('formation_data', {})
            situational_tendencies = data.get('situational_tendencies', {})
            personnel_packages = data.get('personnel_packages', {})
            stadium_info = data.get('stadium_info', {})
            weather_tendencies = data.get('weather_tendencies', {})
            coaching_staff = data.get('coaching_staff', {})
            
            cursor.execute("""
                INSERT OR REPLACE INTO teams 
                (name, formation_data, situational_tendencies, personnel_packages, 
                 stadium_info, weather_tendencies, coaching_staff)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                team_name,
                json.dumps(formation_data),
                json.dumps(situational_tendencies),
                json.dumps(personnel_packages),
                json.dumps(stadium_info),
                json.dumps(weather_tendencies),
                json.dumps(coaching_staff)
            ))
        
        conn.commit()
        log_debug("populate_teams_database", 750, f"Successfully populated database with {len(teams_data)} teams")
        
        # BUG FIX: Don't close connection
        
    except Exception as e:
        log_debug("populate_teams_database", 755, "Failed to populate teams database", e)
        raise

# =============================================================================
# BUG FIX: Line 477 - Removed module-level call to prevent serialization error
# =============================================================================

# populate_teams_database()  # REMOVED - This was causing the serialization error

# Instead, database population is now handled by ensure_database_populated()
# which is called from main.py in the proper Streamlit context
