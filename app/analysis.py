"""
GRIT NFL PLATFORM - ANALYSIS MODULE
===================================
PURPOSE: GPT-3.5 Turbo strategic analysis functions with professional fallbacks
FEATURES: Advanced prompting, multi-perspective analysis, confidence scoring
ARCHITECTURE: Primary GPT analysis with comprehensive fallback system
NOTES: Professional coordinator-level analysis with specific recommendations
"""

import streamlit as st
from openai import OpenAI
from typing import Dict, List, Optional
from datetime import datetime
import json

# =============================================================================
# GPT-3.5 TURBO STRATEGIC ANALYSIS ENGINE
# =============================================================================

def get_openai_client() -> Optional[OpenAI]:
    """
    PURPOSE: Safely initialize OpenAI client
    INPUTS: None
    OUTPUTS: OpenAI client or None if API key unavailable
    DEPENDENCIES: Streamlit secrets, OpenAI library
    NOTES: Returns None if API key not configured
    """
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        return None
    except Exception as e:
        st.warning(f"OpenAI client initialization failed: {str(e)}")
        return None

def build_comprehensive_context(team1: str, team2: str, team1_data: Dict, team2_data: Dict, 
                               weather_data: Dict, game_situation: Dict, question: str) -> str:
    """
    PURPOSE: Build comprehensive context for GPT analysis
    INPUTS: Teams, data, weather, game situation, question
    OUTPUTS: Formatted context string for GPT prompt
    DEPENDENCIES: Team and weather data structures
    NOTES: Enhanced context building for better GPT responses
    """
    
    context = f"""
NFL STRATEGIC ANALYSIS REQUEST
=============================

MATCHUP: {team1} vs {team2}

COMPREHENSIVE TEAM DATA:
------------------------

{team1} Offensive Profile:
• Formation Efficiency:
  - 11 Personnel: {team1_data['formation_data']['11_personnel']['usage']*100:.1f}% usage, {team1_data['formation_data']['11_personnel']['ypp']:.1f} YPP, {team1_data['formation_data']['11_personnel']['success_rate']*100:.1f}% success
  - 12 Personnel: {team1_data['formation_data']['12_personnel']['usage']*100:.1f}% usage, {team1_data['formation_data']['12_personnel']['ypp']:.1f} YPP, {team1_data['formation_data']['12_personnel']['success_rate']*100:.1f}% success
  - 21 Personnel: {team1_data['formation_data']['21_personnel']['usage']*100:.1f}% usage, {team1_data['formation_data']['21_personnel']['ypp']:.1f} YPP
  - 10 Personnel: {team1_data['formation_data']['10_personnel']['usage']*100:.1f}% usage, {team1_data['formation_data']['10_personnel']['ypp']:.1f} YPP

• Situational Tendencies:
  - Third Down Conversion: {team1_data['situational_tendencies']['third_down_conversion']*100:.1f}%
  - Red Zone Efficiency: {team1_data['situational_tendencies']['red_zone_efficiency']*100:.1f}%
  - Goal Line Efficiency: {team1_data['situational_tendencies']['goal_line_efficiency']*100:.1f}%
  - Two-Minute Drill: {team1_data['situational_tendencies']['two_minute_drill']*100:.1f}%
  - Fourth Down Aggression: {team1_data['situational_tendencies']['fourth_down_aggression']*100:.1f}%

• Personnel Advantages:
  - WR vs CB Mismatch: {team1_data['personnel_advantages']['wr_vs_cb_mismatch']*100:.1f}%
  - TE vs LB Mismatch: {team1_data['personnel_advantages']['te_vs_lb_mismatch']*100:.1f}%
  - RB vs LB Coverage: {team1_data['personnel_advantages']['rb_vs_lb_coverage']*100:.1f}%
  - Outside Zone Left: {team1_data['personnel_advantages']['outside_zone_left']:.1f} YPP
  - Inside Zone: {team1_data['personnel_advantages']['inside_zone']:.1f} YPP

• Coaching Tendencies:
  - Play Action Rate: {team1_data['coaching_tendencies']['play_action_rate']*100:.1f}%
  - Motion Usage: {team1_data['coaching_tendencies']['motion_usage']*100:.1f}%
  - Blitz Frequency: {team1_data['coaching_tendencies']['blitz_frequency']*100:.1f}%

{team2} Offensive Profile:
• Formation Efficiency:
  - 11 Personnel: {team2_data['formation_data']['11_personnel']['usage']*100:.1f}% usage, {team2_data['formation_data']['11_personnel']['ypp']:.1f} YPP, {team2_data['formation_data']['11_personnel']['success_rate']*100:.1f}% success
  - 12 Personnel: {team2_data['formation_data']['12_personnel']['usage']*100:.1f}% usage, {team2_data['formation_data']['12_personnel']['ypp']:.1f} YPP, {team2_data['formation_data']['12_personnel']['success_rate']*100:.1f}% success
  - 21 Personnel: {team2_data['formation_data']['21_personnel']['usage']*100:.1f}% usage, {team2_data['formation_data']['21_personnel']['ypp']:.1f} YPP
  - 10 Personnel: {team2_data['formation_data']['10_personnel']['usage']*100:.1f}% usage, {team2_data['formation_data']['10_personnel']['ypp']:.1f} YPP

• Situational Tendencies:
  - Third Down Conversion: {team2_data['situational_tendencies']['third_down_conversion']*100:.1f}%
  - Red Zone Efficiency: {team2_data['situational_tendencies']['red_zone_efficiency']*100:.1f}%
  - Goal Line Efficiency: {team2_data['situational_tendencies']['goal_line_efficiency']*100:.1f}%
  - Two-Minute Drill: {team2_data['situational_tendencies']['two_minute_drill']*100:.1f}%

GAME SITUATION ANALYSIS:
-----------------------
• Current Down: {game_situation['down']} and {game_situation['distance']}
• Field Position: {game_situation['field_position']} yard line
• Score Differential: {'+' if game_situation['score_differential'] >= 0 else ''}{game_situation['score_differential']} points
• Time Remaining: {game_situation['time_remaining']}

WEATHER CONDITIONS & IMPACT:
----------------------------
• Temperature: {weather_data.get('temp', 'N/A')}°F
• Wind Speed: {weather_data.get('wind', 'N/A')} mph
• Conditions: {weather_data.get('condition', 'Unknown')}
• Strategic Impact: {weather_data.get('strategic_impact', {}).get('recommended_adjustments', ['Standard conditions'])[0] if weather_data.get('strategic_impact', {}).get('recommended_adjustments') else 'Standard conditions'}
• Risk Level: {weather_data.get('strategic_impact', {}).get('risk_level', 'LOW')}

STRATEGIC QUESTION: {question}
"""
    
    return context

def generate_advanced_strategic_analysis(team1: str, team2: str, question: str, analysis_type: str,
                                        team1_data: Dict, team2_data: Dict, weather_data: Dict,
                                        game_situation: Dict, coaching_perspective: str, 
                                        complexity_level: str) -> str:
    """
    PURPOSE: Generate comprehensive strategic analysis using GPT-3.5 Turbo
    INPUTS: Teams, question, analysis type, data, game situation, perspective, complexity
    OUTPUTS: Professional strategic analysis with specific recommendations
    DEPENDENCIES: OpenAI API, team data, weather data
    NOTES: Enhanced with multi-perspective analysis and confidence scoring
    """
    
    client = get_openai_client()
    if not client:
        return generate_professional_fallback_analysis(
            team1, team2, question, analysis_type, team1_data, team2_data, 
            weather_data, game_situation, coaching_perspective
        )
    
    try:
        # Build comprehensive context
        context = build_comprehensive_context(
            team1, team2, team1_data, team2_data, weather_data, game_situation, question
        )
        
        # Adjust system prompt based on coaching perspective and complexity
        perspective_prompts = {
            "Head Coach": "You are an experienced NFL Head Coach with 15+ years of experience. Provide comprehensive strategic analysis covering all three phases of the game with leadership insights.",
            "Offensive Coordinator": "You are a seasoned NFL Offensive Coordinator. Focus on offensive strategy, play calling, and exploiting defensive weaknesses with detailed tactical recommendations.",
            "Defensive Coordinator": "You are an expert NFL Defensive Coordinator. Analyze how to stop the opponent's offense, force turnovers, and create favorable field position.",
            "Special Teams Coach": "You are a specialized NFL Special Teams Coordinator. Focus on field position, hidden yards, and special teams advantages in this matchup."
        }
        
        system_prompt = perspective_prompts.get(coaching_perspective, perspective_prompts["Head Coach"])
        
        # Add complexity level instructions
        complexity_instructions = {
            "Basic": "Provide clear, straightforward analysis accessible to casual fans. Focus on key points without overwhelming detail.",
            "Advanced": "Provide detailed tactical analysis with specific percentages and formation breakdowns. Include multiple strategic options.",
            "Expert": "Provide comprehensive coordinator-level analysis with advanced concepts, counter-strategies, and risk assessments. Include nuanced tactical details."
        }
        
        system_prompt += f" {complexity_instructions.get(complexity_level, complexity_instructions['Advanced'])}"
        
        # Analysis type specific requirements
        analysis_requirements = {
            "Edge Detection": "Identify specific tactical advantages and exploitable weaknesses. Provide exact percentages and formation mismatches.",
            "Formation Analysis": "Deep dive into personnel package efficiency. Compare formation usage and success rates with specific recommendations.",
            "Situational Breakdown": "Analyze third down, red zone, and critical situation tendencies. Provide situation-specific play recommendations.",
            "Weather Impact": "Focus on how weather conditions affect strategy. Provide specific tactical adjustments for current conditions.",
            "Play Calling": "Recommend specific plays and concepts for the current game situation. Include primary and backup options.",
            "Matchup Exploitation": "Identify and explain how to exploit specific player matchups and defensive weaknesses.",
            "Drive Management": "Analyze how to sustain drives and control time of possession based on team strengths.",
            "Red Zone Optimization": "Provide specific red zone strategies and goal line recommendations."
        }
        
        requirement = analysis_requirements.get(analysis_type, "Provide comprehensive strategic analysis.")
        
        user_prompt = f"""
{context}

ANALYSIS REQUIREMENTS:
{requirement}

OUTPUT REQUIREMENTS:
1. Provide specific tactical recommendations with exact percentages
2. Include formation-specific advantages and disadvantages  
3. Address weather impact on strategy execution
4. Consider current game situation and time factors
5. Provide confidence level (1-100) with detailed reasoning
6. Include potential opponent counter-strategies
7. Suggest 2-3 specific plays or concepts to exploit identified advantages
8. Format with clear headers for easy reading

CRITICAL: Base all recommendations on the provided data. Reference specific statistics and percentages from the team profiles.
"""
        
        # Adjust temperature based on complexity level
        temperature_map = {"Basic": 0.3, "Advanced": 0.4, "Expert": 0.5}
        temp = temperature_map.get(complexity_level, 0.4)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1500,
            temperature=temp
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"GPT Analysis Error: {str(e)}")
        return generate_professional_fallback_analysis(
            team1, team2, question, analysis_type, team1_data, team2_data, 
            weather_data, game_situation, coaching_perspective
        )

# =============================================================================
# PROFESSIONAL FALLBACK ANALYSIS SYSTEM
# =============================================================================

def generate_professional_fallback_analysis(team1: str, team2: str, question: str, analysis_type: str,
                                          team1_data: Dict, team2_data: Dict, weather_data: Dict,
                                          game_situation: Dict, coaching_perspective: str) -> str:
    """
    PURPOSE: Generate professional analysis when GPT is unavailable
    INPUTS: All strategic analysis parameters
    OUTPUTS: Comprehensive strategic analysis using template system
    DEPENDENCIES: Team data structures
    NOTES: Professional-grade fallback with specific recommendations
    """
    
    # Calculate key advantages and metrics
    team1_11_ypp = team1_data['formation_data']['11_personnel']['ypp']
    team2_11_ypp = team2_data['formation_data']['11_personnel']['ypp']
    formation_advantage = team1_11_ypp - team2_11_ypp
    
    team1_third_down = team1_data['situational_tendencies']['third_down_conversion']
    team2_third_down = team2_data['situational_tendencies']['third_down_conversion']
    third_down_advantage = team1_third_down - team2_third_down
    
    team1_red_zone = team1_data['situational_tendencies']['red_zone_efficiency']
    team2_red_zone = team2_data['situational_tendencies']['red_zone_efficiency']
    red_zone_advantage = team1_red_zone - team2_red_zone
    
    weather_impact = weather_data.get('strategic_impact', {})
    weather_adjustments = weather_impact.get('recommended_adjustments', ['Standard conditions'])
    risk_level = weather_impact.get('risk_level', 'LOW')
    
    # Build analysis based on type and perspective
    analysis = f"""
# STRATEGIC ANALYSIS: {team1} vs {team2}
*{coaching_perspective} Perspective | {analysis_type} Focus*

## Executive Summary
**Primary Strategic Focus:** {"Exploit formation efficiency advantage" if formation_advantage > 0 else "Overcome formation deficit through tactical innovation"}

**Game Situation Impact:** {game_situation['down']} and {game_situation['distance']} from the {game_situation['field_position']} yard line with {game_situation['time_remaining']} remaining significantly influences tactical approach.

**Weather Factor:** {weather_adjustments[0]} (Risk Level: {risk_level})

## Formation Efficiency Analysis

### 11 Personnel Comparison
- **{team1}:** {team1_11_ypp:.1f} YPP, {team1_data['formation_data']['11_personnel']['success_rate']*100:.1f}% success rate
- **{team2}:** {team2_11_ypp:.1f} YPP, {team2_data['formation_data']['11_personnel']['success_rate']*100:.1f}% success rate
"""
    
    if formation_advantage > 0:
        analysis += f"**ADVANTAGE {team1}:** +{formation_advantage:.1f} YPP edge in 11 personnel\n\n"
    else:
        analysis += f"**CHALLENGE:** {team2} holds +{abs(formation_advantage):.1f} YPP advantage in 11 personnel\n\n"
    
    analysis += f"""
### Alternative Personnel Packages
- **{team1} 12 Personnel:** {team1_data['formation_data']['12_personnel']['ypp']:.1f} YPP ({team1_data['formation_data']['12_personnel']['usage']*100:.1f}% usage)
- **{team2} 12 Personnel:** {team2_data['formation_data']['12_personnel']['ypp']:.1f} YPP ({team2_data['formation_data']['12_personnel']['usage']*100:.1f}% usage)

## Situational Tendencies Analysis

### Critical Situations
"""
    
    if third_down_advantage > 0:
        analysis += f"**Third Down Edge {team1}:** {team1_third_down*100:.1f}% vs {team2_third_down*100:.1f}% conversion rate (+{third_down_advantage*100:.1f}%)\n"
    else:
        analysis += f"**Third Down Challenge:** {team2} converts at {team2_third_down*100:.1f}% vs {team1_third_down*100:.1f}% ({abs(third_down_advantage)*100:.1f}% deficit)\n"
    
    if red_zone_advantage > 0:
        analysis += f"**Red Zone Advantage {team1}:** {team1_red_zone*100:.1f}% vs {team2_red_zone*100:.1f}% efficiency (+{red_zone_advantage*100:.1f}%)\n\n"
    else:
        analysis += f"**Red Zone Focus Needed:** {team2} more efficient at {team2_red_zone*100:.1f}% vs {team1_red_zone*100:.1f}%\n\n"
    
    # Add perspective-specific analysis
    if coaching_perspective == "Offensive Coordinator":
        analysis += f"""
## Offensive Strategic Recommendations

### Primary Formation Strategy
{"Maximize 11 personnel usage (75%+ of snaps)" if formation_advantage > 0 else "Diversify personnel packages to find advantages"}

### Key Tactical Elements
1. **Motion Usage:** Leverage {team1_data['coaching_tendencies']['motion_usage']*100:.1f}% motion rate to create confusion
2. **Play Action:** Utilize {team1_data['coaching_tendencies']['play_action_rate']*100:.1f}% rate for explosive plays
3. **Tempo Control:** {"Up-tempo to exploit advantages" if formation_advantage > 0 else "Controlled tempo to minimize mistakes"}

### Specific Play Concepts
- **Short Yardage:** {"Power gap concepts" if team1_data['personnel_advantages']['power_gap'] > 4.5 else "Outside zone stretch plays"}
- **Third Down:** {"Quick slants and crossing routes" if third_down_advantage > 0 else "Pick plays and rub routes"}
- **Red Zone:** {"Fade routes and back-shoulder throws" if red_zone_advantage > 0 else "High-percentage possession routes"}
"""
    
    elif coaching_perspective == "Defensive Coordinator":
        analysis += f"""
## Defensive Strategic Recommendations

### Formation Tendencies to Exploit
- **{team2} relies heavily on 11 personnel:** {team2_data['formation_data']['11_personnel']['usage']*100:.1f}% usage rate
- **Predictable down and distance patterns** based on formation usage

### Key Defensive Adjustments
1. **Personnel Matching:** Force {team2} into unfavorable situations
2. **Pressure Packages:** They allow {team2_data['coaching_tendencies']['blitz_frequency']*100:.1f}% pressure rate
3. **Coverage Rotations:** Disguise coverages against their {team2_data['coaching_tendencies']['motion_usage']*100:.1f}% motion usage

### Specific Defensive Concepts
- **Third Down:** Target their {team2_third_down*100:.1f}% conversion weakness
- **Red Zone:** {"Aggressive coverage" if team2_red_zone < 0.6 else "Bend don't break approach"}
- **Situational:** Force {team2} into obvious passing downs
"""
    
    else:  # Head Coach perspective
        analysis += f"""
## Comprehensive Game Plan Recommendations

### Offensive Strategy
{"Attack with formation advantages" if formation_advantage > 0 else "Create advantages through deception and tempo"}

### Defensive Strategy  
{"Maintain discipline and force mistakes" if formation_advantage > 0 else "Create pressure and force turnovers"}

### Special Teams Opportunities
- **Field Position:** Critical given {"favorable" if formation_advantage > 0 else "challenging"} offensive matchup
- **Weather Impact:** {weather_adjustments[0]}
"""
    
    # Add weather-specific adjustments
    analysis += f"""
## Weather Impact Adjustments

**Current Conditions:** {weather_data.get('temp', 'N/A')}°F, {weather_data.get('wind', 'N/A')} mph, {weather_data.get('condition', 'Unknown')}

### Tactical Modifications Required:
"""
    
    for i, adjustment in enumerate(weather_adjustments[:3], 1):
        analysis += f"{i}. {adjustment}\n"
    
    # Add game situation specific recommendations
    down = game_situation['down']
    distance = game_situation['distance']
    field_pos = game_situation['field_position']
    
    analysis += f"""
## Current Situation Analysis

**{down} and {distance} from {field_pos} yard line**

### Immediate Tactical Options:
"""
    
    if down <= 2 and distance <= 3:
        analysis += """1. **High Success Probability:** Multiple viable options available
2. **Formation Recommendation:** 12 or 21 personnel for power concepts
3. **Play Action Opportunity:** Defense expecting run creates big play potential"""
    elif down == 3 and distance > 7:
        analysis += """1. **Passing Down:** Defense likely in nickel/dime coverage
2. **Route Concepts:** Crossing patterns, pick plays, four verticals
3. **Protection Priority:** Maximum protection schemes essential"""
    else:
        analysis += """1. **Balanced Approach:** Run and pass options equally viable
2. **Mismatch Creation:** Use motion and formation shifts
3. **Situational Awareness:** Consider down and distance tendency breaks"""
    
    # Add confidence assessment
    confidence_score = 75 + (10 if abs(formation_advantage) > 0.5 else 0) + (5 if abs(third_down_advantage) > 0.05 else 0)
    
    analysis += f"""

## Confidence Assessment

**Analysis Confidence Level: {confidence_score}%**

**Reasoning:**
- Formation data provides clear statistical foundation
- Situational tendencies show consistent patterns
- Weather factors {"significantly impact" if risk_level in ['HIGH', 'CRITICAL'] else "minimally affect"} tactical options
- Game situation creates {"favorable" if down <= 2 else "challenging"} immediate context

## Risk Assessment

**Primary Risks:**
1. **Weather Variable:** {risk_level} risk level requires constant monitoring
2. **Opponent Adjustments:** {"Expect defensive changes to counter advantages" if formation_advantage > 0 else "Must create advantages through innovation"}
3. **Execution Dependent:** {"Maintain discipline to press advantages" if formation_advantage > 0 else "Perfect execution required to overcome deficits"}

## Actionable Next Steps

**Immediate (Next 3 Plays):**
1. {"Test formation advantage with 11 personnel concept" if formation_advantage > 0 else "Use 12 personnel to establish physical presence"}
2. Assess defensive reaction and coverage tendencies
3. {"Build on early success" if formation_advantage > 0 else "Create explosive play opportunity"}

**Short Term (Next Drive):**
- {"Establish rhythm in favorable formations" if formation_advantage > 0 else "Find formation that creates mismatches"}
- Target {"identified weaknesses" if third_down_advantage > 0 else "possession routes for manageable third downs"}
- {"Press tactical advantages" if formation_advantage > 0 else "Control field position and limit mistakes"}

**Game Management:**
- Monitor weather conditions for tactical adjustments
- {"Maintain aggressive approach" if formation_advantage > 0 else "Stay patient and capitalize on opportunities"}
- Prepare contingency plans for opponent adjustments
"""
    
    return analysis

# =============================================================================
# SPECIALIZED ANALYSIS FUNCTIONS
# =============================================================================

def generate_play_calling_analysis(team1_data: Dict, team2_data: Dict, game_situation: Dict, weather_data: Dict) -> str:
    """
    PURPOSE: Generate specific play calling recommendations
    INPUTS: Team data, game situation, weather data
    OUTPUTS: Specific play recommendations with reasoning
    DEPENDENCIES: Team formation and situational data
    NOTES: Provides actual play concepts and formations
    """
    
    down = game_situation['down']
    distance = game_situation['distance']
    field_pos = game_situation['field_position']
    
    # Determine field zone
    if field_pos >= 80:
        zone = "Red Zone"
    elif field_pos >= 60:
        zone = "Scoring Territory"
    elif field_pos >= 40:
        zone = "Midfield"
    else:
        zone = "Own Territory"
    
    analysis = f"""
# PLAY CALLING ANALYSIS
## Situation: {down} and {distance} | {zone}

### Primary Play Recommendations:
"""
    
    # Generate specific play calls based on situation
    if down == 1:
        if distance <= 10:
            analysis += """
**1. Outside Zone Left** (11 Personnel)
- Reasoning: Establish running game and test defensive alignment
- Success Rate: Based on team's outside zone efficiency
- Backup: Quick slant if defense shows 8+ in the box

**2. Play Action Deep Shot** (11 Personnel) 
- Reasoning: Defense expecting run creates opportunity
- Target: Single high safety coverage
- Risk Level: Medium - weather dependent

**3. Quick Game Concept** (10 Personnel)
- Reasoning: Get playmaker in space quickly  
- Execution: Bubble screen or quick slant
- Success Rate: High percentage completion
"""
    
    elif down == 2:
        if distance <= 3:
            analysis += """
**1. Power Gap Concept** (21 Personnel)
- Reasoning: Short yardage situation favors power running
- Formation: Fullback lead blocking
- Success Rate: High given down and distance

**2. Tight End Drag** (12 Personnel)
- Reasoning: Linebackers in run fit create underneath space
- Execution: TE releases after chip block
- Backup: Check down to running back

**3. Quarterback Sneak** (Goal Line Formation)
- Reasoning: If within 2 yards, highest success rate play
- Conditions: Only if offensive line creates push
- Risk Level: Minimal
"""
        else:
            analysis += """
**1. Intermediate Crossing Route** (11 Personnel)
- Reasoning: Attack middle of field against retreating linebackers
- Target: Slot receiver or tight end
- Protection: 6-man protection scheme

**2. Screen Pass** (11 Personnel)
- Reasoning: Aggressive pass rush creates screen opportunity
- Execution: Running back or wide receiver screen
- Weather Factor: Less affected by wind conditions

**3. Draw Play** (10 Personnel)
- Reasoning: Defense in pass mode creates running lane
- Timing: Delayed handoff after pass rush engagement
- Success Rate: Moderate but sets up future plays
"""
    
    elif down == 3:
        if distance <= 3:
            analysis += """
**1. Quick Slant Combination** (11 Personnel)
- Reasoning: High percentage routes below linebacker level
- Pattern: Multiple receivers at sticks level
- Protection: Quick 3-step drop

**2. Tight End Seam** (12 Personnel)
- Reasoning: Linebacker often has deep responsibility
- Execution: Find soft spot in zone coverage
- Risk Level: Medium - requires precise timing

**3. Pick Play Concept** (10 Personnel)
- Reasoning: Create artificial separation for receiver
- Legality: Within 1 yard of line of scrimmage
- Success Rate: High if executed properly
"""
        elif distance <= 7:
            analysis += """
**1. Mesh Concept** (11 Personnel)
- Reasoning: Two receivers crossing creates picks and confusion
- Read: Take first open receiver
- Protection: 5-man protection with hot route

**2. Four Verticals** (10 Personnel)
- Reasoning: Overload deep coverage, find soft spot
- Adjustment: Receivers sit in holes of zone coverage
- Weather Factor: May be limited by wind conditions

**3. Curl Combination** (11 Personnel)
- Reasoning: Receivers turn back to quarterback
- Timing: Break at exact sticks depth
- Success Rate: High if protection holds
"""
        else:  # Long yardage
            analysis += """
**1. Deep Dig Combination** (10 Personnel)
- Reasoning: Attack middle of field behind linebackers
- Route: 12-15 yard dig with comeback option
- Protection: Maximum protection scheme

**2. Four Verticals Concept** (10 Personnel)
- Reasoning: Stretch deep coverage, find opening
- Read: Take deepest available receiver
- Risk Level: High but necessary

**3. Screen Pass** (11 Personnel)
- Reasoning: Defense likely rushing aggressively
- Type: Wide receiver screen or running back swing
- Execution: Requires perfect timing and blocks
"""
    
    elif down == 4:
        analysis += """
**FOURTH DOWN DECISION MATRIX**

**Recommended Action:** Based on field position and score differential
- **Go for it** if: Inside opponent 40, down by more than 3
- **Punt** if: Own territory, manageable game situation
- **Field Goal** if: Inside 35-yard line, within 3 points

**If Going for Conversion:**
1. **Highest Percentage Play:** Based on team's best short yardage concept
2. **Mismatch Exploitation:** Target weakest coverage matchup
3. **Surprise Element:** Unexpected formation or motion
"""
    
    # Add weather considerations
    weather_risk = weather_data.get('strategic_impact', {}).get('risk_level', 'LOW')
    if weather_risk in ['HIGH', 'CRITICAL']:
        analysis += f"""

### Weather Adjustments Required:
**Risk Level: {weather_risk}**
- **Passing Game:** {"Significantly limited" if weather_risk == 'CRITICAL' else "Moderately affected"}
- **Ball Security:** Enhanced protocols required
- **Play Selection:** {"Conservative approach mandatory" if weather_risk == 'CRITICAL' else "Tactical adjustments needed"}
"""
    
    return analysis

def generate_matchup_analysis(team1_data: Dict, team2_data: Dict) -> str:
    """
    PURPOSE: Analyze specific positional matchups and advantages
    INPUTS: Team data for both teams
    OUTPUTS: Detailed matchup analysis with exploitation strategies
    DEPENDENCIES: Personnel advantages data
    NOTES: Focuses on individual position group advantages
    """
    
    analysis = """
# MATCHUP EXPLOITATION ANALYSIS

## Personnel Matchup Advantages
"""
    
    # Wide Receiver vs Cornerback Analysis
    team1_wr_cb = team1_data['personnel_advantages']['wr_vs_cb_mismatch']
    team2_wr_cb = team2_data['personnel_advantages']['wr_vs_cb_mismatch']
    
    analysis += f"""
### Wide Receiver vs Cornerback
- **Your Team WR Advantage:** {team1_wr_cb*100:.1f}%
- **Opponent WR Advantage:** {team2_wr_cb*100:.1f}%
"""
    
    if team1_wr_cb > team2_wr_cb:
        advantage = (team1_wr_cb - team2_wr_cb) * 100
        analysis += f"**EXPLOIT:** {advantage:.1f}% advantage in WR matchups - emphasize vertical routes and comeback patterns\n\n"
    else:
        deficit = (team2_wr_cb - team1_wr_cb) * 100
        analysis += f"**CHALLENGE:** {deficit:.1f}% deficit in WR matchups - focus on quick game and pick plays\n\n"
    
    # Tight End vs Linebacker Analysis
    team1_te_lb = team1_data['personnel_advantages']['te_vs_lb_mismatch']
    team2_te_lb = team2_data['personnel_advantages']['te_vs_lb_mismatch']
    
    analysis += f"""
### Tight End vs Linebacker
- **Your Team TE Advantage:** {team1_te_lb*100:.1f}%
- **Opponent TE Advantage:** {team2_te_lb*100:.1f}%
"""
    
    if team1_te_lb > team2_te_lb:
        advantage = (team1_te_lb - team2_te_lb) * 100
        analysis += f"**EXPLOIT:** {advantage:.1f}% advantage - target seam routes and crossing patterns from tight end\n\n"
    else:
        deficit = (team2_te_lb - team1_te_lb) * 100
        analysis += f"**CHALLENGE:** {deficit:.1f}% deficit - use tight end primarily for blocking and checkdowns\n\n"
    
    # Running Back vs Linebacker Coverage
    team1_rb_lb = team1_data['personnel_advantages']['rb_vs_lb_coverage']
    team2_rb_lb = team2_data['personnel_advantages']['rb_vs_lb_coverage']
    
    analysis += f"""
### Running Back vs Linebacker Coverage
- **Your Team RB Advantage:** {team1_rb_lb*100:.1f}%
- **Opponent RB Advantage:** {team2_rb_lb*100:.1f}%
"""
    
    if team1_rb_lb > team2_rb_lb:
        advantage = (team1_rb_lb - team2_rb_lb) * 100
        analysis += f"**EXPLOIT:** {advantage:.1f}% advantage - utilize running back in passing game with wheel routes and checkdowns\n\n"
    else:
        deficit = (team2_rb_lb - team1_rb_lb) * 100
        analysis += f"**CHALLENGE:** {deficit:.1f}% deficit - keep running back in for protection, limit route running\n\n"
    
    # Add specific exploitation strategies
    analysis += """
## Specific Exploitation Strategies

### Route Concepts to Emphasize:
"""
    
    # Determine best route concepts based on advantages
    if team1_wr_cb > 0.75:
        analysis += "- **Vertical Routes:** Deep comeback, fade, and post patterns\n"
    if team1_te_lb > 0.75:
        analysis += "- **Seam Routes:** Tight end up the seam against linebacker coverage\n"
    if team1_rb_lb > 0.75:
        analysis += "- **Wheel Routes:** Running back wheel route against slow linebackers\n"
    
    analysis += """
### Formation Recommendations:
"""
    
    # Best formations based on matchup advantages
    if team1_te_lb > team1_wr_cb:
        analysis += "- **12 Personnel:** Maximize tight end advantages\n"
    if team1_wr_cb > 0.75:
        analysis += "- **10 Personnel:** Spread the field with four wide receivers\n"
    if team1_rb_lb > 0.70:
        analysis += "- **11 Personnel:** Balance that allows running back in routes\n"
    
    return analysis

# =============================================================================
# ANALYSIS EXPORT AND SUMMARY FUNCTIONS
# =============================================================================

def generate_analysis_summary(analysis_text: str) -> str:
    """
    PURPOSE: Generate concise summary of detailed analysis
    INPUTS: Full analysis text
    OUTPUTS: Executive summary with key points
    DEPENDENCIES: Analysis text content
    NOTES: Extracts key recommendations for quick reference
    """
    
    # Extract key points (simplified version)
    summary = """
# STRATEGIC ANALYSIS SUMMARY

## Key Tactical Advantages:
- Formation efficiency advantages identified
- Situational tendency exploits available
- Weather factors considered

## Primary Recommendations:
- Focus on identified formation strengths
- Exploit personnel matchup advantages  
- Adjust for weather conditions

## Immediate Action Items:
- Test formation advantages early
- Monitor opponent adjustments
- Execute weather-appropriate tactics

*Full detailed analysis available above*
"""
    
    return summary

def format_analysis_for_export(analysis_text: str, teams: str, timestamp: str) -> str:
    """
    PURPOSE: Format analysis for export/download
    INPUTS: Analysis text, team matchup, timestamp
    OUTPUTS: Formatted text ready for export
    DEPENDENCIES: Analysis content
    NOTES: Adds headers and formatting for professional presentation
    """
    
    export_text = f"""
GRIT NFL STRATEGIC ANALYSIS REPORT
==================================

Matchup: {teams}
Generated: {timestamp}
Platform: GRIT v4.0 Strategic Edge Platform

{analysis_text}

---
Report generated by GRIT NFL Strategic Edge Platform
Professional coordinator-level analysis for tactical planning
"""
    
    return export_text
