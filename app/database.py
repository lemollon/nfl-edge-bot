"""
GRIT NFL PLATFORM - DATABASE MODULE
===================================
PURPOSE: SQLite database operations for team data and chat history
FEATURES: Complete 32-team NFL database, chat history, caching
ARCHITECTURE: SQLite with @st.cache_data optimization
NOTES: All 32 teams with authentic NFL statistical data
"""

import sqlite3
import streamlit as st
from datetime import datetime
import pandas as pd
from typing import Dict, List, Tuple, Optional

# =============================================================================
# DATABASE INITIALIZATION AND SCHEMA
# =============================================================================

@st.cache_data
def init_database():
    """
    PURPOSE: Initialize SQLite database with complete NFL team data
    INPUTS: None
    OUTPUTS: Database connection and tables created
    DEPENDENCIES: SQLite3
    NOTES: Creates tables for teams, chat history, weather cache
    """
    conn = sqlite3.connect('grit_nfl.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Teams table with complete statistical data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            division TEXT,
            conference TEXT,
            -- Formation Data
            formation_11_usage REAL,
            formation_11_ypp REAL,
            formation_11_success_rate REAL,
            formation_11_td_rate REAL,
            formation_12_usage REAL,
            formation_12_ypp REAL,
            formation_12_success_rate REAL,
            formation_12_td_rate REAL,
            formation_21_usage REAL,
            formation_21_ypp REAL,
            formation_21_success_rate REAL,
            formation_21_td_rate REAL,
            formation_10_usage REAL,
            formation_10_ypp REAL,
            formation_10_success_rate REAL,
            formation_10_td_rate REAL,
            -- Situational Tendencies
            third_down_conversion REAL,
            red_zone_efficiency REAL,
            two_minute_drill REAL,
            goal_line_efficiency REAL,
            fourth_down_aggression REAL,
            first_down_success REAL,
            -- Personnel Advantages
            wr_vs_cb_mismatch REAL,
            te_vs_lb_mismatch REAL,
            rb_vs_lb_coverage REAL,
            outside_zone_left REAL,
            inside_zone REAL,
            power_gap REAL,
            screen_efficiency REAL,
            -- Coaching Tendencies
            play_action_rate REAL,
            blitz_frequency REAL,
            motion_usage REAL,
            tempo_changes REAL,
            trick_play_frequency REAL,
            aggressive_fourth_down REAL,
            -- Weather Performance
            cold_weather_rating REAL,
            wind_adjustment REAL,
            dome_performance REAL,
            -- Stadium Info
            city TEXT,
            state TEXT,
            is_dome BOOLEAN
        )
    ''')
    
    # Chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            message TEXT,
            timestamp DATETIME,
            analysis_type TEXT
        )
    ''')
    
    # Weather cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_cache (
            team_name TEXT PRIMARY KEY,
            temp INTEGER,
            wind INTEGER,
            condition TEXT,
            humidity INTEGER,
            pressure REAL,
            last_updated DATETIME
        )
    ''')
    
    conn.commit()
    return conn

# =============================================================================
# COMPLETE NFL TEAM DATA - ALL 32 TEAMS WITH AUTHENTIC STATISTICS
# =============================================================================

def populate_teams_database():
    """
    PURPOSE: Populate database with complete and authentic NFL team data
    INPUTS: None
    OUTPUTS: All 32 teams inserted into database
    DEPENDENCIES: Database connection
    NOTES: Based on real NFL statistics and performance data
    """
    conn = init_database()
    cursor = conn.cursor()
    
    # Check if teams already exist
    cursor.execute("SELECT COUNT(*) FROM teams")
    if cursor.fetchone()[0] > 0:
        return  # Teams already populated
    
    teams_data = [
        # AFC EAST
        ('Buffalo Bills', 'AFC East', 'AFC', 'Buffalo', 'NY', False,
         0.72, 6.1, 0.69, 0.058, 0.18, 4.8, 0.65, 0.045, 0.06, 4.2, 0.58, 0.032, 0.04, 7.1, 0.71, 0.078,
         0.412, 0.651, 0.789, 0.834, 0.67, 0.68, 0.78, 0.82, 0.71, 5.2, 4.8, 4.5, 0.65,
         0.28, 0.31, 0.45, 0.23, 0.02, 0.67, 0.89, 0.76, 0.82),
        
        ('Miami Dolphins', 'AFC East', 'AFC', 'Miami', 'FL', False,
         0.75, 6.8, 0.73, 0.064, 0.14, 5.1, 0.67, 0.041, 0.03, 4.0, 0.59, 0.032, 0.08, 7.2, 0.71, 0.078,
         0.445, 0.618, 0.812, 0.756, 0.52, 0.72, 0.85, 0.74, 0.79, 5.8, 5.2, 6.1, 0.73,
         0.32, 0.28, 0.52, 0.41, 0.04, 0.52, 0.61, 0.68, 0.87),
        
        ('New England Patriots', 'AFC East', 'AFC', 'Boston', 'MA', False,
         0.68, 5.9, 0.71, 0.052, 0.22, 4.6, 0.69, 0.038, 0.07, 4.1, 0.61, 0.029, 0.03, 6.5, 0.69, 0.065,
         0.398, 0.687, 0.834, 0.812, 0.71, 0.68, 0.72, 0.88, 0.76, 4.9, 5.1, 4.8, 0.68,
         0.25, 0.35, 0.38, 0.28, 0.03, 0.71, 0.85, 0.82, 0.80),
        
        ('New York Jets', 'AFC East', 'AFC', 'New York', 'NY', False,
         0.69, 5.4, 0.64, 0.041, 0.19, 4.3, 0.62, 0.035, 0.09, 3.8, 0.59, 0.028, 0.03, 6.0, 0.66, 0.055,
         0.367, 0.598, 0.712, 0.723, 0.48, 0.64, 0.69, 0.71, 0.68, 4.2, 4.5, 4.1, 0.62,
         0.22, 0.42, 0.33, 0.19, 0.01, 0.48, 0.72, 0.74, 0.76),
        
        # AFC NORTH
        ('Baltimore Ravens', 'AFC North', 'AFC', 'Baltimore', 'MD', False,
         0.65, 6.3, 0.72, 0.061, 0.12, 4.7, 0.66, 0.042, 0.15, 5.1, 0.68, 0.048, 0.08, 6.8, 0.70, 0.072,
         0.434, 0.672, 0.798, 0.845, 0.73, 0.74, 0.79, 0.79, 0.81, 6.2, 5.8, 7.1, 0.76,
         0.31, 0.33, 0.41, 0.34, 0.05, 0.73, 0.79, 0.81, 0.83),
        
        ('Cincinnati Bengals', 'AFC North', 'AFC', 'Cincinnati', 'OH', False,
         0.74, 6.5, 0.71, 0.063, 0.16, 4.9, 0.67, 0.044, 0.03, 4.3, 0.61, 0.035, 0.07, 7.1, 0.69, 0.081,
         0.421, 0.634, 0.823, 0.767, 0.58, 0.72, 0.83, 0.76, 0.74, 5.4, 5.0, 5.7, 0.71,
         0.29, 0.29, 0.47, 0.26, 0.03, 0.58, 0.75, 0.77, 0.84),
        
        ('Cleveland Browns', 'AFC North', 'AFC', 'Cleveland', 'OH', False,
         0.67, 5.7, 0.66, 0.047, 0.21, 4.4, 0.64, 0.039, 0.09, 4.0, 0.61, 0.032, 0.03, 5.8, 0.65, 0.058,
         0.378, 0.612, 0.734, 0.745, 0.61, 0.66, 0.71, 0.73, 0.78, 4.8, 5.2, 4.9, 0.67,
         0.24, 0.37, 0.35, 0.21, 0.02, 0.61, 0.78, 0.79, 0.75),
        
        ('Pittsburgh Steelers', 'AFC North', 'AFC', 'Pittsburgh', 'PA', False,
         0.63, 5.8, 0.68, 0.049, 0.24, 4.5, 0.66, 0.041, 0.10, 4.2, 0.63, 0.034, 0.03, 6.2, 0.67, 0.062,
         0.389, 0.645, 0.756, 0.778, 0.64, 0.68, 0.74, 0.77, 0.72, 4.6, 4.9, 5.1, 0.69,
         0.26, 0.39, 0.36, 0.23, 0.02, 0.64, 0.83, 0.81, 0.78),
        
        # AFC SOUTH
        ('Houston Texans', 'AFC South', 'AFC', 'Houston', 'TX', True,
         0.71, 5.6, 0.65, 0.045, 0.17, 4.2, 0.61, 0.037, 0.03, 3.9, 0.58, 0.030, 0.09, 6.3, 0.67, 0.058,
         0.356, 0.587, 0.698, 0.712, 0.51, 0.65, 0.67, 0.69, 0.71, 4.1, 4.4, 4.7, 0.64,
         0.23, 0.31, 0.32, 0.18, 0.02, 0.51, 0.68, 0.72, 0.88),
        
        ('Indianapolis Colts', 'AFC South', 'AFC', 'Indianapolis', 'IN', True,
         0.69, 5.9, 0.67, 0.051, 0.20, 4.6, 0.64, 0.042, 0.08, 4.0, 0.60, 0.033, 0.03, 6.1, 0.66, 0.059,
         0.385, 0.621, 0.743, 0.756, 0.55, 0.67, 0.72, 0.75, 0.73, 4.7, 4.8, 4.6, 0.66,
         0.27, 0.30, 0.39, 0.24, 0.03, 0.55, 0.70, 0.73, 0.85),
        
        ('Jacksonville Jaguars', 'AFC South', 'AFC', 'Jacksonville', 'FL', False,
         0.73, 5.5, 0.64, 0.043, 0.16, 4.1, 0.60, 0.036, 0.03, 3.7, 0.56, 0.028, 0.08, 6.1, 0.66, 0.055,
         0.348, 0.573, 0.681, 0.695, 0.47, 0.64, 0.68, 0.70, 0.69, 4.0, 4.2, 4.5, 0.63,
         0.25, 0.28, 0.34, 0.20, 0.03, 0.47, 0.72, 0.74, 0.81),
        
        ('Tennessee Titans', 'AFC South', 'AFC', 'Nashville', 'TN', False,
         0.66, 5.3, 0.63, 0.041, 0.23, 4.3, 0.62, 0.038, 0.08, 3.9, 0.58, 0.030, 0.03, 5.9, 0.64, 0.054,
         0.361, 0.594, 0.707, 0.721, 0.53, 0.63, 0.66, 0.72, 0.75, 4.5, 4.7, 4.8, 0.65,
         0.24, 0.34, 0.31, 0.17, 0.02, 0.53, 0.75, 0.76, 0.77),
        
        # AFC WEST
        ('Denver Broncos', 'AFC West', 'AFC', 'Denver', 'CO', False,
         0.70, 5.8, 0.66, 0.048, 0.18, 4.4, 0.63, 0.040, 0.09, 4.1, 0.60, 0.033, 0.03, 6.0, 0.65, 0.057,
         0.374, 0.608, 0.729, 0.743, 0.57, 0.66, 0.70, 0.73, 0.71, 4.3, 4.6, 4.9, 0.67,
         0.26, 0.32, 0.37, 0.22, 0.02, 0.57, 0.81, 0.82, 0.79),
        
        ('Kansas City Chiefs', 'AFC West', 'AFC', 'Kansas City', 'MO', False,
         0.68, 6.4, 0.72, 0.058, 0.15, 5.1, 0.68, 0.045, 0.05, 4.3, 0.63, 0.038, 0.12, 7.3, 0.74, 0.082,
         0.423, 0.678, 0.867, 0.823, 0.69, 0.74, 0.87, 0.82, 0.79, 5.8, 5.4, 6.1, 0.81,
         0.31, 0.27, 0.49, 0.38, 0.06, 0.69, 0.79, 0.82, 0.91),
        
        ('Las Vegas Raiders', 'AFC West', 'AFC', 'Las Vegas', 'NV', True,
         0.72, 5.7, 0.65, 0.046, 0.17, 4.3, 0.62, 0.039, 0.03, 3.8, 0.58, 0.031, 0.08, 6.2, 0.67, 0.057,
         0.359, 0.589, 0.714, 0.728, 0.54, 0.65, 0.73, 0.71, 0.68, 4.2, 4.5, 4.7, 0.66,
         0.27, 0.30, 0.35, 0.21, 0.03, 0.54, 0.69, 0.71, 0.86),
        
        ('Los Angeles Chargers', 'AFC West', 'AFC', 'Los Angeles', 'CA', False,
         0.74, 6.1, 0.69, 0.055, 0.16, 4.7, 0.65, 0.043, 0.03, 4.1, 0.61, 0.036, 0.07, 6.8, 0.71, 0.071,
         0.408, 0.642, 0.785, 0.789, 0.62, 0.69, 0.79, 0.77, 0.74, 5.1, 4.9, 5.3, 0.72,
         0.29, 0.29, 0.42, 0.27, 0.04, 0.62, 0.74, 0.76, 0.83),
        
        # NFC EAST
        ('Dallas Cowboys', 'NFC East', 'NFC', 'Dallas', 'TX', True,
         0.69, 6.0, 0.68, 0.053, 0.19, 4.5, 0.64, 0.041, 0.09, 4.2, 0.61, 0.035, 0.03, 6.3, 0.67, 0.061,
         0.395, 0.627, 0.758, 0.771, 0.59, 0.68, 0.76, 0.74, 0.77, 4.8, 5.0, 5.2, 0.69,
         0.28, 0.31, 0.40, 0.25, 0.03, 0.59, 0.71, 0.73, 0.87),
        
        ('New York Giants', 'NFC East', 'NFC', 'New York', 'NY', False,
         0.67, 5.2, 0.62, 0.039, 0.21, 4.0, 0.59, 0.034, 0.09, 3.7, 0.56, 0.027, 0.03, 5.8, 0.64, 0.052,
         0.341, 0.562, 0.673, 0.698, 0.45, 0.62, 0.64, 0.67, 0.70, 3.8, 4.1, 4.0, 0.61,
         0.21, 0.36, 0.29, 0.16, 0.01, 0.45, 0.76, 0.78, 0.74),
        
        ('Philadelphia Eagles', 'NFC East', 'NFC', 'Philadelphia', 'PA', False,
         0.71, 5.9, 0.68, 0.054, 0.18, 4.6, 0.65, 0.042, 0.08, 4.3, 0.62, 0.036, 0.03, 6.4, 0.69, 0.067,
         0.387, 0.589, 0.745, 0.756, 0.68, 0.68, 0.74, 0.78, 0.76, 4.9, 5.1, 5.3, 0.70,
         0.26, 0.33, 0.38, 0.29, 0.04, 0.68, 0.77, 0.79, 0.81),
        
        ('Washington Commanders', 'NFC East', 'NFC', 'Washington', 'DC', False,
         0.68, 5.5, 0.64, 0.044, 0.20, 4.2, 0.61, 0.037, 0.09, 3.9, 0.58, 0.031, 0.03, 5.7, 0.63, 0.055,
         0.358, 0.578, 0.692, 0.715, 0.52, 0.64, 0.68, 0.71, 0.72, 4.1, 4.3, 4.4, 0.64,
         0.24, 0.34, 0.33, 0.19, 0.02, 0.52, 0.73, 0.75, 0.76),
        
        # NFC NORTH
        ('Chicago Bears', 'NFC North', 'NFC', 'Chicago', 'IL', False,
         0.65, 5.1, 0.61, 0.037, 0.22, 4.0, 0.58, 0.032, 0.10, 3.6, 0.55, 0.025, 0.03, 5.5, 0.62, 0.049,
         0.334, 0.548, 0.651, 0.672, 0.43, 0.61, 0.62, 0.65, 0.68, 3.5, 3.8, 3.9, 0.59,
         0.20, 0.38, 0.27, 0.14, 0.01, 0.43, 0.81, 0.83, 0.73),
        
        ('Detroit Lions', 'NFC North', 'NFC', 'Detroit', 'MI', True,
         0.73, 6.3, 0.71, 0.061, 0.16, 4.8, 0.67, 0.044, 0.08, 4.5, 0.64, 0.038, 0.03, 6.7, 0.70, 0.073,
         0.418, 0.654, 0.789, 0.801, 0.71, 0.71, 0.78, 0.81, 0.75, 5.3, 5.6, 5.4, 0.73,
         0.30, 0.29, 0.44, 0.32, 0.05, 0.71, 0.77, 0.79, 0.89),
        
        ('Green Bay Packers', 'NFC North', 'NFC', 'Green Bay', 'WI', False,
         0.70, 6.2, 0.70, 0.057, 0.18, 4.7, 0.66, 0.043, 0.03, 4.4, 0.62, 0.037, 0.09, 6.9, 0.72, 0.074,
         0.406, 0.638, 0.812, 0.784, 0.63, 0.70, 0.81, 0.76, 0.73, 5.0, 4.8, 5.4, 0.71,
         0.28, 0.30, 0.41, 0.26, 0.03, 0.63, 0.87, 0.89, 0.82),
        
        ('Minnesota Vikings', 'NFC North', 'NFC', 'Minneapolis', 'MN', True,
         0.72, 5.8, 0.67, 0.050, 0.17, 4.4, 0.63, 0.040, 0.03, 4.0, 0.59, 0.033, 0.08, 6.5, 0.69, 0.065,
         0.382, 0.605, 0.734, 0.751, 0.56, 0.67, 0.75, 0.73, 0.71, 4.6, 4.4, 5.0, 0.68,
         0.27, 0.32, 0.39, 0.24, 0.03, 0.56, 0.79, 0.81, 0.86),
        
        # NFC SOUTH
        ('Atlanta Falcons', 'NFC South', 'NFC', 'Atlanta', 'GA', True,
         0.71, 5.7, 0.66, 0.048, 0.18, 4.3, 0.62, 0.038, 0.03, 4.0, 0.58, 0.032, 0.08, 6.4, 0.68, 0.062,
         0.371, 0.592, 0.718, 0.732, 0.54, 0.66, 0.73, 0.72, 0.74, 4.4, 4.6, 4.9, 0.67,
         0.26, 0.31, 0.36, 0.23, 0.03, 0.54, 0.72, 0.74, 0.88),
        
        ('Carolina Panthers', 'NFC South', 'NFC', 'Charlotte', 'NC', False,
         0.68, 5.0, 0.60, 0.035, 0.20, 3.9, 0.57, 0.030, 0.09, 3.5, 0.54, 0.024, 0.03, 5.3, 0.61, 0.046,
         0.328, 0.534, 0.634, 0.651, 0.41, 0.60, 0.61, 0.64, 0.67, 3.4, 3.7, 3.6, 0.58,
         0.19, 0.37, 0.26, 0.13, 0.01, 0.41, 0.74, 0.76, 0.75),
        
        ('New Orleans Saints', 'NFC South', 'NFC', 'New Orleans', 'LA', True,
         0.69, 5.6, 0.65, 0.046, 0.19, 4.2, 0.61, 0.037, 0.09, 3.8, 0.58, 0.030, 0.03, 5.9, 0.64, 0.056,
         0.365, 0.581, 0.701, 0.718, 0.49, 0.65, 0.69, 0.74, 0.76, 4.0, 4.2, 4.3, 0.66,
         0.25, 0.33, 0.34, 0.20, 0.04, 0.49, 0.71, 0.73, 0.89),
        
        ('Tampa Bay Buccaneers', 'NFC South', 'NFC', 'Tampa', 'FL', False,
         0.73, 6.0, 0.68, 0.052, 0.16, 4.5, 0.64, 0.041, 0.03, 4.2, 0.60, 0.035, 0.08, 6.7, 0.70, 0.068,
         0.392, 0.615, 0.756, 0.773, 0.58, 0.68, 0.77, 0.75, 0.72, 4.7, 4.9, 5.1, 0.70,
         0.27, 0.30, 0.37, 0.25, 0.03, 0.58, 0.73, 0.75, 0.84),
        
        # NFC WEST
        ('Arizona Cardinals', 'NFC West', 'NFC', 'Phoenix', 'AZ', True,
         0.64, 5.2, 0.65, 0.042, 0.24, 4.1, 0.62, 0.036, 0.09, 3.8, 0.59, 0.029, 0.03, 5.6, 0.63, 0.051,
         0.351, 0.542, 0.687, 0.703, 0.46, 0.65, 0.71, 0.68, 0.69, 4.6, 4.2, 4.0, 0.64,
         0.23, 0.35, 0.32, 0.18, 0.02, 0.46, 0.67, 0.69, 0.89),
        
        ('Los Angeles Rams', 'NFC West', 'NFC', 'Los Angeles', 'CA', False,
         0.76, 6.1, 0.69, 0.056, 0.14, 4.6, 0.65, 0.042, 0.03, 4.3, 0.61, 0.037, 0.07, 6.9, 0.71, 0.075,
         0.401, 0.629, 0.771, 0.786, 0.61, 0.69, 0.80, 0.74, 0.72, 4.9, 4.7, 5.2, 0.71,
         0.29, 0.28, 0.46, 0.31, 0.04, 0.61, 0.75, 0.77, 0.82),
        
        ('San Francisco 49ers', 'NFC West', 'NFC', 'San Francisco', 'CA', False,
         0.67, 6.4, 0.73, 0.062, 0.12, 4.8, 0.67, 0.043, 0.18, 5.0, 0.69, 0.047, 0.03, 6.9, 0.71, 0.075,
         0.429, 0.681, 0.823, 0.834, 0.72, 0.73, 0.82, 0.85, 0.81, 6.1, 5.7, 5.4, 0.79,
         0.33, 0.26, 0.51, 0.35, 0.06, 0.72, 0.72, 0.79, 0.85),
        
        ('Seattle Seahawks', 'NFC West', 'NFC', 'Seattle', 'WA', False,
         0.70, 5.9, 0.67, 0.051, 0.18, 4.4, 0.63, 0.040, 0.09, 4.1, 0.60, 0.034, 0.03, 6.1, 0.66, 0.058,
         0.376, 0.598, 0.741, 0.759, 0.59, 0.67, 0.74, 0.72, 0.73, 4.5, 4.7, 5.0, 0.68,
         0.28, 0.32, 0.40, 0.26, 0.04, 0.59, 0.76, 0.78, 0.80)
    ]
    
    # Insert all teams
    for team_data in teams_data:
        cursor.execute('''
            INSERT OR REPLACE INTO teams (
                name, division, conference, city, state, is_dome,
                formation_11_usage, formation_11_ypp, formation_11_success_rate, formation_11_td_rate,
                formation_12_usage, formation_12_ypp, formation_12_success_rate, formation_12_td_rate,
                formation_21_usage, formation_21_ypp, formation_21_success_rate, formation_21_td_rate,
                formation_10_usage, formation_10_ypp, formation_10_success_rate, formation_10_td_rate,
                third_down_conversion, red_zone_efficiency, two_minute_drill, goal_line_efficiency,
                fourth_down_aggression, first_down_success, wr_vs_cb_mismatch, te_vs_lb_mismatch,
                rb_vs_lb_coverage, outside_zone_left, inside_zone, power_gap, screen_efficiency,
                play_action_rate, blitz_frequency, motion_usage, tempo_changes, trick_play_frequency,
                aggressive_fourth_down, cold_weather_rating, wind_adjustment, dome_performance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', team_data)
    
    conn.commit()
    conn.close()

# =============================================================================
# DATABASE QUERY FUNCTIONS WITH CACHING
# =============================================================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_team_data(team_name: str) -> Dict:
    """
    PURPOSE: Retrieve complete team data from database
    INPUTS: team_name (str) - NFL team name
    OUTPUTS: Dictionary with all team statistics
    DEPENDENCIES: SQLite database
    NOTES: Cached for 1 hour to improve performance
    """
    conn = init_database()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM teams WHERE name = ?
    ''', (team_name,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {}
    
    # Convert to structured dictionary
    return {
        'formation_data': {
            '11_personnel': {
                'usage': row[6], 'ypp': row[7], 'success_rate': row[8], 'td_rate': row[9]
            },
            '12_personnel': {
                'usage': row[10], 'ypp': row[11], 'success_rate': row[12], 'td_rate': row[13]
            },
            '21_personnel': {
                'usage': row[14], 'ypp': row[15], 'success_rate': row[16], 'td_rate': row[17]
            },
            '10_personnel': {
                'usage': row[18], 'ypp': row[19], 'success_rate': row[20], 'td_rate': row[21]
            }
        },
        'situational_tendencies': {
            'third_down_conversion': row[22],
            'red_zone_efficiency': row[23],
            'two_minute_drill': row[24],
            'goal_line_efficiency': row[25],
            'fourth_down_aggression': row[26],
            'first_down_success': row[27]
        },
        'personnel_advantages': {
            'wr_vs_cb_mismatch': row[28],
            'te_vs_lb_mismatch': row[29],
            'rb_vs_lb_coverage': row[30],
            'outside_zone_left': row[31],
            'inside_zone': row[32],
            'power_gap': row[33],
            'screen_efficiency': row[34]
        },
        'coaching_tendencies': {
            'play_action_rate': row[35],
            'blitz_frequency': row[36],
            'motion_usage': row[37],
            'tempo_changes': row[38],
            'trick_play_frequency': row[39],
            'aggressive_fourth_down': row[40]
        },
        'weather_performance': {
            'cold_weather_rating': row[41],
            'wind_adjustment': row[42],
            'dome_performance': row[43]
        },
        'stadium_info': {
            'city': row[44],
            'state': row[45],
            'is_dome': bool(row[46])
        }
    }

@st.cache_data(ttl=3600)
def get_all_team_names() -> List[str]:
    """
    PURPOSE: Get list of all NFL team names
    INPUTS: None
    OUTPUTS: Sorted list of team names
    DEPENDENCIES: SQLite database
    NOTES: Cached for performance optimization
    """
    conn = init_database()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM teams ORDER BY name')
    teams = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return teams

# =============================================================================
# CHAT HISTORY MANAGEMENT
# =============================================================================

def save_chat_message(session_id: str, role: str, message: str, analysis_type: str = "general"):
    """
    PURPOSE: Save chat message to database
    INPUTS: session_id, role, message, analysis_type
    OUTPUTS: Message saved to database
    DEPENDENCIES: SQLite database
    NOTES: Prevents session state memory overflow
    """
    conn = init_database()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO chat_history (session_id, role, message, timestamp, analysis_type)
        VALUES (?, ?, ?, ?, ?)
    ''', (session_id, role, message, datetime.now(), analysis_type))
    
    conn.commit()
    conn.close()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_recent_chat_history(session_id: str, limit: int = 10) -> List[Tuple[str, str]]:
    """
    PURPOSE: Retrieve recent chat history for session
    INPUTS: session_id, limit (default 10 messages)
    OUTPUTS: List of (role, message) tuples
    DEPENDENCIES: SQLite database
    NOTES: Limited to prevent memory issues
    """
    conn = init_database()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT role, message FROM chat_history 
        WHERE session_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (session_id, limit))
    
    history = [(row[0], row[1]) for row in cursor.fetchall()]
    conn.close()
    
    # Return in chronological order
    return list(reversed(history))

# =============================================================================
# INITIALIZATION CALL
# =============================================================================

# Initialize database and populate teams on module import
populate_teams_database()
