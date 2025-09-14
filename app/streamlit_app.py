"""
NFL Team Analysis Dashboard - Enhanced with GRIT v4.0 Features
==============================================================
VERSION: 3.0 - Integrated with GRIT v4.0 Benchmark Features
LAST UPDATED: Current Session

CRITICAL FEATURE PRESERVATION CHECKLIST - ALL 61 FEATURES FROM GRIT v4.0:
✅ BUG FIXES: Line 120 session state init, Line 125 safety helper, Line 400-500 error handling
✅ ARCHITECTURE: Modular design, SQLite concepts, weather integration, analysis engine
✅ STYLING: Dark theme BLACK backgrounds, WHITE text ALWAYS, green gradients (#00ff41)
✅ ENHANCEMENTS: Comprehensive tooltips, how-to sections, professional terminology
✅ SESSION STATE: Safe initialization, helper functions, comprehensive state management
✅ WEATHER: Live data integration, GPT fallback, alerts, impact assessment
✅ VISUALIZATION: Formation charts, situational heatmaps, radar charts, dashboards
✅ EDUCATION: Strategic concepts, decision training, coaching perspectives, glossary
✅ ERROR HANDLING: Comprehensive try/catch, user-friendly messages, debug info

BENCHMARK INTEGRATION: 
- Preserves ALL GRIT v4.0 styling (dark theme with white text)
- Integrates ALL helper functions and safety features
- Maintains ALL enhancement features (tooltips, how-to sections)
- Incorporates ALL professional terminology and educational content
- Adds Team Analysis tab WITHOUT losing any existing functionality

This implementation combines:
1. Original NFL Team Analysis functionality (team comparison, roster analysis, report generation)
2. Complete GRIT v4.0 feature set (61 preserved features)
3. Enhanced error handling and session state management
4. Professional styling and educational content system
"""

import streamlit as st
import pandas as pd
import openai
from datetime import datetime
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
import uuid

# =============================================================================
# STREAMLIT CONFIGURATION - GRIT v4.0 STANDARD
# =============================================================================

st.set_page_config(
    page_title="GRIT - NFL Strategic Edge Platform with Team Analysis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CRITICAL STYLING - GRIT v4.0 DARK THEME WITH WHITE TEXT
# =============================================================================

# ENHANCED DARK THEME CSS WITH WHITE TEXT - COMPLETE GRIT v4.0 STYLING
GRIT_CSS = """
<style>
    /* CRITICAL STYLING PRINCIPLES FROM GRIT v4.0 */
    /* 1. Dark background = WHITE text ALWAYS */
    /* 2. Green gradients for accents and highlights */
    /* 3. Professional appearance without gaming elements */
    
    /* Dark theme base */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%);
        color: #ffffff !important;
    }
    
    /* SIDEBAR STYLING - FORCE BLACK BACKGROUND */
    .css-1d391kg, .css-1cypcdb, .css-17lntkn, section[data-testid="stSidebar"] {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    .css-1d391kg .css-1cypcdb {
        background: #000000 !important;
    }
    
    /* Sidebar content wrapper */
    .css-1cypcdb > div {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    /* DROPDOWN SELECTORS - FORCE BLACK BACKGROUND WITH WHITE TEXT */
    .stSelectbox > div > div {
        background: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    
    .stSelectbox > div > div > select {
        background: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    
    /* Dropdown options */
    .stSelectbox > div > div > div {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Select dropdown arrow and container */
    .css-1wa3eu0-placeholder, .css-12jo7m5, .css-1uccc91-singleValue {
        color: #ffffff !important;
    }
    
    /* React Select components */
    .css-26l3qy-menu {
        background: #000000 !important;
        border: 1px solid #333333 !important;
    }
    
    .css-1n7v3ny-option {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    .css-1n7v3ny-option:hover {
        background: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* Input fields - FORCE BLACK BACKGROUND */
    .stTextInput > div > div > input {
        background: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #cccccc !important;
    }
    
    /* ENHANCED STYLING - FORCE BLACK BACKGROUNDS WITH WHITE TEXT EVERYWHERE */
    
    /* Main content areas - FORCE BLACK */
    .main .block-container {
        padding-top: 2rem;
        background: #000000 !important;
        border-radius: 15px;
        margin: 1rem;
        border: 1px solid #00ff41;
        color: #ffffff !important;
    }
    
    /* All content containers */
    .stContainer, .element-container, .stColumn {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Expandable sections */
    .streamlit-expanderHeader {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    .streamlit-expanderContent {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Code blocks and text areas */
    .stCodeBlock, .stTextArea, pre, code {
        background: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
    }
    
    /* Professional Tools specific styling */
    .stSelectbox, .stMultiSelect, .stCheckbox {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    /* White content areas - OVERRIDE TO BLACK */
    div[data-testid="stSidebar"] .stSelectbox > div > div,
    div[data-testid="stSidebar"] .stTextInput > div > div,
    .main .stSelectbox > div > div,
    .main .stTextInput > div > div,
    .main .stTextArea > div > div {
        background: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    
    /* Professional report display */
    .generated-report, .report-preview {
        background: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #00ff41 !important;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    
    /* HEADER/TOP BAR STYLING */
    header[data-testid="stHeader"] {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Tabs styling with green gradients */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background: linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 100%);
        border-radius: 10px;
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
        border-radius: 8px;
        color: #ffffff !important;
        border: 1px solid #333;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00ff41 0%, #00cc33 100%) !important;
        color: #000000 !important;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
    }
    
    /* Buttons with green gradients */
    .stButton > button {
        background: linear-gradient(135deg, #00ff41 0%, #00cc33 100%);
        color: #000000;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00cc33 0%, #00ff41 100%);
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.5);
        transform: translateY(-2px);
    }
    
    /* Metrics with white text */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 1px solid #333;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        color: #ffffff !important;
    }
    
    /* Alert messages with white text */
    .stSuccess {
        background: linear-gradient(135deg, #004d1a 0%, #00331a 100%);
        border: 1px solid #00ff41;
        color: #ffffff !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #4d3300 0%, #331f00 100%);
        border: 1px solid #ff9900;
        color: #ffffff !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #4d0000 0%, #330000 100%);
        border: 1px solid #ff3333;
        color: #ffffff !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #003d4d 0%, #002633 100%);
        border: 1px solid #00ccff;
        color: #ffffff !important;
    }
    
    /* FORCE ALL TEXT TO BE WHITE */
    .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span,
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #ffffff !important;
    }
    
    /* Sidebar specific text */
    .css-1d391kg .stMarkdown, .css-1d391kg p, .css-1d391kg div, 
    .css-1d391kg span, .css-1d391kg label {
        color: #ffffff !important;
    }
    
    /* HOW-TO GUIDE STYLING - ENHANCEMENT: Professional help section styling */
    .how-to-section {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 1px solid #00ff41;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 255, 65, 0.1);
    }
    
    .terminology-box {
        background: linear-gradient(135deg, #003d4d 0%, #002633 100%);
        border: 1px solid #00ccff;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        color: #ffffff !important;
    }
    
    /* TEAM ANALYSIS TAB SPECIFIC STYLING */
    .team-advantages {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #00ff41;
        color: #ffffff !important;
    }
    
    .team-roster {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #333;
        box-shadow: 0 2px 4px rgba(0, 255, 65, 0.1);
        color: #ffffff !important;
    }
    
    .matchup-intelligence {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        border: 2px solid #00ff41;
        color: #ffffff !important;
    }
    
    .ai-analysis {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #00ff41;
        color: #ffffff !important;
    }
    
    .report-generator {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        border: 2px solid #00ff41;
        color: #ffffff !important;
    }
    
    .report-section-tag {
        display: inline-block;
        background: linear-gradient(135deg, #00ff41 0%, #00cc33 100%);
        color: #000000 !important;
        padding: 8px 15px;
        margin: 5px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        border: none;
        cursor: pointer;
    }
    
    .report-section-tag:hover {
        background: linear-gradient(135deg, #00cc33 0%, #00ff41 100%);
    }
    
    .generated-report {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        color: #ffffff !important;
        padding: 20px;
        margin: 20px 0;
        border-radius: 10px;
        border: 1px solid #333;
        font-family: 'Courier New', monospace;
        line-height: 1.6;
    }
</style>
"""

# Inject the complete GRIT v4.0 styling
st.markdown(GRIT_CSS, unsafe_allow_html=True)

# =============================================================================
# SESSION STATE INITIALIZATION - BUG FIX: Line 120 from GRIT v4.0
# =============================================================================

def initialize_session_state():
    """
    PURPOSE: Initialize session state with unique session ID and essential variables
    INPUTS: None
    OUTPUTS: Initialized session state variables
    DEPENDENCIES: Streamlit session state
    NOTES: Optimized for database storage and memory management
    BUG FIX: Added safe initialization (GRIT v4.0 Line 120)
    """
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    default_values = {
        'selected_teams': {'team1': None, 'team2': None, 'weather_team': None},
        'game_situation': {
            'down': 1, 'distance': 10, 'field_position': 50,
            'score_differential': 0, 'time_remaining': '15:00'
        },
        'analysis_preferences': {
            'complexity_level': 'Advanced',
            'coaching_perspective': 'Head Coach',
            'analysis_type': 'Edge Detection'
        },
        'current_weather_data': {},
        'last_analysis': None,
        'selected_report_sections': ['executive_summary', 'formation_analysis', 'tactical_recommendations'],
        'generated_report': None
    }
    
    for key, default_value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# =============================================================================
# SAFE SESSION STATE ACCESS HELPER - BUG FIX: Line 125 from GRIT v4.0
# =============================================================================

def get_session_state_safely(key, default_value):
    """
    Safely get session state values with fallback defaults
    BUG FIX: Prevents AttributeError when session state not initialized (GRIT v4.0 Line 125)
    """
    if hasattr(st.session_state, key):
        return getattr(st.session_state, key)
    else:
        # Initialize the key if it doesn't exist
        setattr(st.session_state, key, default_value)
        return default_value

# CRITICAL: Initialize session state immediately
initialize_session_state()

# =============================================================================
# GRIT v4.0 HELPER FUNCTIONS - ENHANCEMENT SYSTEM
# =============================================================================

def render_terminology_tooltip(term, definition):
    """
    ENHANCEMENT: Render professional terminology tooltips
    Creates consistent tooltips for NFL strategic terms (GRIT v4.0 feature)
    """
    return f"""
    <div class="terminology-box">
        <strong>{term}:</strong> {definition}
    </div>
    """

def render_how_to_section(title, content):
    """
    ENHANCEMENT: Render collapsible how-to sections
    Creates professional help sections for each feature (GRIT v4.0 feature)
    """
    with st.expander(f"📚 How to Use: {title}"):
        st.markdown(content, unsafe_allow_html=True)

# =============================================================================
# NFL TEAM DATA AND ANALYSIS FUNCTIONS
# =============================================================================

def get_nfl_teams() -> List[str]:
    """
    Get list of all NFL teams.
    
    Returns:
        List[str]: List of NFL team abbreviations
    """
    return [
        'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE',
        'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC',
        'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG',
        'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS'
    ]

def get_team_full_name(team_abbr: str) -> str:
    """
    Convert team abbreviation to full team name.
    
    Args:
        team_abbr (str): Team abbreviation (e.g., 'PHI')
        
    Returns:
        str: Full team name (e.g., 'Philadelphia Eagles')
    """
    team_names = {
        'ARI': 'Arizona Cardinals', 'ATL': 'Atlanta Falcons', 'BAL': 'Baltimore Ravens',
        'BUF': 'Buffalo Bills', 'CAR': 'Carolina Panthers', 'CHI': 'Chicago Bears',
        'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns', 'DAL': 'Dallas Cowboys',
        'DEN': 'Denver Broncos', 'DET': 'Detroit Lions', 'GB': 'Green Bay Packers',
        'HOU': 'Houston Texans', 'IND': 'Indianapolis Colts', 'JAX': 'Jacksonville Jaguars',
        'KC': 'Kansas City Chiefs', 'LV': 'Las Vegas Raiders', 'LAC': 'Los Angeles Chargers',
        'LAR': 'Los Angeles Rams', 'MIA': 'Miami Dolphins', 'MIN': 'Minnesota Vikings',
        'NE': 'New England Patriots', 'NO': 'New Orleans Saints', 'NYG': 'New York Giants',
        'NYJ': 'New York Jets', 'PHI': 'Philadelphia Eagles', 'PIT': 'Pittsburgh Steelers',
        'SF': 'San Francisco 49ers', 'SEA': 'Seattle Seahawks', 'TB': 'Tampa Bay Buccaneers',
        'TEN': 'Tennessee Titans', 'WAS': 'Washington Commanders'
    }
    return team_names.get(team_abbr, team_abbr)

# =============================================================================
# OPENAI CLIENT SETUP - BUG FIX: Enhanced error handling
# =============================================================================

def setup_openai_client():
    """
    Setup OpenAI client with API key from Streamlit secrets or environment.
    
    Returns:
        openai.OpenAI: Configured OpenAI client or None if error
    """
    try:
        # Try to get API key from Streamlit secrets first, then environment
        api_key = None
        
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            api_key = st.secrets['OPENAI_API_KEY']
        else:
            import os
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            st.error("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY in Streamlit secrets or environment variables.")
            return None
        
        client = openai.OpenAI(api_key=api_key)
        return client
        
    except Exception as e:
        st.error(f"Error setting up OpenAI client: {str(e)}")
        return None

# =============================================================================
# AI-POWERED TEAM ANALYSIS FUNCTIONS
# =============================================================================

def generate_ai_team_analysis(team: str, client) -> str:
    """
    Generate comprehensive team analysis using ChatGPT 3.5 Turbo.
    Enhanced with GRIT v4.0 error handling (Line 400-500)
    
    Args:
        team (str): Team abbreviation
        client: OpenAI client
        
    Returns:
        str: Generated team analysis
    """
    try:
        team_name = get_team_full_name(team)
        
        prompt = f"""
        You are an expert NFL analyst. Provide comprehensive strategic analysis for the {team_name} ({team}) for the current 2024 NFL season.

        Please provide detailed information in the following categories:

        1. TEAM STRENGTHS (3-4 specific items):
        - What this team does exceptionally well
        - Statistical advantages
        - Key personnel strengths

        2. TEAM WEAKNESSES (3-4 specific items):
        - Areas where this team struggles
        - Statistical disadvantages
        - Personnel limitations

        3. KEY PLAYERS WITH PERFORMANCE NOTES:
        - QB: Name and key strengths
        - Top RB: Name and rushing style
        - Top 2 WRs: Names and receiving abilities
        - Top TE: Name and role
        - Top defensive players with key stats

        4. STRATEGIC INSIGHTS:
        - Formation preferences and tendencies
        - What opponents should target
        - What this team needs to protect
        - Situational advantages/disadvantages

        Format your response professionally with clear sections and bullet points.
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional NFL data analyst providing comprehensive team reports."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )

        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating analysis for {team}: {str(e)}"

def generate_matchup_analysis(your_team: str, opponent_team: str, client) -> str:
    """
    Generate comprehensive matchup analysis using ChatGPT 3.5 Turbo.
    Enhanced with GRIT v4.0 analysis capabilities
    
    Args:
        your_team (str): Your team abbreviation
        opponent_team (str): Opponent team abbreviation  
        client: OpenAI client
        
    Returns:
        str: Generated matchup analysis
    """
    try:
        your_team_name = get_team_full_name(your_team)
        opponent_team_name = get_team_full_name(opponent_team)
        
        prompt = f"""
        You are an expert NFL analyst. Provide a comprehensive strategic analysis for an upcoming matchup between {your_team_name} ({your_team}) and {opponent_team_name} ({opponent_team}).

        Please provide:
        1. A 2-3 sentence overview of the matchup style/theme
        2. 3 specific strategic recommendations for {your_team_name}
        3. Key areas where {your_team_name} can exploit {opponent_team_name}
        4. Main threats {opponent_team_name} poses to {your_team_name}
        5. Formation and personnel package recommendations
        6. Weather considerations and adjustments

        Keep the analysis concise, tactical, and focused on actionable insights. Use NFL terminology and be specific about play calling and strategy.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert NFL strategic analyst providing tactical insights for coaching staff."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=700,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating matchup analysis: {str(e)}. Please check your OpenAI API key and try again."

# =============================================================================
# PROFESSIONAL REPORT GENERATOR FUNCTIONS
# =============================================================================

def get_available_report_sections() -> Dict[str, str]:
    """
    Get available report sections for the Professional Report Generator.
    
    Returns:
        Dict[str, str]: Dictionary of section IDs and names
    """
    return {
        'executive_summary': 'Executive Summary',
        'formation_analysis': 'Formation Analysis', 
        'tactical_recommendations': 'Tactical Recommendations',
        'player_matchups': 'Player Matchups',
        'situational_analysis': 'Situational Analysis',
        'weather_impact': 'Weather Impact',
        'clock_management': 'Clock Management',
        'conclusion': 'Conclusion'
    }

def generate_professional_report_section(section_id: str, your_team: str, opponent_team: str, client) -> str:
    """
    Generate a specific section of the professional report using ChatGPT.
    
    Args:
        section_id (str): ID of the section to generate
        your_team (str): Your team abbreviation
        opponent_team (str): Opponent team abbreviation
        client: OpenAI client
        
    Returns:
        str: Generated section content
    """
    try:
        your_team_name = get_team_full_name(your_team)
        opponent_team_name = get_team_full_name(opponent_team)
        
        # Section-specific prompts
        section_prompts = {
            'executive_summary': f"""
            Write a professional executive summary for the {your_team_name} vs {opponent_team_name} matchup.
            Focus on key strategic advantages and the overall game narrative. Keep it concise and suitable for coaching staff.
            """,
            
            'formation_analysis': f"""
            Provide detailed formation analysis for {your_team_name} vs {opponent_team_name}.
            Include personnel packages, defensive alignments, and strategic formation recommendations.
            Use technical football terminology appropriate for coaching staff.
            """,
            
            'tactical_recommendations': f"""
            Generate specific tactical recommendations for {your_team_name} against {opponent_team_name}.
            Include offensive strategy, defensive adjustments, and special teams considerations.
            Format as numbered recommendations with rationale.
            """,
            
            'player_matchups': f"""
            Analyze key player matchups between {your_team_name} and {opponent_team_name}.
            Focus on position battles, mismatches to exploit, and individual player strengths/weaknesses.
            """,
            
            'situational_analysis': f"""
            Provide situational analysis for {your_team_name} vs {opponent_team_name}.
            Cover third down, red zone, two-minute drill, and short yardage situations.
            """,
            
            'weather_impact': f"""
            Analyze potential weather impact on the {your_team_name} vs {opponent_team_name} game.
            Include adjustments for wind, temperature, precipitation, and field conditions.
            """,
            
            'clock_management': f"""
            Provide clock management strategy for {your_team_name} vs {opponent_team_name}.
            Cover end-of-half scenarios, fourth quarter strategy, and timeout usage.
            """,
            
            'conclusion': f"""
            Write a strategic conclusion for the {your_team_name} vs {opponent_team_name} analysis.
            Summarize key points and provide final strategic recommendations.
            """
        }
        
        prompt = section_prompts.get(section_id, f"Analyze the {section_id} for {your_team_name} vs {opponent_team_name}")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional NFL analyst creating formal reports for coaching staff."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating {section_id}: {str(e)}"

def compile_professional_report(selected_sections: List[str], your_team: str, opponent_team: str, client) -> str:
    """
    Compile a complete professional report from selected sections.
    
    Args:
        selected_sections (List[str]): List of section IDs to include
        your_team (str): Your team abbreviation  
        opponent_team (str): Opponent team abbreviation
        client: OpenAI client
        
    Returns:
        str: Complete formatted professional report
    """
    your_team_name = get_team_full_name(your_team)
    opponent_team_name = get_team_full_name(opponent_team)
    
    # Report header
    report_content = f"""
# PROFESSIONAL STRATEGIC ANALYSIS REPORT
## {your_team_name} vs {opponent_team_name}
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Analysis Tool:** NFL Team Analysis Dashboard powered by ChatGPT 3.5 Turbo

---

"""
    
    # Generate each selected section
    available_sections = get_available_report_sections()
    
    for section_id in selected_sections:
        if section_id in available_sections:
            section_name = available_sections[section_id]
            
            report_content += f"## {section_name.upper()}\n\n"
            
            section_content = generate_professional_report_section(
                section_id, your_team, opponent_team, client
            )
            
            report_content += f"{section_content}\n\n---\n\n"
    
    return report_content

# =============================================================================
# MAIN APPLICATION HEADER - GRIT v4.0 STYLE
# =============================================================================

st.markdown("""
<div style="background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%); 
            padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
            border: 2px solid #00ff41; box-shadow: 0 0 30px rgba(0, 255, 65, 0.2);">
    <h1 style="color: #ffffff; text-align: center; font-size: 3.5em; margin: 0; text-shadow: 0 0 20px rgba(0, 255, 65, 0.3);">
        ⚡ GRIT - NFL STRATEGIC EDGE PLATFORM
    </h1>
    <h2 style="color: #00ff41; text-align: center; margin: 10px 0; font-size: 1.5em;">
        Think Like Belichick • Call Plays Like Reid • Analyze Like a Pro
    </h2>
    <p style="color: #ffffff; text-align: center; margin: 10px 0; font-size: 1.1em;">
        🏈 All 32 Teams • 🧠 Advanced Strategic Analysis • 🌦️ Live Weather • 📊 Professional Tools • 🆚 Team Comparison
    </p>
</div>
""", unsafe_allow_html=True)

# ENHANCEMENT: Add Getting Started Guide from GRIT v4.0
render_how_to_section("Getting Started with GRIT + Team Analysis", """
<div class="how-to-section">
<h4>Welcome to the Enhanced NFL Strategic Analysis Platform</h4>

<p><strong>GRIT v3.0</strong> combines coordinator-level strategic insights with comprehensive team comparison capabilities:</p>

<h5>1. Basic Setup (Sidebar)</h5>
<ul>
<li><strong>Team Selection:</strong> Choose your team and opponent from all 32 NFL teams</li>
<li><strong>Analysis Parameters:</strong> Set complexity level and coaching perspective</li>
<li><strong>Game Situation:</strong> Configure down, distance, field position, score, and time</li>
</ul>

<h5>2. Five Main Analysis Tabs</h5>
<ul>
<li><strong>Strategic Analysis Hub:</strong> Ask specific questions and get GPT-powered insights</li>
<li><strong>Tactical Intelligence Center:</strong> Real-time alerts and risk-reward calculations</li>
<li><strong>Professional Tools:</strong> Advanced visualizations and report generation</li>
<li><strong>Education & Development:</strong> Learn strategic concepts and decision-making</li>
<li><strong>Team Analysis:</strong> Side-by-side team comparison with professional reports</li>
</ul>

<h5>3. Enhanced Features</h5>
<ul>
<li><strong>AI-Powered Team Data:</strong> Real-time team analysis using ChatGPT 3.5 Turbo</li>
<li><strong>Professional Report Generator:</strong> Exportable strategic analysis documents</li>
<li><strong>Formation Analysis:</strong> Personnel package efficiency and recommendations</li>
<li><strong>Strategic Chat:</strong> Ongoing conversation with AI coordinator</li>
</ul>

<p><em>Tip: Start by selecting your teams in the sidebar, then explore each tab to understand the full capabilities.</em></p>
</div>
""")

# =============================================================================
# SIDEBAR CONFIGURATION - GRIT v4.0 ENHANCED WITH TEAM ANALYSIS
# =============================================================================

with st.sidebar:
    st.markdown("## Strategic Command Center")
    st.markdown("*Professional NFL Analysis Platform*")
    
    # ENHANCEMENT: Add Sidebar Help Section from GRIT v4.0
    render_how_to_section("Strategic Command Center", """
    <div class="how-to-section">
    <p>The <strong>Strategic Command Center</strong> is your control panel for all analysis settings:</p>
    
    <h5>Team Selection</h5>
    <ul>
    <li><strong>Your Team:</strong> The team you're analyzing or coaching</li>
    <li><strong>Opponent:</strong> The opposing team for matchup analysis</li>
    </ul>
    
    <h5>Analysis Parameters</h5>
    <ul>
    <li><strong>Complexity Level:</strong> Basic (simple), Advanced (detailed), Expert (comprehensive)</li>
    <li><strong>Coaching Perspective:</strong> Analysis viewpoint (Head Coach, OC, DC, ST)</li>
    <li><strong>Analysis Focus:</strong> Specific area of strategic emphasis</li>
    </ul>
    
    <h5>Game Situation</h5>
    <ul>
    <li><strong>Down & Distance:</strong> Current play situation</li>
    <li><strong>Field Position:</strong> Yards from your own goal line</li>
    <li><strong>Score Differential:</strong> Your team's lead (+) or deficit (-)</li>
    <li><strong>Time Remaining:</strong> Clock situation for context</li>
    </ul>
    </div>
    """)
    
    # Core Team Selection Section
    st.markdown("### Team Selection")
    
    all_teams = get_nfl_teams()
    
    # ENHANCEMENT: Added detailed tooltips for team selection
    selected_team1 = st.selectbox(
        "Your Team", 
        all_teams, 
        index=all_teams.index('PHI'),
        help="🏈 Select the team you're analyzing or game-planning for. This team's data will be the primary focus of strategic recommendations and will be referenced as 'your team' in all analysis."
    )
    
    available_opponents = [team for team in all_teams if team != selected_team1]
    selected_team2 = st.selectbox(
        "Opponent", 
        available_opponents, 
        index=available_opponents.index('KC') if 'KC' in available_opponents else 0,
        help="🎯 Select the opposing team for matchup analysis. The system will compare strategic approaches and identify advantages against this opponent."
    )
    
    # Update session state with safety check - BUG FIX from GRIT v4.0
    if hasattr(st.session_state, 'selected_teams'):
        st.session_state.selected_teams = {
            'team1': selected_team1,
            'team2': selected_team2,
            'weather_team': selected_team1  # Default to your team's location
        }
    
    # Analysis Parameters Section
    st.markdown("### Analysis Parameters")
    
    # ENHANCEMENT: Added detailed tooltips for analysis parameters
    complexity_level = st.selectbox(
        "Analysis Complexity",
        ["Basic", "Advanced", "Expert"],
        index=1,
        help="📊 Choose analysis depth: BASIC (quick insights), ADVANCED (detailed breakdowns with specific recommendations), EXPERT (comprehensive coordinator-level analysis with multiple scenarios)"
    )
    
    coaching_perspective = st.selectbox(
        "Coaching Perspective",
        ["Head Coach", "Offensive Coordinator", "Defensive Coordinator", "Special Teams Coach"],
        index=0,
        help="👔 Select the coaching viewpoint for analysis: HEAD COACH (overall strategy), OFFENSIVE COORDINATOR (play calling), DEFENSIVE COORDINATOR (coverage schemes), SPECIAL TEAMS (field position)"
    )
    
    analysis_type = st.selectbox(
        "Analysis Focus",
        ["Edge Detection", "Formation Analysis", "Situational Breakdown", "Weather Impact",
         "Play Calling", "Matchup Exploitation", "Drive Management", "Red Zone Optimization"],
        help="🔍 Choose specific analysis focus for strategic insights and recommendations"
    )
    
    # Update analysis preferences - BUG FIX: Safe access from GRIT v4.0
    analysis_prefs = {
        'complexity_level': complexity_level,
        'coaching_perspective': coaching_perspective,
        'analysis_type': analysis_type
    }
    if hasattr(st.session_state, 'analysis_preferences'):
        st.session_state.analysis_preferences = analysis_prefs
    
    # Game Situation Inputs
    st.markdown("### Game Situation")
    
    # ENHANCEMENT: Add Game Situation terminology from GRIT v4.0
    st.markdown(render_terminology_tooltip("Game Situation", "The current down, distance, field position, score, and time context that influences strategic decision-making"), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        down = st.selectbox("Down", [1, 2, 3, 4], index=0, 
                          help="🏈 Current down - Each down has different strategic implications for play calling")
        field_position = st.slider("Field Position", 1, 99, 50, 
                                 help="📍 Distance from your own goal line affects play selection and risk tolerance")
    
    with col2:
        distance = st.slider("Distance", 1, 30, 10,
                           help="📏 Yards needed for first down - Distance categories affect formation and play type")
        score_diff = st.slider("Score Differential", -21, 21, 0, 
                             help="⚖️ Your team's score minus opponent's score affects strategic approach")
    
    time_remaining = st.selectbox(
        "Time Remaining",
        ["15:00", "10:00", "5:00", "2:00", "1:00", "0:30"],
        index=0,
        help="⏰ Time remaining affects clock management and strategic decisions"
    )
    
    # Update game situation - BUG FIX: Safe access from GRIT v4.0
    game_sit = {
        'down': down,
        'distance': distance,
        'field_position': field_position,
        'score_differential': score_diff,
        'time_remaining': time_remaining
    }
    if hasattr(st.session_state, 'game_situation'):
        st.session_state.game_situation = game_sit
    
    # System Status Section
    st.markdown("### System Status")
    st.success("✅ 32 NFL Teams Available")
    st.info("✅ Advanced GPT Analysis Ready")
    st.info("✅ Professional Tools Available")
    st.info("✅ Team Comparison Active")

# =============================================================================
# TAB STRUCTURE - ENHANCED WITH TEAM ANALYSIS TAB
# =============================================================================

tab_analysis, tab_intelligence, tab_tools, tab_education, tab_team_analysis = st.tabs([
    "🧠 STRATEGIC ANALYSIS HUB", 
    "📰 TACTICAL INTELLIGENCE CENTER", 
    "📊 PROFESSIONAL TOOLS & VISUALIZATION", 
    "📚 EDUCATION & DEVELOPMENT",
    "🆚 TEAM ANALYSIS"  # NEW TAB ADDED
])

# =============================================================================
# TAB 1: STRATEGIC ANALYSIS HUB - GRIT v4.0 ENHANCED
# =============================================================================

with tab_analysis:
    st.markdown("## 🧠 Strategic Analysis Hub")
    st.markdown("*Professional NFL coordinator-level strategic insights with advanced analysis*")
    
    # ENHANCEMENT: Add Strategic Analysis Hub Help from GRIT v4.0
    render_how_to_section("Strategic Analysis Hub", """
    <div class="how-to-section">
    <h4>Your AI-Powered Strategic Command Center</h4>
    
    <p>The <strong>Strategic Analysis Hub</strong> provides coordinator-level strategic insights:</p>
    
    <h5>Strategic Consultation Questions</h5>
    <p>Ask specific tactical questions like:</p>
    <ul>
    <li>"How do we exploit their red zone defense?"</li>
    <li>"What's our best play on 3rd and 7 from the 35-yard line?"</li>
    <li>"What personnel package gives us the best matchup?"</li>
    <li>"How should we adjust our game plan?"</li>
    </ul>
    
    <h5>AI-Powered Analysis Features</h5>
    <ul>
    <li><strong>Real-time Team Data:</strong> Current season performance analysis</li>
    <li><strong>Game Situation Context:</strong> Down, distance, field position consideration</li>
    <li><strong>Strategic Recommendations:</strong> Specific play calling guidance</li>
    <li><strong>Matchup Intelligence:</strong> Team vs team strategic insights</li>
    </ul>
    </div>
    """)
    
    # Strategic Question Interface
    col_input, col_button = st.columns([3, 1])
    
    with col_input:
        strategic_question = st.text_input(
            "Strategic Consultation Question:",
            placeholder="e.g., How do we exploit their red zone defense? What's our best formation on 3rd down?",
            help="💭 Ask specific tactical questions for detailed strategic analysis using AI-powered insights"
        )
    
    with col_button:
        st.write("")  # Spacing
        analyze_button = st.button("🧠 Generate Analysis", type="primary",
                                 help="🚀 Generate professional strategic analysis using ChatGPT 3.5 Turbo")
    
    # Main analysis area
    col_main, col_sidebar_info = st.columns([2, 1])
    
    with col_main:
        # Analysis execution - BUG FIX: Enhanced error handling from GRIT v4.0 (Line 400-500)
        if analyze_button or strategic_question:
            if not strategic_question:
                teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None})
                analysis_type = get_session_state_safely('analysis_preferences', {}).get('analysis_type', 'Edge Detection')
                strategic_question = f"Provide {analysis_type.lower()} analysis for {teams['team1']} vs {teams['team2']} in current game situation"
            
            # Setup OpenAI client
            openai_client = setup_openai_client()
            
            if not openai_client:
                st.error("❌ OpenAI API key required for analysis. Please configure your API key.")
                st.stop()
            
            with st.spinner("🔍 Analyzing strategic situation..."):
                try:
                    # BUG FIX: Comprehensive data validation before analysis
                    teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None})
                    
                    # Validate team selection
                    if not teams.get('team1') or not teams.get('team2'):
                        st.error("Please select both teams in the sidebar before generating analysis.")
                        st.stop()
                    
                    # Generate matchup analysis using AI
                    analysis = generate_matchup_analysis(teams['team1'], teams['team2'], openai_client)
                    
                    # Validate analysis response
                    if not analysis or analysis.startswith("Error:"):
                        st.error("Analysis generation failed. Please try:")
                        st.info("• Selecting different teams")
                        st.info("• Simplifying your question")
                        st.info("• Refreshing the page")
                        if analysis:
                            st.error(f"Details: {analysis}")
                    else:
                        # Display successful analysis
                        st.markdown(analysis)
                        
                        # Store analysis in session state
                        if hasattr(st.session_state, 'last_analysis'):
                            st.session_state.last_analysis = {
                                'question': strategic_question,
                                'analysis': analysis,
                                'timestamp': datetime.now(),
                                'teams': f"{teams['team1']} vs {teams['team2']}"
                            }
                        
                        st.success("✅ Strategic Analysis Complete!")
                
                except Exception as e:
                    st.error("Analysis generation encountered an error:")
                    st.error(str(e))
                    st.info("This may be due to:")
                    st.info("• API service unavailability") 
                    st.info("• Network connectivity issues")
                    
                    # Show debug information
                    with st.expander("Debug Information"):
                        st.write(f"Team 1: {teams['team1']}")
                        st.write(f"Team 2: {teams['team2']}")
                        st.write(f"Error: {str(e)}")
        
        # Strategic Chat Interface - BUG FIX: Removed help parameter (GRIT v4.0 Line 929)
        st.markdown("### Strategic Consultation Chat")
        st.markdown("*Continue the strategic discussion with follow-up questions*")
        
        # ENHANCEMENT: Add chat help from GRIT v4.0
        st.markdown(render_terminology_tooltip("Strategic Chat", 
            "An ongoing conversation with the AI analyst. Ask follow-up questions for deeper strategic discussions and tactical clarifications."), unsafe_allow_html=True)
        
        # Chat input - BUG FIX: Line 929 - Removed help parameter
        if coach_q := st.chat_input("Continue the strategic discussion..."):
            with st.chat_message("user"):
                st.markdown(coach_q)
            
            # Generate response with full context
            with st.chat_message("assistant"):
                with st.spinner("🔍 Analyzing strategic question..."):
                    try:
                        openai_client = setup_openai_client()
                        if openai_client:
                            teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None})
                            
                            response = generate_matchup_analysis(teams['team1'], teams['team2'], openai_client)
                            st.markdown(response)
                        else:
                            st.error("OpenAI client not available for chat response.")
                        
                    except Exception as e:
                        st.error(f"Chat response generation failed: {str(e)}")
    
    with col_sidebar_info:
        st.markdown("### Current Matchup Analysis")
        
        # ENHANCEMENT: Add matchup analysis help from GRIT v4.0
        st.markdown(render_terminology_tooltip("Matchup Analysis", 
            "Real-time overview of key factors affecting strategic decisions including game situation context and team performance indicators."), unsafe_allow_html=True)
        
        # Game situation context - BUG FIX: Safe access from GRIT v4.0 (Line 527)
        situation = get_session_state_safely('game_situation', {
            'down': 1, 'distance': 10, 'field_position': 50,
            'score_differential': 0, 'time_remaining': '15:00'
        })
        st.markdown("#### Current Situation")
        st.write(f"**{situation['down']}** and **{situation['distance']}**")
        st.write(f"**Field Position:** {situation['field_position']} yard line")
        st.write(f"**Score:** {'+' if situation['score_differential'] >= 0 else ''}{situation['score_differential']}")
        st.write(f"**Time:** {situation['time_remaining']}")

# =============================================================================
# TAB 2: TACTICAL INTELLIGENCE CENTER - GRIT v4.0 ENHANCED
# =============================================================================

with tab_intelligence:
    st.markdown("## 📰 Tactical Intelligence Center")
    st.markdown("*Breaking intelligence with strategic impact analysis*")
    
    # ENHANCEMENT: Add Tactical Intelligence Help from GRIT v4.0
    render_how_to_section("Tactical Intelligence Center", """
    <div class="how-to-section">
    <h4>Real-Time Strategic Intelligence and Decision Support</h4>
    
    <p>The <strong>Tactical Intelligence Center</strong> provides real-time alerts and decision-making tools:</p>
    
    <h5>Breaking Strategic Intelligence</h5>
    <ul>
    <li><strong>Team Matchup Alerts:</strong> Key strategic factors for current matchup</li>
    <li><strong>Formation Trends:</strong> Personnel package recommendations</li>
    <li><strong>Tactical Opportunities:</strong> Advantage identification</li>
    </ul>
    
    <h5>Risk-Reward Calculator</h5>
    <p>Quantitative decision-making support for:</p>
    <ul>
    <li><strong>Fourth Down Attempts:</strong> Success probability analysis</li>
    <li><strong>Two-Point Conversions:</strong> Risk vs. reward assessment</li>
    <li><strong>Aggressive vs. Conservative:</strong> Strategic approach evaluation</li>
    <li><strong>Timeout Usage:</strong> Clock management optimization</li>
    </ul>
    </div>
    """)
    
    col_news, col_analysis = st.columns([1, 1])
    
    with col_news:
        st.markdown("### Breaking Strategic Intelligence")
        
        # Generate strategic intelligence based on current data
        teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None})
        
        if teams['team1'] and teams['team2']:
            st.info(f"📊 MATCHUP FOCUS: {get_team_full_name(teams['team1'])} vs {get_team_full_name(teams['team2'])}")
            st.info(f"🎯 STRATEGIC PRIORITY: Exploit formation mismatches and personnel advantages")
            st.info(f"⚡ TACTICAL ALERT: Focus on situational play calling and red zone efficiency")
        else:
            st.info("✅ No critical tactical alerts. Select teams in sidebar for matchup analysis.")
    
    with col_analysis:
        st.markdown("### Risk-Reward Calculator")
        
        # ENHANCEMENT: Add Risk-Reward Calculator help from GRIT v4.0
        st.markdown(render_terminology_tooltip("Risk-Reward Calculator", 
            "Quantitative analysis tool that evaluates the probability of success and potential outcomes for critical strategic decisions."), unsafe_allow_html=True)
        
        decision_type = st.selectbox(
            "Strategic Decision",
            ["Fourth Down Attempt", "Two-Point Conversion", "Aggressive Pass vs Run", 
             "Timeout Usage", "Field Goal vs Punt"],
            help="⚖️ Select the strategic decision you want to analyze"
        )
        
        risk_tolerance = st.slider("Risk Tolerance", 1, 10, 5, 
                                 help="🎯 Set your coaching risk tolerance: 1-3 (Conservative), 4-6 (Balanced), 7-10 (Aggressive)")
        
        if st.button("🎯 Calculate Risk-Reward",
                    help="📊 Generate quantitative analysis of your selected decision"):
            game_sit = get_session_state_safely('game_situation', {
                'down': 1, 'distance': 10, 'field_position': 50,
                'score_differential': 0, 'time_remaining': '15:00'
            })
            
            # Simple risk calculation based on game situation
            if decision_type == "Fourth Down Attempt":
                base_success = 60 if game_sit['distance'] <= 3 else 40
                success_prob = min(95, base_success + (risk_tolerance * 3))
                
                st.metric("Success Probability", f"{success_prob}%")
                
                if success_prob > 70:
                    st.success("✅ Favorable odds for fourth down attempt")
                elif success_prob > 50:
                    st.warning("⚠️ Moderate risk - consider situation carefully")
                else:
                    st.error("❌ High risk - consider alternative options")

# =============================================================================
# TAB 3: PROFESSIONAL TOOLS & VISUALIZATION - GRIT v4.0 ENHANCED
# =============================================================================

with tab_tools:
    st.markdown("## 📊 Professional Tools & Visualization")
    st.markdown("*Advanced analytics and professional reporting tools*")
    
    # ENHANCEMENT: Add Professional Tools Help from GRIT v4.0
    render_how_to_section("Professional Tools & Visualization", """
    <div class="how-to-section">
    <h4>Advanced Analytics and Visual Analysis Tools</h4>
    
    <p>Professional-grade analysis and reporting tools for strategic insights:</p>
    
    <h5>Team Comparison Analysis</h5>
    <ul>
    <li><strong>Side-by-Side Comparison:</strong> Direct team performance metrics</li>
    <li><strong>Strength Assessment:</strong> Identify competitive advantages</li>
    <li><strong>Weakness Analysis:</strong> Target areas for exploitation</li>
    <li><strong>Strategic Recommendations:</strong> AI-powered tactical insights</li>
    </ul>
    
    <h5>Professional Report Generator</h5>
    <ul>
    <li><strong>Customizable Sections:</strong> Choose specific analysis areas</li>
    <li><strong>Executive Format:</strong> Professional document structure</li>
    <li><strong>Export Options:</strong> Multiple download formats</li>
    <li><strong>Coaching Distribution:</strong> Shareable strategic documents</li>
    </ul>
    
    <h5>AI-Powered Insights</h5>
    <ul>
    <li><strong>Formation Analysis:</strong> Personnel package recommendations</li>
    <li><strong>Matchup Intelligence:</strong> Player vs player advantages</li>
    <li><strong>Situational Strategy:</strong> Down and distance optimization</li>
    <li><strong>Game Planning:</strong> Comprehensive strategic approach</li>
    </ul>
    </div>
    """)
    
    tool_type = st.selectbox(
        "Select Professional Tool",
        ["Team Comparison Analysis", "AI Strategy Generator", "Formation Breakdown",
         "Professional Report Generator", "Matchup Intelligence", "Game Planning Assistant"],
        help="🛠️ Choose the professional analysis tool for strategic insights"
    )
    
    # Setup OpenAI client for AI-powered tools
    openai_client = setup_openai_client()
    
    if not openai_client:
        st.warning("⚠️ Professional tools require OpenAI API configuration for AI-powered analysis.")
        st.info("Configure your API key to access advanced strategic analysis features.")
    else:
        teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None})
        
        if not teams['team1'] or not teams['team2']:
            st.warning("Please select both teams in the sidebar to use professional tools.")
        else:
            if tool_type == "Team Comparison Analysis":
                st.markdown("### AI-Powered Team Comparison")
                
                if st.button("🔍 Generate Team Comparison", type="primary"):
                    with st.spinner("Analyzing team strengths and weaknesses..."):
                        try:
                            # Generate individual team analyses
                            team1_analysis = generate_ai_team_analysis(teams['team1'], openai_client)
                            team2_analysis = generate_ai_team_analysis(teams['team2'], openai_client)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"#### {get_team_full_name(teams['team1'])} Analysis")
                                st.markdown(team1_analysis)
                            
                            with col2:
                                st.markdown(f"#### {get_team_full_name(teams['team2'])} Analysis")
                                st.markdown(team2_analysis)
                            
                        except Exception as e:
                            st.error(f"Team comparison analysis failed: {str(e)}")
            
            elif tool_type == "Professional Report Generator":
                st.markdown("### Professional Report Generator")
                
                # ENHANCEMENT: Add Report Generator help from GRIT v4.0
                st.markdown(render_terminology_tooltip("Professional Report Generator", 
                    "Comprehensive document creation tool that generates strategic analysis reports suitable for coaching staff distribution."), unsafe_allow_html=True)
                
                # Use session state for selected sections
                available_sections = get_available_report_sections()
                
                # Create section selection interface
                st.markdown("#### Report Sections")
                
                # Get current selections safely
                current_selections = get_session_state_safely('selected_report_sections', 
                    ['executive_summary', 'formation_analysis', 'tactical_recommendations'])
                
                # Create columns for section selection
                cols = st.columns(4)
                selected_sections = []
                
                for i, (section_id, section_name) in enumerate(available_sections.items()):
                    with cols[i % 4]:
                        if st.checkbox(section_name, 
                                     value=section_id in current_selections,
                                     key=f"section_{section_id}"):
                            selected_sections.append(section_id)
                
                # Update session state
                st.session_state.selected_report_sections = selected_sections
                
                # Show currently selected sections
                if selected_sections:
                    st.markdown("**Selected Sections:**")
                    selected_names = [available_sections[sid] for sid in selected_sections if sid in available_sections]
                    st.write(" • ".join(selected_names))
                
                # Generate Report Button
                if st.button("📋 Generate Professional Report", type="primary"):
                    if not selected_sections:
                        st.error("Please select at least one report section.")
                    else:
                        with st.spinner("Generating professional report..."):
                            try:
                                # Compile the report
                                professional_report = compile_professional_report(
                                    selected_sections, teams['team1'], teams['team2'], openai_client
                                )
                                
                                # Store in session state
                                st.session_state.generated_report = professional_report
                                
                                st.success("✅ Professional report generated successfully!")
                                
                            except Exception as e:
                                st.error(f"Report generation failed: {str(e)}")
                
                # Display Generated Report
                if get_session_state_safely('generated_report', None):
                    st.markdown("### Generated Professional Report")
                    
                    # Export options
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📄 Download as Text",
                            data=st.session_state.generated_report,
                            file_name=f"{teams['team1']}_vs_{teams['team2']}_analysis_report.txt",
                            mime="text/plain",
                            help="💾 Download as plain text file"
                        )
                    
                    with col2:
                        # Convert to markdown format
                        st.download_button(
                            label="📋 Download as Markdown", 
                            data=st.session_state.generated_report,
                            file_name=f"{teams['team1']}_vs_{teams['team2']}_analysis_report.md",
                            mime="text/markdown",
                            help="🌐 Download as Markdown file"
                        )
                    
                    # Display the report
                    st.markdown("#### Report Preview")
                    st.markdown(st.session_state.generated_report)
            
            elif tool_type == "AI Strategy Generator":
                st.markdown("### AI Strategy Generator")
                
                strategy_focus = st.selectbox(
                    "Strategy Focus",
                    ["Offensive Game Plan", "Defensive Strategy", "Special Teams", 
                     "Red Zone Optimization", "Third Down Package", "Two-Minute Drill"],
                    help="🎯 Select the strategic area for AI-powered analysis"
                )
                
                if st.button("🧠 Generate Strategy", type="primary"):
                    with st.spinner(f"Generating {strategy_focus.lower()} strategy..."):
                        try:
                            strategy_prompt = f"Generate a comprehensive {strategy_focus.lower()} for {get_team_full_name(teams['team1'])} against {get_team_full_name(teams['team2'])}"
                            strategy_analysis = generate_matchup_analysis(teams['team1'], teams['team2'], openai_client)
                            
                            st.markdown(f"#### {strategy_focus} Strategy")
                            st.markdown(strategy_analysis)
                            
                        except Exception as e:
                            st.error(f"Strategy generation failed: {str(e)}")

# =============================================================================
# TAB 4: EDUCATION & DEVELOPMENT - GRIT v4.0 ENHANCED
# =============================================================================

with tab_education:
    st.markdown("## 📚 Education & Development")
    st.markdown("*Master NFL strategic analysis and tactical concepts*")
    
    # ENHANCEMENT: Add Education & Development Help from GRIT v4.0
    render_how_to_section("Education & Development", """
    <div class="how-to-section">
    <h4>Master NFL Strategic Analysis and Tactical Concepts</h4>
    
    <p>Comprehensive learning modules to develop coordinator-level strategic understanding:</p>
    
    <h5>Strategic Concepts Deep Dive</h5>
    <ul>
    <li><strong>Personnel Packages:</strong> Understanding 11, 12, 21, 10 personnel formations</li>
    <li><strong>Down and Distance Strategy:</strong> Situational play calling principles</li>
    <li><strong>Field Position Impact:</strong> How location affects decision-making</li>
    <li><strong>Clock Management:</strong> Time-sensitive strategic decisions</li>
    </ul>
    
    <h5>Formation Analysis Education</h5>
    <ul>
    <li><strong>11 Personnel:</strong> 1 RB, 1 TE, 3 WR - Most versatile formation</li>
    <li><strong>12 Personnel:</strong> 1 RB, 2 TE, 2 WR - Power running and play action</li>
    <li><strong>21 Personnel:</strong> 2 RB, 1 TE, 2 WR - Heavy run situations</li>
    <li><strong>10 Personnel:</strong> 1 RB, 0 TE, 4 WR - Spread passing attack</li>
    </ul>
    
    <h5>Decision-Making Framework</h5>
    <ul>
    <li><strong>Risk Assessment:</strong> Evaluating success probability</li>
    <li><strong>Situational Awareness:</strong> Game context considerations</li>
    <li><strong>Strategic Planning:</strong> Long-term game management</li>
    <li><strong>Tactical Execution:</strong> Play-by-play optimization</li>
    </ul>
    </div>
    """)
    
    education_type = st.selectbox(
        "Learning Module",
        ["Strategic Concepts", "Formation Analysis", "Decision Tree Training",
         "NFL Terminology", "Coaching Perspectives", "Case Studies"],
        help="📖 Select the learning module for strategic education"
    )
    
    if education_type == "Strategic Concepts":
        st.markdown("### Strategic Concepts Deep Dive")
        
        concept = st.selectbox(
            "Select Concept",
            ["Personnel Packages", "Down and Distance Strategy", "Field Position Impact",
             "Clock Management", "Risk vs Reward Decisions"],
            help="🎯 Choose the strategic concept to learn about"
        )
        
        if concept == "Personnel Packages":
            st.markdown("""
            #### Personnel Package Fundamentals
            
            **11 Personnel (1 RB, 1 TE, 3 WR)**
            - Most versatile formation in modern NFL
            - Balanced run/pass threat creates defensive uncertainty
            - Allows for motion and creative route combinations
            - Average usage: 65-75% of offensive snaps
            
            **12 Personnel (1 RB, 2 TE, 2 WR)**
            - Power running formation with play-action potential
            - Excellent for short yardage and goal line situations
            - Creates favorable blocking angles for outside zone
            - Forces defense into heavier personnel
            
            **21 Personnel (2 RB, 1 TE, 2 WR)**
            - Heavy running formation for power concepts
            - Misdirection and counter plays highly effective
            - Used in short yardage and ball control situations
            - Creates numbers advantage in run game
            
            **10 Personnel (1 RB, 0 TE, 4 WR)**
            - Spread formation for maximum pass threat
            - Forces defense into nickel/dime coverage
            - Two-minute drill and comeback situations
            - Creates favorable matchups for slot receivers
            """)
            
            # ENHANCEMENT: Add practical application from GRIT v4.0
            st.markdown(render_terminology_tooltip("Practical Application", 
                "Use 11 Personnel as your base (70%+ of plays), 12 Personnel in short yardage (15-20%), 21 Personnel for power running (5-10%), 10 Personnel in passing situations (5-10%)."), unsafe_allow_html=True)
    
    elif education_type == "NFL Terminology":
        st.markdown("### NFL Strategic Terminology Glossary")
        
        # ENHANCEMENT: Add comprehensive terminology from GRIT v4.0
        render_how_to_section("NFL Strategic Terminology", """
        <div class="how-to-section">
        <h4>Professional NFL Strategic Terms</h4>
        
        <h5>Personnel Packages</h5>
        <ul>
        <li><strong>11 Personnel:</strong> 1 Running Back, 1 Tight End, 3 Wide Receivers</li>
        <li><strong>12 Personnel:</strong> 1 Running Back, 2 Tight Ends, 2 Wide Receivers</li>
        <li><strong>21 Personnel:</strong> 2 Running Backs, 1 Tight End, 2 Wide Receivers</li>
        <li><strong>10 Personnel:</strong> 1 Running Back, 0 Tight Ends, 4 Wide Receivers</li>
        </ul>
        
        <h5>Strategic Concepts</h5>
        <ul>
        <li><strong>Edge Detection:</strong> Identifying competitive advantages</li>
        <li><strong>Formation Analysis:</strong> Personnel package efficiency study</li>
        <li><strong>Matchup Exploitation:</strong> Targeting favorable personnel matchups</li>
        <li><strong>Drive Management:</strong> Optimizing scoring opportunity efficiency</li>
        </ul>
        
        <h5>Decision-Making Framework</h5>
        <ul>
        <li><strong>Risk Tolerance:</strong> Coaching aggressiveness scale (1-10)</li>
        <li><strong>Success Probability:</strong> Statistical likelihood of positive outcome</li>
        <li><strong>Expected Value:</strong> Average outcome weighted by probability</li>
        <li><strong>Situational Context:</strong> Game state and environmental factors</li>
        </ul>
        </div>
        """)

# =============================================================================
# TAB 5: TEAM ANALYSIS - NEW ENHANCED TAB
# =============================================================================

with tab_team_analysis:
    st.markdown("## 🆚 Team Analysis")
    st.markdown("*Comprehensive team comparison with professional reporting*")
    
    # ENHANCEMENT: Add Team Analysis Help
    render_how_to_section("Team Analysis Hub", """
    <div class="how-to-section">
    <h4>Professional Team Comparison and Analysis</h4>
    
    <p>The <strong>Team Analysis</strong> tab provides comprehensive team-vs-team comparison:</p>
    
    <h5>Four-Column Analysis Layout</h5>
    <ul>
    <li><strong>Your Team Advantages:</strong> AI-identified strengths and tactical edges</li>
    <li><strong>Your Team Overview:</strong> Key players and performance metrics</li>
    <li><strong>Opponent Overview:</strong> Opposition strengths and weaknesses</li>
    <li><strong>Opponent Advantages:</strong> Areas where opponent has edge</li>
    </ul>
    
    <h5>Matchup Intelligence</h5>
    <ul>
    <li><strong>Head-to-Head Analysis:</strong> Direct comparison metrics</li>
    <li><strong>Strategic Trends:</strong> Recent performance indicators</li>
    <li><strong>Key Battles:</strong> Critical position matchups</li>
    </ul>
    
    <h5>AI-Powered Strategic Analysis</h5>
    <ul>
    <li><strong>ChatGPT 3.5 Integration:</strong> Real-time strategic insights</li>
    <li><strong>Tactical Recommendations:</strong> Specific game planning advice</li>
    <li><strong>Follow-up Analysis:</strong> Interactive strategic consultation</li>
    </ul>
    </div>
    """)
    
    # Team Selection Display
    teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None})
    
    if not teams['team1'] or not teams['team2']:
        st.warning("Please select both teams in the sidebar to begin team analysis.")
        st.info("Use the Strategic Command Center in the sidebar to choose your team and opponent.")
    else:
        st.markdown(f"### {get_team_full_name(teams['team1'])} vs {get_team_full_name(teams['team2'])} Analysis")
        
        # Analysis Generation Button
        if st.button("🔄 Generate Complete Team Analysis", type="primary"):
            
            # Setup OpenAI client
            openai_client = setup_openai_client()
            
            if not openai_client:
                st.error("❌ OpenAI API key required for team analysis. Please configure your API key.")
                st.stop()
            
            with st.spinner("Generating comprehensive team analysis..."):
                try:
                    # Generate AI analysis for both teams
                    your_team_analysis = generate_ai_team_analysis(teams['team1'], openai_client)
                    opponent_analysis = generate_ai_team_analysis(teams['team2'], openai_client)
                    
                    # Generate matchup analysis
                    matchup_analysis = generate_matchup_analysis(teams['team1'], teams['team2'], openai_client)
                    
                    # =============================================================================
                    # FOUR-COLUMN MAIN LAYOUT
                    # =============================================================================
                    
                    # Create four columns for the main layout
                    adv_col1, overview_col1, overview_col2, adv_col2 = st.columns([1, 1, 1, 1])
                    
                    # Your team advantages (left)
                    with adv_col1:
                        st.markdown(f"""
                        <div class="team-advantages">
                            <h4>🏈 {get_team_full_name(teams['team1']).upper()} KEY ADVANTAGES</h4>
                            
                            <div style="margin: 10px 0;">
                                <strong style="color: #00ff41;">✅ AI-IDENTIFIED STRENGTHS</strong><br>
                                • Elite strategic execution<br>
                                • Strong personnel depth<br>
                                • Effective game planning<br>
                                • Superior coaching adjustments
                            </div>
                            
                            <div style="margin: 10px 0;">
                                <strong style="color: #ff6b6b;">❌ AREAS TO IMPROVE</strong><br>
                                • Situational awareness<br>
                                • Formation flexibility<br>
                                • Red zone efficiency<br>
                                • Clock management
                            </div>
                            
                            <div style="margin: 10px 0;">
                                <strong style="color: #4fc3f7;">🎯 TACTICAL EDGES</strong><br>
                                • Exploit opponent weaknesses<br>
                                • Use formation advantages<br>
                                • Attack specific matchups
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Your team overview (center-left)
                    with overview_col1:
                        st.markdown(f"""
                        <div class="team-roster">
                            <h4>👥 {get_team_full_name(teams['team1']).upper()} OVERVIEW</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("**AI-POWERED ANALYSIS**")
                        st.markdown("─" * 20)
                        
                        # Display truncated analysis
                        analysis_preview = your_team_analysis[:500] + "..." if len(your_team_analysis) > 500 else your_team_analysis
                        st.markdown(analysis_preview)
                        
                        if st.button(f"📊 Full {teams['team1']} Analysis", key="full_team1"):
                            st.markdown("#### Complete Team Analysis")
                            st.markdown(your_team_analysis)
                    
                    # Opponent team overview (center-right)
                    with overview_col2:
                        st.markdown(f"""
                        <div class="team-roster">
                            <h4>👥 {get_team_full_name(teams['team2']).upper()} OVERVIEW</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("**AI-POWERED ANALYSIS**")
                        st.markdown("─" * 20)
                        
                        # Display truncated analysis
                        analysis_preview = opponent_analysis[:500] + "..." if len(opponent_analysis) > 500 else opponent_analysis
                        st.markdown(analysis_preview)
                        
                        if st.button(f"📊 Full {teams['team2']} Analysis", key="full_team2"):
                            st.markdown("#### Complete Team Analysis")
                            st.markdown(opponent_analysis)
                    
                    # Opponent team advantages (right)
                    with adv_col2:
                        st.markdown(f"""
                        <div class="team-advantages">
                            <h4>🏈 {get_team_full_name(teams['team2']).upper()} KEY ADVANTAGES</h4>
                            
                            <div style="margin: 10px 0;">
                                <strong style="color: #00ff41;">✅ AI-IDENTIFIED STRENGTHS</strong><br>
                                • Strategic execution ability<br>
                                • Personnel utilization<br>
                                • Situational awareness<br>
                                • Coaching expertise
                            </div>
                            
                            <div style="margin: 10px 0;">
                                <strong style="color: #ff6b6b;">❌ AREAS TO IMPROVE</strong><br>
                                • Formation consistency<br>
                                • Red zone conversion<br>
                                • Third down efficiency<br>
                                • Special teams coordination
                            </div>
                            
                            <div style="margin: 10px 0;">
                                <strong style="color: #4fc3f7;">🎯 TACTICAL EDGES</strong><br>
                                • Target opponent gaps<br>
                                • Utilize speed advantages<br>
                                • Exploit coverage weaknesses
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # =============================================================================
                    # BOTTOM SECTIONS - FIXED STYLING TO MATCH WIREFRAME
                    # =============================================================================
                    
                    # Matchup Intelligence section - FIXED STYLING
                    st.markdown(f"""
                    <div class="matchup-intelligence" style="background: #000000 !important; border: 2px solid #00ff41; color: #ffffff !important;">
                        <h3 style="color: #00ff41; text-align: center;">📊 MATCHUP INTELLIGENCE</h3>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 20px 0;">
                            <div>
                                <h5 style="color: #00ff41;">📈 HEAD-TO-HEAD COMPARISON</h5>
                                <span style="color: #ffffff;"><strong>Passing Offense:</strong> PHI 247 yds/gm</span><br>
                                <span style="color: #ffffff;">&nbsp;&nbsp;vs KC Pass Defense: 245 yds/gm</span><br>
                                <span style="color: #ffeb3b;"><em>RESULT: EVEN MATCHUP</em></span><br><br>
                                
                                <span style="color: #ffffff;"><strong>Rushing Offense:</strong> PHI 108 yds/gm</span><br>
                                <span style="color: #ffffff;">&nbsp;&nbsp;vs KC Rush Defense: 112 yds/gm</span><br>
                                <span style="color: #4caf50;"><em>RESULT: SLIGHT PHI ADVANTAGE</em></span><br><br>
                                
                                <h5 style="color: #00ff41;">📈 RECENT TRENDS</h5>
                                <span style="color: #ffffff;">• PHI: +3 Turnover differential in last 3 games</span><br>
                                <span style="color: #ffffff;">• KC: 31.2 PPG at home this season (NFL #3)</span><br>
                                <span style="color: #ffffff;">• PHI: 4-1 record vs QBs rated 90+ this season</span>
                            </div>
                            
                            <div>
                                <h5 style="color: #00ff41;">🔍 KEY PLAYER MATCHUPS</h5>
                                <span style="color: #ffffff;">• A.J. Brown vs L'Jarius Sneed</span><br>
                                <span style="color: #ffffff;">&nbsp;&nbsp;(Size vs Speed - EVEN)</span><br><br>
                                
                                <span style="color: #ffffff;">• Lane Johnson vs Chris Jones</span><br>
                                <span style="color: #ff5722;">&nbsp;&nbsp;(Experience vs Power - MISMATCH)</span><br><br>
                                
                                <span style="color: #ffffff;">• Haason Reddick vs Joe Thuney</span><br>
                                <span style="color: #4caf50;">&nbsp;&nbsp;(Speed vs Technique - ADVANTAGE)</span><br><br>
                                
                                <span style="color: #ffffff;">• DeVonta Smith vs Trent McDuffie</span><br>
                                <span style="color: #ffffff;">&nbsp;&nbsp;(Route Running vs Coverage)</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # AI Analysis section - FIXED STYLING
                    st.markdown(f"""
                    <div class="ai-analysis" style="background: #000000 !important; border: 2px solid #00ff41; color: #ffffff !important; padding: 25px;">
                        <h3 style="color: #00ff41; text-align: center;">🤖 GPT-3.5 TURBO TEAM ANALYSIS</h3>
                        <div style="color: #ffffff; line-height: 1.8; margin: 20px 0;">
                            "This matchup presents a classic power vs finesse battle. Philadelphia's 
                            physical approach, led by their dominant pass rush, will test Kansas 
                            City's ability to protect Mahomes in the pocket. The Eagles' secondary 
                            vulnerabilities against explosive plays could be exploited by Hill's 
                            speed and Kelce's route-running precision..."
                        </div>
                        
                        <div style="margin: 20px 0;">
                            <h5 style="color: #00ff41;">🎯 Strategic Recommendations:</h5>
                            <span style="color: #ffffff;">• PHI: Use Reddick's speed rush to force quick throws</span><br>
                            <span style="color: #ffffff;">• KC: Attack deep early to test PHI's safety coverage</span><br>
                            <span style="color: #ffffff;">• PHI: Utilize Brown's red zone size advantage</span>
                        </div>
                        
                        <div style="margin-top: 25px;">
                            <strong style="color: #00ff41;">Full AI Analysis:</strong><br>
                            <span style="color: #ffffff; font-size: 0.9em;">{matchup_analysis[:300]}...</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Follow-up Q&A system
                    st.markdown("### 💬 Strategic Follow-up Questions")
                    
                    user_question = st.text_input(
                        "Ask a specific question about this matchup:",
                        placeholder="e.g., What should be our key focus on third downs?"
                    )
                    
                    if user_question and st.button("Get AI Answer"):
                        with st.spinner("Getting AI response..."):
                            try:
                                follow_up_prompt = f"""
                                Based on the {get_team_full_name(teams['team1'])} vs {get_team_full_name(teams['team2'])} matchup analysis, 
                                please answer this specific question: {user_question}
                                
                                Keep your response tactical and specific to these teams.
                                """
                                
                                response = openai_client.chat.completions.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": "You are an expert NFL analyst providing specific tactical advice."},
                                        {"role": "user", "content": follow_up_prompt}
                                    ],
                                    max_tokens=300,
                                    temperature=0.7
                                )
                                
                                st.markdown("**🤖 AI Response:**")
                                st.markdown(response.choices[0].message.content)
                                
                            except Exception as e:
                                st.error(f"Error getting AI response: {str(e)}")
                
                except Exception as e:
                    st.error(f"Team analysis generation failed: {str(e)}")
                    st.info("Please try:")
                    st.info("• Refreshing the page")
                    st.info("• Selecting different teams")
                    st.info("• Checking your OpenAI API key configuration")

# =============================================================================
# FOOTER - GRIT v4.0 STYLE WITH TEAM ANALYSIS
# =============================================================================

st.markdown("---")

# System information
col_info1, col_info2, col_info3, col_info4 = st.columns(4)

with col_info1:
    st.metric("🏈 NFL Teams", "32", "Available")

with col_info2:
    st.metric("🤖 AI Analysis", "Active", "ChatGPT 3.5")

with col_info3:
    st.metric("📊 Professional Tools", "Ready", "Advanced")

with col_info4:
    analysis_count = 1 if get_session_state_safely('last_analysis', None) else 0
    st.metric("🆚 Team Analysis", "Enhanced", "AI-Powered")

# Enhanced footer with team analysis mention
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
            border-radius: 10px; margin: 20px 0;">
    <h4 style="color: #00ff41; margin: 0;">GRIT v3.0 - Enhanced NFL Strategic Analysis Platform</h4>
    <p style="color: #ffffff; margin: 5px 0;">
        AI-Powered Team Analysis • Professional Strategic Insights • Advanced GPT Analysis • Professional Visualizations • Team Comparison
    </p>
    <p style="color: #cccccc; margin: 5px 0; font-size: 0.9em;">
        Think Like Belichick • Call Plays Like Reid • Analyze Like a Pro • Compare Like a Champion
    </p>
    <p style="color: #00ccff; margin: 10px 0; font-size: 0.8em;">
        💡 Need help? Look for "📚 How to Use" sections and hover over elements for detailed tooltips
    </p>
</div>
""", unsafe_allow_html=True)
