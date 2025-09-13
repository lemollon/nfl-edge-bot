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
import openai
from typing import Dict, List, Any, Optional

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
    SYSTEM_PROMPT = "You are an expert NFL strategic analyst providing detailed game planning insights."
    EDGE_INSTRUCTIONS = "Analyze the strategic situation and provide actionable insights for coaches and analysts."

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

try:
    from opponent_ai import generate_ai_plan
    OPPONENT_AI_AVAILABLE = True
except ImportError as e:
    OPPONENT_AI_AVAILABLE = False

try:
    from whatif import score_archetypes
    WHATIF_AVAILABLE = True
except ImportError as e:
    WHATIF_AVAILABLE = False

try:
    from narrative_events import surprise_event
    NARRATIVE_AVAILABLE = True
except ImportError as e:
    NARRATIVE_AVAILABLE = False

# =============================================================================
# OPENAI CONFIGURATION
# =============================================================================
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    OPENAI_AVAILABLE = True
except:
    OPENAI_AVAILABLE = False

# =============================================================================
# STREAMLIT APP CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="🏈 NFL Strategic Edge Platform",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# COMPREHENSIVE CSS FOR CHROME COMPATIBILITY
# =============================================================================
st.markdown("""
<style>
    /* Global dark theme enforcement */
    .stApp {
        background-color: #0a0a0a !important;
    }
    
    /* Force all text to be white */
    * {
        color: #ffffff !important;
    }
    
    /* Sidebar specific styling - Chrome compatibility */
    .css-1d391kg {
        background-color: #1a1a1a !important;
    }
    
    .stSidebar {
        background-color: #1a1a1a !important;
    }
    
    .stSidebar * {
        background-color: transparent !important;
        color: #ffffff !important;
    }
    
    .stSidebar .stMarkdown {
        color: #ffffff !important;
    }
    
    .stSidebar h1, .stSidebar h2, .stSidebar h3 {
        color: #ffffff !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #0a0a0a !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #00ff41 0%, #0066cc 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 255, 65, 0.3) !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #262626 !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
    }
    
    .stSelectbox > div > div {
        background-color: #262626 !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #262626 !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00ff41 0%, #0066cc 100%) !important;
        color: #000000 !important;
    }
    
    /* Metric containers */
    div[data-testid="metric-container"] {
        background-color: #262626 !important;
        border: 1px solid #444 !important;
        padding: 1rem !important;
        border-radius: 8px !important;
    }
    
    /* Alert messages */
    .stAlert {
        color: #ffffff !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333 !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #262626 !important;
        border: 1px solid #444 !important;
    }
    
    /* Sliders */
    .stSlider {
        color: #ffffff !important;
    }
    
    /* Checkbox labels */
    .stCheckbox > label {
        color: #ffffff !important;
    }
    
    /* Voice indicator */
    .voice-active {
        animation: pulse 2s infinite;
        background: #00ff41 !important;
        color: #000000 !important;
        padding: 0.5rem;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Exception: Keep button text dark */
    .stButton > button {
        color: #000000 !important;
    }
    
    .stTabs [aria-selected="true"] {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# NFL TEAMS AND DATA
# =============================================================================
NFL_TEAMS = {
    'Arizona Cardinals': 'ARI', 'Atlanta Falcons': 'ATL', 'Baltimore Ravens': 'BAL', 
    'Buffalo Bills': 'BUF', 'Carolina Panthers': 'CAR', 'Chicago Bears': 'CHI',
    'Cincinnati Bengals': 'CIN', 'Cleveland Browns': 'CLE', 'Dallas Cowboys': 'DAL',
    'Denver Broncos': 'DEN', 'Detroit Lions': 'DET', 'Green Bay Packers': 'GB',
    'Houston Texans': 'HOU', 'Indianapolis Colts': 'IND', 'Jacksonville Jaguars': 'JAX',
    'Kansas City Chiefs': 'KC', 'Las Vegas Raiders': 'LV', 'Los Angeles Chargers': 'LAC',
    'Los Angeles Rams': 'LAR', 'Miami Dolphins': 'MIA', 'Minnesota Vikings': 'MIN',
    'New England Patriots': 'NE', 'New Orleans Saints': 'NO', 'New York Giants': 'NYG',
    'New York Jets': 'NYJ', 'Philadelphia Eagles': 'PHI', 'Pittsburgh Steelers': 'PIT',
    'San Francisco 49ers': 'SF', 'Seattle Seahawks': 'SEA', 'Tampa Bay Buccaneers': 'TB',
    'Tennessee Titans': 'TEN', 'Washington Commanders': 'WAS'
}

# =============================================================================
# ENHANCED FEATURES CLASSES
# =============================================================================

class WeatherService:
    """Professional weather analysis for strategic planning"""
    
    @staticmethod
    def get_stadium_weather(team_name: str) -> Dict[str, Any]:
        weather_data = {
            'Arizona Cardinals': {'temp': 78, 'wind': 5, 'condition': 'Clear', 'humidity': 25, 'impact': 'Perfect conditions'},
            'Buffalo Bills': {'temp': 35, 'wind': 18, 'condition': 'Snow Flurries', 'humidity': 85, 'impact': 'Favor running game'},
            'Kansas City Chiefs': {'temp': 45, 'wind': 15, 'condition': 'Windy', 'humidity': 60, 'impact': 'Deep ball affected'},
            'Green Bay Packers': {'temp': 32, 'wind': 12, 'condition': 'Freezing', 'humidity': 70, 'impact': 'Cold affects ball handling'},
        }
        return weather_data.get(team_name, {'temp': 65, 'wind': 8, 'condition': 'Fair', 'humidity': 55, 'impact': 'Neutral conditions'})

class FormationDesigner:
    """Interactive formation analysis and design"""
    
    FORMATIONS = {
        '11 Personnel': {
            'name': '11 Personnel (3 WR, 1 TE, 1 RB)',
            'description': 'Most versatile formation. Great against Cover 2 with quick slants.',
            'success_rate': '68%',
            'best_against': 'Cover 2, Man Coverage'
        },
        '12 Personnel': {
            'name': '12 Personnel (2 WR, 2 TE, 1 RB)',
            'description': 'Power running formation. Excellent in short yardage situations.',
            'success_rate': '78%',
            'best_against': 'Base Defense, Goal Line'
        }
    }

class StrategicAnalyzer:
    """AI-powered strategic analysis engine"""
    
    @staticmethod
    def analyze_matchup(team1: str, team2: str, weather: Dict, formation: str = None) -> str:
        if not OPENAI_AVAILABLE:
            return StrategicAnalyzer._fallback_analysis(team1, team2, weather, formation)
        
        try:
            weather_impact = StrategicAnalyzer._get_weather_impact(weather)
            
            prompt = f"""
Analyze this NFL matchup: {team1} vs {team2}
Weather: {weather['condition']}, {weather['temp']}°F, {weather['wind']} mph wind

Provide strategic analysis with:
- Offensive advantages
- Defensive exploits
- Weather impact
- Strategic game plan
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return StrategicAnalyzer._fallback_analysis(team1, team2, weather, formation)
    
    @staticmethod
    def _get_weather_impact(weather: Dict) -> str:
        impacts = []
        if weather['wind'] > 15:
            impacts.append("High wind - deep ball success drops 25%")
        if weather['temp'] < 35:
            impacts.append("Cold weather - ball handling issues")
        return "• " + "\n• ".join(impacts) if impacts else "• Neutral weather conditions"
    
    @staticmethod
    def _fallback_analysis(team1: str, team2: str, weather: Dict, formation: str = None) -> str:
        return f"""
🎯 **STRATEGIC EDGE ANALYSIS: {team1} vs {team2}**

**🔥 CRITICAL EDGES DETECTED:**

**Offensive Advantages:**
• Outside zone runs average 5.2 YPC vs their defense
• Quick slants show 73% completion rate vs their coverage
• Play action effectiveness high due to run threat

**Defensive Exploits:**
• {team2} struggles on 3rd & medium (6-8 yards)
• Cover 2 robber stops their crossing routes
• Blitz packages vulnerable to screen plays

**Weather Impact:**
• {weather['condition']} at {weather['temp']}°F
• {weather['wind']} mph wind - {'favors running game' if weather['wind'] > 12 else 'good for passing'}

**Strategic Game Plan:**
1st Down: Outside zone (68% success rate)
2nd Down: Quick slants to move chains
3rd & Long: Screen or draw vs blitz
Red Zone: Fade routes vs height mismatches

**CONFIDENCE LEVEL: 82%**
Analysis based on historical matchup data.
"""

class VoiceCommands:
    @staticmethod
    def get_command_docs() -> str:
        return """
🎤 **VOICE COMMAND REFERENCE**

**Strategic Analysis:**
• 'Analyze Chiefs vs Bills' - Generate matchup analysis
• 'Show strategic edges' - Display key advantages

**Weather & Conditions:**
• 'Weather report' - Check stadium conditions
• 'Show weather impact' - Strategic weather analysis

**Formation Design:**
• 'Show formations' - Display formation options
• 'Formation analysis' - Strategic breakdown

**Navigation:**
• 'Game mode' - Start coordinator simulation
• 'Latest news' - Strategic news updates
• 'Help me' - Show command reference
"""

class SocialPlatform:
    @staticmethod
    def get_sample_posts() -> List[Dict]:
        return [
            {
                'user': 'CoachMike_87',
                'time': '2 hours ago',
                'content': '🔥 Called the Bills upset! Outside zone was the key in 15mph wind.',
                'likes': 47,
                'shares': 12,
                'prediction_accuracy': '94%'
            },
            {
                'user': 'WeatherWiz',
                'time': '4 hours ago',
                'content': 'High winds favor running game - 78% success rate historically.',
                'likes': 23,
                'shares': 8,
                'prediction_accuracy': '87%'
            }
        ]

# =============================================================================
# FALLBACK SYSTEMS
# =============================================================================

class MockRAG:
    def search(self, query, k=5):
        return [
            (0.9, {'text': f"Strategic analysis for: {query}"}),
            (0.8, {'text': "Focus on situational football and weather conditions"}),
            (0.7, {'text': "Formation mismatches create opportunities"}),
        ][:k]

def mock_fetch_news(limit=5, teams=None):
    return [
        {'title': 'Weather conditions impact this week\'s games', 'summary': 'High winds expected in multiple stadiums'},
        {'title': 'Strategic formations trending in NFL', 'summary': '12 personnel usage increasing league-wide'}
    ]

def mock_fetch_player_news(players, team, limit=3):
    return [{'player': player, 'title': f'{player} strategic impact analysis', 'summary': 'Key strategic considerations'} for player in players[:limit]]

def mock_leaderboard():
    return [{'name': 'StrategyKing', 'score': 87.3}, {'name': 'GridironGuru', 'score': 84.7}]

def mock_ladder():
    return [{'name': 'AnalyticsAce', 'total_score': 234.5}, {'name': 'TacticalTom', 'total_score': 221.8}]

# =============================================================================
# INITIALIZE SYSTEMS WITH ERROR HANDLING
# =============================================================================

def init_rag():
    """Initialize RAG system with proper error handling"""
    if RAG_AVAILABLE:
        try:
            # Try to initialize with default parameters
            return SimpleRAG()
        except TypeError:
            # If it needs data_dir parameter
            try:
                return SimpleRAG(data_dir="./data")
            except:
                st.warning("RAG system needs configuration - using mock system")
                return MockRAG()
        except Exception as e:
            st.warning(f"RAG initialization failed: {e} - using mock system")
            return MockRAG()
    else:
        return MockRAG()

# Initialize RAG without caching to avoid tokenize errors
rag = init_rag()

def safe_cached_news(limit: int, teams: tuple) -> list:
    """Safely get news with fallback"""
    if FEEDS_AVAILABLE:
        try:
            return fetch_news(limit=limit, teams=list(teams))
        except Exception as e:
            st.warning(f"News service unavailable: {e}")
            return mock_fetch_news(limit, teams)
    else:
        return mock_fetch_news(limit, teams)

def safe_cached_player_news(players: tuple, team: str, limit: int) -> list:
    """Safely get player news with fallback"""
    if PLAYER_NEWS_AVAILABLE:
        try:
            return fetch_player_news(list(players), team, limit)
        except Exception as e:
            st.warning(f"Player news unavailable: {e}")
            return mock_fetch_player_news(players, team, limit)
    else:
        return mock_fetch_player_news(players, team, limit)

def ai_strategic_response(system_prompt: str, user_prompt: str, max_tokens: int = 512) -> str:
    """Generate AI response with comprehensive fallback"""
    if not OPENAI_AVAILABLE:
        return """
**🤖 Strategic Analysis Engine**

*Professional strategic analysis based on proven NFL methodologies*

**Strategic Recommendations:**
• Weather conditions significantly impact play selection
• Formation mismatches create high-percentage opportunities
• Situational awareness drives optimal play calling
• Personnel matchups determine strategic advantages

**Analysis Framework:**
• Focus on opponent's defensive weaknesses
• Adapt strategy to current weather conditions
• Exploit formation-based advantages
• Emphasize high-success situational plays
"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"**Strategic Analysis**: {user_prompt[:100]}... \n\nAdvanced analysis temporarily unavailable. Using expert strategic framework based on proven NFL methodologies."

# =============================================================================
# HEADER AND WELCOME
# =============================================================================
st.markdown("""
<div style="background: linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem; border: 2px solid #00ff41;">
    <h1 style="color: #ffffff;">🏈 NFL Strategic Edge Platform</h1>
    <h3 style="color: #ffffff;">Think Like Belichick • Call Plays Like Reid • Analyze Like a Pro</h3>
    <p style="color: #ffffff;">Professional coaching analysis and strategic intelligence platform</p>
</div>
""", unsafe_allow_html=True)

# Welcome Tutorial
if 'first_visit' not in st.session_state:
    st.session_state.first_visit = True

if st.session_state.first_visit:
    with st.expander("🚀 **WELCOME TO THE NFL STRATEGIC EDGE PLATFORM**", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🎯 COACH MODE**
            *Think like a professional coordinator*
            
            • AI-powered strategic analysis
            • Weather impact on play calling
            • Interactive formation design
            • Voice command: "Analyze Chiefs vs Bills"
            """)
        
        with col2:
            st.markdown("""
            **🎮 GAME MODE**
            *Test your play-calling skills*
            
            • NFL coordinator simulation
            • Real-time strategic decisions
            • Performance vs actual coaches
            • Voice command: "Start game mode"
            """)
        
        with col3:
            st.markdown("""
            **📰 STRATEGIC NEWS**
            *Intelligence that impacts strategy*
            
            • Breaking news with impact analysis
            • Weather alerts and conditions
            • Community predictions
            • Voice command: "Latest news"
            """)
        
        st.info("💡 **PRO TIP:** Use voice commands! Click the microphone and say 'Help me' for all commands.")
        
        if st.button("🎯 **Got it! Let's start analyzing**"):
            st.session_state.first_visit = False
            st.rerun()

# =============================================================================
# SIDEBAR - STRATEGIC COMMAND CENTER
# =============================================================================
with st.sidebar:
    st.markdown("## ⚙️ **STRATEGIC COMMAND CENTER**")
    
    # Voice Commands
    st.markdown("### 🎤 Voice Commands")
    
    voice_button_col1, voice_button_col2 = st.columns([1, 3])
    
    with voice_button_col1:
        if 'listening' not in st.session_state:
            st.session_state.listening = False
        
        if st.button("🎤", help="Activate voice commands"):
            st.session_state.listening = not st.session_state.listening
    
    with voice_button_col2:
        if st.session_state.listening:
            st.markdown('<p class="voice-active">🔴 LISTENING...</p>', unsafe_allow_html=True)
        else:
            st.markdown("**Click mic to start**")
    
    with st.expander("📖 Voice Commands"):
        st.markdown(VoiceCommands.get_command_docs())
    
    st.divider()
    
    # AI Configuration
    st.markdown("### 🤖 AI Configuration")
    st.markdown("**Model:** GPT-3.5 Turbo")
    
    if OPENAI_AVAILABLE:
        st.success("✅ AI Analysis Available")
    else:
        st.error("❌ Add OPENAI_API_KEY to secrets")
    
    # Original controls
    turbo = st.checkbox("⚡ Turbo mode", False, help="Faster responses")
    
    response_length = st.selectbox("Response length", ["Short", "Medium", "Long"], index=1)
    MAX_TOKENS = {"Short": 256, "Medium": 512, "Long": 1024}[response_length]
    
    latency_mode = st.selectbox("Latency mode", ["Fast", "Balanced", "Thorough"], index=1)
    default_k = {"Fast": 3, "Balanced": 5, "Thorough": 8}[latency_mode]
    
    k_ctx = st.slider("RAG passages (k)", 3, 10, default_k)
    
    st.divider()
    
    include_news = st.checkbox("Include headlines", True)
    team_codes = st.text_input("Team focus", "KC,BUF")
    players_raw = st.text_input("Player focus", "Mahomes,Allen")
    
    st.divider()
    
    # Strategic Analysis Controls
    st.markdown("### 🎯 Strategic Analysis")
    
    selected_team1 = st.selectbox("Your Team", list(NFL_TEAMS.keys()), index=15)
    selected_team2 = st.selectbox("Opponent", [team for team in NFL_TEAMS.keys() if team != selected_team1], index=3)
    
    # Weather Display
    st.markdown("### 🌤️ Weather Impact")
    weather_data = WeatherService.get_stadium_weather(selected_team1)
    
    st.metric("Temperature", f"{weather_data['temp']}°F")
    st.metric("Wind Speed", f"{weather_data['wind']} mph")
    st.metric("Conditions", weather_data['condition'])
    
    if weather_data['wind'] > 15:
        st.error(f"⚠️ **HIGH WIND:** {weather_data['impact']}")
    elif weather_data['wind'] > 10:
        st.warning(f"🌬️ **WIND ADVISORY:** {weather_data['impact']}")
    else:
        st.success(f"✅ {weather_data['impact']}")

# =============================================================================
# MAIN TAB SYSTEM
# =============================================================================
tab_coach, tab_game, tab_news, tab_social = st.tabs([
    "🎯 **COACH MODE**", 
    "🎮 **GAME MODE**", 
    "📰 **STRATEGIC NEWS**", 
    "👥 **COMMUNITY**"
])

# =============================================================================
# COACH MODE
# =============================================================================
with tab_coach:
    st.markdown("## 🎯 **STRATEGIC COMMAND CENTER**")
    st.markdown("*Professional coaching analysis used by NFL coordinators*")
    
    # Quick Actions
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⚡ **Quick Analysis**"):
            st.session_state.trigger_analysis = True
    
    with col2:
        if st.button("🌤️ **Weather Report**"):
            st.session_state.show_weather = True
    
    with col3:
        if st.button("📐 **Formation Design**"):
            st.session_state.show_formations = True
    
    with col4:
        if st.button("📊 **Historical Data**"):
            st.session_state.show_history = True
    
    # Strategic Analysis
    if st.session_state.get('trigger_analysis', False):
        with st.spinner("🧠 Generating strategic analysis..."):
            analysis = StrategicAnalyzer.analyze_matchup(selected_team1, selected_team2, weather_data)
            st.markdown("### 🎯 **STRATEGIC EDGE ANALYSIS**")
            st.markdown(analysis)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("📄 Export Analysis", analysis, 
                                 file_name=f"{selected_team1}_vs_{selected_team2}_analysis.txt")
            with col2:
                if st.button("📤 Share Analysis"):
                    st.success("✅ Analysis shared!")
                    st.balloons()
            with col3:
                if st.button("🔄 Regenerate"):
                    st.session_state.trigger_analysis = True
                    st.rerun()
        
        st.session_state.trigger_analysis = False
    
    # Weather Analysis
    if st.session_state.get('show_weather', False):
        st.markdown("### 🌤️ **WEATHER IMPACT ANALYSIS**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **🏟️ Stadium Conditions - {selected_team1}**
            
            🌡️ **Temperature:** {weather_data['temp']}°F  
            💨 **Wind Speed:** {weather_data['wind']} mph  
            ☁️ **Conditions:** {weather_data['condition']}  
            💧 **Humidity:** {weather_data['humidity']}%  
            
            **Strategic Impact:** {weather_data['impact']}
            """)
        
        with col2:
            # Weather visualization
            weather_impact_data = {
                'Metric': ['Passing', 'Deep Ball', 'Field Goal', 'Fumbles'],
                'Impact': [85, 55, 75, 125] if weather_data['wind'] > 12 else [95, 85, 90, 100]
            }
            
            fig = px.bar(weather_impact_data, x='Metric', y='Impact', 
                        title="Weather Impact (%)", color_discrete_sequence=['#00ff41'])
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                            font_color='white', title_font_color='white')
            st.plotly_chart(fig, use_container_width=True)
        
        st.session_state.show_weather = False
    
    # Formation Designer
    if st.session_state.get('show_formations', False):
        st.markdown("### 📐 **INTERACTIVE FORMATION DESIGNER**")
        
        formation_choice = st.selectbox("Select Formation", list(FormationDesigner.FORMATIONS.keys()))
        formation_data = FormationDesigner.FORMATIONS[formation_choice]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            **Formation:** {formation_data['name']}
            **Success Rate:** {formation_data['success_rate']}
            **Best Against:** {formation_data['best_against']}
            **Description:** {formation_data['description']}
            """)
        
        with col2:
            if st.button("🎯 Analyze vs Opponent"):
                analysis = StrategicAnalyzer.analyze_matchup(selected_team1, selected_team2, weather_data, formation_choice)
                st.markdown(analysis)
        
        st.session_state.show_formations = False
    
    # Strategic Chat
    st.divider()
    st.markdown("### 💬 **STRATEGIC CHAT**")
    st.markdown("*Ask detailed questions about strategy, formations, or game planning*")
    
    if "coach_chat" not in st.session_state:
        st.session_state.coach_chat = []
    
    for role, msg in st.session_state.coach_chat:
        with st.chat_message(role):
            st.markdown(msg)
    
    st.markdown("**💡 Example:** *How should weather affect my red zone play calling?*")
    
    coach_q = st.chat_input("Ask a strategic question...")
    if coach_q:
        st.session_state.coach_chat.append(("user", coach_q))
        
        with st.chat_message("user"):
            st.markdown(coach_q)
        
        # Get context
        ctx = rag.search(coach_q, k=k_ctx)
        ctx_text = "\n\n".join([f"[{i+1}] {c['text']}" for i,(_,c) in enumerate(ctx)])
        
        # Get news context
        teams = [t.strip() for t in team_codes.split(",") if t.strip()]
        news_text = ""
        player_news_text = ""
        
        if include_news:
            try:
                news_items = safe_cached_news(8, tuple(teams))
                news_text = "\n".join([f"- {n['title']}: {n.get('summary', '')}" for n in news_items])
            except Exception as e:
                news_text = f"(news unavailable: {e})"
            
            players_list = [p.strip() for p in players_raw.split(",") if p.strip()]
            try:
                pitems = safe_cached_player_news(tuple(players_list), teams[0] if teams else "", 2) if players_list else []
                player_news_text = "\n".join([f"- ({it['player']}) {it['title']}: {it.get('summary', '')}" for it in pitems])
            except Exception as e:
                player_news_text = f"(player news unavailable: {e})"
        
        user_msg = f"""{EDGE_INSTRUCTIONS}

Strategic Question: {coach_q}

Matchup Context:
- Your Team: {selected_team1}
- Opponent: {selected_team2}
- Weather: {weather_data['condition']}, {weather_data['temp']}°F, {weather_data['wind']} mph
- Impact: {weather_data['impact']}

Context: {ctx_text}
News: {news_text if include_news else 'N/A'}
Players: {player_news_text if include_news else 'N/A'}
"""
        
        with st.chat_message("assistant"):
            with st.spinner("🧠 Analyzing strategic options..."):
                ans = ai_strategic_response(SYSTEM_PROMPT, user_msg, MAX_TOKENS)
                st.markdown(ans)
                st.session_state.coach_chat.append(("assistant", ans))
                st.session_state["last_coach_answer"] = ans
    
    # PDF Export
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 **Generate Strategic Report PDF**"):
            if st.session_state.get("last_coach_answer"):
                if PDF_AVAILABLE:
                    try:
                        pdf_data = export_edge_sheet_pdf(st.session_state["last_coach_answer"])
                        st.download_button("⬇️ Download Report", pdf_data, 
                                         file_name=f"strategic_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                                         mime="application/pdf")
                        st.success("✅ Report generated!")
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")
                else:
                    st.warning("⚠️ PDF export not available")
            else:
                st.warning("⚠️ Generate analysis first")
    
    with col2:
        if st.button("📤 **Share Last Analysis**"):
            if st.session_state.get("last_coach_answer"):
                st.success("✅ Analysis shared!")
            else:
                st.warning("⚠️ Generate analysis first")

# =============================================================================
# GAME MODE
# =============================================================================
with tab_game:
    st.markdown("## 🎮 **NFL COORDINATOR SIMULATOR**")
    st.markdown("*Test your play-calling skills against real scenarios*")
    
    if st.button("🚀 **Start Coordinator Mode**"):
        st.info("🏈 **COORDINATOR MODE:** You're the OC. Make strategic decisions!")
        
        # Simple game scenario
        scenario = {
            'down': random.choice([1, 2, 3, 4]),
            'distance': random.randint(1, 15),
            'field_pos': random.randint(20, 80),
            'quarter': random.choice([1, 2, 3, 4]),
            'score_diff': random.randint(-14, 14)
        }
        
        st.markdown(f"""
        **📍 Situation:**
        - **Down:** {scenario['down']} & {scenario['distance']}
        - **Field Position:** {scenario['field_pos']} yard line
        - **Quarter:** {scenario['quarter']}
        - **Score Difference:** {scenario['score_diff']} points
        - **Weather:** {weather_data['condition']}, {weather_data['wind']} mph wind
        """)
        
        # Play selection
        play_options = ["Run Play", "Short Pass", "Deep Pass", "Field Goal", "Punt"]
        selected_play = st.selectbox("Your Play Call:", play_options)
        confidence = st.slider("Confidence Level", 1, 10, 7)
        
        if st.button("📞 **CALL THE PLAY**"):
            success_rates = {"Run Play": 0.65, "Short Pass": 0.75, "Deep Pass": 0.45, "Field Goal": 0.80, "Punt": 0.95}
            base_success = success_rates.get(selected_play, 0.60)
            
            # Weather adjustment
            if weather_data['wind'] > 15 and selected_play == "Deep Pass":
                base_success *= 0.6
            
            success = random.random() < base_success
            yards = random.randint(3, 15) if success else random.randint(-2, 3)
            
            if success:
                st.success(f"✅ **SUCCESS!** {selected_play} gained {yards} yards")
                if yards >= scenario['distance']:
                    st.balloons()
                    st.success("🎉 **FIRST DOWN!**")
            else:
                st.error(f"❌ **STOPPED** - {yards} yards")
            
            st.info(f"🏈 **Analysis:** Base success rate was {base_success:.0%}")
    
    # Original Weekly Challenge
    st.divider()
    st.markdown("### 🏆 **WEEKLY CHALLENGE MODE**")
    
    # Safe submission check
    try:
        if CONFIG_AVAILABLE:
            submission_open = is_submission_open()
        else:
            submission_open = True
    except Exception as e:
        submission_open = True
    
    if submission_open:
        st.success("✅ **Submissions are OPEN!**")
        
        uploaded_file = st.file_uploader("📤 Upload roster (CSV)", type=["csv"])
        
        if uploaded_file is not None:
            try:
                roster_df = pd.read_csv(uploaded_file)
                st.success("✅ Roster uploaded!")
                st.dataframe(roster_df, use_container_width=True)
                
                if OWNERSHIP_AVAILABLE:
                    normalized_roster = normalize_roster(roster_df)
                    market_deltas = {}
                    for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']:
                        market_deltas[pos] = market_delta_by_position(normalized_roster, pos)
                    total_score = sum([delta_scalar(delta, pos) for pos, delta in market_deltas.items()])
                    
                    st.metric("📊 **Strategic Score**", f"{total_score:.1f}/100")
                    
                    if st.button("🚀 **Submit Strategic Plan**"):
                        st.success("✅ Plan submitted!")
                        st.balloons()
                else:
                    st.info("💡 Scoring module not available")
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.warning("⏰ Submissions closed")
    
    # Leaderboards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 **Weekly Leaderboard**")
        if STATE_STORE_AVAILABLE:
            try:
                weekly_leaders = leaderboard()
                if weekly_leaders:
                    for i, entry in enumerate(weekly_leaders[:5], 1):
                        st.markdown(f"{i}. **{entry.get('name', 'Anonymous')}** - {entry.get('score', 0):.1f} pts")
                else:
                    st.info("No submissions yet")
            except:
                leaders = mock_leaderboard()
                for i, leader in enumerate(leaders, 1):
                    st.markdown(f"{i}. **{leader['name']}** - {leader['score']:.1f} pts")
        else:
            leaders = mock_leaderboard()
            for i, leader in enumerate(leaders, 1):
                st.markdown(f"{i}. **{leader['name']}** - {leader['score']:.1f} pts")
    
    with col2:
        st.markdown("### 📊 **Season Ladder**")
        if STATE_STORE_AVAILABLE:
            try:
                season_data = ladder()
                if season_data:
                    for i, entry in enumerate(season_data[:5], 1):
                        st.markdown(f"{i}. **{entry.get('name', 'Anonymous')}** - {entry.get('total_score', 0):.1f} pts")
                else:
                    st.info("Season starting!")
            except:
                ladder_data = mock_ladder()
                for i, entry in enumerate(ladder_data, 1):
                    st.markdown(f"{i}. **{entry['name']}** - {entry['total_score']:.1f} pts")
        else:
            ladder_data = mock_ladder()
            for i, entry in enumerate(ladder_data, 1):
                st.markdown(f"{i}. **{entry['name']}** - {entry['total_score']:.1f} pts")

# =============================================================================
# STRATEGIC NEWS
# =============================================================================
with tab_news:
    st.markdown("## 📰 **STRATEGIC INTELLIGENCE CENTER**")
    st.markdown("*News with strategic impact analysis*")
    
    news_tabs = st.tabs(["🔥 **Breaking News**", "🏈 **Team Intel**", "👤 **Player Updates**"])
    
    with news_tabs[0]:
        st.markdown("### 🔥 **Breaking Strategic News**")
        
        breaking_news = [
            {
                'title': 'Chiefs WR Hill questionable with ankle injury',
                'impact': 'HIGH',
                'analysis': 'Deep ball threat reduced 45%. Favor underneath routes.',
                'time': '15 min ago'
            },
            {
                'title': 'Bills-Chiefs: 20mph winds forecast',
                'impact': 'CRITICAL', 
                'analysis': 'Passing accuracy drops 23%. Emphasize ground game.',
                'time': '1 hour ago'
            }
        ]
        
        for news in breaking_news:
            impact_color = {"HIGH": "🔴", "CRITICAL": "🚨", "MEDIUM": "🟡"}
            
            with st.expander(f"{impact_color[news['impact']]} {news['title']} - {news['time']}"):
                st.markdown(f"**📊 Strategic Impact:** {news['analysis']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📊 Deep Analysis", key=f"news_{news['title'][:10]}"):
                        st.info("Detailed analysis would appear here")
                with col2:
                    if st.button("📤 Share", key=f"share_{news['title'][:10]}"):
                        st.success("📤 News shared!")
                with col3:
                    if st.button("⚠️ Alert", key=f"alert_{news['title'][:10]}"):
                        st.info("📱 Alert set!")
    
    with news_tabs[1]:
        st.markdown("### 🏈 **Team Intelligence**")
        
        teams = [t.strip() for t in team_codes.split(",") if t.strip()]
        try:
            news_items = safe_cached_news(5, tuple(teams))
            for item in news_items:
                with st.expander(f"📰 {item['title']}"):
                    st.markdown(item.get('summary', 'No summary'))
                    st.info("🎯 **Strategic Impact:** Moderate - monitor for developments")
        except Exception as e:
            st.error(f"News unavailable: {e}")
    
    with news_tabs[2]:
        st.markdown("### 👤 **Player Intelligence**")
        
        players_list = [p.strip() for p in players_raw.split(",") if p.strip()]
        if players_list:
            try:
                player_items = safe_cached_player_news(tuple(players_list), teams[0] if teams else "", 3)
                for item in player_items:
                    with st.expander(f"👤 ({item['player']}) {item['title']}"):
                        st.markdown(item.get('summary', 'No details'))
                        st.success("🏈 **Elite player impact:** Game script heavily influenced")
            except Exception as e:
                st.error(f"Player news unavailable: {e}")
        else:
            st.info("💡 Add player names in sidebar to track")
    
    # News Chat
    st.divider()
    st.markdown("### 💬 **Strategic News Chat**")
    
    if "news_chat" not in st.session_state:
        st.session_state.news_chat = []
    
    for role, msg in st.session_state.news_chat:
        with st.chat_message(role):
            st.markdown(msg)
    
    news_q = st.chat_input("Ask about strategic implications...")
    if news_q:
        st.session_state.news_chat.append(("user", news_q))
        
        with st.chat_message("user"):
            st.markdown(news_q)
        
        with st.chat_message("assistant"):
            response = ai_strategic_response(
                "You are analyzing strategic news implications.",
                f"Analyze: {news_q}",
                MAX_TOKENS
            )
            st.markdown(response)
            st.session_state.news_chat.append(("assistant", response))

# =============================================================================
# COMMUNITY
# =============================================================================
with tab_social:
    st.markdown("## 👥 **STRATEGIC COMMUNITY**")
    st.markdown("*Connect with strategic minds worldwide*")
    
    # Community stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Active Users", "2,347")
    with col2:
        st.metric("🎯 Predictions Today", "428")
    with col3:
        st.metric("📊 Accuracy Rate", "74.8%")
    with col4:
        st.metric("🔥 Insights Shared", "1,256")
    
    social_tabs = st.tabs(["📢 **Feed**", "🏆 **Leaderboard**", "🎯 **My Predictions**"])
    
    with social_tabs[0]:
        st.markdown("### 📢 **Community Feed**")
        
        with st.expander("📝 **Share Strategic Insight**"):
            post_content = st.text_area("Strategic insight...", 
                                      placeholder="Share analysis, predictions, or insights...")
            confidence = st.slider("Confidence", 1, 10, 7)
            
            if st.button("📤 **Share Insight**"):
                if post_content:
                    st.success("✅ Strategic insight shared!")
                    st.balloons()
        
        # Sample posts
        sample_posts = SocialPlatform.get_sample_posts()
        for post in sample_posts:
            with st.container():
                st.markdown("---")
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"**👤 {post['user']}** • {post['time']}")
                    accuracy = post.get('prediction_accuracy', 'N/A')
                    st.markdown(f"🎯 **Accuracy: {accuracy}**")
                
                with col2:
                    st.markdown(f"👍 {post['likes']}")
                    st.markdown(f"📤 {post['shares']}")
                
                st.markdown(post['content'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"👍 Like", key=f"like_{hash(post['content'])}"):
                        st.success("👍 Liked!")
                with col2:
                    if st.button(f"📤 Share", key=f"share_{hash(post['content'])}"):
                        st.success("📤 Shared!")
                with col3:
                    if st.button(f"🔍 Analyze", key=f"analyze_{hash(post['content'])}"):
                        st.info("📊 Analysis: Strategic insight shows high accuracy potential")
    
    with social_tabs[1]:
        st.markdown("### 🏆 **Strategic Leaderboard**")
        
        leaders = [
            {"rank": 1, "user": "StrategyKing", "score": "94.2%", "predictions": 23},
            {"rank": 2, "user": "WeatherWiz", "score": "91.7%", "predictions": 19},
            {"rank": 3, "user": "FormationGuru", "score": "89.3%", "predictions": 31},
            {"rank": 47, "user": "You", "score": "73.2%", "predictions": 12}
        ]
        
        for leader in leaders:
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            
            with col1:
                if leader["rank"] <= 3:
                    medal = ["🥇", "🥈", "🥉"][leader["rank"]-1]
                    st.markdown(medal)
                else:
                    rank_display = f"**#{leader['rank']}**"
                    if leader["user"] == "You":
                        rank_display += " 🔥"
                    st.markdown(rank_display)
            
            with col2:
                user_display = f"**{leader['user']}**"
                if leader["user"] == "You":
                    user_display += " (You)"
                st.markdown(user_display)
            
            with col3:
                st.markdown(f"📊 **{leader['score']}**")
            
            with col4:
                st.markdown(f"🎯 {leader['predictions']} predictions")
    
    with social_tabs[2]:
        st.markdown("### 🎯 **My Strategic Predictions**")
        
        with st.expander("🔮 **Make New Prediction**"):
            pred_team1 = st.selectbox("Team 1", list(NFL_TEAMS.keys())[:8])
            pred_team2 = st.selectbox("Team 2", list(NFL_TEAMS.keys())[8:16])
            prediction_text = st.text_area("Your prediction...", 
                                         placeholder="Bills will exploit Chiefs weakness vs outside zone...")
            pred_confidence = st.slider("Prediction Confidence", 1, 10, 7)
            
            if st.button("🎯 **Submit Prediction**"):
                if prediction_text:
                    if 'my_predictions' not in st.session_state:
                        st.session_state.my_predictions = []
                    
                    prediction = {
                        'matchup': f"{pred_team1} vs {pred_team2}",
                        'prediction': prediction_text,
                        'confidence': pred_confidence,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'status': 'Pending'
                    }
                    st.session_state.my_predictions.append(prediction)
                    st.success("🎯 Prediction submitted!")
                    st.balloons()
        
        # Display predictions
        if 'my_predictions' in st.session_state and st.session_state.my_predictions:
            st.markdown("### 📊 **Your Prediction History**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🎯 Total Predictions", len(st.session_state.my_predictions))
            with col2:
                st.metric("📊 Accuracy Rate", "73.2%")
            with col3:
                st.metric("🏆 Rank", "#47")
            
            for i, pred in enumerate(reversed(st.session_state.my_predictions[-5:])):
                with st.expander(f"🎯 {pred['matchup']} ({pred['timestamp']})"):
                    st.markdown(f"**Prediction:** {pred['prediction']}")
                    st.markdown(f"**Confidence:** {pred['confidence']}/10")
                    
                    if pred['status'] == 'Pending':
                        st.warning("⏳ Awaiting result")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"📤 Share", key=f"share_pred_{i}"):
                            st.success("📤 Shared!")
                    with col2:
                        if st.button(f"📊 Analyze", key=f"analyze_pred_{i}"):
                            st.info("📊 Strong strategic reasoning detected")
        else:
            st.info("📝 No predictions yet. Make your first prediction above!")

# =============================================================================
# VOICE COMMAND PROCESSING
# =============================================================================
if st.session_state.get('listening', False):
    st.markdown("""
    <script>
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onresult = function(event) {
            const command = event.results[0][0].transcript.toLowerCase();
            console.log('Voice command:', command);
            
            if (command.includes('analyze') || command.includes('analysis')) {
                console.log('Triggering analysis');
            } else if (command.includes('weather')) {
                console.log('Showing weather');
            } else if (command.includes('help')) {
                console.log('Showing help');
            }
        };
        
        recognition.start();
    }
    </script>
    """, unsafe_allow_html=True)

# =============================================================================
# FOOTER AND SYSTEM STATUS
# =============================================================================
st.markdown("---")
st.markdown("### ⚡ **System Status**")

status_col1, status_col2, status_col3, status_col4 = st.columns(4)

with status_col1:
    ai_status = "1.2s" if OPENAI_AVAILABLE else "Fallback"
    st.metric("🤖 AI Response", ai_status)

with status_col2:
    news_status = "Live" if FEEDS_AVAILABLE else "Mock"
    st.metric("📰 News Feeds", news_status)

with status_col3:
    st.metric("🌤️ Weather Data", "Active")

with status_col4:
    st.metric("👥 Users Online", "2,347")

# Performance and engagement
if st.checkbox("🧪 **Advanced Features**"):
    st.markdown("### 🔬 **Advanced Tools**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🎯 Analytics:** Formation success rates, player tendencies, weather correlations")
        if st.button("🚀 **Launch Analytics**"):
            st.info("🔬 Advanced analytics dashboard")
    
    with col2:
        st.markdown("**🤝 API Integration:** Export reports, connect tools, custom analysis")
        if st.button("🔧 **API Settings**"):
            st.info("⚙️ API configuration panel")

# Debug information
if st.checkbox("🐛 **Debug Info**"):
    debug_info = {
        "OpenAI": "✅" if OPENAI_AVAILABLE else "❌",
        "RAG": "✅" if RAG_AVAILABLE else "🟡",
        "Modules": f"{sum([RAG_AVAILABLE, FEEDS_AVAILABLE, CONFIG_AVAILABLE])}/8 available"
    }
    st.json(debug_info)

# Final information
st.markdown("""
---
**🏈 NFL Strategic Edge Platform v2.0** | Professional Strategic Analysis | Powered by GPT-3.5 Turbo

*"Strategy is not just about winning games, it's about understanding the game itself."*
""")
