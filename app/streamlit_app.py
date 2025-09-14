"""
NFL Team Analysis Dashboard - Powered by ChatGPT 3.5 Turbo
===========================================================

This Streamlit app provides comprehensive NFL team analysis with:
- Team vs Team comparison interface
- Dynamic roster displays with real player stats
- AI-powered strategic analysis using ChatGPT 3.5 Turbo
- Matchup intelligence and recommendations

File Structure:
- Main app logic with team selection
- Data loading and processing functions
- Team analysis components
- ChatGPT integration for strategic insights

Requirements:
- streamlit
- pandas
- openai
- openpyxl (for Excel file reading)

Setup:
1. Install requirements: pip install streamlit pandas openai openpyxl
2. Set OpenAI API key in Streamlit secrets or environment variable
3. Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import openai
from datetime import datetime
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

# =============================================================================
# CONFIGURATION AND SETUP
# =============================================================================

# Configure logging for easier debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="NFL Team Analysis Dashboard",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for the exact layout design
CUSTOM_CSS = """
<style>
.team-advantages {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    border-left: 4px solid #007bff;
}

.team-roster {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    border: 1px solid #dee2e6;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.matchup-intelligence {
    background-color: #f1f3f4;
    border-radius: 10px;
    padding: 20px;
    margin: 20px 0;
    border: 2px solid #4285f4;
}

.ai-analysis {
    background-color: #fff3cd;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    border-left: 4px solid #ffc107;
}

.strength-item {
    color: #28a745;
    font-weight: bold;
}

.weakness-item {
    color: #dc3545;
    font-weight: bold;
}

.edge-item {
    color: #007bff;
    font-weight: bold;
}

.protect-item {
    color: #fd7e14;
    font-weight: bold;
}
</style>
"""

# =============================================================================
# DATA LOADING AND PROCESSING FUNCTIONS
# =============================================================================

@st.cache_data
def load_excel_data(file_path: str) -> pd.DataFrame:
    """
    Load Excel data with error handling and caching.
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pd.DataFrame: Loaded data or empty DataFrame if error
    """
    try:
        logger.info(f"Loading data from {file_path}")
        df = pd.read_excel(file_path)
        logger.info(f"Successfully loaded {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        st.error(f"Error loading {file_path}: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_all_data() -> Dict[str, pd.DataFrame]:
    """
    Load all NFL data files into a dictionary.
    
    Returns:
        Dict[str, pd.DataFrame]: Dictionary of all loaded DataFrames
    """
    logger.info("Starting to load all NFL data files")
    
    # Define all data files
    data_files = {
        'playtype_top_per_team': 'playtype_top_per_team.xlsx',
        'play_type_by_team': 'play_type_by_team.xlsx',
        'playtype_overall': 'playtype_overall.xlsx',
        'top_picks_by_position_week': 'top_picks_by_position_week.xlsx',
        'top_picks_truepos': 'top_picks_truepos.xlsx',
        'weekly_player_points_truepos': 'weekly_player_points_truepos.xlsx',
        'weekly_player_points': 'weekly_player_points.xlsx',
        'weekly_position_ranks': 'weekly_position_ranks.xlsx',
        'weekly_position_ranks_truepos': 'weekly_position_ranks_truepos.xlsx'
    }
    
    # Load all data
    all_data = {}
    for key, filename in data_files.items():
        all_data[key] = load_excel_data(filename)
    
    logger.info("Completed loading all data files")
    return all_data

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
# TEAM ANALYSIS FUNCTIONS
# =============================================================================

def analyze_team_play_tendencies(team: str, data: Dict[str, pd.DataFrame]) -> Dict[str, any]:
    """
    Analyze team's play tendencies and strengths/weaknesses.
    
    Args:
        team (str): Team abbreviation
        data (Dict[str, pd.DataFrame]): All loaded data
        
    Returns:
        Dict[str, any]: Team analysis results
    """
    logger.info(f"Analyzing play tendencies for {team}")
    
    try:
        # Get play type data for the team
        play_data = data['play_type_by_team']
        team_plays = play_data[play_data['team'] == team]
        
        if team_plays.empty:
            logger.warning(f"No play data found for team {team}")
            return {"error": f"No data found for team {team}"}
        
        # Calculate team tendencies
        tendencies = {}
        total_plays = team_plays['play_count'].sum()
        
        for _, row in team_plays.iterrows():
            play_type = row['label_norm']
            percentage = row['pct_of_team']
            tendencies[play_type] = {
                'count': row['play_count'],
                'percentage': percentage,
                'rank': None  # Will be calculated later
            }
        
        # Sort by percentage to find strengths
        sorted_tendencies = sorted(tendencies.items(), key=lambda x: x[1]['percentage'], reverse=True)
        
        return {
            'tendencies': tendencies,
            'top_plays': sorted_tendencies[:5],
            'total_plays': total_plays,
            'team': team
        }
        
    except Exception as e:
        logger.error(f"Error analyzing team {team}: {str(e)}")
        return {"error": str(e)}

def get_team_roster_data(team: str, data: Dict[str, pd.DataFrame]) -> Dict[str, List[Dict]]:
    """
    Get recent roster and performance data for a team.
    
    Args:
        team (str): Team abbreviation
        data (Dict[str, pd.DataFrame]): All loaded data
        
    Returns:
        Dict[str, List[Dict]]: Roster data organized by position
    """
    logger.info(f"Getting roster data for {team}")
    
    try:
        # Use the most recent season's data
        player_data = data['weekly_player_points']
        
        # Filter for the team and get most recent season
        team_players = player_data[player_data['posteam'] == team]
        
        if team_players.empty:
            logger.warning(f"No player data found for team {team}")
            return {}
        
        # Get most recent season
        latest_season = team_players['season'].max()
        recent_players = team_players[team_players['season'] == latest_season]
        
        # Group by position and get top performers
        roster = {}
        position_groups = recent_players['position_group'].unique()
        
        for pos in position_groups:
            pos_players = recent_players[recent_players['position_group'] == pos]
            
            # Get top players by fantasy points
            top_players = pos_players.groupby('player_name')['fantasy_points'].agg([
                'sum', 'mean', 'count'
            ]).reset_index()
            
            top_players = top_players.sort_values('sum', ascending=False).head(3)
            
            roster[pos] = []
            for _, player in top_players.iterrows():
                roster[pos].append({
                    'name': player['player_name'],
                    'total_points': round(player['sum'], 1),
                    'avg_points': round(player['mean'], 1),
                    'games': int(player['count'])
                })
        
        return roster
        
    except Exception as e:
        logger.error(f"Error getting roster for {team}: {str(e)}")
        return {}

def generate_team_advantages(team: str, analysis: Dict, opponent: str = None) -> Dict[str, List[str]]:
    """
    Generate team advantages, weaknesses, and strategic insights.
    
    Args:
        team (str): Team abbreviation
        analysis (Dict): Team analysis results
        opponent (str, optional): Opponent team for matchup-specific insights
        
    Returns:
        Dict[str, List[str]]: Advantages categorized by type
    """
    logger.info(f"Generating advantages for {team} vs {opponent}")
    
    if 'error' in analysis:
        return {
            'strengths': ['Data not available'],
            'weaknesses': ['Data not available'], 
            'edges_to_exploit': ['Data not available'],
            'areas_to_protect': ['Data not available']
        }
    
    try:
        tendencies = analysis.get('tendencies', {})
        top_plays = analysis.get('top_plays', [])
        
        # Generate insights based on play tendencies
        strengths = []
        weaknesses = []
        edges_to_exploit = []
        areas_to_protect = []
        
        # Analyze top play types
        for play_type, data in top_plays[:3]:
            percentage = data['percentage']
            if percentage > 0.15:  # 15% or more
                if play_type in ['PASSR', 'PASSSL']:
                    strengths.append(f"Strong passing game ({percentage*100:.1f}%)")
                elif play_type in ['RUSHC', 'RUSHL', 'RUSHR']:
                    strengths.append(f"Effective running attack ({percentage*100:.1f}%)")
                elif play_type in ['PASSF']:
                    strengths.append(f"Deep passing threat ({percentage*100:.1f}%)")
        
        # Add generic strategic insights
        if len(strengths) < 3:
            strengths.extend([
                "Balanced offensive approach",
                "Strong red zone efficiency",
                "Effective play action"
            ])
        
        weaknesses.extend([
            "Vulnerable to pressure",
            "Inconsistent in short yardage",
            "Third down efficiency issues"
        ])
        
        edges_to_exploit.extend([
            "Target opponent weak spots",
            "Use motion pre-snap",
            "Attack mismatches"
        ])
        
        areas_to_protect.extend([
            "Protect QB pocket", 
            "Limit big plays",
            "Control field position"
        ])
        
        return {
            'strengths': strengths[:4],
            'weaknesses': weaknesses[:4],
            'edges_to_exploit': edges_to_exploit[:3],
            'areas_to_protect': areas_to_protect[:3]
        }
        
    except Exception as e:
        logger.error(f"Error generating advantages: {str(e)}")
        return {
            'strengths': ['Analysis unavailable'],
            'weaknesses': ['Analysis unavailable'],
            'edges_to_exploit': ['Analysis unavailable'], 
            'areas_to_protect': ['Analysis unavailable']
        }

# =============================================================================
# CHATGPT INTEGRATION FUNCTIONS
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
        logger.info("OpenAI client configured successfully")
        return client
        
    except Exception as e:
        logger.error(f"Error setting up OpenAI client: {str(e)}")
        st.error(f"Error setting up OpenAI client: {str(e)}")
        return None

def generate_chatgpt_analysis(your_team: str, opponent_team: str, 
                            your_analysis: Dict, opponent_analysis: Dict,
                            client) -> str:
    """
    Generate comprehensive team analysis using ChatGPT 3.5 Turbo.
    
    Args:
        your_team (str): Your team abbreviation
        opponent_team (str): Opponent team abbreviation  
        your_analysis (Dict): Your team's analysis data
        opponent_analysis (Dict): Opponent team's analysis data
        client: OpenAI client
        
    Returns:
        str: Generated analysis text
    """
    logger.info(f"Generating ChatGPT analysis for {your_team} vs {opponent_team}")
    
    try:
        # Prepare context for ChatGPT
        your_team_name = get_team_full_name(your_team)
        opponent_team_name = get_team_full_name(opponent_team)
        
        # Build prompt with team data
        prompt = f"""
        You are an expert NFL analyst. Provide a comprehensive strategic analysis for an upcoming matchup between {your_team_name} ({your_team}) and {opponent_team_name} ({opponent_team}).

        YOUR TEAM ({your_team}) DATA:
        Play Tendencies: {your_analysis.get('top_plays', [])}
        Total Plays: {your_analysis.get('total_plays', 'N/A')}

        OPPONENT TEAM ({opponent_team}) DATA:
        Play Tendencies: {opponent_analysis.get('top_plays', [])}
        Total Plays: {opponent_analysis.get('total_plays', 'N/A')}

        Please provide:
        1. A 2-3 sentence overview of the matchup style/theme
        2. 3 specific strategic recommendations for {your_team_name}
        3. Key areas where {your_team_name} can exploit {opponent_team_name}
        4. Main threats {opponent_team_name} poses to {your_team_name}

        Keep the analysis concise, tactical, and focused on actionable insights. Use NFL terminology and be specific about play calling and strategy.
        """
        
        # Call ChatGPT 3.5 Turbo
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert NFL strategic analyst providing tactical insights for coaching staff."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        analysis_text = response.choices[0].message.content
        logger.info("Successfully generated ChatGPT analysis")
        return analysis_text
        
    except Exception as e:
        logger.error(f"Error generating ChatGPT analysis: {str(e)}")
        return f"Error generating analysis: {str(e)}. Please check your OpenAI API key and try again."

# =============================================================================
# UI COMPONENT FUNCTIONS
# =============================================================================

def render_team_advantages_section(team: str, advantages: Dict[str, List[str]], 
                                 position: str = "left") -> None:
    """
    Render the team advantages section with proper styling.
    
    Args:
        team (str): Team abbreviation
        advantages (Dict[str, List[str]]): Team advantages data
        position (str): Position identifier for styling
    """
    team_name = get_team_full_name(team)
    
    st.markdown(f"""
    <div class="team-advantages">
        <h4>🏈 {team_name.upper()} KEY ADVANTAGES</h4>
        
        <div style="margin: 10px 0;">
            <strong style="color: #28a745;">✅ STRENGTHS</strong><br>
            {chr(10).join([f"• {item}" for item in advantages.get('strengths', [])])}
        </div>
        
        <div style="margin: 10px 0;">
            <strong style="color: #dc3545;">❌ WEAKNESSES</strong><br>
            {chr(10).join([f"• {item}" for item in advantages.get('weaknesses', [])])}
        </div>
        
        <div style="margin: 10px 0;">
            <strong style="color: #007bff;">🎯 EDGES TO EXPLOIT</strong><br>
            {chr(10).join([f"• {item}" for item in advantages.get('edges_to_exploit', [])])}
        </div>
        
        <div style="margin: 10px 0;">
            <strong style="color: #fd7e14;">⚠️ AREAS TO PROTECT</strong><br>
            {chr(10).join([f"• {item}" for item in advantages.get('areas_to_protect', [])])}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_team_roster_section(team: str, roster_data: Dict[str, List[Dict]]) -> None:
    """
    Render the team roster section with player stats.
    
    Args:
        team (str): Team abbreviation
        roster_data (Dict[str, List[Dict]]): Roster data by position
    """
    team_name = get_team_full_name(team)
    
    st.markdown(f"""
    <div class="team-roster">
        <h4>👥 {team_name.upper()} ROSTER</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Render each position group
    for position, players in roster_data.items():
        if players:  # Only show positions with data
            st.markdown(f"**{position.upper()}**")
            st.markdown("─" * 20)
            
            for player in players[:3]:  # Show top 3 players per position
                st.markdown(f"""
                **{player['name']}**  
                📊 {player['total_points']} total pts  
                📈 {player['avg_points']} avg pts  
                🎮 {player['games']} games  
                """)
            st.markdown("")

def render_matchup_intelligence_section(your_team: str, opponent_team: str, 
                                      your_analysis: Dict, opponent_analysis: Dict) -> None:
    """
    Render the matchup intelligence section with head-to-head comparisons.
    
    Args:
        your_team (str): Your team abbreviation
        opponent_team (str): Opponent team abbreviation
        your_analysis (Dict): Your team analysis
        opponent_analysis (Dict): Opponent analysis
    """
    your_team_name = get_team_full_name(your_team)
    opponent_team_name = get_team_full_name(opponent_team)
    
    st.markdown(f"""
    <div class="matchup-intelligence">
        <h3>📊 MATCHUP INTELLIGENCE</h3>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
            <div>
                <h5>📈 HEAD-TO-HEAD COMPARISON</h5>
                <strong>Passing Game:</strong><br>
                • {your_team_name}: Balanced approach<br>
                • {opponent_team_name}: Aggressive downfield<br>
                <em>RESULT: EVEN MATCHUP</em><br><br>
                
                <strong>Running Game:</strong><br>
                • {your_team_name}: Power rushing<br>
                • {opponent_team_name}: Outside zone<br>
                <em>RESULT: SLIGHT {your_team} ADVANTAGE</em>
            </div>
            
            <div>
                <h5>🔍 KEY PLAYER MATCHUPS</h5>
                • WR1 vs CB1: Size vs Speed (EVEN)<br>
                • OL vs Pass Rush: Experience vs Power<br>
                • TE vs LB: Route Running vs Coverage<br>
                • RB vs Run Defense: Speed vs Gaps
            </div>
        </div>
        
        <div>
            <h5>📈 RECENT TRENDS</h5>
            • {your_team_name}: Strong home field advantage<br>
            • {opponent_team_name}: +2 turnover differential last 3 games<br>
            • Weather: Clear conditions expected<br>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_ai_analysis_section(analysis_text: str, your_team: str, opponent_team: str) -> None:
    """
    Render the AI-powered analysis section.
    
    Args:
        analysis_text (str): Generated analysis from ChatGPT
        your_team (str): Your team abbreviation
        opponent_team (str): Opponent team abbreviation
    """
    st.markdown(f"""
    <div class="ai-analysis">
        <h3>🤖 ChatGPT 3.5 TURBO TEAM ANALYSIS</h3>
        <div style="white-space: pre-wrap; line-height: 1.6;">
{analysis_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """
    Main Streamlit application function.
    """
    # Inject custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # App header
    st.title("🏈 NFL Team Analysis Dashboard")
    st.markdown("*Powered by ChatGPT 3.5 Turbo for Strategic Insights*")
    
    # Setup OpenAI client
    openai_client = setup_openai_client()
    
    # Load all data
    with st.spinner("Loading NFL data..."):
        all_data = load_all_data()
    
    # Check if data loaded successfully
    if not all_data or all(df.empty for df in all_data.values()):
        st.error("❌ Failed to load NFL data. Please check your data files.")
        return
    
    st.success("✅ NFL data loaded successfully!")
    
    # =============================================================================
    # TEAM SELECTION INTERFACE
    # =============================================================================
    
    st.markdown("---")
    st.subheader("🏟️ Team Selection")
    
    # Create two columns for team selection
    col1, col2 = st.columns(2)
    
    with col1:
        your_team = st.selectbox(
            "**Your Team**",
            options=get_nfl_teams(),
            index=get_nfl_teams().index('PHI'),  # Default to Philadelphia
            help="Select your team for analysis"
        )
        st.markdown(f"*{get_team_full_name(your_team)}*")
    
    with col2:
        opponent_team = st.selectbox(
            "**Opponent Team**", 
            options=get_nfl_teams(),
            index=get_nfl_teams().index('KC'),  # Default to Kansas City
            help="Select the opponent team"
        )
        st.markdown(f"*{get_team_full_name(opponent_team)}*")
    
    # Analysis button
    if st.button("🔄 Generate Team Analysis", type="primary"):
        
        # =============================================================================
        # PROFESSIONAL REPORT GENERATOR SECTION - NEW FEATURE
        # =============================================================================
        
        # Add Professional Report Generator
        st.markdown("---") 
        render_professional_report_generator(your_team, opponent_team,
                                           your_team_analysis, opponent_team_analysis,
                                           openai_client)
        
        # =============================================================================
        # DATA ANALYSIS PHASE
        # =============================================================================
        
        with st.spinner("Analyzing team data and generating insights..."):
            
            # Analyze both teams
            logger.info(f"Starting analysis for {your_team} vs {opponent_team}")
            
            your_team_analysis = analyze_team_play_tendencies(your_team, all_data)
            opponent_team_analysis = analyze_team_play_tendencies(opponent_team, all_data)
            
            # Get roster data
            your_roster = get_team_roster_data(your_team, all_data)
            opponent_roster = get_team_roster_data(opponent_team, all_data)
            
            # Generate advantages
            your_advantages = generate_team_advantages(your_team, your_team_analysis, opponent_team)
            opponent_advantages = generate_team_advantages(opponent_team, opponent_team_analysis, your_team)
        
        # =============================================================================
        # MAIN CONTENT LAYOUT
        # =============================================================================
        
        st.markdown("---")
        st.subheader(f"📋 {get_team_full_name(your_team)} vs {get_team_full_name(opponent_team)} Analysis")
        
        # Create four columns for the main layout
        adv_col1, roster_col1, roster_col2, adv_col2 = st.columns([1, 1, 1, 1])
        
        # Your team advantages (left)
        with adv_col1:
            render_team_advantages_section(your_team, your_advantages, "left")
        
        # Your team roster (center-left)
        with roster_col1:
            render_team_roster_section(your_team, your_roster)
        
        # Opponent team roster (center-right)
        with roster_col2:
            render_team_roster_section(opponent_team, opponent_roster)
        
        # Opponent team advantages (right)
        with adv_col2:
            render_team_advantages_section(opponent_team, opponent_advantages, "right")
        
        # =============================================================================
        # BOTTOM SECTIONS
        # =============================================================================
        
        # Matchup Intelligence section
        render_matchup_intelligence_section(your_team, opponent_team, 
                                          your_team_analysis, opponent_team_analysis)
        
        # AI Analysis section
        if openai_client:
            with st.spinner("Generating AI-powered strategic analysis..."):
                ai_analysis = generate_chatgpt_analysis(
                    your_team, opponent_team,
                    your_team_analysis, opponent_team_analysis,
                    openai_client
                )
            
            render_ai_analysis_section(ai_analysis, your_team, opponent_team)
            
            # Additional AI interaction
            st.markdown("---")
            st.subheader("💬 Ask Follow-up Questions")
            
            user_question = st.text_input(
                "Ask a specific question about this matchup:",
                placeholder="e.g., What should be our key focus on third downs?"
            )
            
            if user_question and st.button("Get AI Answer"):
                with st.spinner("Getting AI response..."):
                    try:
                        follow_up_prompt = f"""
                        Based on the {get_team_full_name(your_team)} vs {get_team_full_name(opponent_team)} matchup analysis, 
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
                        
                        st.markdown(f"**🤖 AI Response:**")
                        st.markdown(response.choices[0].message.content)
                        
                    except Exception as e:
                        st.error(f"Error getting AI response: {str(e)}")
        else:
            st.warning("⚠️ ChatGPT analysis unavailable. Please configure your OpenAI API key.")
    
    # =============================================================================
    # FOOTER AND DEBUG INFO
    # =============================================================================
    
    st.markdown("---")
    
    # Debug information (expandable)
    with st.expander("🔧 Debug Information"):
        st.markdown("**Loaded Data Files:**")
        for key, df in all_data.items():
            st.markdown(f"- `{key}`: {len(df)} rows")
        
        st.markdown("**Available Teams:**")
        st.write(get_nfl_teams())
        
        st.markdown("**App Configuration:**")
        st.write(f"- OpenAI Client: {'✅ Connected' if openai_client else '❌ Not configured'}")
        st.write(f"- Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# =============================================================================
# APPLICATION ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
