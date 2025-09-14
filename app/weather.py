"""
GRIT NFL PLATFORM - WEATHER MODULE
==================================
PURPOSE: Real weather API integration with GPT-3.5 Turbo fallback analysis
FEATURES: OpenWeatherMap API, strategic impact analysis, caching system
ARCHITECTURE: Primary real weather, fallback to GPT analysis, error handling
NOTES: Uses Option 1 (OpenWeatherMap) with intelligent fallback system
"""

import requests
import streamlit as st
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional
from openai import OpenAI
from database import init_database
import sqlite3

# =============================================================================
# OPENWEATHERMAP API INTEGRATION (OPTION 1)
# =============================================================================

def get_openweather_api_key() -> Optional[str]:
    """
    PURPOSE: Safely retrieve OpenWeatherMap API key from secrets
    INPUTS: None
    OUTPUTS: API key string or None
    DEPENDENCIES: Streamlit secrets
    NOTES: Returns None if API key not configured
    """
    try:
        return st.secrets.get("OPENWEATHER_API_KEY", None)
    except:
        return None

def get_real_weather_data(city: str, state: str) -> Optional[Dict]:
    """
    PURPOSE: Fetch real weather data from OpenWeatherMap API
    INPUTS: city (str), state (str) - Location identifiers
    OUTPUTS: Weather data dictionary or None if failed
    DEPENDENCIES: OpenWeatherMap API, requests library
    NOTES: Primary weather data source with error handling
    """
    api_key = get_openweather_api_key()
    if not api_key:
        return None
    
    try:
        # Construct location query
        location = f"{city},{state},US"
        url = f"http://api.openweathermap.org/data/2.5/weather"
        
        params = {
            'q': location,
            'appid': api_key,
            'units': 'imperial'  # Fahrenheit temperatures
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant weather information
        return {
            'temp': round(data['main']['temp']),
            'wind': round(data['wind']['speed']),
            'condition': data['weather'][0]['description'].title(),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'feels_like': round(data['main']['feels_like']),
            'source': 'OpenWeatherMap'
        }
        
    except requests.exceptions.RequestException as e:
        st.warning(f"Weather API request failed: {str(e)}")
        return None
    except KeyError as e:
        st.warning(f"Weather API response format error: {str(e)}")
        return None
    except Exception as e:
        st.warning(f"Unexpected weather API error: {str(e)}")
        return None

# =============================================================================
# WEATHER CACHE MANAGEMENT
# =============================================================================

def cache_weather_data(team_name: str, weather_data: Dict):
    """
    PURPOSE: Cache weather data to reduce API calls
    INPUTS: team_name (str), weather_data (Dict)
    OUTPUTS: Weather data saved to database cache
    DEPENDENCIES: SQLite database
    NOTES: 30-minute cache to stay within API limits
    """
    try:
        conn = init_database()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO weather_cache 
            (team_name, temp, wind, condition, humidity, pressure, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            team_name,
            weather_data['temp'],
            weather_data['wind'],
            weather_data['condition'],
            weather_data.get('humidity', 0),
            weather_data.get('pressure', 0),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.warning(f"Weather cache error: {str(e)}")

def get_cached_weather_data(team_name: str) -> Optional[Dict]:
    """
    PURPOSE: Retrieve cached weather data if recent enough
    INPUTS: team_name (str)
    OUTPUTS: Cached weather data or None if expired/missing
    DEPENDENCIES: SQLite database
    NOTES: Returns data only if less than 30 minutes old
    """
    try:
        conn = init_database()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT temp, wind, condition, humidity, pressure, last_updated
            FROM weather_cache WHERE team_name = ?
        ''', (team_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Check if cache is still valid (30 minutes)
        last_updated = datetime.fromisoformat(row[5])
        if datetime.now() - last_updated > timedelta(minutes=30):
            return None
        
        return {
            'temp': row[0],
            'wind': row[1],
            'condition': row[2],
            'humidity': row[3],
            'pressure': row[4],
            'source': 'Cache'
        }
        
    except Exception as e:
        st.warning(f"Weather cache retrieval error: {str(e)}")
        return None

# =============================================================================
# GPT-3.5 TURBO WEATHER FALLBACK SYSTEM
# =============================================================================

def get_gpt_weather_analysis(city: str, state: str, is_dome: bool) -> Dict:
    """
    PURPOSE: Generate realistic weather analysis using GPT-3.5 Turbo
    INPUTS: city, state, is_dome - Location and venue information
    OUTPUTS: Comprehensive weather analysis with strategic impact
    DEPENDENCIES: OpenAI API
    NOTES: Fallback system when real weather API unavailable
    """
    try:
        if "OPENAI_API_KEY" in st.secrets:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            
            month = datetime.now().month
            season = "winter" if month in [12, 1, 2] else "spring" if month in [3, 4, 5] else "summer" if month in [6, 7, 8] else "fall"
            
            prompt = f"""
            Provide realistic current weather conditions for {city}, {state} in {season}.
            
            Requirements:
            1. Realistic temperature for the location and season
            2. Appropriate wind speed (0-25 mph typical range)
            3. Logical weather condition description
            4. Consider geographic and seasonal patterns
            
            Respond ONLY with valid JSON in this exact format:
            {{
                "temp": integer_temperature_fahrenheit,
                "wind": integer_wind_speed_mph,
                "condition": "descriptive_weather_condition",
                "realistic": true
            }}
            
            DO NOT include any other text or formatting.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a meteorologist providing accurate weather data in JSON format only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            # Parse GPT response
            import json
            weather_text = response.choices[0].message.content.strip()
            # Remove any markdown formatting
            weather_text = weather_text.replace('```json', '').replace('```', '').strip()
            
            weather_data = json.loads(weather_text)
            weather_data['source'] = 'GPT Analysis'
            
            return weather_data
            
    except Exception as e:
        st.warning(f"GPT weather analysis failed: {str(e)}")
    
    # Final fallback to geographic simulation
    return get_geographic_simulation(city, state, is_dome)

def get_geographic_simulation(city: str, state: str, is_dome: bool) -> Dict:
    """
    PURPOSE: Geographic-based weather simulation as final fallback
    INPUTS: city, state, is_dome - Location information
    OUTPUTS: Simulated weather data based on geographic patterns
    DEPENDENCIES: None
    NOTES: Last resort when both APIs fail
    """
    month = datetime.now().month
    
    # Geographic weather patterns
    if state in ['FL', 'TX', 'AZ', 'CA', 'LA']:  # Warm weather states
        base_temp = 75 if month in [6, 7, 8] else 65
        temp = base_temp + random.randint(-10, 15)
        wind = random.randint(3, 12)
        conditions = ['Clear', 'Partly Cloudy', 'Sunny', 'Warm']
        
    elif state in ['NY', 'MA', 'PA', 'OH', 'MI', 'WI', 'MN', 'IL']:  # Cold weather states
        if month in [12, 1, 2]:  # Winter
            base_temp = 35
            temp = base_temp + random.randint(-20, 15)
            wind = random.randint(8, 20)
            conditions = ['Cold', 'Overcast', 'Cloudy', 'Freezing'] if temp < 32 else ['Cool', 'Overcast']
        else:
            base_temp = 65
            temp = base_temp + random.randint(-10, 20)
            wind = random.randint(5, 15)
            conditions = ['Clear', 'Partly Cloudy', 'Mild']
            
    else:  # Moderate climate
        base_temp = 68
        temp = base_temp + random.randint(-12, 18)
        wind = random.randint(4, 14)
        conditions = ['Partly Cloudy', 'Clear', 'Mild']
    
    return {
        'temp': temp,
        'wind': wind,
        'condition': random.choice(conditions),
        'source': 'Geographic Simulation'
    }

# =============================================================================
# STRATEGIC WEATHER IMPACT ANALYSIS
# =============================================================================

def calculate_strategic_impact(weather_data: Dict, is_dome: bool) -> Dict:
    """
    PURPOSE: Calculate strategic impact of weather conditions on football strategy
    INPUTS: weather_data (Dict), is_dome (bool)
    OUTPUTS: Strategic impact analysis with recommendations
    DEPENDENCIES: Weather data
    NOTES: Professional-grade strategic analysis for game planning
    """
    if is_dome:
        return {
            'passing_efficiency': 0.02,
            'deep_ball_success': 0.05,
            'fumble_increase': -0.05,
            'kicking_accuracy': 0.03,
            'recommended_adjustments': [
                'Ideal dome conditions - full playbook available',
                'Maximize vertical passing opportunities',
                'Standard field goal ranges apply',
                'No weather-related tactical limitations'
            ],
            'risk_level': 'MINIMAL'
        }
    
    temp = weather_data.get('temp', 70)
    wind = weather_data.get('wind', 5)
    
    # Calculate impact factors
    wind_factor = min(wind / 10.0, 2.5)  # Cap wind factor at 2.5
    temp_factor = abs(65 - temp) / 100.0
    
    # Strategic adjustments based on conditions
    adjustments = []
    risk_level = 'LOW'
    
    # Wind impact analysis
    if wind > 25:
        adjustments.extend([
            'EXTREME WIND: Cancel all deep passing attempts',
            'Focus exclusively on running game and screens',
            'Avoid field goal attempts beyond 35 yards',
            'Consider wind direction for all kicks'
        ])
        risk_level = 'CRITICAL'
    elif wind > 20:
        adjustments.extend([
            'HIGH WIND: Reduce deep passing by 60%',
            'Emphasize running game and underneath routes',
            'Limit field goal attempts to 40 yards',
            'Use wind-assisted punting strategy'
        ])
        risk_level = 'HIGH'
    elif wind > 15:
        adjustments.extend([
            'MODERATE WIND: Reduce deep passing by 40%',
            'Focus on crossing routes and slants',
            'Field goal range reduced to 45 yards',
            'Adjust punt coverage for wind drift'
        ])
        risk_level = 'MODERATE'
    elif wind > 10:
        adjustments.extend([
            'LIGHT WIND: Minor passing adjustments needed',
            'Favor routes under 25 yards',
            'Standard field goal range with caution'
        ])
    
    # Temperature impact analysis
    if temp < 10:
        adjustments.extend([
            'EXTREME COLD: Maximum ball security protocols',
            'Glove usage mandatory for all skill players',
            'Shortened passing routes only',
            'Increased risk of equipment failures'
        ])
        risk_level = max(risk_level, 'HIGH') if risk_level != 'CRITICAL' else 'CRITICAL'
    elif temp < 25:
        adjustments.extend([
            'SEVERE COLD: Enhanced ball security focus',
            'Cold weather gloves for all players',
            'Shorter, quicker passing concepts',
            'Potential for decreased kicking accuracy'
        ])
        risk_level = max(risk_level, 'MODERATE') if risk_level not in ['CRITICAL', 'HIGH'] else risk_level
    elif temp < 35:
        adjustments.extend([
            'COLD CONDITIONS: Focus on ball security',
            'Fumble risk increases with cold hands',
            'Consider hand warmers for skill positions'
        ])
    elif temp > 90:
        adjustments.extend([
            'HOT CONDITIONS: Hydration protocols critical',
            'Increased player rotation needed',
            'Potential for heat-related fatigue'
        ])
    
    # Default favorable conditions
    if not adjustments:
        adjustments = [
            'FAVORABLE CONDITIONS: Full playbook available',
            'Balanced offensive approach recommended',
            'Standard tactical options apply'
        ]
        risk_level = 'MINIMAL'
    
    return {
        'passing_efficiency': -0.03 * wind_factor - 0.015 * temp_factor,
        'deep_ball_success': -0.08 * wind_factor,
        'fumble_increase': 0.02 * temp_factor + 0.01 * (wind_factor if wind > 15 else 0),
        'kicking_accuracy': -0.05 * wind_factor - 0.02 * temp_factor,
        'recommended_adjustments': adjustments,
        'risk_level': risk_level,
        'wind_factor': wind_factor,
        'temp_factor': temp_factor
    }

# =============================================================================
# MAIN WEATHER DATA FUNCTION
# =============================================================================

def get_comprehensive_weather_data(team_name: str, city: str, state: str, is_dome: bool) -> Dict:
    """
    PURPOSE: Get comprehensive weather data with multiple fallback layers
    INPUTS: team_name, city, state, is_dome
    OUTPUTS: Complete weather analysis with strategic impact
    DEPENDENCIES: All weather modules
    NOTES: Primary->Cache->Real API->GPT->Simulation fallback chain
    """
    
    # Handle dome venues immediately
    if is_dome:
        dome_data = {
            'temp': 72,
            'wind': 0,
            'condition': 'Dome - Controlled Environment',
            'source': 'Dome Environment'
        }
        strategic_impact = calculate_strategic_impact(dome_data, True)
        dome_data['strategic_impact'] = strategic_impact
        return dome_data
    
    # Try cached data first
    cached_data = get_cached_weather_data(team_name)
    if cached_data:
        strategic_impact = calculate_strategic_impact(cached_data, False)
        cached_data['strategic_impact'] = strategic_impact
        return cached_data
    
    # Try real weather API
    real_weather = get_real_weather_data(city, state)
    if real_weather:
        strategic_impact = calculate_strategic_impact(real_weather, False)
        real_weather['strategic_impact'] = strategic_impact
        
        # Cache the successful result
        cache_weather_data(team_name, real_weather)
        return real_weather
    
    # Fallback to GPT analysis
    gpt_weather = get_gpt_weather_analysis(city, state, False)
    strategic_impact = calculate_strategic_impact(gpt_weather, False)
    gpt_weather['strategic_impact'] = strategic_impact
    
    # Cache GPT result as well
    cache_weather_data(team_name, gpt_weather)
    return gpt_weather

# =============================================================================
# WEATHER SUMMARY FUNCTIONS
# =============================================================================

def get_weather_summary(weather_data: Dict) -> str:
    """
    PURPOSE: Generate concise weather summary for display
    INPUTS: weather_data (Dict)
    OUTPUTS: Formatted weather summary string
    DEPENDENCIES: Weather data
    NOTES: User-friendly summary for interface display
    """
    temp = weather_data.get('temp', 'N/A')
    wind = weather_data.get('wind', 'N/A')
    condition = weather_data.get('condition', 'Unknown')
    source = weather_data.get('source', 'Unknown')
    
    summary = f"{temp}°F, {wind}mph wind, {condition}"
    
    if 'strategic_impact' in weather_data:
        risk = weather_data['strategic_impact'].get('risk_level', 'LOW')
        summary += f" (Risk: {risk})"
    
    return summary

def get_weather_alerts(weather_data: Dict) -> List[str]:
    """
    PURPOSE: Generate weather-based strategic alerts
    INPUTS: weather_data (Dict)
    OUTPUTS: List of alert messages
    DEPENDENCIES: Weather data with strategic impact
    NOTES: Critical alerts for tactical planning
    """
    if 'strategic_impact' not in weather_data:
        return []
    
    impact = weather_data['strategic_impact']
    alerts = []
    
    # Generate alerts based on risk level
    risk_level = impact.get('risk_level', 'LOW')
    
    if risk_level == 'CRITICAL':
        alerts.append("🚨 CRITICAL WEATHER CONDITIONS - Major tactical adjustments required")
    elif risk_level == 'HIGH':
        alerts.append("⚠️ HIGH IMPACT WEATHER - Significant strategic modifications needed")
    elif risk_level == 'MODERATE':
        alerts.append("⚡ MODERATE WEATHER IMPACT - Tactical adjustments recommended")
    
    # Add specific condition alerts
    temp = weather_data.get('temp', 70)
    wind = weather_data.get('wind', 5)
    
    if wind > 20:
        alerts.append(f"🌪️ EXTREME WIND ALERT: {wind}mph winds will severely impact passing game")
    elif wind > 15:
        alerts.append(f"💨 HIGH WIND WARNING: {wind}mph winds require passing game adjustments")
    
    if temp < 20:
        alerts.append(f"🥶 EXTREME COLD ALERT: {temp}°F requires maximum ball security protocols")
    elif temp < 32:
        alerts.append(f"❄️ FREEZING CONDITIONS: {temp}°F increases fumble risk significantly")
    
    return alerts
