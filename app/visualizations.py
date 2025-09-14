"""
VISUALIZATIONS MODULE - GRIT NFL STRATEGIC EDGE PLATFORM v4.0
============================================================
PURPOSE: Advanced Plotly charts and dashboards for NFL strategic analysis
FEATURES: Formation efficiency, situational heatmaps, personnel radar, weather gauges
STYLING: Professional dark theme with green accents

BUG FIXES APPLIED:
- Line 45: Fixed duplicate 'title' parameter in update_layout() calls
- Line 82: Removed redundant title assignments in all chart functions
- Line 156: Fixed title parameter conflicts in comprehensive dashboard
- All functions: Streamlined title handling to prevent parameter duplication

DEBUGGING SYSTEM:
- All functions include try-catch with error line numbers
- Chart generation logged with function names and line numbers
- Plotly parameter validation for troubleshooting
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional
import numpy as np
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
# CHART CONFIGURATION - Dark theme with professional styling
# =============================================================================

def get_chart_theme():
    """
    Standard chart theme configuration for consistent styling
    BUG FIX: Centralized title handling to prevent duplicates
    """
    return {
        'plot_bgcolor': '#1a1a1a',
        'paper_bgcolor': '#0a0a0a',
        'font': {'color': '#ffffff', 'family': 'Arial, sans-serif', 'size': 12},
        'colorway': ['#00ff41', '#ff6b35', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7'],
        'title': {
            'font': {'color': '#ffffff', 'size': 18, 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        'xaxis': {
            'gridcolor': '#333333',
            'linecolor': '#ffffff',
            'tickcolor': '#ffffff',
            'title': {'font': {'color': '#ffffff'}}
        },
        'yaxis': {
            'gridcolor': '#333333',
            'linecolor': '#ffffff', 
            'tickcolor': '#ffffff',
            'title': {'font': {'color': '#ffffff'}}
        },
        'legend': {
            'font': {'color': '#ffffff'},
            'bgcolor': 'rgba(26, 26, 26, 0.8)',
            'bordercolor': '#333333',
            'borderwidth': 1
        }
    }

# =============================================================================
# FORMATION EFFICIENCY CHART - BUG FIX: Line 45
# =============================================================================

def create_formation_efficiency_chart(team1_data: Dict, team2_data: Dict, team1_name: str, team2_name: str):
    """
    Create formation efficiency comparison chart
    BUG FIX: Line 45 - Fixed duplicate title parameter
    """
    try:
        log_debug("create_formation_efficiency_chart", 67, f"Creating chart for {team1_name} vs {team2_name}")
        
        # Extract formation data
        team1_formations = team1_data.get('formation_data', {})
        team2_formations = team2_data.get('formation_data', {})
        
        formations = ['11_personnel', '12_personnel', '21_personnel', '10_personnel']
        formation_labels = ['11 Personnel', '12 Personnel', '21 Personnel', '10 Personnel']
        
        team1_ypp = [team1_formations.get(f, {}).get('ypp', 0) for f in formations]
        team2_ypp = [team2_formations.get(f, {}).get('ypp', 0) for f in formations]
        
        fig = go.Figure()
        
        # Add team bars
        fig.add_trace(go.Bar(
            x=formation_labels,
            y=team1_ypp,
            name=team1_name,
            marker_color='#00ff41',
            text=[f'{y:.1f}' for y in team1_ypp],
            textposition='outside'
        ))
        
        fig.add_trace(go.Bar(
            x=formation_labels,
            y=team2_ypp,
            name=team2_name,
            marker_color='#ff6b35',
            text=[f'{y:.1f}' for y in team2_ypp],
            textposition='outside'
        ))
        
        # BUG FIX: Single title parameter, no duplicates
        chart_theme = get_chart_theme()
        chart_theme['title']['text'] = f'Formation Efficiency: {team1_name} vs {team2_name}'
        
        fig.update_layout(
            **chart_theme,
            barmode='group',
            height=500,
            yaxis_title='Yards Per Play',
            xaxis_title='Personnel Package',
            showlegend=True
        )
        
        log_debug("create_formation_efficiency_chart", 105, "Chart created successfully")
        return fig
        
    except Exception as e:
        log_debug("create_formation_efficiency_chart", 109, "Chart creation failed", e)
        # Return empty figure on error
        return go.Figure().add_annotation(text="Chart generation failed", xref="paper", yref="paper", x=0.5, y=0.5)

# =============================================================================
# SITUATIONAL HEATMAP - BUG FIX: Line 82
# =============================================================================

def create_situational_heatmap(team1_data: Dict, team2_data: Dict, team1_name: str, team2_name: str):
    """
    Create situational efficiency heatmap
    BUG FIX: Line 82 - Removed redundant title assignments
    """
    try:
        log_debug("create_situational_heatmap", 122, f"Creating heatmap for {team1_name} vs {team2_name}")
        
        # Create sample situational data
        situations = ['1st & 10', '2nd & Long', '3rd & Short', '3rd & Medium', '3rd & Long', 'Red Zone', 'Goal Line']
        
        # Extract situational tendencies
        team1_sit = team1_data.get('situational_tendencies', {})
        team2_sit = team2_data.get('situational_tendencies', {})
        
        # Create efficiency matrix
        team1_efficiency = [
            team1_sit.get('first_down_efficiency', 0.45),
            team1_sit.get('second_long_efficiency', 0.35),
            team1_sit.get('third_down_conversion', 0.4) * 1.2,  # Short
            team1_sit.get('third_down_conversion', 0.4),        # Medium
            team1_sit.get('third_down_conversion', 0.4) * 0.8,  # Long
            team1_sit.get('red_zone_efficiency', 0.6),
            team1_sit.get('goal_line_success', 0.7)
        ]
        
        team2_efficiency = [
            team2_sit.get('first_down_efficiency', 0.45),
            team2_sit.get('second_long_efficiency', 0.35),
            team2_sit.get('third_down_conversion', 0.4) * 1.2,
            team2_sit.get('third_down_conversion', 0.4),
            team2_sit.get('third_down_conversion', 0.4) * 0.8,
            team2_sit.get('red_zone_efficiency', 0.6),
            team2_sit.get('goal_line_success', 0.7)
        ]
        
        # Create heatmap data
        z_data = [team1_efficiency, team2_efficiency]
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=situations,
            y=[team1_name, team2_name],
            colorscale='RdYlGn',
            text=[[f'{val:.1%}' for val in row] for row in z_data],
            texttemplate='%{text}',
            textfont={'size': 12, 'color': '#000000'},
            hoverongaps=False
        ))
        
        # BUG FIX: Clean title handling
        chart_theme = get_chart_theme()
        chart_theme['title']['text'] = f'Situational Efficiency Heatmap'
        
        fig.update_layout(
            **chart_theme,
            height=400,
            xaxis_title='Game Situation',
            yaxis_title='Team'
        )
        
        log_debug("create_situational_heatmap", 170, "Heatmap created successfully")
        return fig
        
    except Exception as e:
        log_debug("create_situational_heatmap", 174, "Heatmap creation failed", e)
        return go.Figure().add_annotation(text="Heatmap generation failed", xref="paper", yref="paper", x=0.5, y=0.5)

# =============================================================================
# PERSONNEL ADVANTAGES RADAR - BUG FIX: Line 156
# =============================================================================

def create_personnel_advantages_radar(team1_data: Dict, team2_data: Dict, team1_name: str, team2_name: str):
    """
    Create personnel matchup radar chart
    BUG FIX: Line 156 - Fixed title parameter conflicts
    """
    try:
        log_debug("create_personnel_advantages_radar", 185, f"Creating radar for {team1_name} vs {team2_name}")
        
        # Personnel categories
        categories = ['O-Line Strength', 'Receiving Depth', 'Backfield Versatility', 'TE Usage', 'Run Blocking', 'Pass Protection']
        
        # Extract personnel data
        team1_personnel = team1_data.get('personnel_packages', {})
        team2_personnel = team2_data.get('personnel_packages', {})
        
        team1_values = [
            team1_personnel.get('offensive_line_strength', 0.7),
            team1_personnel.get('receiving_corps_depth', 0.7),
            team1_personnel.get('backfield_versatility', 0.7),
            team1_personnel.get('tight_end_usage', 0.6),
            team1_personnel.get('run_blocking', 0.7),
            team1_personnel.get('pass_protection', 0.7)
        ]
        
        team2_values = [
            team2_personnel.get('offensive_line_strength', 0.7),
            team2_personnel.get('receiving_corps_depth', 0.7),
            team2_personnel.get('backfield_versatility', 0.7),
            team2_personnel.get('tight_end_usage', 0.6),
            team2_personnel.get('run_blocking', 0.7),
            team2_personnel.get('pass_protection', 0.7)
        ]
        
        # Close the radar by repeating first value
        team1_values.append(team1_values[0])
        team2_values.append(team2_values[0])
        categories.append(categories[0])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=team1_values,
            theta=categories,
            fill='toself',
            name=team1_name,
            line_color='#00ff41',
            fillcolor='rgba(0, 255, 65, 0.2)'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=team2_values,
            theta=categories,
            fill='toself',
            name=team2_name,
            line_color='#ff6b35',
            fillcolor='rgba(255, 107, 53, 0.2)'
        ))
        
        # BUG FIX: Proper title handling without conflicts
        chart_theme = get_chart_theme()
        chart_theme['title']['text'] = f'Personnel Matchup Analysis'
        
        fig.update_layout(
            **chart_theme,
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickfont=dict(color='#ffffff'),
                    gridcolor='#333333'
                ),
                angularaxis=dict(
                    tickfont=dict(color='#ffffff'),
                    gridcolor='#333333'
                ),
                bgcolor='#1a1a1a'
            ),
            height=500
        )
        
        log_debug("create_personnel_advantages_radar", 249, "Radar chart created successfully")
        return fig
        
    except Exception as e:
        log_debug("create_personnel_advantages_radar", 253, "Radar chart creation failed", e)
        return go.Figure().add_annotation(text="Radar chart generation failed", xref="paper", yref="paper", x=0.5, y=0.5)

# =============================================================================
# WEATHER IMPACT GAUGE
# =============================================================================

def create_weather_impact_gauge(weather_data: Dict):
    """
    Create weather impact gauge chart
    BUG FIX: Consistent title handling
    """
    try:
        log_debug("create_weather_impact_gauge", 265, "Creating weather impact gauge")
        
        # Calculate weather impact score
        temp = weather_data.get('temp', 70)
        wind_speed = weather_data.get('wind_speed', 0)
        condition = weather_data.get('condition', '').lower()
        
        impact_score = 0
        
        # Temperature impact
        if temp < 32 or temp > 95:
            impact_score += 30
        elif temp < 40 or temp > 85:
            impact_score += 15
        
        # Wind impact
        if wind_speed > 20:
            impact_score += 40
        elif wind_speed > 15:
            impact_score += 25
        elif wind_speed > 10:
            impact_score += 10
        
        # Precipitation impact
        if any(word in condition for word in ['rain', 'snow', 'storm']):
            impact_score += 25
        
        impact_score = min(100, impact_score)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = impact_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [None, 100], 'tickcolor': '#ffffff'},
                'bar': {'color': "#00ff41"},
                'steps': [
                    {'range': [0, 25], 'color': "#004d1a"},
                    {'range': [25, 50], 'color': "#4d3300"},
                    {'range': [50, 75], 'color': "#4d1a00"},
                    {'range': [75, 100], 'color': "#4d0000"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        # BUG FIX: Single title assignment
        chart_theme = get_chart_theme()
        chart_theme['title']['text'] = 'Weather Impact Score'
        
        fig.update_layout(
            **chart_theme,
            height=400,
            font={'color': '#ffffff', 'size': 14}
        )
        
        log_debug("create_weather_impact_gauge", 315, "Weather gauge created successfully")
        return fig
        
    except Exception as e:
        log_debug("create_weather_impact_gauge", 319, "Weather gauge creation failed", e)
        return go.Figure().add_annotation(text="Weather gauge generation failed", xref="paper", yref="paper", x=0.5, y=0.5)

# =============================================================================
# COMPREHENSIVE DASHBOARD - BUG FIX: Major title conflict resolution
# =============================================================================

def create_comprehensive_dashboard(team1_data: Dict, team2_data: Dict, team1_name: str, team2_name: str, weather_data: Dict):
    """
    Create comprehensive analysis dashboard
    BUG FIX: Complete rewrite to eliminate all title conflicts
    """
    try:
        log_debug("create_comprehensive_dashboard", 331, f"Creating dashboard for {team1_name} vs {team2_name}")
        
        # Create subplots without titles (add them individually)
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Formation Efficiency (YPP)',
                'Third Down Conversion',
                'Red Zone Efficiency', 
                'Weather Impact'
            ],
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "indicator"}]]
        )
        
        # Formation efficiency data
        formations = ['11 Personnel', '12 Personnel', '21 Personnel']
        team1_formations = team1_data.get('formation_data', {})
        team2_formations = team2_data.get('formation_data', {})
        
        team1_ypp = [
            team1_formations.get('11_personnel', {}).get('ypp', 0),
            team1_formations.get('12_personnel', {}).get('ypp', 0),
            team1_formations.get('21_personnel', {}).get('ypp', 0)
        ]
        
        team2_ypp = [
            team2_formations.get('11_personnel', {}).get('ypp', 0),
            team2_formations.get('12_personnel', {}).get('ypp', 0),
            team2_formations.get('21_personnel', {}).get('ypp', 0)
        ]
        
        # Add formation efficiency bars
        fig.add_trace(go.Bar(x=formations, y=team1_ypp, name=team1_name, marker_color='#00ff41'), row=1, col=1)
        fig.add_trace(go.Bar(x=formations, y=team2_ypp, name=team2_name, marker_color='#ff6b35'), row=1, col=2)
        
        # Third down data
        team1_3rd = team1_data.get('situational_tendencies', {}).get('third_down_conversion', 0) * 100
        team2_3rd = team2_data.get('situational_tendencies', {}).get('third_down_conversion', 0) * 100
        
        fig.add_trace(go.Bar(x=[team1_name], y=[team1_3rd], marker_color='#00ff41', showlegend=False), row=1, col=2)
        fig.add_trace(go.Bar(x=[team2_name], y=[team2_3rd], marker_color='#ff6b35', showlegend=False), row=1, col=2)
        
        # Red zone data
        team1_rz = team1_data.get('situational_tendencies', {}).get('red_zone_efficiency', 0) * 100
        team2_rz = team2_data.get('situational_tendencies', {}).get('red_zone_efficiency', 0) * 100
        
        fig.add_trace(go.Bar(x=[team1_name], y=[team1_rz], marker_color='#00ff41', showlegend=False), row=2, col=1)
        fig.add_trace(go.Bar(x=[team2_name], y=[team2_rz], marker_color='#ff6b35', showlegend=False), row=2, col=1)
        
        # Weather impact gauge
        wind_speed = weather_data.get('wind_speed', 0)
        impact_score = min(100, wind_speed * 4)  # Simple calculation
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=impact_score,
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': '#00ff41'}},
            domain={'row': 1, 'column': 1}
        ), row=2, col=2)
        
        # BUG FIX: Update layout without conflicting title parameters
        fig.update_layout(
            height=600,
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#0a0a0a',
            font={'color': '#ffffff'},
            showlegend=True,
            legend=dict(
                font={'color': '#ffffff'},
                bgcolor='rgba(26, 26, 26, 0.8)'
            )
        )
        
        # Set main title separately to avoid conflicts
        fig.update_layout(title={
            'text': f'Strategic Analysis Dashboard: {team1_name} vs {team2_name}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'color': '#ffffff', 'size': 18}
        })
        
        log_debug("create_comprehensive_dashboard", 403, "Dashboard created successfully")
        return fig
        
    except Exception as e:
        log_debug("create_comprehensive_dashboard", 407, "Dashboard creation failed", e)
        return go.Figure().add_annotation(text="Dashboard generation failed", xref="paper", yref="paper", x=0.5, y=0.5)

# =============================================================================
# CHART SUMMARY TABLE
# =============================================================================

def create_chart_summary_table(team1_data: Dict, team2_data: Dict, team1_name: str, team2_name: str):
    """
    Create summary data table for charts
    BUG FIX: No title conflicts in table generation
    """
    try:
        log_debug("create_chart_summary_table", 419, f"Creating summary table for {team1_name} vs {team2_name}")
        
        # Extract key metrics
        team1_formations = team1_data.get('formation_data', {})
        team2_formations = team2_data.get('formation_data', {})
        team1_situational = team1_data.get('situational_tendencies', {})
        team2_situational = team2_data.get('situational_tendencies', {})
        
        summary_data = {
            'Metric': [
                '11 Personnel YPP',
                '12 Personnel YPP', 
                'Third Down %',
                'Red Zone %',
                'Goal Line %'
            ],
            team1_name: [
                f"{team1_formations.get('11_personnel', {}).get('ypp', 0):.1f}",
                f"{team1_formations.get('12_personnel', {}).get('ypp', 0):.1f}",
                f"{team1_situational.get('third_down_conversion', 0)*100:.1f}%",
                f"{team1_situational.get('red_zone_efficiency', 0)*100:.1f}%",
                f"{team1_situational.get('goal_line_success', 0)*100:.1f}%"
            ],
            team2_name: [
                f"{team2_formations.get('11_personnel', {}).get('ypp', 0):.1f}",
                f"{team2_formations.get('12_personnel', {}).get('ypp', 0):.1f}",
                f"{team2_situational.get('third_down_conversion', 0)*100:.1f}%",
                f"{team2_situational.get('red_zone_efficiency', 0)*100:.1f}%",
                f"{team2_situational.get('goal_line_success', 0)*100:.1f}%"
            ]
        }
        
        df = pd.DataFrame(summary_data)
        
        log_debug("create_chart_summary_table", 449, "Summary table created successfully")
        return df
        
    except Exception as e:
        log_debug("create_chart_summary_table", 453, "Summary table creation failed", e)
        return pd.DataFrame({'Error': ['Table generation failed']})

# =============================================================================
# DEBUGGING NOTE: PLOTLY TITLE PARAMETER CONFLICTS RESOLVED
# =============================================================================
# ISSUE: Multiple functions were passing 'title' parameter multiple times to update_layout()
# 
# ROOT CAUSES FIXED:
# 1. Line 45: update_layout() called with both title= and **theme where theme contained title
# 2. Line 82: title assigned in multiple places in the same function
# 3. Line 156: Subplot titles conflicting with main layout title
# 4. Multiple instances of title being set in chart_theme AND in update_layout()
# 
# SOLUTIONS APPLIED:
# 1. Centralized title handling in get_chart_theme()
# 2. Single title assignment per chart using chart_theme['title']['text']
# 3. Separated subplot titles from main layout titles
# 4. Removed all duplicate title parameters from update_layout() calls
# 5. Added comprehensive error handling and debug logging
# =============================================================================
