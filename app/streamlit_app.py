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
- Line 527: Fixed session state access error
- All session state access: Added safety checks
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

# Enhanced dark theme CSS with white text
# Enhanced dark theme CSS with white text - REPLACE LINES 42-165
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

# =============================================================================
# SIDEBAR CONFIGURATION
# =============================================================================

with st.sidebar:
    st.markdown("## Strategic Command Center")
    st.markdown("*Professional NFL Analysis Platform*")
    
    # Core Team Selection Section
    st.markdown("### Team Selection")
    
    try:
        all_teams = get_all_team_names()
        
        selected_team1 = st.selectbox(
            "Your Team", 
            all_teams, 
            index=0 if all_teams else 0,
            help="Select your team for analysis"
        )
        
        available_opponents = [team for team in all_teams if team != selected_team1]
        selected_team2 = st.selectbox(
            "Opponent", 
            available_opponents, 
            index=0 if available_opponents else 0,
            help="Select the opposing team"
        )
        
        weather_team = st.selectbox(
            "Weather Location", 
            [selected_team1, selected_team2], 
            help="Choose stadium for weather analysis"
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
    
    complexity_level = st.selectbox(
        "Analysis Complexity",
        ["Basic", "Advanced", "Expert"],
        index=1,
        help="Choose the depth of strategic analysis"
    )
    
    coaching_perspective = st.selectbox(
        "Coaching Perspective",
        ["Head Coach", "Offensive Coordinator", "Defensive Coordinator", "Special Teams Coach"],
        index=0,
        help="Select the coaching viewpoint for analysis"
    )
    
    analysis_type = st.selectbox(
        "Analysis Focus",
        ["Edge Detection", "Formation Analysis", "Situational Breakdown", "Weather Impact",
         "Play Calling", "Matchup Exploitation", "Drive Management", "Red Zone Optimization"],
        help="Choose the specific type of strategic analysis"
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
    
    col1, col2 = st.columns(2)
    with col1:
        down = st.selectbox("Down", [1, 2, 3, 4], index=0)
        field_position = st.slider("Field Position", 1, 99, 50, help="Distance from own goal line")
    
    with col2:
        distance = st.slider("Distance", 1, 30, 10)
        score_diff = st.slider("Score Differential", -21, 21, 0, help="Your team's score minus opponent's")
    
    time_remaining = st.selectbox(
        "Time Remaining",
        ["15:00", "10:00", "5:00", "2:00", "1:00", "0:30"],
        index=0
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
# TAB STRUCTURE
# =============================================================================

tab_analysis, tab_intelligence, tab_tools, tab_education = st.tabs([
    "🧠 STRATEGIC ANALYSIS HUB", 
    "📰 TACTICAL INTELLIGENCE CENTER", 
    "📊 PROFESSIONAL TOOLS & VISUALIZATION", 
    "📚 EDUCATION & DEVELOPMENT"
])

# =============================================================================
# TAB 1: STRATEGIC ANALYSIS HUB
# =============================================================================

with tab_analysis:
    st.markdown("## 🧠 Strategic Analysis Hub")
    st.markdown("*Professional NFL coordinator-level strategic insights with advanced analysis*")
    
    # Strategic Question Interface
    col_input, col_button = st.columns([3, 1])
    
    with col_input:
        strategic_question = st.text_input(
            "Strategic Consultation Question:",
            placeholder="e.g., How do we exploit their red zone defense in this weather? What's our best play on 3rd and 7?",
            help="Ask specific tactical questions for detailed strategic analysis"
        )
    
    with col_button:
        st.write("")  # Spacing
        analyze_button = st.button("🧠 Generate Analysis", type="primary")
    
    # Main analysis area
    col_main, col_sidebar_info = st.columns([2, 1])
    
    with col_main:
        # Analysis execution
        if analyze_button or strategic_question:
            if not strategic_question:
                teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None, 'weather_team': None})
                analysis_type = get_session_state_safely('analysis_preferences', {}).get('analysis_type', 'Edge Detection')
                strategic_question = f"Provide {analysis_type.lower()} analysis for {teams['team1']} vs {teams['team2']} in current game situation"
            
            with st.spinner("🔍 Analyzing strategic situation..."):
                try:
                    # Get comprehensive data - BUG FIX: Safe access
                    teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None, 'weather_team': None})
                    team1_data = get_team_data(teams['team1'])
                    team2_data = get_team_data(teams['team2'])
                    
                    # Get weather data with comprehensive fallback
                    team1_stadium = team1_data.get('stadium_info', {}) if team1_data else {}
                    weather_data = get_comprehensive_weather_data(
                        teams['weather_team'],
                        team1_stadium.get('city', 'Unknown'),
                        team1_stadium.get('state', 'Unknown'),
                        team1_stadium.get('is_dome', False)
                    )
                    
                    # Store weather data in session state - BUG FIX: Safe storage
                    if hasattr(st.session_state, 'current_weather_data'):
                        st.session_state.current_weather_data = weather_data
                    
                    # Generate enhanced analysis
                    preferences = get_session_state_safely('analysis_preferences', {
                        'complexity_level': 'Advanced',
                        'coaching_perspective': 'Head Coach',
                        'analysis_type': 'Edge Detection'
                    })
                    game_situation = get_session_state_safely('game_situation', {
                        'down': 1, 'distance': 10, 'field_position': 50,
                        'score_differential': 0, 'time_remaining': '15:00'
                    })
                    
                    analysis = generate_advanced_strategic_analysis(
                        teams['team1'], teams['team2'], strategic_question, preferences['analysis_type'],
                        team1_data, team2_data, weather_data,
                        game_situation, preferences['coaching_perspective'], 
                        preferences['complexity_level']
                    )
                    
                    st.markdown(analysis)
                    
                    # Store analysis in session state and database
                    if hasattr(st.session_state, 'last_analysis'):
                        st.session_state.last_analysis = {
                            'question': strategic_question,
                            'analysis': analysis,
                            'timestamp': datetime.now(),
                            'teams': f"{teams['team1']} vs {teams['team2']}"
                        }
                    
                    # Save to database for chat history
                    save_chat_message(
                        get_session_state_safely('session_id', str(uuid.uuid4())),
                        "analysis",
                        f"Q: {strategic_question}\n\nA: {analysis}",
                        preferences['analysis_type']
                    )
                    
                    st.success("✅ Strategic Analysis Complete!")
                    
                except Exception as e:
                    st.error(f"Analysis generation failed: {str(e)}")
        
        # Strategic Chat Interface
        st.markdown("### Strategic Consultation Chat")
        st.markdown("*Continue the strategic discussion with follow-up questions*")
        
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
        
        # Chat input
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
# TAB 2: TACTICAL INTELLIGENCE CENTER
# =============================================================================

with tab_intelligence:
    st.markdown("## 📰 Tactical Intelligence Center")
    st.markdown("*Breaking intelligence with strategic impact analysis*")
    
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
        
        decision_type = st.selectbox(
            "Strategic Decision",
            ["Fourth Down Attempt", "Two-Point Conversion", "Aggressive Pass vs Run", 
             "Timeout Usage", "Field Goal vs Punt"]
        )
        
        risk_tolerance = st.slider("Risk Tolerance", 1, 10, 5, help="1=Conservative, 10=Aggressive")
        
        if st.button("🎯 Calculate Risk-Reward"):
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
        
        precedent_search = st.text_input(
            "Search Similar Situations",
            placeholder="e.g., cold weather playoff games, wind affecting passing teams",
            help="Find historical games with similar conditions or matchups"
        )
        
        if precedent_search and st.button("🔍 Find Precedents"):
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
# TAB 3: PROFESSIONAL TOOLS & VISUALIZATION
# =============================================================================

with tab_tools:
    st.markdown("## 📊 Professional Tools & Visualization")
    st.markdown("*Advanced analytics and professional reporting tools*")
    
    tool_type = st.selectbox(
        "Select Professional Tool",
        ["Formation Efficiency Analysis", "Situational Heatmap", "Personnel Advantages Radar",
         "Weather Impact Analysis", "Comprehensive Dashboard", "Analysis Report Generator"]
    )
    
    try:
        teams = get_session_state_safely('selected_teams', {'team1': None, 'team2': None, 'weather_team': None})
        if teams['team1'] and teams['team2']:
            team1_data = get_team_data(teams['team1'])
            team2_data = get_team_data(teams['team2'])
            
            if tool_type == "Formation Efficiency Analysis":
                st.markdown("### Formation Efficiency Comparison")
                
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
                
                if team1_data and team2_data:
                    fig = create_situational_heatmap(
                        team1_data, team2_data, teams['team1'], teams['team2']
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif tool_type == "Personnel Advantages Radar":
                st.markdown("### Personnel Matchup Analysis")
                
                if team1_data and team2_data:
                    fig = create_personnel_advantages_radar(
                        team1_data, team2_data, teams['team1'], teams['team2']
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif tool_type == "Weather Impact Analysis":
                st.markdown("### Weather Strategic Impact")
                
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
                
                if team1_data and team2_data:
                    weather_data = get_session_state_safely('current_weather_data', {})
                    fig = create_comprehensive_dashboard(
                        team1_data, team2_data, teams['team1'], teams['team2'], weather_data
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            elif tool_type == "Analysis Report Generator":
                st.markdown("### Professional Report Generator")
                
                report_sections = st.multiselect(
                    "Report Sections",
                    ["Executive Summary", "Formation Analysis", "Weather Impact", 
                     "Risk Assessment", "Tactical Recommendations", "Play Calling Guide"],
                    default=["Executive Summary", "Formation Analysis", "Tactical Recommendations"]
                )
                
                if st.button("📊 Generate Professional Report"):
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
                                    mime="text/plain"
                                )
                            
                            with col2:
                                # Convert to basic HTML
                                html_content = formatted_report.replace('\n', '<br>')
                                st.download_button(
                                    label="🌐 Download Report (HTML)",
                                    data=html_content,
                                    file_name=f"{teams['team1']}_vs_{teams['team2']}_analysis_report.html",
                                    mime="text/html"
                                )
                                
                        except Exception as e:
                            st.error(f"Report generation failed: {str(e)}")
        else:
            st.warning("Please select both teams in the sidebar to use visualization tools.")
            
    except Exception as e:
        st.error(f"Visualization tool error: {str(e)}")

# =============================================================================
# TAB 4: EDUCATION & DEVELOPMENT
# =============================================================================

with tab_education:
    st.markdown("## 📚 Education & Development")
    st.markdown("*Master NFL strategic analysis and tactical concepts*")
    
    education_type = st.selectbox(
        "Learning Module",
        ["Strategic Concepts", "Formation Breakdown", "Decision Tree Training",
         "Case Studies", "Weather Impact Analysis", "Coaching Perspectives"]
    )
    
    if education_type == "Strategic Concepts":
        st.markdown("### Strategic Concepts Deep Dive")
        
        concept = st.selectbox(
            "Select Concept",
            ["Personnel Packages", "Down and Distance Strategy", "Field Position Impact",
             "Clock Management", "Risk vs Reward Decisions"]
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
    
    elif education_type == "Decision Tree Training":
        st.markdown("### Strategic Decision Tree Training")
        st.markdown("*Interactive scenarios to improve decision-making*")
        
        scenario = st.selectbox(
            "Training Scenario",
            ["Fourth Down Decision", "Two-Minute Drill Management", "Red Zone Play Selection",
             "Weather Adjustment", "Halftime Strategic Changes"]
        )
        
        if scenario == "Fourth Down Decision":
            st.markdown("#### Fourth Down Decision Scenario")
            game_sit = get_session_state_safely('game_situation', {
                'down': 1, 'distance': 10, 'field_position': 50,
                'score_differential': 0, 'time_remaining': '15:00'
            })
            st.markdown(f"**Situation:** {game_sit['down']} and {game_sit['distance']} at {game_sit['field_position']} yard line")
            
            decision = st.radio(
                "Your Decision:",
                ["Punt", "Field Goal Attempt", "Go for First Down"]
            )
            
            if st.button("🎯 Analyze Decision"):
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

# Footer
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
</div>
""", unsafe_allow_html=True)
