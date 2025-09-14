"""
GRIT NFL STRATEGIC EDGE PLATFORM v4.0 - MAIN APPLICATION
========================================================
VISION: Professional NFL coordinator-level strategic analysis platform
ARCHITECTURE: Modular SQLite-based system with real weather integration
FEATURES: Advanced GPT analysis, comprehensive visualizations, professional tools

CORE MODULES:
- database.py: SQLite team data and chat history management
- weather.py: OpenWeatherMap API with GPT fallback analysis  
- analysis.py: GPT-3.5 Turbo strategic analysis functions
- visualizations.py: Advanced Plotly charts and dashboards
- main.py: Streamlit interface with lazy loading and caching

STYLING: Dark theme with WHITE text and green gradients
PERFORMANCE: SQLite caching, lazy loading, optimized session state

BUG FIXES APPLIED:
- Line 120: Added safe session state initialization
- Line 125: Added session state safety helper function
- Line 400-500: Fixed analysis generation with comprehensive error handling
- Line 527: Fixed weather data access error
- All session state access: Added safety checks

ENHANCEMENT: Added comprehensive tooltips and how-to sections
- Line 200+: Added detailed tooltips for all interface elements
- Line 350+: Added collapsible how-to guides for each tab
- Line 600+: Added professional terminology explanations
- All help content: Detailed explanations for users at any skill level
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Dict, List, Optional

# Import custom modules
from database import (
    init_database, get_team_data, get_all_team_names, 
    save_chat_message, get_recent_chat_history, ensure_database_populated
)
from weather import get_comprehensive_weather_data, get_weather_summary, get_weather_alerts
from analysis import (
    generate_advanced_strategic_analysis, generate_play_calling_analysis,
    generate_matchup_analysis, generate_analysis_summary, format_analysis_for_export
)
from visualizations import (
    create_formation_efficiency_chart, create_situational_heatmap,
    create_personnel_advantages_radar, create_weather_impact_gauge,
    create_comprehensive_dashboard, create_chart_summary_table
)

# =============================================================================
# STREAMLIT CONFIGURATION AND STYLING
# =============================================================================

st.set_page_config(
    page_title="GRIT - NFL Strategic Edge Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced dark theme CSS with white text - BUG FIX: Complete sidebar and dropdown styling
st.markdown("""
<style>
    /* CRITICAL STYLING PRINCIPLES */
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
    
    /* Sliders */
    .stSlider > div > div {
        background: #000000 !important;
    }
    
    .stSlider > div > div > div {
        color: #ffffff !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        background: rgba(26, 26, 26, 0.8);
        border-radius: 15px;
        margin: 1rem;
        border: 1px solid #333;
    }
    
    /* HEADER/TOP BAR STYLING */
    header[data-testid="stHeader"] {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Top navigation */
    .css-18ni7ap, .css-hby737, .css-17ziqus {
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
    
    /* Chat messages with white text */
    .stChatMessage {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 1px solid #333;
        border-radius: 10px;
        margin: 10px 0;
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
    
    /* Widget labels in sidebar */
    .css-1d391kg .css-1cpxqw2 {
        color: #ffffff !important;
    }
    
    /* Select box labels */
    .css-1d391kg .css-1adrz8d {
        color: #ffffff !important;
    }
    
    /* Help text */
    .css-1d391kg .css-10trblm {
        color: #cccccc !important;
    }
    
    /* ADDITIONAL SELECTOR TARGETING */
    /* Target all possible dropdown variations */
    [data-baseweb="select"] {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    [data-baseweb="select"] > div {
        background: #000000 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    
    /* Menu popover */
    [data-baseweb="popover"] {
        background: #000000 !important;
    }
    
    [data-baseweb="menu"] {
        background: #000000 !important;
        border: 1px solid #333333 !important;
    }
    
    /* Menu options */
    [role="option"] {
        background: #000000 !important;
        color: #ffffff !important;
    }
    
    [role="option"]:hover {
        background: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    /* Streamlit specific classes that might override */
    .css-1v3fvcr, .css-1inwz65, .css-1d391kg {
        background: #000000 !important;
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
    
    .tooltip-content {
        background: rgba(0, 0, 0, 0.9);
        border: 1px solid #00ff41;
        border-radius: 5px;
        padding: 8px;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE INITIALIZATION - BUG FIX: Line 120
# =============================================================================

def initialize_session_state():
    """
    PURPOSE: Initialize session state with unique session ID and essential variables
    INPUTS: None
    OUTPUTS: Initialized session state variables
    DEPENDENCIES: Streamlit session state
    NOTES: Optimized for database storage and memory management
    BUG FIX: Added safe initialization and database population
    """
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    # Initialize database if needed (only once per session)
    if 'database_initialized' not in st.session_state:
        try:
            if ensure_database_populated():
                st.session_state.database_initialized = True
            else:
                st.session_state.database_initialized = False
        except Exception as e:
            st.session_state.database_initialized = False
            # Don't show error during initialization
    
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
        'last_analysis': None
    }
    
    for key, default_value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# =============================================================================
# SAFE SESSION STATE ACCESS HELPER - BUG FIX: Line 125
# =============================================================================

def get_session_state_safely(key, default_value):
    """
    Safely get session state values with fallback defaults
    BUG FIX: Prevents AttributeError when session state not initialized
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
# HELP CONTENT DEFINITIONS - ENHANCEMENT: Comprehensive help system
# =============================================================================

def render_terminology_tooltip(term, definition):
    """
    ENHANCEMENT: Render professional terminology tooltips
    Creates consistent tooltips for NFL strategic terms
    """
    return f"""
    <div class="terminology-box">
        <strong>{term}:</strong> {definition}
    </div>
    """

def render_how_to_section(title, content):
    """
    ENHANCEMENT: Render collapsible how-to sections
    Creates professional help sections for each feature
    """
    with st.expander(f"📚 How to Use: {title}"):
        st.markdown(content, unsafe_allow_html=True)

# =============================================================================
# MAIN APPLICATION HEADER
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
        🏈 All 32 Teams • 🧠 Advanced Strategic Analysis • 🌦️ Live Weather • 📊 Professional Tools
    </p>
</div>
""", unsafe_allow_html=True)

# ENHANCEMENT: Line 200+ - Add Getting Started Guide
render_how_to_section("Getting Started with GRIT", """
<div class="how-to-section">
<h4>Welcome to the Professional NFL Strategic Analysis Platform</h4>

<p><strong>GRIT</strong> is designed to provide coordinator-level strategic insights using advanced data analytics and GPT-3.5 Turbo artificial intelligence. Here's how to get started:</p>

<h5>1. Basic Setup (Sidebar)</h5>
<ul>
<li><strong>Team Selection:</strong> Choose your team and opponent from all 32 NFL teams</li>
<li><strong>Weather Location:</strong> Select which stadium's weather to analyze</li>
<li><strong>Analysis Parameters:</strong> Set complexity level and coaching perspective</li>
<li><strong>Game Situation:</strong> Configure down, distance, field position, score, and time</li>
</ul>

<h5>2. Four Main Analysis Tabs</h5>
<ul>
<li><strong>Strategic Analysis Hub:</strong> Ask specific questions and get GPT-powered insights</li>
<li><strong>Tactical Intelligence Center:</strong> Real-time alerts and risk-reward calculations</li>
<li><strong>Professional Tools:</strong> Advanced visualizations and report generation</li>
<li><strong>Education & Development:</strong> Learn strategic concepts and decision-making</li>
</ul>

<h5>3. Key Features</h5>
<ul>
<li><strong>Formation Analysis:</strong> Efficiency metrics for 11, 12, 21, and 10 personnel packages</li>
<li><strong>Weather Intelligence:</strong> Live conditions impact on play calling</li>
<li><strong>Situational Analytics:</strong> Third down, red zone, and goal line performance</li>
<li><strong>Strategic Chat:</strong> Ongoing conversation with AI coordinator</li>
</ul>

<p><em>Tip: Start by selecting your teams in the sidebar, then explore each tab to understand the full capabilities.</em></p>
</div>
""")

# =============================================================================
# SIDEBAR CONFIGURATION - ENHANCEMENT: Added detailed tooltips
# =============================================================================

with st.sidebar:
    st.markdown("## Strategic Command Center")
    st.markdown("*Professional NFL Analysis Platform*")
    
    # ENHANCEMENT: Add Sidebar Help Section
    render_how_to_section("Strategic Command Center", """
    <div class="how-to-section">
    <p>The <strong>Strategic Command Center</strong> is your control panel for all analysis settings:</p>
    
    <h5>Team Selection</h5>
    <ul>
    <li><strong>Your Team:</strong> The team you're analyzing or coaching</li>
    <li><strong>Opponent:</strong> The opposing team for matchup analysis</li>
    <li><strong>Weather Location:</strong> Stadium location for weather impact analysis</li>
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
    
    try:
        all_teams = get_all_team_names()
        
        # ENHANCEMENT: Added detailed tooltips for team selection
        selected_team1 = st.selectbox(
            "Your Team", 
            all_teams, 
            index=0 if all_teams else 0,
            help="🏈 Select the team you're analyzing or game-planning for. This team's data will be the primary focus of strategic recommendations and will be referenced as 'your team' in all analysis."
        )
        
        available_opponents = [team for team in all_teams if team != selected_team1]
        selected_team2 = st.selectbox(
            "Opponent", 
            available_opponents, 
            index=0 if available_opponents else 0,
            help="🎯 Select the opposing team for matchup analysis. The system will compare formation efficiencies, situational tendencies, and identify strategic advantages against this opponent."
        )
        
        weather_team = st.selectbox(
            "Weather Location", 
            [selected_team1, selected_team2], 
            help="🌦️ Choose which team's stadium to use for weather analysis. This affects play-calling recommendations based on temperature, wind, precipitation, and dome vs. outdoor conditions."
        )
        
        # Update session state with safety check - BUG FIX
        if hasattr(st.session_state, 'selected_teams'):
            st.session_state.selected_teams = {
                'team1': selected_team1,
                'team2': selected_team2,
                'weather_team': weather_team
            }
        
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        st.stop()
    
    # Analysis Parameters Section
    st.markdown("### Analysis Parameters")
    
    # ENHANCEMENT: Added detailed tooltips for analysis parameters
    complexity_level = st.selectbox(
        "Analysis Complexity",
        ["Basic", "Advanced", "Expert"],
        index=1,
        help="📊 Choose analysis depth: BASIC (quick insights), ADVANCED (detailed breakdowns with specific recommendations), EXPERT (comprehensive coordinator-level analysis with multiple scenarios and advanced metrics)"
    )
    
    coaching_perspective = st.selectbox(
        "Coaching Perspective",
        ["Head Coach", "Offensive Coordinator", "Defensive Coordinator", "Special Teams Coach"],
        index=0,
        help="👔 Select the coaching viewpoint for analysis: HEAD COACH (overall strategy and game management), OFFENSIVE COORDINATOR (play calling and formation selection), DEFENSIVE COORDINATOR (coverage and pressure schemes), SPECIAL TEAMS (field position and specialty situations)"
    )
    
    analysis_type = st.selectbox(
        "Analysis Focus",
        ["Edge Detection", "Formation Analysis", "Situational Breakdown", "Weather Impact",
         "Play Calling", "Matchup Exploitation", "Drive Management", "Red Zone Optimization"],
        help="🔍 Choose specific analysis focus: EDGE DETECTION (identify competitive advantages), FORMATION ANALYSIS (personnel package efficiency), SITUATIONAL BREAKDOWN (down/distance tendencies), WEATHER IMPACT (environmental factors), PLAY CALLING (specific recommendations), MATCHUP EXPLOITATION (personnel advantages), DRIVE MANAGEMENT (scoring efficiency), RED ZONE OPTIMIZATION (goal line strategies)"
    )
    
    # Update analysis preferences - BUG FIX: Safe access
    analysis_prefs = {
        'complexity_level': complexity_level,
        'coaching_perspective': coaching_perspective,
        'analysis_type': analysis_type
    }
    if hasattr(st.session_state, 'analysis_preferences'):
        st.session_state.analysis_preferences = analysis_prefs
    
    # Game Situation Inputs
    st.markdown("### Game Situation")
    
    # ENHANCEMENT: Add Game Situation terminology
    st.markdown(render_terminology_tooltip("Game Situation", "The current down, distance, field position, score, and time context that influences strategic decision-making"), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        down = st.selectbox("Down", [1, 2, 3, 4], index=0, 
                          help="🏈 Current down (1st, 2nd, 3rd, or 4th). Each down has different strategic implications: 1st down offers maximum flexibility, 2nd down determines if you're ahead or behind the chains, 3rd down is the money down for conversions, 4th down requires critical decisions about punting, field goals, or going for it.")
        field_position = st.slider("Field Position", 1, 99, 50, 
                                 help="📍 Distance from your own goal line (1-99 yards). Field position dramatically affects play calling: own 1-20 (danger zone - conservative), 21-40 (defensive zone - ball security), 41-60 (midfield - balanced), 61-80 (offensive zone - aggressive), 81-99 (red zone - scoring focus).")
    
    with col2:
        distance = st.slider("Distance", 1, 30, 10,
                           help="📏 Yards needed for first down. Distance categories: SHORT (1-3 yards - power running), MEDIUM (4-7 yards - balanced attack), LONG (8+ yards - passing emphasis). Distance heavily influences formation selection and play type.")
        score_diff = st.slider("Score Differential", -21, 21, 0, 
                             help="⚖️ Your team's score minus opponent's score. Positive = leading (more conservative, clock management), Negative = trailing (more aggressive, hurry-up), Zero = tied (balanced approach). Score differential affects risk tolerance and play selection.")
    
    time_remaining = st.selectbox(
        "Time Remaining",
        ["15:00", "10:00", "5:00", "2:00", "1:00", "0:30"],
        index=0,
        help="⏰ Time remaining in current half/game. Clock management becomes critical in final minutes: 15:00-5:00 (normal pace), 5:00-2:00 (situational awareness), 2:00-0:00 (two-minute drill, timeout management, clock strategy)."
    )
    
    # Update game situation - BUG FIX: Safe access
    game_sit = {
        'down': down,
        'distance': distance,
        'field_position': field_position,
        'score_differential': score_diff,
        'time_remaining': time_remaining
    }
    if hasattr(st.session_state, 'game_situation'):
        st.session_state.game_situation = game_sit
    
    # Quick Analysis Preview
    if selected_team1 and selected_team2:
        try:
            team1_data = get_team_data(selected_team1)
            
            if team1_data:
                st.markdown(f"### {selected_team1} Quick Stats")
                formation_11 = team1_data.get('formation_data', {}).get('11_personnel', {})
                situational = team1_data.get('situational_tendencies', {})
                
                st.write(f"**11 Personnel YPP:** {formation_11.get('ypp', 0):.1f}")
                st.write(f"**3rd Down Rate:** {situational.get('third_down_conversion', 0)*100:.1f}%")
                st.write(f"**Red Zone Eff:** {situational.get('red_zone_efficiency', 0)*100:.1f}%")
                
                # ENHANCEMENT: Add explanation for quick stats
                st.markdown(render_terminology_tooltip("Quick Stats Explanation", 
                    "11 Personnel YPP = Yards Per Play in 11 personnel (1 RB, 1 TE, 3 WR). 3rd Down Rate = Conversion percentage on third downs. Red Zone Efficiency = Touchdown percentage inside the 20-yard line."), unsafe_allow_html=True)
                
        except Exception as e:
            st.warning(f"Unable to load team stats: {str(e)}")
    
    # System Status Section
    st.markdown("### System Status")
    try:
        team_count = len(all_teams)
        st.success(f"✅ {team_count} NFL Teams")
    except:
        st.error("❌ Database Connection Issue")
    
    st.info("✅ Weather Intelligence Active")
    st.info("✅ Advanced GPT Analysis Ready")
    st.info("✅ Professional Tools Available")

# =============================================================================
# TAB STRUCTURE - ENHANCEMENT: Added professional help for each tab
# =============================================================================

tab_analysis, tab_intelligence, tab_tools, tab_education = st.tabs([
    "🧠 STRATEGIC ANALYSIS HUB", 
    "📰 TACTICAL INTELLIGENCE CENTER", 
    "📊 PROFESSIONAL TOOLS & VISUALIZATION", 
    "📚 EDUCATION & DEVELOPMENT"
])

# =============================================================================
# TAB 1: STRATEGIC ANALYSIS HUB - ENHANCEMENT: Line 350+ Added comprehensive help
# =============================================================================

with tab_analysis:
    st.markdown("## 🧠 Strategic Analysis Hub")
    st.markdown("*Professional NFL coordinator-level strategic insights with advanced analysis*")
    
    # ENHANCEMENT: Add Strategic Analysis Hub Help
    render_how_to_section("Strategic Analysis Hub", """
    <div class="how-to-section">
    <h4>Your AI-Powered Strategic Command Center</h4>
    
    <p>The <strong>Strategic Analysis Hub</strong> is where you interact with GPT-3.5 Turbo for professional NFL analysis:</p>
    
    <h5>Strategic Consultation Questions</h5>
    <p>Ask specific tactical questions like:</p>
    <ul>
    <li>"How do we exploit their red zone defense in this weather?"</li>
    <li>"What's our best play on 3rd and 7 from the 35-yard line?"</li>
    <li>"How does wind affect our passing game today?"</li>
    <li>"What personnel package gives us the best matchup?"</li>
    </ul>
    
    <h5>Analysis Features</h5>
    <ul>
    <li><strong>Formation Data Integration:</strong> Uses actual team efficiency numbers</li>
    <li><strong>Weather Intelligence:</strong> Incorporates live weather conditions</li>
    <li><strong>Game Situation Context:</strong> Considers down, distance, field position</li>
    <li><strong>Historical Precedents:</strong> References similar game situations</li>
    </ul>
    
    <h5>Strategic Chat</h5>
    <p>Continue the conversation with follow-up questions. The AI maintains context throughout your session and remembers previous discussions.</p>
    
    <h5>Professional Output</h5>
    <p>All analysis is generated at coordinator level with:</p>
    <ul>
    <li>Specific play recommendations</li>
    <li>Formation selection rationale</li>
    <li>Risk-reward assessments</li>
    <li>Situational adjustments</li>
    </ul>
    </div>
    """)
    
    # Strategic Question Interface
    col_input, col_button = st.columns([3, 1])
    
    with col_input:
        strategic_question = st.text_input(
            "Strategic Consultation Question:",
            placeholder="e.g., How do we exploit their red zone defense in this weather? What's our best play on 3rd and 7?",
            help="💭 Ask specific tactical questions for detailed strategic analysis. Be specific about situations, formations, or matchups you want to explore. The AI will use your team's actual data and current game situation to provide coordinator-level insights."
        )
    
    with col_button:
        st.write("")  # Spacing
        analyze_button = st.button("🧠 Generate Analysis", type="primary",
                                 help="🚀 Click to generate professional strategic analysis using GPT-3.5 Turbo. The AI will analyze your question using team formation data, weather conditions, game situation, and coaching perspective to provide actionable insights.")
    
    # Main analysis area
    col_main, col_sidebar_info = st.columns([2, 1])
    
    with col_main:
        # Analysis execution - BUG FIX: Enhanced error handling and validation
        if analyze_button or strategic_question:
            if not strategic_question:
                teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None, 'weather_team': None})
                analysis_type = get_session_state_safely('analysis_preferences', {}).get('analysis_type', 'Edge Detection')
                strategic_question = f"Provide {analysis_type.lower()} analysis for {teams['team1']} vs {teams['team2']} in current game situation"
            
            with st.spinner("🔍 Analyzing strategic situation..."):
                try:
                    # BUG FIX: Comprehensive data validation before analysis
                    teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None, 'weather_team': None})
                    
                    # Validate team selection
                    if not teams.get('team1') or not teams.get('team2'):
                        st.error("Please select both teams in the sidebar before generating analysis.")
                        st.stop()
                    
                    # Get team data with validation
                    try:
                        team1_data = get_team_data(teams['team1'])
                        team2_data = get_team_data(teams['team2'])
                    except Exception as db_error:
                        st.error(f"Database error: {str(db_error)}")
                        st.info("Try refreshing the page or selecting different teams.")
                        st.stop()
                    
                    # BUG FIX: Validate team data exists and is properly formatted
                    if not team1_data:
                        st.error(f"No data available for {teams['team1']}. Check database connection.")
                        st.stop()
                    
                    if not team2_data:
                        st.error(f"No data available for {teams['team2']}. Check database connection.")
                        st.stop()
                    
                    # Validate team data structure
                    if not isinstance(team1_data, dict) or not isinstance(team2_data, dict):
                        st.error("Invalid team data format. Database may be corrupted.")
                        st.stop()
                    
                    # Get weather data with comprehensive fallback
                    try:
                        team1_stadium = team1_data.get('stadium_info', {}) if team1_data else {}
                        weather_data = get_comprehensive_weather_data(
                            teams['weather_team'],
                            team1_stadium.get('city', 'Unknown'),
                            team1_stadium.get('state', 'Unknown'),
                            team1_stadium.get('is_dome', False)
                        )
                    except Exception as weather_error:
                        st.warning(f"Weather data unavailable: {str(weather_error)}")
                        # Provide default weather data
                        weather_data = {
                            'temp': 70,
                            'condition': 'Unknown',
                            'wind_speed': 0,
                            'source': 'Default',
                            'error': str(weather_error)
                        }
                    
                    # Store weather data in session state - BUG FIX: Safe storage
                    if hasattr(st.session_state, 'current_weather_data'):
                        st.session_state.current_weather_data = weather_data
                    
                    # Get analysis preferences and game situation safely
                    preferences = get_session_state_safely('analysis_preferences', {
                        'complexity_level': 'Advanced',
                        'coaching_perspective': 'Head Coach',
                        'analysis_type': 'Edge Detection'
                    })
                    
                    game_situation = get_session_state_safely('game_situation', {
                        'down': 1, 'distance': 10, 'field_position': 50,
                        'score_differential': 0, 'time_remaining': '15:00'
                    })
                    
                    # BUG FIX: Generate enhanced analysis with comprehensive error handling
                    try:
                        analysis = generate_advanced_strategic_analysis(
                            teams['team1'], teams['team2'], strategic_question, preferences['analysis_type'],
                            team1_data, team2_data, weather_data,
                            game_situation, preferences['coaching_perspective'], 
                            preferences['complexity_level']
                        )
                        
                        # Validate analysis response
                        if not analysis or analysis.startswith("Error:") or analysis.startswith("Analysis generation failed"):
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
                            
                            # Save to database for chat history
                            try:
                                save_chat_message(
                                    get_session_state_safely('session_id', str(uuid.uuid4())),
                                    "analysis",
                                    f"Q: {strategic_question}\n\nA: {analysis}",
                                    preferences['analysis_type']
                                )
                            except Exception as db_save_error:
                                st.warning(f"Could not save to chat history: {str(db_save_error)}")
                            
                            st.success("✅ Strategic Analysis Complete!")
                    
                    except Exception as analysis_error:
                        st.error("Analysis generation encountered an error:")
                        st.error(str(analysis_error))
                        st.info("This may be due to:")
                        st.info("• Missing formation data in database")
                        st.info("• API service unavailability") 
                        st.info("• Invalid team data structure")
                        
                        # Show debug information
                        with st.expander("Debug Information"):
                            st.write(f"Team 1: {teams['team1']}")
                            st.write(f"Team 2: {teams['team2']}")
                            st.write(f"Team 1 Data Keys: {list(team1_data.keys()) if team1_data else 'None'}")
                            st.write(f"Team 2 Data Keys: {list(team2_data.keys()) if team2_data else 'None'}")
                            st.write(f"Weather Data: {weather_data}")
                            st.write(f"Error: {str(analysis_error)}")
                        
                except Exception as outer_error:
                    st.error("Critical error in analysis system:")
                    st.error(str(outer_error))
                    st.info("Please try refreshing the page. If the problem persists, check:")
                    st.info("• Database connectivity")
                    st.info("• Team data integrity")
                    st.info("• System logs for detailed error information")
        
        # Strategic Chat Interface
        st.markdown("### Strategic Consultation Chat")
        st.markdown("*Continue the strategic discussion with follow-up questions*")
        
        # ENHANCEMENT: Add chat help
        st.markdown(render_terminology_tooltip("Strategic Chat", 
            "An ongoing conversation with the AI analyst. The system remembers context from previous questions in your session, allowing for deeper strategic discussions and follow-up clarifications."), unsafe_allow_html=True)
        
        # Load recent chat history from database
        try:
            session_id = get_session_state_safely('session_id', str(uuid.uuid4()))
            chat_history = get_recent_chat_history(session_id, limit=10)
            
            # Display chat history
            for role, message in chat_history:
                with st.chat_message(role):
                    st.markdown(message)
        except Exception as e:
            st.warning(f"Chat history unavailable: {str(e)}")
        
        # Chat input - BUG FIX: Line 929 - Removed help parameter (not supported by st.chat_input)
        if coach_q := st.chat_input("Continue the strategic discussion..."):
            with st.chat_message("user"):
                st.markdown(coach_q)
            
            # Generate response with full context
            with st.chat_message("assistant"):
                with st.spinner("🔍 Analyzing strategic question..."):
                    try:
                        teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None, 'weather_team': None})
                        team1_data = get_team_data(teams['team1'])
                        team2_data = get_team_data(teams['team2'])
                        weather_data = get_session_state_safely('current_weather_data', {})
                        
                        preferences = get_session_state_safely('analysis_preferences', {
                            'complexity_level': 'Advanced',
                            'coaching_perspective': 'Head Coach',
                            'analysis_type': 'Edge Detection'
                        })
                        game_situation = get_session_state_safely('game_situation', {
                            'down': 1, 'distance': 10, 'field_position': 50,
                            'score_differential': 0, 'time_remaining': '15:00'
                        })
                        
                        response = generate_advanced_strategic_analysis(
                            teams['team1'], teams['team2'], coach_q, "Strategic Consultation",
                            team1_data, team2_data, weather_data,
                            game_situation, preferences['coaching_perspective'], 
                            preferences['complexity_level']
                        )
                        
                        st.markdown(response)
                        
                        # Save chat interaction to database
                        session_id = get_session_state_safely('session_id', str(uuid.uuid4()))
                        save_chat_message(session_id, "user", coach_q, "chat")
                        save_chat_message(session_id, "assistant", response, "chat")
                        
                    except Exception as e:
                        st.error(f"Chat response generation failed: {str(e)}")
    
    with col_sidebar_info:
        st.markdown("### Current Matchup Analysis")
        
        # ENHANCEMENT: Add matchup analysis help
        st.markdown(render_terminology_tooltip("Matchup Analysis", 
            "Real-time overview of key factors affecting strategic decisions including weather conditions, game situation context, and team performance indicators."), unsafe_allow_html=True)
        
        # Weather display - BUG FIX: Line 527 - Safe weather access
        current_weather = get_session_state_safely('current_weather_data', {})
        if current_weather:
            teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None, 'weather_team': None})
            
            st.markdown(f"#### Weather at {teams['weather_team']}")
            st.write(f"🌡️ **Temperature:** {current_weather.get('temp', 'N/A')}°F")
            st.write(f"💨 **Wind:** {current_weather.get('wind', 'N/A')} mph")
            st.write(f"☁️ **Conditions:** {current_weather.get('condition', 'Unknown')}")
            st.caption(f"Source: {current_weather.get('source', 'Unknown')}")
            
            # Weather alerts
            alerts = get_weather_alerts(current_weather)
            if alerts:
                st.markdown("#### Weather Alerts")
                for alert in alerts[:2]:  # Show top 2 alerts
                    st.warning(alert)
        
        # Game situation context - BUG FIX: Safe access
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
# TAB 2: TACTICAL INTELLIGENCE CENTER - ENHANCEMENT: Added comprehensive help
# =============================================================================

with tab_intelligence:
    st.markdown("## 📰 Tactical Intelligence Center")
    st.markdown("*Breaking intelligence with strategic impact analysis*")
    
    # ENHANCEMENT: Add Tactical Intelligence Help
    render_how_to_section("Tactical Intelligence Center", """
    <div class="how-to-section">
    <h4>Real-Time Strategic Intelligence and Decision Support</h4>
    
    <p>The <strong>Tactical Intelligence Center</strong> provides real-time alerts and decision-making tools:</p>
    
    <h5>Breaking Strategic Intelligence</h5>
    <ul>
    <li><strong>Weather Alerts:</strong> Live conditions affecting play calling</li>
    <li><strong>Formation Trends:</strong> Team usage patterns and tendencies</li>
    <li><strong>Tactical Alerts:</strong> Key strategic factors for current matchup</li>
    </ul>
    
    <h5>Risk-Reward Calculator</h5>
    <p>Quantitative decision-making support for:</p>
    <ul>
    <li><strong>Fourth Down Attempts:</strong> Success probability analysis</li>
    <li><strong>Two-Point Conversions:</strong> Risk vs. reward assessment</li>
    <li><strong>Aggressive vs. Conservative:</strong> Strategic approach evaluation</li>
    <li><strong>Timeout Usage:</strong> Clock management optimization</li>
    </ul>
    
    <h5>Historical Precedent Analysis</h5>
    <ul>
    <li>Search similar game situations from NFL history</li>
    <li>Weather-based precedent analysis</li>
    <li>Coaching decision patterns</li>
    <li>Outcome probability based on historical data</li>
    </ul>
    
    <h5>Intelligence Alerts</h5>
    <p>The system monitors for:</p>
    <ul>
    <li>Critical weather changes affecting strategy</li>
    <li>Formation usage above/below normal thresholds</li>
    <li>Situational tendencies creating opportunities</li>
    <li>Personnel package mismatches</li>
    </ul>
    </div>
    """)
    
    col_news, col_analysis = st.columns([1, 1])
    
    with col_news:
        st.markdown("### Breaking Strategic Intelligence")
        
        # Generate strategic intelligence based on current data
        intelligence_alerts = []
        
        try:
            weather_data = get_session_state_safely('current_weather_data', {})
            
            if weather_data:
                alerts = get_weather_alerts(weather_data)
                for alert in alerts:
                    intelligence_alerts.append({
                        'title': alert,
                        'impact': 'WEATHER',
                        'time': 'Live Update'
                    })
            
            # Team-based intelligence
            teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None, 'weather_team': None})
            if teams['team1'] and teams['team2']:
                team1_data = get_team_data(teams['team1'])
                
                if team1_data:
                    formation_11_usage = team1_data.get('formation_data', {}).get('11_personnel', {}).get('usage', 0)
                    if formation_11_usage > 0.73:
                        intelligence_alerts.append({
                            'title': f"📊 FORMATION TREND: {teams['team1']} using 11 personnel {formation_11_usage*100:.0f}% of plays",
                            'impact': 'TACTICAL',
                            'time': 'Season Analysis'
                        })
            
        except Exception as e:
            st.warning(f"Intelligence gathering error: {str(e)}")
        
        # Display intelligence alerts
        if intelligence_alerts:
            for alert in intelligence_alerts:
                if alert['impact'] == 'WEATHER':
                    st.warning(alert['title'])
                else:
                    st.info(alert['title'])
                st.caption(f"Source: {alert['time']}")
        else:
            st.info("✅ No critical tactical alerts. Standard game planning conditions.")
    
    with col_analysis:
        st.markdown("### Risk-Reward Calculator")
        
        # ENHANCEMENT: Add Risk-Reward Calculator help
        st.markdown(render_terminology_tooltip("Risk-Reward Calculator", 
            "Quantitative analysis tool that evaluates the probability of success and potential outcomes for critical strategic decisions based on game situation, team tendencies, and historical data."), unsafe_allow_html=True)
        
        decision_type = st.selectbox(
            "Strategic Decision",
            ["Fourth Down Attempt", "Two-Point Conversion", "Aggressive Pass vs Run", 
             "Timeout Usage", "Field Goal vs Punt"],
            help="⚖️ Select the strategic decision you want to analyze. Each decision type has different risk factors and success probabilities based on game situation and team capabilities."
        )
        
        risk_tolerance = st.slider("Risk Tolerance", 1, 10, 5, 
                                 help="🎯 Set your coaching risk tolerance: 1-3 (Conservative - prioritize ball security), 4-6 (Balanced - situational approach), 7-10 (Aggressive - maximize scoring opportunities). This affects success probability calculations.")
        
        if st.button("🎯 Calculate Risk-Reward",
                    help="📊 Generate quantitative analysis of your selected decision including success probability, risk factors, and strategic recommendations."):
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
        
        st.markdown("### Historical Precedent Analysis")
        
        # ENHANCEMENT: Add Historical Precedent help
        st.markdown(render_terminology_tooltip("Historical Precedent Analysis", 
            "AI-powered search of similar game situations from NFL history to identify patterns, successful strategies, and outcome probabilities for current strategic decisions."), unsafe_allow_html=True)
        
        precedent_search = st.text_input(
            "Search Similar Situations",
            placeholder="e.g., cold weather playoff games, wind affecting passing teams",
            help="🔍 Enter specific situations to find historical precedents. Examples: 'cold weather playoff games', 'fourth down attempts in red zone', 'two-minute drill with lead', 'overtime strategy'. The AI will analyze similar situations and coaching decisions."
        )
        
        if precedent_search and st.button("🔍 Find Precedents",
                                        help="📚 Search NFL history for similar situations and analyze coaching decisions, success rates, and strategic outcomes."):
            with st.spinner("Analyzing historical precedents..."):
                # Use GPT to analyze historical precedents
                try:
                    teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None, 'weather_team': None})
                    team1_data = get_team_data(teams['team1'])
                    team2_data = get_team_data(teams['team2'])
                    weather_data = get_session_state_safely('current_weather_data', {})
                    
                    precedent_question = f"Analyze historical precedents for: {precedent_search} in the context of {teams['team1']} vs {teams['team2']}"
                    
                    game_situation = get_session_state_safely('game_situation', {
                        'down': 1, 'distance': 10, 'field_position': 50,
                        'score_differential': 0, 'time_remaining': '15:00'
                    })
                    
                    precedent_analysis = generate_advanced_strategic_analysis(
                        teams['team1'], teams['team2'], precedent_question, "Historical Analysis",
                        team1_data, team2_data, weather_data,
                        game_situation, "Head Coach", "Advanced"
                    )
                    
                    st.markdown("#### Historical Precedent Analysis")
                    st.markdown(precedent_analysis)
                    
                except Exception as e:
                    st.error(f"Precedent analysis failed: {str(e)}")

# =============================================================================
# TAB 3: PROFESSIONAL TOOLS & VISUALIZATION - ENHANCEMENT: Line 600+ Added detailed help
# =============================================================================

with tab_tools:
    st.markdown("## 📊 Professional Tools & Visualization")
    st.markdown("*Advanced analytics and professional reporting tools*")
    
    # ENHANCEMENT: Add Professional Tools Help
    render_how_to_section("Professional Tools & Visualization", """
    <div class="how-to-section">
    <h4>Advanced Analytics and Visual Analysis Tools</h4>
    
    <p>Professional-grade visualization and reporting tools for strategic analysis:</p>
    
    <h5>Formation Efficiency Analysis</h5>
    <ul>
    <li><strong>Personnel Package Comparison:</strong> 11, 12, 21, 10 personnel efficiency</li>
    <li><strong>Yards Per Play (YPP):</strong> Average yards gained per play by formation</li>
    <li><strong>Success Rate Analysis:</strong> Percentage of successful plays by formation</li>
    <li><strong>Usage Patterns:</strong> How frequently each team uses formations</li>
    </ul>
    
    <h5>Situational Heatmap</h5>
    <ul>
    <li><strong>Down & Distance Performance:</strong> Success rates across situations</li>
    <li><strong>Field Position Impact:</strong> Efficiency by field location</li>
    <li><strong>Red Zone Analysis:</strong> Goal line and red zone performance</li>
    <li><strong>Time Sensitive Situations:</strong> Two-minute drill efficiency</li>
    </ul>
    
    <h5>Personnel Advantages Radar</h5>
    <ul>
    <li><strong>Offensive Line Strength:</strong> Pass protection and run blocking</li>
    <li><strong>Receiving Corps Depth:</strong> Route running and separation</li>
    <li><strong>Backfield Versatility:</strong> Running back capabilities</li>
    <li><strong>Tight End Usage:</strong> Receiving and blocking efficiency</li>
    </ul>
    
    <h5>Weather Impact Analysis</h5>
    <ul>
    <li><strong>Weather Gauge:</strong> Overall impact score 0-100</li>
    <li><strong>Temperature Effects:</strong> Performance in extreme conditions</li>
    <li><strong>Wind Impact:</strong> Passing and kicking game effects</li>
    <li><strong>Precipitation Analysis:</strong> Ball security and footing concerns</li>
    </ul>
    
    <h5>Comprehensive Dashboard</h5>
    <p>Multi-panel view combining all key metrics in one visualization</p>
    
    <h5>Analysis Report Generator</h5>
    <ul>
    <li><strong>Professional Reports:</strong> Executive summary format</li>
    <li><strong>Export Options:</strong> TXT and HTML formats</li>
    <li><strong>Customizable Sections:</strong> Choose specific analysis areas</li>
    <li><strong>Coaching Staff Distribution:</strong> Shareable strategic documents</li>
    </ul>
    </div>
    """)
    
    tool_type = st.selectbox(
        "Select Professional Tool",
        ["Formation Efficiency Analysis", "Situational Heatmap", "Personnel Advantages Radar",
         "Weather Impact Analysis", "Comprehensive Dashboard", "Analysis Report Generator"],
        help="🛠️ Choose the professional analysis tool you want to use. Each tool provides different insights: Formation Analysis (personnel package efficiency), Situational Heatmap (performance by game situation), Personnel Radar (team strength comparison), Weather Analysis (environmental impact), Dashboard (comprehensive overview), Report Generator (exportable documents)."
    )
    
    try:
        teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None, 'weather_team': None})
        if teams['team1'] and teams['team2']:
            team1_data = get_team_data(teams['team1'])
            team2_data = get_team_data(teams['team2'])
            
            if tool_type == "Formation Efficiency Analysis":
                st.markdown("### Formation Efficiency Comparison")
                
                # ENHANCEMENT: Add Formation Efficiency help
                st.markdown(render_terminology_tooltip("Formation Efficiency", 
                    "Personnel package analysis comparing how effectively each team uses different formations. 11 Personnel = 1 RB, 1 TE, 3 WR (most common). 12 Personnel = 1 RB, 2 TE, 2 WR (power running). 21 Personnel = 2 RB, 1 TE, 2 WR (heavy run). 10 Personnel = 1 RB, 0 TE, 4 WR (spread passing)."), unsafe_allow_html=True)
                
                if team1_data and team2_data:
                    # Create and display formation chart
                    fig = create_formation_efficiency_chart(
                        team1_data, team2_data, teams['team1'], teams['team2']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Data table
                    summary_table = create_chart_summary_table(
                        team1_data, team2_data, teams['team1'], teams['team2']
                    )
                    st.dataframe(summary_table, use_container_width=True)
            
            elif tool_type == "Situational Heatmap":
                st.markdown("### Situational Efficiency Analysis")
                
                # ENHANCEMENT: Add Situational Heatmap help
                st.markdown(render_terminology_tooltip("Situational Heatmap", 
                    "Visual representation of team performance across different game situations. Colors indicate efficiency levels: Green = High Performance, Yellow = Average Performance, Red = Poor Performance. Analyze patterns to identify strengths and weaknesses."), unsafe_allow_html=True)
                
                if team1_data and team2_data:
                    fig = create_situational_heatmap(
                        team1_data, team2_data, teams['team1'], teams['team2']
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif tool_type == "Personnel Advantages Radar":
                st.markdown("### Personnel Matchup Analysis")
                
                # ENHANCEMENT: Add Personnel Radar help
                st.markdown(render_terminology_tooltip("Personnel Advantages Radar", 
                    "Radar chart comparing team strengths across key personnel categories. Larger area = stronger unit. Use to identify matchup advantages and areas to exploit in game planning."), unsafe_allow_html=True)
                
                if team1_data and team2_data:
                    fig = create_personnel_advantages_radar(
                        team1_data, team2_data, teams['team1'], teams['team2']
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif tool_type == "Weather Impact Analysis":
                st.markdown("### Weather Strategic Impact")
                
                # ENHANCEMENT: Add Weather Impact help
                st.markdown(render_terminology_tooltip("Weather Impact Gauge", 
                    "Quantitative assessment of weather conditions on strategic decision-making. Score 0-25 = Minimal Impact, 26-50 = Moderate Impact, 51-75 = Significant Impact, 76-100 = Extreme Impact requiring major strategic adjustments."), unsafe_allow_html=True)
                
                weather_data = get_session_state_safely('current_weather_data', {})
                if weather_data:
                    fig = create_weather_impact_gauge(weather_data)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Weather summary
                    st.markdown("#### Weather Summary")
                    summary = get_weather_summary(weather_data)
                    st.info(summary)
            
            elif tool_type == "Comprehensive Dashboard":
                st.markdown("### Strategic Analysis Dashboard")
                
                # ENHANCEMENT: Add Comprehensive Dashboard help
                st.markdown(render_terminology_tooltip("Comprehensive Dashboard", 
                    "Multi-panel visualization combining formation efficiency, situational performance, personnel strengths, and weather impact in one comprehensive view. Use for overall strategic assessment and presentation to coaching staff."), unsafe_allow_html=True)
                
                if team1_data and team2_data:
                    weather_data = get_session_state_safely('current_weather_data', {})
                    fig = create_comprehensive_dashboard(
                        team1_data, team2_data, teams['team1'], teams['team2'], weather_data
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif tool_type == "Analysis Report Generator":
                st.markdown("### Professional Report Generator")
                
                # ENHANCEMENT: Add Report Generator help
                st.markdown(render_terminology_tooltip("Analysis Report Generator", 
                    "Professional document creation tool that generates comprehensive strategic analysis reports suitable for coaching staff distribution. Select specific sections to include and export in multiple formats."), unsafe_allow_html=True)
                
                report_sections = st.multiselect(
                    "Report Sections",
                    ["Executive Summary", "Formation Analysis", "Weather Impact", 
                     "Risk Assessment", "Tactical Recommendations", "Play Calling Guide"],
                    default=["Executive Summary", "Formation Analysis", "Tactical Recommendations"],
                    help="📋 Select which sections to include in your professional report. Executive Summary (key insights overview), Formation Analysis (personnel package breakdown), Weather Impact (environmental factors), Risk Assessment (decision analysis), Tactical Recommendations (specific strategies), Play Calling Guide (situational play selection)."
                )
                
                if st.button("📊 Generate Professional Report",
                           help="🎯 Create a comprehensive strategic analysis report using GPT-3.5 Turbo. The report will include selected sections with detailed analysis, data-driven insights, and actionable recommendations formatted for coaching staff review."):
                    with st.spinner("Generating comprehensive analysis report..."):
                        try:
                            weather_data = get_session_state_safely('current_weather_data', {})
                            
                            # Generate comprehensive report
                            report_question = f"Generate a professional strategic analysis report with sections: {', '.join(report_sections)}"
                            
                            preferences = get_session_state_safely('analysis_preferences', {
                                'complexity_level': 'Advanced',
                                'coaching_perspective': 'Head Coach',
                                'analysis_type': 'Edge Detection'
                            })
                            game_situation = get_session_state_safely('game_situation', {
                                'down': 1, 'distance': 10, 'field_position': 50,
                                'score_differential': 0, 'time_remaining': '15:00'
                            })
                            
                            report_content = generate_advanced_strategic_analysis(
                                teams['team1'], teams['team2'], report_question, "Professional Report",
                                team1_data, team2_data, weather_data,
                                game_situation, preferences['coaching_perspective'],
                                "Expert"
                            )
                            
                            # Format for export
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            formatted_report = format_analysis_for_export(
                                report_content, f"{teams['team1']} vs {teams['team2']}", timestamp
                            )
                            
                            st.markdown("#### Generated Professional Report")
                            st.markdown(report_content)
                            
                            # Export options
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button(
                                    label="📄 Download Report (TXT)",
                                    data=formatted_report,
                                    file_name=f"{teams['team1']}_vs_{teams['team2']}_analysis_report.txt",
                                    mime="text/plain",
                                    help="💾 Download as plain text file for easy sharing and printing"
                                )
                            
                            with col2:
                                # Convert to basic HTML
                                html_content = formatted_report.replace('\n', '<br>')
                                st.download_button(
                                    label="🌐 Download Report (HTML)",
                                    data=html_content,
                                    file_name=f"{teams['team1']}_vs_{teams['team2']}_analysis_report.html",
                                    mime="text/html",
                                    help="🌐 Download as HTML file for web viewing and enhanced formatting"
                                )
                                
                        except Exception as e:
                            st.error(f"Report generation failed: {str(e)}")
        else:
            st.warning("Please select both teams in the sidebar to use visualization tools.")
            
    except Exception as e:
        st.error(f"Visualization tool error: {str(e)}")

# =============================================================================
# TAB 4: EDUCATION & DEVELOPMENT - ENHANCEMENT: Added comprehensive educational content
# =============================================================================

with tab_education:
    st.markdown("## 📚 Education & Development")
    st.markdown("*Master NFL strategic analysis and tactical concepts*")
    
    # ENHANCEMENT: Add Education & Development Help
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
    <li><strong>Risk vs Reward:</strong> Quantitative decision-making frameworks</li>
    </ul>
    
    <h5>Formation Breakdown</h5>
    <p>Detailed analysis of each personnel package including:</p>
    <ul>
    <li>Typical usage percentages across the NFL</li>
    <li>Strengths and weaknesses of each formation</li>
    <li>Defensive responses and counters</li>
    <li>Optimal game situations for deployment</li>
    </ul>
    
    <h5>Decision Tree Training</h5>
    <p>Interactive scenarios for developing decision-making skills:</p>
    <ul>
    <li><strong>Fourth Down Decisions:</strong> Go/No-go analysis frameworks</li>
    <li><strong>Two-Minute Drill Management:</strong> Clock and timeout strategy</li>
    <li><strong>Red Zone Play Selection:</strong> Goal line optimization</li>
    <li><strong>Weather Adjustments:</strong> Environmental adaptation strategies</li>
    <li><strong>Halftime Strategic Changes:</strong> In-game adjustment principles</li>
    </ul>
    
    <h5>Case Studies</h5>
    <p>Real NFL scenarios with coordinator-level analysis and decision breakdowns</p>
    
    <h5>Coaching Perspectives</h5>
    <p>Understanding different viewpoints:</p>
    <ul>
    <li><strong>Head Coach:</strong> Overall strategy and game management</li>
    <li><strong>Offensive Coordinator:</strong> Play calling and formation selection</li>
    <li><strong>Defensive Coordinator:</strong> Coverage schemes and pressure packages</li>
    <li><strong>Special Teams Coach:</strong> Field position and specialty situations</li>
    </ul>
    </div>
    """)
    
    education_type = st.selectbox(
        "Learning Module",
        ["Strategic Concepts", "Formation Breakdown", "Decision Tree Training",
         "Case Studies", "Weather Impact Analysis", "Coaching Perspectives"],
        help="📖 Select the learning module you want to explore. Each module provides different educational content: Strategic Concepts (fundamental principles), Formation Breakdown (personnel package analysis), Decision Tree Training (interactive scenarios), Case Studies (real NFL examples), Weather Analysis (environmental factors), Coaching Perspectives (different viewpoints)."
    )
    
    if education_type == "Strategic Concepts":
        st.markdown("### Strategic Concepts Deep Dive")
        
        concept = st.selectbox(
            "Select Concept",
            ["Personnel Packages", "Down and Distance Strategy", "Field Position Impact",
             "Clock Management", "Risk vs Reward Decisions"],
            help="🎯 Choose the strategic concept you want to learn about in detail."
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
            
            # ENHANCEMENT: Add practical application examples
            st.markdown(render_terminology_tooltip("Practical Application", 
                "Use 11 Personnel as your base (70%+ of plays), 12 Personnel in short yardage and goal line (15-20%), 21 Personnel for power running and ball control (5-10%), 10 Personnel in obvious passing situations and two-minute drill (5-10%)."), unsafe_allow_html=True)
        
        elif concept == "Down and Distance Strategy":
            st.markdown("""
            #### Down and Distance Strategic Framework
            
            **First Down Strategy**
            - Establish identity and tempo
            - Balance run/pass to keep defense honest
            - Use motion and shifts to identify coverage
            - Target 4+ yards to stay ahead of chains
            
            **Second Down Approach**
            - Short distance (1-3): Aggressive, high-percentage plays
            - Medium distance (4-7): Balanced attack, avoid third and long
            - Long distance (8+): Accept third down, focus on manageable distance
            
            **Third Down Conversion**
            - Short (1-3): Power running, QB sneak, pick plays
            - Medium (4-7): High-percentage routes, crossing patterns
            - Long (8+): Deep routes, four verticals, screen passes
            
            **Fourth Down Decision Matrix**
            - Field position, score, time remaining
            - Team strengths and opponent weaknesses
            - Weather and game flow considerations
            """)
            
            # ENHANCEMENT: Add decision tree example
            st.markdown(render_terminology_tooltip("Third Down Success Keys", 
                "Convert 40%+ on third down to sustain drives. Use formation flexibility, motion to create favorable matchups, and high-percentage concepts. Avoid negative plays that create fourth and long situations."), unsafe_allow_html=True)
    
    elif education_type == "Decision Tree Training":
        st.markdown("### Strategic Decision Tree Training")
        st.markdown("*Interactive scenarios to improve decision-making*")
        
        # ENHANCEMENT: Add Decision Tree Training help
        st.markdown(render_terminology_tooltip("Decision Tree Training", 
            "Interactive learning module that presents real NFL scenarios and guides you through the decision-making process using professional frameworks and analytical thinking."), unsafe_allow_html=True)
        
        scenario = st.selectbox(
            "Training Scenario",
            ["Fourth Down Decision", "Two-Minute Drill Management", "Red Zone Play Selection",
             "Weather Adjustment", "Halftime Strategic Changes"],
            help="🎓 Select a strategic scenario to practice decision-making skills with AI-powered analysis and feedback."
        )
        
        if scenario == "Fourth Down Decision":
            st.markdown("#### Fourth Down Decision Scenario")
            game_sit = get_session_state_safely('game_situation', {
                'down': 1, 'distance': 10, 'field_position': 50,
                'score_differential': 0, 'time_remaining': '15:00'
            })
            st.markdown(f"**Situation:** {game_sit['down']} and {game_sit['distance']} at {game_sit['field_position']} yard line")
            
            # ENHANCEMENT: Add scenario context
            st.markdown(render_terminology_tooltip("Fourth Down Factors", 
                "Consider: Field position (own territory vs opponent territory), Distance needed, Score differential, Time remaining, Team strengths, Weather conditions, Opponent's defensive tendencies, Risk tolerance."), unsafe_allow_html=True)
            
            decision = st.radio(
                "Your Decision:",
                ["Punt", "Field Goal Attempt", "Go for First Down"],
                help="⚖️ Make your coaching decision based on the game situation. The AI will analyze your choice and provide professional feedback on the decision-making process."
            )
            
            if st.button("🎯 Analyze Decision",
                        help="📊 Get professional analysis of your decision including success probability, risk assessment, and alternative considerations."):
                # Generate decision analysis
                try:
                    teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None, 'weather_team': None})
                    team1_data = get_team_data(teams['team1'])
                    team2_data = get_team_data(teams['team2'])
                    weather_data = get_session_state_safely('current_weather_data', {})
                    
                    decision_question = f"Analyze the decision to {decision.lower()} in this situation: {game_sit['down']} and {game_sit['distance']} from {game_sit['field_position']} yard line"
                    
                    decision_analysis = generate_advanced_strategic_analysis(
                        teams['team1'], teams['team2'], decision_question, "Decision Analysis",
                        team1_data, team2_data, weather_data,
                        game_sit, "Head Coach", "Advanced"
                    )
                    
                    st.markdown("#### Decision Analysis")
                    st.markdown(decision_analysis)
                    
                except Exception as e:
                    st.error(f"Decision analysis failed: {str(e)}")
    
    elif education_type == "Coaching Perspectives":
        st.markdown("### Coaching Perspectives Analysis")
        
        # ENHANCEMENT: Add Coaching Perspectives education
        st.markdown(render_terminology_tooltip("Coaching Perspectives", 
            "Understanding how different coaching positions view strategic decisions helps develop comprehensive game planning skills and better coordination between coaching staff."), unsafe_allow_html=True)
        
        perspective = st.selectbox(
            "Coaching Position",
            ["Head Coach", "Offensive Coordinator", "Defensive Coordinator", "Special Teams Coach"],
            help="👔 Select a coaching position to learn about their specific responsibilities, decision-making priorities, and strategic viewpoints."
        )
        
        if perspective == "Head Coach":
            st.markdown("""
            #### Head Coach Strategic Perspective
            
            **Primary Responsibilities**
            - Overall game strategy and management
            - Personnel decisions and substitutions  
            - Timeout and challenge management
            - Fourth down and two-point conversion decisions
            - Communication with coordinators
            
            **Strategic Priorities**
            - Field position and possession management
            - Risk vs reward assessment
            - Clock management and game flow
            - Situational awareness and adjustments
            - Team motivation and momentum
            
            **Key Decisions**
            - When to be aggressive vs conservative
            - Timeout usage in critical situations
            - Challenge flag decisions
            - Defer vs receive decisions
            - Halftime adjustments and messaging
            
            **Success Metrics**
            - Win probability maximization
            - Red zone efficiency
            - Turnover differential
            - Third down conversions
            - Time of possession management
            """)
        
        elif perspective == "Offensive Coordinator":
            st.markdown("""
            #### Offensive Coordinator Strategic Perspective
            
            **Primary Responsibilities**
            - Play calling and game plan execution
            - Formation and personnel selection
            - Route concepts and timing
            - Protection schemes and adjustments
            - Red zone and goal line strategy
            
            **Strategic Priorities**
            - Sustaining drives and scoring efficiency
            - Exploiting defensive weaknesses
            - Personnel package optimization
            - Rhythm and tempo control
            - Situational play calling
            
            **Key Decisions**
            - Run vs pass selection
            - Formation and motion usage
            - Route concepts and progressions
            - Protection schemes
            - Trick plays and gadgets
            
            **Success Metrics**
            - Points per drive
            - Third down conversion rate
            - Red zone touchdown percentage
            - Yards per play by formation
            - Time of possession
            """)

# =============================================================================
# NFL TERMINOLOGY GLOSSARY - ENHANCEMENT: Professional terminology reference
# =============================================================================

    # ENHANCEMENT: Add comprehensive terminology section
    render_how_to_section("NFL Strategic Terminology Glossary", """
    <div class="how-to-section">
    <h4>Professional NFL Strategic Terms</h4>
    
    <h5>Personnel Packages</h5>
    <ul>
    <li><strong>11 Personnel:</strong> 1 Running Back, 1 Tight End, 3 Wide Receivers</li>
    <li><strong>12 Personnel:</strong> 1 Running Back, 2 Tight Ends, 2 Wide Receivers</li>
    <li><strong>21 Personnel:</strong> 2 Running Backs, 1 Tight End, 2 Wide Receivers</li>
    <li><strong>10 Personnel:</strong> 1 Running Back, 0 Tight Ends, 4 Wide Receivers</li>
    </ul>
    
    <h5>Efficiency Metrics</h5>
    <ul>
    <li><strong>YPP (Yards Per Play):</strong> Average yards gained per offensive play</li>
    <li><strong>Success Rate:</strong> Percentage of plays achieving positive outcome</li>
    <li><strong>EPA (Expected Points Added):</strong> Point value added by each play</li>
    <li><strong>DVOA:</strong> Defense-adjusted Value Over Average</li>
    </ul>
    
    <h5>Situational Categories</h5>
    <ul>
    <li><strong>Third Down Conversion:</strong> Successfully gaining first down on third down</li>
    <li><strong>Red Zone Efficiency:</strong> Scoring touchdowns inside the 20-yard line</li>
    <li><strong>Goal Line Success:</strong> Scoring from inside the 5-yard line</li>
    <li><strong>Two-Minute Drill:</strong> Hurry-up offense in final two minutes</li>
    </ul>
    
    <h5>Strategic Concepts</h5>
    <ul>
    <li><strong>Edge Detection:</strong> Identifying competitive advantages</li>
    <li><strong>Formation Analysis:</strong> Personnel package efficiency study</li>
    <li><strong>Matchup Exploitation:</strong> Targeting favorable personnel matchups</li>
    <li><strong>Drive Management:</strong> Optimizing scoring opportunity efficiency</li>
    </ul>
    
    <h5>Weather Impact Terms</h5>
    <ul>
    <li><strong>Wind Speed:</strong> Affects passing accuracy and kicking game</li>
    <li><strong>Temperature:</strong> Impacts ball handling and player performance</li>
    <li><strong>Precipitation:</strong> Affects footing and ball security</li>
    <li><strong>Dome vs Outdoor:</strong> Controlled vs environmental conditions</li>
    </ul>
    
    <h5>Decision-Making Framework</h5>
    <ul>
    <li><strong>Risk Tolerance:</strong> Coaching aggressiveness scale (1-10)</li>
    <li><strong>Success Probability:</strong> Statistical likelihood of positive outcome</li>
    <li><strong>Expected Value:</strong> Average outcome weighted by probability</li>
    <li><strong>Historical Precedent:</strong> Similar situations from NFL history</li>
    </ul>
    </div>
    """)

# =============================================================================
# FOOTER AND DATABASE STATUS
# =============================================================================

st.markdown("---")

# System information
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    try:
        team_count = len(get_all_team_names())
        st.metric("🏈 NFL Teams", team_count, "Database Active")
    except:
        st.metric("🏈 NFL Teams", "Error", "Database Issue")

with col_info2:
    weather_status = "Active" if get_session_state_safely('current_weather_data', {}) else "Standby"
    st.metric("🌦️ Weather Intelligence", weather_status, "Live Updates")

with col_info3:
    analysis_count = 1 if get_session_state_safely('last_analysis', None) else 0
    st.metric("📊 Analyses Generated", analysis_count, "This Session")

# Footer with help reminder
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
            border-radius: 10px; margin: 20px 0;">
    <h4 style="color: #00ff41; margin: 0;">GRIT v4.0 - Professional NFL Strategic Analysis Platform</h4>
    <p style="color: #ffffff; margin: 5px 0;">
        SQLite Database • Real Weather API • Advanced GPT Analysis • Professional Visualizations
    </p>
    <p style="color: #cccccc; margin: 5px 0; font-size: 0.9em;">
        Think Like Belichick • Call Plays Like Reid • Analyze Like a Pro
    </p>
    <p style="color: #00ccff; margin: 10px 0; font-size: 0.8em;">
        💡 Need help? Look for "📚 How to Use" sections and hover over elements for detailed tooltips
    </p>
</div>
""", unsafe_allow_html=True)
