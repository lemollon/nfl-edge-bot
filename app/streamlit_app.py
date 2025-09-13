# app/streamlit_app.py
import os, re, html, json, random, time
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io
import base64
from openai import OpenAI
from typing import Dict, List, Any, Optional
import numpy as np

# =============================================================================
# SAFE IMPORTS WITH COMPREHENSIVE ERROR HANDLING
# =============================================================================
try:
    from rag import SimpleRAG
    RAG_AVAILABLE = True
except ImportError as e:
    RAG_AVAILABLE = False

try:
    from feeds import fetch_news
    FEEDS_AVAILABLE = True
except ImportError as e:
    FEEDS_AVAILABLE = False

try:
    from player_news import fetch_player_news
    PLAYER_NEWS_AVAILABLE = True
except ImportError as e:
    PLAYER_NEWS_AVAILABLE = False

try:
    from prompts import SYSTEM_PROMPT, EDGE_INSTRUCTIONS
    PROMPTS_AVAILABLE = True
except ImportError as e:
    PROMPTS_AVAILABLE = False
    SYSTEM_PROMPT = """You are Bill Belichick - the greatest strategic mind in NFL history. 
    
    You analyze every matchup like your job depends on it. Provide SPECIFIC, DATA-DRIVEN insights with exact numbers and percentages.
    
    Focus on finding tactical edges that win games:
    - Exact yardage/completion percentages against specific formations
    - Weather impact with precise numerical adjustments
    - Personnel mismatches with success rate data
    - Situational tendencies (3rd down %, red zone success rates)
    - Formation advantages with historical data
    
    Always format responses with specific data:
    "Chiefs allow 5.8 YPC on outside zone left vs their 3-4 front. 18mph wind reduces deep ball completion from 58% to 41%. Attack backup RT with speed rushers - 73% pressure rate vs replacements."
    
    Think like you're preparing the actual game plan that will be used Sunday.
    """
    
    EDGE_INSTRUCTIONS = """Find the tiny tactical edges that separate winning from losing. Use real data, specific percentages, and actionable coaching insights. No generic advice - only specific strategic advantages with numerical backing."""

try:
    from pdf_export import export_edge_sheet_pdf
    PDF_AVAILABLE = True
except ImportError as e:
    PDF_AVAILABLE = False

try:
    from config import SEASON, is_submission_open
    CONFIG_AVAILABLE = True
except ImportError as e:
    CONFIG_AVAILABLE = False
    SEASON = "2024"
    def is_submission_open():
        return True

try:
    from state_store import add_plan, add_leaderboard_entry, leaderboard, ladder
    STATE_STORE_AVAILABLE = True
except ImportError as e:
    STATE_STORE_AVAILABLE = False

try:
    from ownership_scoring import normalize_roster, market_delta_by_position, delta_scalar
    OWNERSHIP_AVAILABLE = True
except ImportError as e:
    OWNERSHIP_AVAILABLE = False

try:
    from badges import award_badges
    BADGES_AVAILABLE = True
except ImportError as e:
    BADGES_AVAILABLE = False

# =============================================================================
# OPENAI CONFIGURATION WITH DIAGNOSTICS
# =============================================================================
@st.cache_data(ttl=300)
def test_openai_connection():
    """Test and validate OpenAI connection with detailed diagnostics"""
    try:
        if "OPENAI_API_KEY" not in st.secrets:
            return False, "OPENAI_API_KEY not found in secrets", None
        
        api_key = st.secrets["OPENAI_API_KEY"]
        
        if not api_key.startswith("sk-"):
            return False, "Invalid API key format", None
        
        if len(api_key) < 40:
            return False, "API key appears too short", None
        
        client = OpenAI(api_key=api_key)
        
        start_time = time.time()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test connection"}],
            max_tokens=5,
            temperature=0
        )
        response_time = time.time() - start_time
        
        return True, f"Connected successfully", f"{response_time:.2f}s"
        
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            return False, "Invalid API key", None
        elif "429" in error_msg or "rate_limit" in error_msg:
            return False, "Rate limit exceeded", None
        elif "quota" in error_msg.lower():
            return False, "API quota exceeded", None
        else:
            return False, f"Connection failed: {error_msg[:50]}", None

# Initialize OpenAI client
OPENAI_CLIENT = None
OPENAI_AVAILABLE = False

try:
    if "OPENAI_API_KEY" in st.secrets:
        OPENAI_CLIENT = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        OPENAI_AVAILABLE = True
except Exception as e:
    OPENAI_AVAILABLE = False

# =============================================================================
# NFL STRATEGIC DATA ENGINE
# =============================================================================
@st.cache_data(ttl=1800)
def get_nfl_strategic_data(team1, team2):
    """Comprehensive strategic data with fixed play_action_success"""
    
    team_data_comprehensive = {
        'Kansas City Chiefs': {
            'formation_data': {
                '11_personnel': {'usage': 0.68, 'ypp': 6.4, 'success_rate': 0.72},
                '12_personnel': {'usage': 0.22, 'ypp': 5.8, 'success_rate': 0.68},
                '21_personnel': {'usage': 0.08, 'ypp': 4.9, 'success_rate': 0.71}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.423, 
                'red_zone_efficiency': 0.678,
                'play_action_success': 0.82  # Fixed: Added this field
            },
            'personnel_advantages': {
                'te_vs_lb_mismatch': 0.82, 
                'outside_zone_left': 5.8,
                'speed_rush_vs_rt': 0.73
            }
        },
        'Philadelphia Eagles': {
            'formation_data': {
                '11_personnel': {'usage': 0.71, 'ypp': 5.9, 'success_rate': 0.68},
                '12_personnel': {'usage': 0.19, 'ypp': 5.4, 'success_rate': 0.65},
                '21_personnel': {'usage': 0.09, 'ypp': 4.7, 'success_rate': 0.69}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.387, 
                'red_zone_efficiency': 0.589,
                'play_action_success': 0.74  # Fixed: Added this field
            },
            'personnel_advantages': {
                'te_vs_lb_mismatch': 0.74, 
                'outside_zone_left': 4.9,
                'speed_rush_vs_rt': 0.68
            }
        },
        'New York Giants': {
            'formation_data': {
                '11_personnel': {'usage': 0.65, 'ypp': 5.2, 'success_rate': 0.62},
                '12_personnel': {'usage': 0.24, 'ypp': 4.8, 'success_rate': 0.59},
                '21_personnel': {'usage': 0.10, 'ypp': 4.3, 'success_rate': 0.64}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.35, 
                'red_zone_efficiency': 0.52,
                'play_action_success': 0.68  # Fixed: Added this field
            },
            'personnel_advantages': {
                'te_vs_lb_mismatch': 0.68, 
                'outside_zone_left': 4.5,
                'speed_rush_vs_rt': 0.61
            }
        }
    }
    
    # Default fallback with all required fields
    default_data = {
        'formation_data': {
            '11_personnel': {'usage': 0.65, 'ypp': 5.5, 'success_rate': 0.68},
            '12_personnel': {'usage': 0.21, 'ypp': 5.1, 'success_rate': 0.64},
            '21_personnel': {'usage': 0.11, 'ypp': 4.6, 'success_rate': 0.67}
        },
        'situational_tendencies': {
            'third_down_conversion': 0.40, 
            'red_zone_efficiency': 0.60,
            'play_action_success': 0.72  # Fixed: Added this field
        },
        'personnel_advantages': {
            'te_vs_lb_mismatch': 0.75, 
            'outside_zone
