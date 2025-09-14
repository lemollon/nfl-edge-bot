"""
GRIT NFL PLATFORM - VISUALIZATIONS MODULE
=========================================
PURPOSE: Advanced Plotly charts and data visualizations with lazy loading
FEATURES: Formation charts, heatmaps, strategic dashboards, interactive plots
ARCHITECTURE: Cached visualizations with professional styling
NOTES: Dark theme consistent styling with white text and green accents
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# =============================================================================
# CHART STYLING CONFIGURATION - DARK THEME WITH WHITE TEXT
# =============================================================================

def get_chart_template() -> Dict:
    """
    PURPOSE: Get consistent dark theme styling for all charts
    INPUTS: None
    OUTPUTS: Plotly template configuration dictionary
    DEPENDENCIES: None
    NOTES: Ensures consistent styling across all visualizations
    """
    return {
        'layout': {
            'template': 'plotly_dark',
            'paper_bgcolor': 'rgba(26,26,26,0.8)',
            'plot_bgcolor': 'rgba(26,26,26,0.8)',
            'font': {'color': '#ffffff', 'family': 'Arial, sans-serif'},
            'title': {'font': {'color': '#ffffff', 'size': 18}},
            'xaxis': {
                'gridcolor': '#444444',
                'linecolor': '#666666',
                'tickcolor': '#ffffff',
                'titlefont': {'color': '#ffffff'}
            },
            'yaxis': {
                'gridcolor': '#444444',
                'linecolor': '#666666', 
                'tickcolor': '#ffffff',
                'titlefont': {'color': '#ffffff'}
            },
            'colorway': ['#00ff41', '#ff6b35', '#00ccff', '#ff9900', '#9966ff', '#ff3366']
        }
    }

# =============================================================================
# FORMATION EFFICIENCY VISUALIZATIONS
# =============================================================================

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def create_formation_efficiency_chart(team1_data: Dict, team2_data: Dict, 
                                     team1_name: str, team2_name: str) -> go.Figure:
    """
    PURPOSE: Create interactive formation efficiency comparison chart
    INPUTS: Team data dictionaries and team names
    OUTPUTS: Plotly figure object with formation comparison
    DEPENDENCIES: Plotly, team formation data
    NOTES: Cached for performance, compares YPP across formations
    """
    
    formations = ['11 Personnel', '12 Personnel', '21 Personnel', '10 Personnel']
    formation_keys = ['11_personnel', '12_personnel', '21_personnel', '10_personnel']
    
    # Extract YPP data safely
    team1_ypp = []
    team2_ypp = []
    team1_usage = []
    team2_usage = []
    
    for key in formation_keys:
        team1_formation = team1_data.get('formation_data', {}).get(key, {})
        team2_formation = team2_data.get('formation_data', {}).get(key, {})
        
        team1_ypp.append(team1_formation.get('ypp', 0))
        team2_ypp.append(team2_formation.get('ypp', 0))
        team1_usage.append(team1_formation.get('usage', 0) * 100)
        team2_usage.append(team2_formation.get('usage', 0) * 100)
    
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]],
        subplot_titles=(f"Formation Efficiency: {team1_name} vs {team2_name}",)
    )
    
    # Add YPP bars
    fig.add_trace(
        go.Bar(
            name=f'{team1_name} YPP',
            x=formations,
            y=team1_ypp,
            marker_color='#00ff41',
            opacity=0.8,
            text=[f'{ypp:.1f}' for ypp in team1_ypp],
            textposition='auto',
            hovertemplate=f'<b>{team1_name}</b><br>YPP: %{{y:.1f}}<br>Usage: %{{customdata:.1f}}%<extra></extra>',
            customdata=team1_usage
        ),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(
            name=f'{team2_name} YPP',
            x=formations,
            y=team2_ypp,
            marker_color='#ff6b35',
            opacity=0.8,
            text=[f'{ypp:.1f}' for ypp in team2_ypp],
            textposition='auto',
            hovertemplate=f'<b>{team2_name}</b><br>YPP: %{{y:.1f}}<br>Usage: %{{customdata:.1f}}%<extra></extra>',
            customdata=team2_usage
        ),
        secondary_y=False
    )
    
    # Add usage line charts
    fig.add_trace(
        go.Scatter(
            name=f'{team1_name} Usage %',
            x=formations,
            y=team1_usage,
            mode='lines+markers',
            line=dict(color='#00ff41', width=3, dash='dot'),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate=f'<b>{team1_name} Usage</b><br>%{{y:.1f}}%<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.add_trace(
        go.Scatter(
            name=f'{team2_name} Usage %',
            x=formations,
            y=team2_usage,
            mode='lines+markers',
            line=dict(color='#ff6b35', width=3, dash='dot'),
            marker=dict(size=8),
            yaxis='y2',
            hovertemplate=f'<b>{team2_name} Usage</b><br>%{{y:.1f}}%<extra></extra>'
        ),
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        **get_chart_template()['layout'],
        title='Formation Efficiency Analysis',
        barmode='group',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update y-axes
    fig.update_yaxes(title_text="Yards Per Play", secondary_y=False, color='#ffffff')
    fig.update_yaxes(title_text="Usage Percentage", secondary_y=True, color='#ffffff')
    
    return fig

@st.cache_data(ttl=1800)
def create_formation_success_rate_chart(team1_data: Dict, team2_data: Dict,
                                       team1_name: str, team2_name: str) -> go.Figure:
    """
    PURPOSE: Create formation success rate comparison chart
    INPUTS: Team data and names
    OUTPUTS: Plotly figure showing success rates by formation
    DEPENDENCIES: Plotly, team formation data
    NOTES: Shows success rate percentages with confidence intervals
    """
    
    formations = ['11 Personnel', '12 Personnel', '21 Personnel', '10 Personnel']
    formation_keys = ['11_personnel', '12_personnel', '21_personnel', '10_personnel']
    
    team1_success = []
    team2_success = []
    
    for key in formation_keys:
        team1_formation = team1_data.get('formation_data', {}).get(key, {})
        team2_formation = team2_data.get('formation_data', {}).get(key, {})
        
        team1_success.append(team1_formation.get('success_rate', 0) * 100)
        team2_success.append(team2_formation.get('success_rate', 0) * 100)
    
    fig = go.Figure()
    
    # Add radar chart for success rates
    fig.add_trace(go.Scatterpolar(
        r=team1_success + [team1_success[0]],  # Close the loop
        theta=formations + [formations[0]],
        fill='toself',
        name=team1_name,
        line_color='#00ff41',
        fillcolor='rgba(0,255,65,0.2)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=team2_success + [team2_success[0]],  # Close the loop
        theta=formations + [formations[0]],
        fill='toself',
        name=team2_name,
        line_color='#ff6b35',
        fillcolor='rgba(255,107,53,0.2)'
    ))
    
    fig.update_layout(
        **get_chart_template()['layout'],
        title='Formation Success Rate Comparison',
        polar=dict(
            bgcolor='rgba(26,26,26,0.8)',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                color='#ffffff',
                gridcolor='#444444'
            ),
            angularaxis=dict(
                color='#ffffff',
                gridcolor='#444444'
            )
        ),
        height=500
    )
    
    return fig

# =============================================================================
# SITUATIONAL ANALYSIS HEATMAPS
# =============================================================================

@st.cache_data(ttl=1800)
def create_situational_heatmap(team1_data: Dict, team2_data: Dict,
                              team1_name: str, team2_name: str) -> go.Figure:
    """
    PURPOSE: Create situational efficiency heatmap comparison
    INPUTS: Team data and names
    OUTPUTS: Plotly heatmap figure
    DEPENDENCIES: Plotly, team situational data
    NOTES: Visual representation of situational strengths/weaknesses
    """
    
    situations = ['Third Down', 'Red Zone', 'Goal Line', 'Two Minute', 'Fourth Down']
    situation_keys = ['third_down_conversion', 'red_zone_efficiency', 'goal_line_efficiency', 
                     'two_minute_drill', 'fourth_down_aggression']
    
    # Extract situational data
    team1_values = []
    team2_values = []
    
    for key in situation_keys:
        team1_val = team1_data.get('situational_tendencies', {}).get(key, 0) * 100
        team2_val = team2_data.get('situational_tendencies', {}).get(key, 0) * 100
        team1_values.append(team1_val)
        team2_values.append(team2_val)
    
    # Create difference heatmap
    differences = [t1 - t2 for t1, t2 in zip(team1_values, team2_values)]
    
    fig = go.Figure(data=go.Heatmap(
        z=[team1_values, team2_values, differences],
        x=situations,
        y=[team1_name, team2_name, 'Advantage'],
        colorscale='RdYlGn',
        text=[[f'{val:.1f}%' for val in team1_values],
              [f'{val:.1f}%' for val in team2_values],
              [f'{diff:+.1f}%' for diff in differences]],
        texttemplate='%{text}',
        textfont={"size": 12, "color": "white"},
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>%{x}: %{text}<extra></extra>'
    ))
    
    fig.update_layout(
        **get_chart_template()['layout'],
        title='Situational Efficiency Analysis',
        height=400
    )
    
    return fig

@st.cache_data(ttl=1800)
def create_personnel_advantages_radar(team1_data: Dict, team2_data: Dict,
                                     team1_name: str, team2_name: str) -> go.Figure:
    """
    PURPOSE: Create radar chart for personnel advantages
    INPUTS: Team data and names
    OUTPUTS: Plotly radar chart figure
    DEPENDENCIES: Plotly, personnel advantages data
    NOTES: Shows matchup advantages across different personnel groups
    """
    
    categories = ['WR vs CB', 'TE vs LB', 'RB vs LB', 'Outside Zone', 'Inside Zone', 'Screen Efficiency']
    
    # Extract personnel advantage data
    team1_advantages = [
        team1_data.get('personnel_advantages', {}).get('wr_vs_cb_mismatch', 0) * 100,
        team1_data.get('personnel_advantages', {}).get('te_vs_lb_mismatch', 0) * 100,
        team1_data.get('personnel_advantages', {}).get('rb_vs_lb_coverage', 0) * 100,
        team1_data.get('personnel_advantages', {}).get('outside_zone_left', 0) * 20,  # Scale to 100
        team1_data.get('personnel_advantages', {}).get('inside_zone', 0) * 20,
        team1_data.get('personnel_advantages', {}).get('screen_efficiency', 0) * 100
    ]
    
    team2_advantages = [
        team2_data.get('personnel_advantages', {}).get('wr_vs_cb_mismatch', 0) * 100,
        team2_data.get('personnel_advantages', {}).get('te_vs_lb_mismatch', 0) * 100,
        team2_data.get('personnel_advantages', {}).get('rb_vs_lb_coverage', 0) * 100,
        team2_data.get('personnel_advantages', {}).get('outside_zone_left', 0) * 20,
        team2_data.get('personnel_advantages', {}).get('inside_zone', 0) * 20,
        team2_data.get('personnel_advantages', {}).get('screen_efficiency', 0) * 100
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=team1_advantages + [team1_advantages[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=team1_name,
        line_color='#00ff41',
        fillcolor='rgba(0,255,65,0.2)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=team2_advantages + [team2_advantages[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name=team2_name,
        line_color='#ff6b35',
        fillcolor='rgba(255,107,53,0.2)'
    ))
    
    fig.update_layout(
        **get_chart_template()['layout'],
        title='Personnel Matchup Advantages',
        polar=dict(
            bgcolor='rgba(26,26,26,0.8)',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                color='#ffffff',
                gridcolor='#444444'
            ),
            angularaxis=dict(
                color='#ffffff',
                gridcolor='#444444'
            )
        ),
        height=500
    )
    
    return fig

# =============================================================================
# WEATHER IMPACT VISUALIZATIONS
# =============================================================================

@st.cache_data(ttl=1800)
def create_weather_impact_gauge(weather_data: Dict) -> go.Figure:
    """
    PURPOSE: Create weather impact gauge chart
    INPUTS: Weather data with strategic impact
    OUTPUTS: Plotly gauge figure
    DEPENDENCIES: Plotly, weather impact data
    NOTES: Visual representation of weather risk level
    """
    
    risk_levels = {'MINIMAL': 20, 'LOW': 40, 'MODERATE': 60, 'HIGH': 80, 'CRITICAL': 100}
    risk_level = weather_data.get('strategic_impact', {}).get('risk_level', 'LOW')
    risk_value = risk_levels.get(risk_level, 40)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = risk_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Weather Impact Risk"},
        delta = {'reference': 40},
        gauge = {
            'axis': {'range': [None, 100], 'tickcolor': '#ffffff'},
            'bar': {'color': "#00ff41"},
            'steps': [
                {'range': [0, 25], 'color': "#004d1a"},
                {'range': [25, 50], 'color': "#006d25"},
                {'range': [50, 75], 'color': "#ff9900"},
                {'range': [75, 100], 'color': "#ff3333"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': risk_value
            }
        }
    ))
    
    fig.update_layout(
        **get_chart_template()['layout'],
        height=300,
        title=f"Weather Risk: {risk_level}"
    )
    
    return fig

@st.cache_data(ttl=1800)
def create_weather_impact_bars(weather_data: Dict) -> go.Figure:
    """
    PURPOSE: Create weather impact bar chart showing specific effects
    INPUTS: Weather data with strategic impact
    OUTPUTS: Plotly bar chart figure
    DEPENDENCIES: Plotly, weather strategic impact data
    NOTES: Shows percentage impact on different aspects of gameplay
    """
    
    impact_data = weather_data.get('strategic_impact', {})
    
    categories = ['Passing Efficiency', 'Deep Ball Success', 'Fumble Risk', 'Kicking Accuracy']
    values = [
        impact_data.get('passing_efficiency', 0) * 100,
        impact_data.get('deep_ball_success', 0) * 100,
        impact_data.get('fumble_increase', 0) * 100,
        impact_data.get('kicking_accuracy', 0) * 100
    ]
    
    # Color bars based on positive/negative impact
    colors = ['#ff3333' if val < 0 else '#00ff41' for val in values]
    
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=[f'{val:+.1f}%' for val in values],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Impact: %{y:+.1f}%<extra></extra>'
    )])
    
    fig.update_layout(
        **get_chart_template()['layout'],
        title='Weather Impact on Performance Metrics',
        yaxis_title='Impact Percentage',
        height=400
    )
    
    return fig

# =============================================================================
# CUSTOM DASHBOARD VISUALIZATIONS
# =============================================================================

@st.cache_data(ttl=1800)
def create_comprehensive_dashboard(team1_data: Dict, team2_data: Dict,
                                  team1_name: str, team2_name: str,
                                  weather_data: Dict) -> go.Figure:
    """
    PURPOSE: Create comprehensive dashboard with multiple metrics
    INPUTS: Team data, names, and weather data
    OUTPUTS: Multi-panel Plotly figure
    DEPENDENCIES: Plotly subplots, team data
    NOTES: Overview dashboard with key metrics in one view
    """
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Formation Efficiency (YPP)', 'Situational Success Rate (%)', 
                       'Personnel Advantages', 'Weather Impact'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "polar"}, {"type": "indicator"}]]
    )
    
    # Formation efficiency bars
    formations = ['11', '12', '21', '10']
    formation_keys = ['11_personnel', '12_personnel', '21_personnel', '10_personnel']
    
    team1_ypp = [team1_data.get('formation_data', {}).get(key, {}).get('ypp', 0) for key in formation_keys]
    team2_ypp = [team2_data.get('formation_data', {}).get(key, {}).get('ypp', 0) for key in formation_keys]
    
    fig.add_trace(
        go.Bar(name=team1_name, x=formations, y=team1_ypp, marker_color='#00ff41'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name=team2_name, x=formations, y=team2_ypp, marker_color='#ff6b35'),
        row=1, col=1
    )
    
    # Situational success rates
    situations = ['3rd Down', 'Red Zone', 'Goal Line']
    sit_keys = ['third_down_conversion', 'red_zone_efficiency', 'goal_line_efficiency']
    
    team1_sit = [team1_data.get('situational_tendencies', {}).get(key, 0) * 100 for key in sit_keys]
    team2_sit = [team2_data.get('situational_tendencies', {}).get(key, 0) * 100 for key in sit_keys]
    
    fig.add_trace(
        go.Bar(name=team1_name, x=situations, y=team1_sit, marker_color='#00ff41', showlegend=False),
        row=1, col=2
    )
    fig.add_trace(
        go.Bar(name=team2_name, x=situations, y=team2_sit, marker_color='#ff6b35', showlegend=False),
        row=1, col=2
    )
    
    # Personnel advantages radar
    categories = ['WR vs CB', 'TE vs LB', 'RB vs LB']
    team1_pers = [
        team1_data.get('personnel_advantages', {}).get('wr_vs_cb_mismatch', 0) * 100,
        team1_data.get('personnel_advantages', {}).get('te_vs_lb_mismatch', 0) * 100,
        team1_data.get('personnel_advantages', {}).get('rb_vs_lb_coverage', 0) * 100
    ]
    team2_pers = [
        team2_data.get('personnel_advantages', {}).get('wr_vs_cb_mismatch', 0) * 100,
        team2_data.get('personnel_advantages', {}).get('te_vs_lb_mismatch', 0) * 100,
        team2_data.get('personnel_advantages', {}).get('rb_vs_lb_coverage', 0) * 100
    ]
    
    fig.add_trace(
        go.Scatterpolar(
            r=team1_pers + [team1_pers[0]], theta=categories + [categories[0]],
            fill='toself', name=team1_name, line_color='#00ff41', showlegend=False
        ),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatterpolar(
            r=team2_pers + [team2_pers[0]], theta=categories + [categories[0]],
            fill='toself', name=team2_name, line_color='#ff6b35', showlegend=False
        ),
        row=2, col=1
    )
    
    # Weather impact gauge
    risk_levels = {'MINIMAL': 20, 'LOW': 40, 'MODERATE': 60, 'HIGH': 80, 'CRITICAL': 100}
    risk_level = weather_data.get('strategic_impact', {}).get('risk_level', 'LOW')
    risk_value = risk_levels.get(risk_level, 40)
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=risk_value,
            title={'text': f"Weather Risk: {risk_level}"},
            gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#00ff41"}},
            domain={'row': 1, 'column': 1}
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        **get_chart_template()['layout'],
        height=800,
        title_text="Strategic Analysis Dashboard",
        showlegend=True
    )
    
    return fig

# =============================================================================
# TREND ANALYSIS AND HISTORICAL CHARTS
# =============================================================================

@st.cache_data(ttl=1800)
def create_performance_trends_chart(team_data: Dict, team_name: str) -> go.Figure:
    """
    PURPOSE: Create simulated performance trends over time
    INPUTS: Team data and name
    OUTPUTS: Plotly line chart with performance trends
    DEPENDENCIES: Plotly, team data
    NOTES: Simulated historical performance for trend analysis
    """
    
    # Simulate weekly performance data
    weeks = list(range(1, 18))  # NFL season weeks
    base_ypp = team_data.get('formation_data', {}).get('11_personnel', {}).get('ypp', 5.5)
    
    # Add realistic variation
    np.random.seed(42)  # Consistent results
    ypp_trend = [base_ypp + np.random.normal(0, 0.5) for _ in weeks]
    success_trend = [team_data.get('formation_data', {}).get('11_personnel', {}).get('success_rate', 0.65) * 100 + 
                    np.random.normal(0, 3) for _ in weeks]
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Yards Per Play Trend', 'Success Rate Trend'),
        vertical_spacing=0.1
    )
    
    # YPP trend
    fig.add_trace(
        go.Scatter(
            x=weeks, y=ypp_trend,
            mode='lines+markers',
            name='YPP',
            line=dict(color='#00ff41', width=3),
            marker=dict(size=6)
        ),
        row=1, col=1
    )
    
    # Success rate trend
    fig.add_trace(
        go.Scatter(
            x=weeks, y=success_trend,
            mode='lines+markers',
            name='Success Rate %',
            line=dict(color='#ff6b35', width=3),
            marker=dict(size=6)
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        **get_chart_template()['layout'],
        title=f'{team_name} Performance Trends',
        height=600
    )
    
    fig.update_xaxes(title_text="Week", row=2, col=1)
    fig.update_yaxes(title_text="Yards Per Play", row=1, col=1)
    fig.update_yaxes(title_text="Success Rate %", row=2, col=1)
    
    return fig

# =============================================================================
# EXPORT AND UTILITY FUNCTIONS
# =============================================================================

def save_chart_as_html(fig: go.Figure, filename: str) -> str:
    """
    PURPOSE: Save Plotly chart as HTML file
    INPUTS: Plotly figure and filename
    OUTPUTS: HTML file path
    DEPENDENCIES: Plotly
    NOTES: Allows users to save charts for external use
    """
    
    html_str = fig.to_html(include_plotlyjs='cdn')
    
    # Add timestamp to filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.html"
    
    return html_str, full_filename

def create_chart_summary_table(team1_data: Dict, team2_data: Dict,
                              team1_name: str, team2_name: str) -> pd.DataFrame:
    """
    PURPOSE: Create summary table of key metrics for charts
    INPUTS: Team data and names
    OUTPUTS: Pandas DataFrame with summary statistics
    DEPENDENCIES: Pandas, team data
    NOTES: Provides data table to accompany visualizations
    """
    
    # Create summary data
    summary_data = {
        'Metric': [
            '11 Personnel YPP',
            '11 Personnel Success Rate',
            'Third Down Conversion',
            'Red Zone Efficiency',
            'WR vs CB Advantage',
            'TE vs LB Advantage'
        ],
        team1_name: [
            f"{team1_data.get('formation_data', {}).get('11_personnel', {}).get('ypp', 0):.1f}",
            f"{team1_data.get('formation_data', {}).get('11_personnel', {}).get('success_rate', 0)*100:.1f}%",
            f"{team1_data.get('situational_tendencies', {}).get('third_down_conversion', 0)*100:.1f}%",
            f"{team1_data.get('situational_tendencies', {}).get('red_zone_efficiency', 0)*100:.1f}%",
            f"{team1_data.get('personnel_advantages', {}).get('wr_vs_cb_mismatch', 0)*100:.1f}%",
            f"{team1_data.get('personnel_advantages', {}).get('te_vs_lb_mismatch', 0)*100:.1f}%"
        ],
        team2_name: [
            f"{team2_data.get('formation_data', {}).get('11_personnel', {}).get('ypp', 0):.1f}",
            f"{team2_data.get('formation_data', {}).get('11_personnel', {}).get('success_rate', 0)*100:.1f}%",
            f"{team2_data.get('situational_tendencies', {}).get('third_down_conversion', 0)*100:.1f}%",
            f"{team2_data.get('situational_tendencies', {}).get('red_zone_efficiency', 0)*100:.1f}%",
            f"{team2_data.get('personnel_advantages', {}).get('wr_vs_cb_mismatch', 0)*100:.1f}%",
            f"{team2_data.get('personnel_advantages', {}).get('te_vs_lb_mismatch', 0)*100:.1f}%"
        ]
    }
    
    return pd.DataFrame(summary_data)
