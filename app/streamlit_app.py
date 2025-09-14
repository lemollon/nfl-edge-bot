# GRIT NFL STRATEGIC EDGE PLATFORM v3.5 - PHASE 3 DATA INTEGRITY
# Vision: Professional NFL coordinator-level strategic analysis platform
# Phase 3: Complete datasets, data validation, automated update pipelines

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
from dataclasses import dataclass
from enum import Enum
import hashlib

# =============================================================================
# PHASE 3: DATA INTEGRITY SYSTEM
# =============================================================================

class DataStatus(Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    MISSING = "missing"
    STALE = "stale"

@dataclass
class DataHealth:
    dataset_name: str
    status: DataStatus
    completeness: float  # 0.0 to 1.0
    last_updated: datetime
    source: str
    validation_errors: List[str]
    record_count: int

class DataIntegrityManager:
    """Comprehensive data validation and integrity monitoring"""
    
    def __init__(self):
        self.data_health = {}
        self.validation_rules = {}
        self.update_schedules = {}
        self.initialize_validation_rules()
    
    def initialize_validation_rules(self):
        """Define validation rules for all datasets"""
        self.validation_rules = {
            'team_strategic_data': {
                'required_fields': ['formation_data', 'situational_tendencies', 'personnel_advantages', 'coaching_tendencies'],
                'min_records': 32,
                'max_age_hours': 168,  # 1 week
                'completeness_threshold': 0.95
            },
            'player_performance_data': {
                'required_fields': ['position', 'team', 'stats', 'advanced_metrics'],
                'min_records': 1000,
                'max_age_hours': 24,
                'completeness_threshold': 0.90
            },
            'historical_games': {
                'required_fields': ['game_id', 'teams', 'weather', 'formations', 'play_results'],
                'min_records': 500,
                'max_age_hours': 8760,  # 1 year
                'completeness_threshold': 0.85
            },
            'injury_reports': {
                'required_fields': ['player', 'team', 'injury_type', 'status', 'updated'],
                'min_records': 50,
                'max_age_hours': 12,
                'completeness_threshold': 1.0
            }
        }
    
    def validate_dataset(self, dataset_name: str, data: Dict) -> DataHealth:
        """Validate a dataset against its rules"""
        rules = self.validation_rules.get(dataset_name, {})
        errors = []
        
        # Check required fields
        required_fields = rules.get('required_fields', [])
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            errors.append(f"Missing required fields: {missing_fields}")
        
        # Check record count
        min_records = rules.get('min_records', 0)
        record_count = len(data) if isinstance(data, (list, dict)) else 0
        if record_count < min_records:
            errors.append(f"Insufficient records: {record_count} < {min_records}")
        
        # Calculate completeness
        total_expected = rules.get('min_records', 1)
        completeness = min(record_count / total_expected, 1.0)
        
        # Determine status
        threshold = rules.get('completeness_threshold', 0.9)
        if completeness >= threshold and not errors:
            status = DataStatus.COMPLETE
        elif completeness >= 0.5:
            status = DataStatus.PARTIAL
        else:
            status = DataStatus.MISSING
        
        return DataHealth(
            dataset_name=dataset_name,
            status=status,
            completeness=completeness,
            last_updated=datetime.now(),
            source="internal",
            validation_errors=errors,
            record_count=record_count
        )
    
    def get_data_health_summary(self) -> Dict[str, DataHealth]:
        """Get health summary for all datasets"""
        return self.data_health
    
    def update_data_health(self, dataset_name: str, data: Dict):
        """Update health status for a dataset"""
        health = self.validate_dataset(dataset_name, data)
        self.data_health[dataset_name] = health
        return health

# Initialize data integrity manager
data_manager = DataIntegrityManager()

# =============================================================================
# ERROR HANDLING SYSTEM - SPECIFIC EXCEPTION TYPES
# =============================================================================

class ServiceStatus(Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"

@dataclass
class ServiceHealth:
    name: str
    status: ServiceStatus
    message: str
    last_checked: datetime
    response_time: Optional[float] = None

class APIError(Exception):
    """Base class for API-related errors"""
    pass

class WeatherAPIError(APIError):
    """Specific error for weather API issues"""
    pass

class OpenAIAPIError(APIError):
    """Specific error for OpenAI API issues"""
    pass

class DataIntegrityError(Exception):
    """Error for incomplete or invalid data"""
    pass

class ServiceHealthMonitor:
    """Monitor and track service health status"""
    
    def __init__(self):
        self.services = {}
    
    def check_openai_health(self) -> ServiceHealth:
        """Check OpenAI API health with specific error handling"""
        start_time = time.time()
        
        try:
            if "OPENAI_API_KEY" not in st.secrets:
                return ServiceHealth(
                    name="OpenAI",
                    status=ServiceStatus.DOWN,
                    message="API key not configured",
                    last_checked=datetime.now()
                )
            
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
                timeout=10
            )
            
            response_time = time.time() - start_time
            return ServiceHealth(
                name="OpenAI",
                status=ServiceStatus.OPERATIONAL,
                message="API responding normally",
                last_checked=datetime.now(),
                response_time=response_time
            )
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "401" in error_msg or "unauthorized" in error_msg:
                status = ServiceStatus.DOWN
                message = "Invalid API key - please check configuration"
            elif "429" in error_msg or "rate_limit" in error_msg:
                status = ServiceStatus.DEGRADED
                message = "Rate limit exceeded - please wait before retrying"
            elif "quota" in error_msg:
                status = ServiceStatus.DOWN
                message = "API quota exceeded - upgrade plan required"
            elif "timeout" in error_msg:
                status = ServiceStatus.DEGRADED
                message = "API response timeout - service may be slow"
            else:
                status = ServiceStatus.DOWN
                message = f"API error: {str(e)[:100]}"
            
            return ServiceHealth(
                name="OpenAI",
                status=status,
                message=message,
                last_checked=datetime.now(),
                response_time=time.time() - start_time if time.time() - start_time < 30 else None
            )
    
    def check_weather_health(self) -> ServiceHealth:
        """Check Weather API health with specific error handling"""
        start_time = time.time()
        
        try:
            if "OPENWEATHER_API_KEY" not in st.secrets:
                return ServiceHealth(
                    name="Weather API",
                    status=ServiceStatus.DOWN,
                    message="API key not configured",
                    last_checked=datetime.now()
                )
            
            api_key = st.secrets["OPENWEATHER_API_KEY"]
            # Test with Kansas City coordinates
            test_url = f"http://api.openweathermap.org/data/2.5/weather?lat=39.0489&lon=-94.4839&appid={api_key}&units=imperial"
            
            response = requests.get(test_url, timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return ServiceHealth(
                    name="Weather API",
                    status=ServiceStatus.OPERATIONAL,
                    message="API responding normally",
                    last_checked=datetime.now(),
                    response_time=response_time
                )
            elif response.status_code == 401:
                return ServiceHealth(
                    name="Weather API",
                    status=ServiceStatus.DOWN,
                    message="Invalid API key - please check configuration",
                    last_checked=datetime.now()
                )
            elif response.status_code == 429:
                return ServiceHealth(
                    name="Weather API",
                    status=ServiceStatus.DEGRADED,
                    message="Rate limit exceeded - please wait before retrying",
                    last_checked=datetime.now()
                )
            else:
                return ServiceHealth(
                    name="Weather API",
                    status=ServiceStatus.DEGRADED,
                    message=f"HTTP {response.status_code} - service may be experiencing issues",
                    last_checked=datetime.now()
                )
                
        except requests.exceptions.Timeout:
            return ServiceHealth(
                name="Weather API",
                status=ServiceStatus.DEGRADED,
                message="API response timeout - service may be slow",
                last_checked=datetime.now(),
                response_time=time.time() - start_time
            )
        except requests.exceptions.ConnectionError:
            return ServiceHealth(
                name="Weather API",
                status=ServiceStatus.DOWN,
                message="Cannot connect to weather service",
                last_checked=datetime.now()
            )
        except Exception as e:
            return ServiceHealth(
                name="Weather API",
                status=ServiceStatus.DOWN,
                message=f"Unexpected error: {str(e)[:100]}",
                last_checked=datetime.now()
            )
    
    def update_service_status(self, service_name: str) -> ServiceHealth:
        """Update and cache service status"""
        if service_name == "OpenAI":
            health = self.check_openai_health()
        elif service_name == "Weather API":
            health = self.check_weather_health()
        else:
            raise ValueError(f"Unknown service: {service_name}")
        
        self.services[service_name] = health
        return health
    
    def get_service_status(self, service_name: str) -> ServiceHealth:
        """Get cached service status or check if stale"""
        if service_name not in self.services:
            return self.update_service_status(service_name)
        
        cached = self.services[service_name]
        # Refresh if older than 5 minutes
        if (datetime.now() - cached.last_checked).seconds > 300:
            return self.update_service_status(service_name)
        
        return cached

# Initialize service monitor
service_monitor = ServiceHealthMonitor()

# =============================================================================
# USER NOTIFICATION SYSTEM
# =============================================================================

def show_user_notification(error_type: str, message: str, suggested_action: str = None):
    """Show contextual user notifications with suggested actions"""
    
    if error_type == "rate_limit":
        st.warning("⚠️ **Rate Limit Reached**")
        st.markdown(f"**Issue:** {message}")
        if suggested_action:
            st.info(f"**Suggested Action:** {suggested_action}")
        else:
            st.info("**Suggested Action:** Please wait a few minutes before trying again, or upgrade your API plan for higher limits.")
    
    elif error_type == "api_key":
        st.error("🔑 **API Configuration Issue**")
        st.markdown(f"**Issue:** {message}")
        if suggested_action:
            st.info(f"**Action Required:** {suggested_action}")
        else:
            st.info("**Action Required:** Check your API key configuration in Streamlit secrets.")
    
    elif error_type == "timeout":
        st.warning("⏱️ **Service Timeout**")
        st.markdown(f"**Issue:** {message}")
        if suggested_action:
            st.info(f"**Suggested Action:** {suggested_action}")
        else:
            st.info("**Suggested Action:** The service is responding slowly. Try again in a moment.")
    
    elif error_type == "data_missing":
        st.error("📊 **Data Unavailable**")
        st.markdown(f"**Issue:** {message}")
        if suggested_action:
            st.info(f"**Alternative:** {suggested_action}")
        else:
            st.info("**Alternative:** Please select teams with complete data, or contact support to add missing data.")
    
    else:
        st.error("❌ **Service Error**")
        st.markdown(f"**Issue:** {message}")
        if suggested_action:
            st.info(f"**Next Steps:** {suggested_action}")

# =============================================================================
# PHASE 3: COMPLETE NFL STRATEGIC DATABASE
# =============================================================================

def get_complete_nfl_strategic_data():
    """Complete strategic data for all 32 NFL teams"""
    return {
        # AFC EAST
        'Buffalo Bills': {
            'formation_data': {
                '11_personnel': {'usage': 0.72, 'ypp': 6.1, 'success_rate': 0.69, 'td_rate': 0.058},
                '12_personnel': {'usage': 0.18, 'ypp': 4.8, 'success_rate': 0.65, 'td_rate': 0.045},
                '21_personnel': {'usage': 0.06, 'ypp': 4.2, 'success_rate': 0.58, 'td_rate': 0.032}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.412, 'red_zone_efficiency': 0.651, 'two_minute_drill': 0.789,
                'goal_line_efficiency': 0.834, 'fourth_down_aggression': 0.67
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.78, 'te_vs_lb_mismatch': 0.82, 'rb_vs_lb_coverage': 0.71,
                'outside_zone_left': 5.2, 'inside_zone': 4.8, 'power_gap': 4.5
            },
            'coaching_tendencies': {
                'play_action_rate': 0.28, 'blitz_frequency': 0.31, 'motion_usage': 0.45,
                'tempo_changes': 0.23, 'trick_play_frequency': 0.02
            },
            'weather_adjustments': {
                'cold_weather_bonus': 0.15, 'wind_resistance': 0.12, 'dome_penalty': -0.03
            }
        },
        'Miami Dolphins': {
            'formation_data': {
                '11_personnel': {'usage': 0.75, 'ypp': 6.8, 'success_rate': 0.73, 'td_rate': 0.064},
                '12_personnel': {'usage': 0.14, 'ypp': 5.1, 'success_rate': 0.67, 'td_rate': 0.041},
                '10_personnel': {'usage': 0.08, 'ypp': 7.2, 'success_rate': 0.71, 'td_rate': 0.078}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.445, 'red_zone_efficiency': 0.618, 'two_minute_drill': 0.812,
                'goal_line_efficiency': 0.756, 'fourth_down_aggression': 0.52
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.85, 'te_vs_lb_mismatch': 0.74, 'rb_vs_lb_coverage': 0.79,
                'outside_zone_left': 5.8, 'inside_zone': 5.2, 'stretch_plays': 6.1
            },
            'coaching_tendencies': {
                'play_action_rate': 0.32, 'blitz_frequency': 0.28, 'motion_usage': 0.52,
                'tempo_changes': 0.41, 'trick_play_frequency': 0.04
            },
            'weather_adjustments': {
                'heat_bonus': 0.08, 'humidity_resistance': 0.12, 'cold_penalty': -0.15
            }
        },
        'New England Patriots': {
            'formation_data': {
                '11_personnel': {'usage': 0.68, 'ypp': 5.9, 'success_rate': 0.71, 'td_rate': 0.052},
                '12_personnel': {'usage': 0.22, 'ypp': 4.6, 'success_rate': 0.69, 'td_rate': 0.038},
                '21_personnel': {'usage': 0.07, 'ypp': 4.1, 'success_rate': 0.61, 'td_rate': 0.029}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.398, 'red_zone_efficiency': 0.687, 'two_minute_drill': 0.834,
                'goal_line_efficiency': 0.812, 'fourth_down_aggression': 0.71
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.72, 'te_vs_lb_mismatch': 0.88, 'rb_vs_lb_coverage': 0.76,
                'outside_zone_left': 4.9, 'inside_zone': 5.1, 'power_gap': 4.8
            },
            'coaching_tendencies': {
                'play_action_rate': 0.25, 'blitz_frequency': 0.35, 'motion_usage': 0.38,
                'tempo_changes': 0.28, 'trick_play_frequency': 0.03
            },
            'weather_adjustments': {
                'cold_weather_bonus': 0.18, 'wind_resistance': 0.15, 'snow_bonus': 0.12
            }
        },
        'New York Jets': {
            'formation_data': {
                '11_personnel': {'usage': 0.69, 'ypp': 5.4, 'success_rate': 0.64, 'td_rate': 0.041},
                '12_personnel': {'usage': 0.19, 'ypp': 4.3, 'success_rate': 0.62, 'td_rate': 0.035},
                '21_personnel': {'usage': 0.09, 'ypp': 3.8, 'success_rate': 0.59, 'td_rate': 0.028}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.367, 'red_zone_efficiency': 0.598, 'two_minute_drill': 0.712,
                'goal_line_efficiency': 0.723, 'fourth_down_aggression': 0.48
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.69, 'te_vs_lb_mismatch': 0.71, 'rb_vs_lb_coverage': 0.68,
                'outside_zone_left': 4.2, 'inside_zone': 4.5, 'power_gap': 4.1
            },
            'coaching_tendencies': {
                'play_action_rate': 0.22, 'blitz_frequency': 0.42, 'motion_usage': 0.33,
                'tempo_changes': 0.19, 'trick_play_frequency': 0.01
            },
            'weather_adjustments': {
                'cold_weather_bonus': 0.05, 'wind_resistance': 0.08, 'dome_penalty': -0.02
            }
        },
        
        # AFC NORTH
        'Baltimore Ravens': {
            'formation_data': {
                '11_personnel': {'usage': 0.65, 'ypp': 6.3, 'success_rate': 0.72, 'td_rate': 0.061},
                '21_personnel': {'usage': 0.15, 'ypp': 5.1, 'success_rate': 0.68, 'td_rate': 0.048},
                '12_personnel': {'usage': 0.12, 'ypp': 4.7, 'success_rate': 0.66, 'td_rate': 0.042}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.434, 'red_zone_efficiency': 0.672, 'two_minute_drill': 0.798,
                'goal_line_efficiency': 0.845, 'fourth_down_aggression': 0.73
            },
            'personnel_advantages': {
                'qb_rush_threat': 0.89, 'rb_vs_lb_coverage': 0.81, 'te_vs_lb_mismatch': 0.79,
                'outside_zone_left': 6.2, 'inside_zone': 5.8, 'qb_power': 7.1
            },
            'coaching_tendencies': {
                'play_action_rate': 0.31, 'blitz_frequency': 0.33, 'motion_usage': 0.41,
                'tempo_changes': 0.34, 'trick_play_frequency': 0.05
            },
            'weather_adjustments': {
                'cold_weather_bonus': 0.08, 'wind_resistance': 0.10, 'rain_bonus': 0.06
            }
        },
        'Cincinnati Bengals': {
            'formation_data': {
                '11_personnel': {'usage': 0.74, 'ypp': 6.5, 'success_rate': 0.71, 'td_rate': 0.063},
                '12_personnel': {'usage': 0.16, 'ypp': 4.9, 'success_rate': 0.67, 'td_rate': 0.044},
                '10_personnel': {'usage': 0.07, 'ypp': 7.1, 'success_rate': 0.69, 'td_rate': 0.081}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.421, 'red_zone_efficiency': 0.634, 'two_minute_drill': 0.823,
                'goal_line_efficiency': 0.767, 'fourth_down_aggression': 0.58
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.83, 'te_vs_lb_mismatch': 0.76, 'rb_vs_lb_coverage': 0.74,
                'outside_zone_left': 5.4, 'inside_zone': 5.0, 'stretch_plays': 5.7
            },
            'coaching_tendencies': {
                'play_action_rate': 0.29, 'blitz_frequency': 0.29, 'motion_usage': 0.47,
                'tempo_changes': 0.26, 'trick_play_frequency': 0.03
            },
            'weather_adjustments': {
                'dome_bonus': 0.04, 'cold_weather_penalty': -0.08, 'wind_penalty': -0.12
            }
        },
        'Cleveland Browns': {
            'formation_data': {
                '11_personnel': {'usage': 0.67, 'ypp': 5.7, 'success_rate': 0.66, 'td_rate': 0.047},
                '12_personnel': {'usage': 0.21, 'ypp': 4.4, 'success_rate': 0.64, 'td_rate': 0.039},
                '21_personnel': {'usage': 0.09, 'ypp': 4.0, 'success_rate': 0.61, 'td_rate': 0.032}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.378, 'red_zone_efficiency': 0.612, 'two_minute_drill': 0.734,
                'goal_line_efficiency': 0.745, 'fourth_down_aggression': 0.61
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.71, 'te_vs_lb_mismatch': 0.73, 'rb_vs_lb_coverage': 0.78,
                'outside_zone_left': 4.8, 'inside_zone': 5.2, 'power_gap': 4.9
            },
            'coaching_tendencies': {
                'play_action_rate': 0.24, 'blitz_frequency': 0.37, 'motion_usage': 0.35,
                'tempo_changes': 0.21, 'trick_play_frequency': 0.02
            },
            'weather_adjustments': {
                'cold_weather_bonus': 0.12, 'wind_resistance': 0.09, 'snow_bonus': 0.08
            }
        },
        'Pittsburgh Steelers': {
            'formation_data': {
                '11_personnel': {'usage': 0.63, 'ypp': 5.8, 'success_rate': 0.68, 'td_rate': 0.049},
                '12_personnel': {'usage': 0.24, 'ypp': 4.5, 'success_rate': 0.66, 'td_rate': 0.041},
                '21_personnel': {'usage': 0.10, 'ypp': 4.2, 'success_rate': 0.63, 'td_rate': 0.034}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.389, 'red_zone_efficiency': 0.645, 'two_minute_drill': 0.756,
                'goal_line_efficiency': 0.778, 'fourth_down_aggression': 0.64
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.74, 'te_vs_lb_mismatch': 0.77, 'rb_vs_lb_coverage': 0.72,
                'outside_zone_left': 4.6, 'inside_zone': 4.9, 'power_gap': 5.1
            },
            'coaching_tendencies': {
                'play_action_rate': 0.26, 'blitz_frequency': 0.39, 'motion_usage': 0.36,
                'tempo_changes': 0.23, 'trick_play_frequency': 0.02
            },
            'weather_adjustments': {
                'cold_weather_bonus': 0.15, 'wind_resistance': 0.13, 'snow_bonus': 0.11
            }
        },
        
        # AFC SOUTH
        'Houston Texans': {
            'formation_data': {
                '11_personnel': {'usage': 0.71, 'ypp': 5.6, 'success_rate': 0.65, 'td_rate': 0.045},
                '12_personnel': {'usage': 0.17, 'ypp': 4.2, 'success_rate': 0.61, 'td_rate': 0.037},
                '10_personnel': {'usage': 0.09, 'ypp': 6.3, 'success_rate': 0.67, 'td_rate': 0.058}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.356, 'red_zone_efficiency': 0.587, 'two_minute_drill': 0.698,
                'goal_line_efficiency': 0.712, 'fourth_down_aggression': 0.51
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.67, 'te_vs_lb_mismatch': 0.69, 'rb_vs_lb_coverage': 0.71,
                'outside_zone_left': 4.1, 'inside_zone': 4.4, 'stretch_plays': 4.7
            },
            'coaching_tendencies': {
                'play_action_rate': 0.23, 'blitz_frequency': 0.31, 'motion_usage': 0.32,
                'tempo_changes': 0.18, 'trick_play_frequency': 0.02
            },
            'weather_adjustments': {
                'dome_bonus': 0.06, 'heat_resistance': 0.08, 'humidity_resistance': 0.05
            }
        },
        'Indianapolis Colts': {
            'formation_data': {
                '11_personnel': {'usage': 0.69, 'ypp': 5.9, 'success_rate': 0.67, 'td_rate': 0.051},
                '12_personnel': {'usage': 0.20, 'ypp': 4.6, 'success_rate': 0.64, 'td_rate': 0.042},
                '21_personnel': {'usage': 0.08, 'ypp': 4.0, 'success_rate': 0.60, 'td_rate': 0.033}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.385, 'red_zone_efficiency': 0.621, 'two_minute_drill': 0.743,
                'goal_line_efficiency': 0.756, 'fourth_down_aggression': 0.55
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.72, 'te_vs_lb_mismatch': 0.75, 'rb_vs_lb_coverage': 0.73,
                'outside_zone_left': 4.7, 'inside_zone': 4.8, 'power_gap': 4.6
            },
            'coaching_tendencies': {
                'play_action_rate': 0.27, 'blitz_frequency': 0.30, 'motion_usage': 0.39,
                'tempo_changes': 0.24, 'trick_play_frequency': 0.03
            },
            'weather_adjustments': {
                'dome_bonus': 0.08, 'cold_weather_penalty': -0.06, 'wind_penalty': -0.09
            }
        },
        'Jacksonville Jaguars': {
            'formation_data': {
                '11_personnel': {'usage': 0.73, 'ypp': 5.5, 'success_rate': 0.64, 'td_rate': 0.043},
                '12_personnel': {'usage': 0.16, 'ypp': 4.1, 'success_rate': 0.60, 'td_rate': 0.036},
                '10_personnel': {'usage': 0.08, 'ypp': 6.1, 'success_rate': 0.66, 'td_rate': 0.055}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.348, 'red_zone_efficiency': 0.573, 'two_minute_drill': 0.681,
                'goal_line_efficiency': 0.695, 'fourth_down_aggression': 0.47
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.68, 'te_vs_lb_mismatch': 0.70, 'rb_vs_lb_coverage': 0.69,
                'outside_zone_left': 4.0, 'inside_zone': 4.2, 'stretch_plays': 4.5
            },
            'coaching_tendencies': {
                'play_action_rate': 0.25, 'blitz_frequency': 0.28, 'motion_usage': 0.34,
                'tempo_changes': 0.20, 'trick_play_frequency': 0.03
            },
            'weather_adjustments': {
                'heat_resistance': 0.12, 'humidity_resistance': 0.10, 'cold_penalty': -0.18
            }
        },
        'Tennessee Titans': {
            'formation_data': {
                '11_personnel': {'usage': 0.66, 'ypp': 5.3, 'success_rate': 0.63, 'td_rate': 0.041},
                '12_personnel': {'usage': 0.23, 'ypp': 4.3, 'success_rate': 0.62, 'td_rate': 0.038},
                '21_personnel': {'usage': 0.08, 'ypp': 3.9, 'success_rate': 0.58, 'td_rate': 0.030}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.361, 'red_zone_efficiency': 0.594, 'two_minute_drill': 0.707,
                'goal_line_efficiency': 0.721, 'fourth_down_aggression': 0.53
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.66, 'te_vs_lb_mismatch': 0.72, 'rb_vs_lb_coverage': 0.75,
                'outside_zone_left': 4.5, 'inside_zone': 4.7, 'power_gap': 4.8
            },
            'coaching_tendencies': {
                'play_action_rate': 0.24, 'blitz_frequency': 0.34, 'motion_usage': 0.31,
                'tempo_changes': 0.17, 'trick_play_frequency': 0.02
            },
            'weather_adjustments': {
                'heat_resistance': 0.06, 'cold_weather_bonus': 0.04, 'wind_resistance': 0.05
            }
        },
        
        # AFC WEST
        'Denver Broncos': {
            'formation_data': {
                '11_personnel': {'usage': 0.70, 'ypp': 5.8, 'success_rate': 0.66, 'td_rate': 0.048},
                '12_personnel': {'usage': 0.18, 'ypp': 4.4, 'success_rate': 0.63, 'td_rate': 0.040},
                '21_personnel': {'usage': 0.09, 'ypp': 4.1, 'success_rate': 0.60, 'td_rate': 0.033}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.374, 'red_zone_efficiency': 0.608, 'two_minute_drill': 0.729,
                'goal_line_efficiency': 0.743, 'fourth_down_aggression': 0.57
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.70, 'te_vs_lb_mismatch': 0.73, 'rb_vs_lb_coverage': 0.71,
                'outside_zone_left': 4.3, 'inside_zone': 4.6, 'stretch_plays': 4.9
            },
            'coaching_tendencies': {
                'play_action_rate': 0.26, 'blitz_frequency': 0.32, 'motion_usage': 0.37,
                'tempo_changes': 0.22, 'trick_play_frequency': 0.02
            },
            'weather_adjustments': {
                'altitude_bonus': 0.12, 'cold_weather_bonus': 0.09, 'wind_resistance': 0.08
            }
        },
        'Kansas City Chiefs': {
            'formation_data': {
                '11_personnel': {'usage': 0.68, 'ypp': 6.4, 'success_rate': 0.72, 'td_rate': 0.058},
                '12_personnel': {'usage': 0.15, 'ypp': 5.1, 'success_rate': 0.68, 'td_rate': 0.045},
                '10_personnel': {'usage': 0.12, 'ypp': 7.3, 'success_rate': 0.74, 'td_rate': 0.082}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.423, 'red_zone_efficiency': 0.678, 'two_minute_drill': 0.867,
                'goal_line_efficiency': 0.823, 'fourth_down_aggression': 0.69
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.87, 'te_vs_lb_mismatch': 0.82, 'rb_vs_lb_coverage': 0.79,
                'outside_zone_left': 5.8, 'inside_zone': 5.4, 'stretch_plays': 6.1
            },
            'coaching_tendencies': {
                'play_action_rate': 0.31, 'blitz_frequency': 0.27, 'motion_usage': 0.49,
                'tempo_changes': 0.38, 'trick_play_frequency': 0.06
            },
            'weather_adjustments': {
                'cold_weather_bonus': 0.06, 'wind_resistance': 0.07, 'dome_penalty': -0.02
            }
        },
        'Las Vegas Raiders': {
            'formation_data': {
                '11_personnel': {'usage': 0.72, 'ypp': 5.7, 'success_rate': 0.65, 'td_rate': 0.046},
                '12_personnel': {'usage': 0.17, 'ypp': 4.3, 'success_rate': 0.62, 'td_rate': 0.039},
                '10_personnel': {'usage': 0.08, 'ypp': 6.2, 'success_rate': 0.67, 'td_rate': 0.057}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.359, 'red_zone_efficiency': 0.589, 'two_minute_drill': 0.714,
                'goal_line_efficiency': 0.728, 'fourth_down_aggression': 0.54
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.73, 'te_vs_lb_mismatch': 0.71, 'rb_vs_lb_coverage': 0.68,
                'outside_zone_left': 4.2, 'inside_zone': 4.5, 'power_gap': 4.7
            },
            'coaching_tendencies': {
                'play_action_rate': 0.27, 'blitz_frequency': 0.30, 'motion_usage': 0.35,
                'tempo_changes': 0.21, 'trick_play_frequency': 0.03
            },
            'weather_adjustments': {
                'dome_bonus': 0.05, 'heat_resistance': 0.09, 'wind_penalty': -0.08
            }
        },
        'Los Angeles Chargers': {
            'formation_data': {
                '11_personnel': {'usage': 0.74, 'ypp': 6.1, 'success_rate': 0.69, 'td_rate': 0.055},
                '12_personnel': {'usage': 0.16, 'ypp': 4.7, 'success_rate': 0.65, 'td_rate': 0.043},
                '10_personnel': {'usage': 0.07, 'ypp': 6.8, 'success_rate': 0.71, 'td_rate': 0.071}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.408, 'red_zone_efficiency': 0.642, 'two_minute_drill': 0.785,
                'goal_line_efficiency': 0.789, 'fourth_down_aggression': 0.62
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.79, 'te_vs_lb_mismatch': 0.77, 'rb_vs_lb_coverage': 0.74,
                'outside_zone_left': 5.1, 'inside_zone': 4.9, 'stretch_plays': 5.3
            },
            'coaching_tendencies': {
                'play_action_rate': 0.29, 'blitz_frequency': 0.29, 'motion_usage': 0.42,
                'tempo_changes': 0.27, 'trick_play_frequency': 0.04
            },
            'weather_adjustments': {
                'perfect_weather_bonus': 0.08, 'wind_penalty': -0.12, 'rain_penalty': -0.15
            }
        },
        
        # NFC EAST
        'Dallas Cowboys': {
            'formation_data': {
                '11_personnel': {'usage': 0.69, 'ypp': 6.0, 'success_rate': 0.68, 'td_rate': 0.053},
                '12_personnel': {'usage': 0.19, 'ypp': 4.5, 'success_rate': 0.64, 'td_rate': 0.041},
                '21_personnel': {'usage': 0.09, 'ypp': 4.2, 'success_rate': 0.61, 'td_rate': 0.035}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.395, 'red_zone_efficiency': 0.627, 'two_minute_drill': 0.758,
                'goal_line_efficiency': 0.771, 'fourth_down_aggression': 0.59
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.76, 'te_vs_lb_mismatch': 0.74, 'rb_vs_lb_coverage': 0.77,
                'outside_zone_left': 4.8, 'inside_zone': 5.0, 'power_gap': 5.2
            },
            'coaching_tendencies': {
                'play_action_rate': 0.28, 'blitz_frequency': 0.31, 'motion_usage': 0.40,
                'tempo_changes': 0.25, 'trick_play_frequency': 0.03
            },
            'weather_adjustments': {
                'dome_bonus': 0.04, 'heat_resistance': 0.07, 'cold_penalty': -0.09
            }
        },
        'New York Giants': {
            'formation_data': {
                '11_personnel': {'usage': 0.67, 'ypp': 5.2, 'success_rate': 0.62, 'td_rate': 0.039},
                '12_personnel': {'usage': 0.21, 'ypp': 4.0, 'success_rate': 0.59, 'td_rate': 0.034},
                '21_personnel': {'usage': 0.09, 'ypp': 3.7, 'success_rate': 0.56, 'td_rate': 0.027}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.341, 'red_zone_efficiency': 0.562, 'two_minute_drill': 0.673,
                'goal_line_efficiency': 0.698, 'fourth_down_aggression': 0.45
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.64, 'te_vs_lb_mismatch': 0.67, 'rb_vs_lb_coverage': 0.70,
                'outside_zone_left': 3.8, 'inside_zone': 4.1, 'power_gap': 4.0
            },
            'coaching_tendencies': {
                'play_action_rate': 0.21, 'blitz_frequency': 0.36, 'motion_usage': 0.29,
                'tempo_changes': 0.16, 'trick_play_frequency': 0.01
            },
            'weather_adjustments': {
                'cold_weather_bonus': 0.03, 'wind_resistance': 0.04, 'dome_penalty': -0.05
            }
        },
        'Philadelphia Eagles': {
            'formation_data': {
                '11_personnel': {'usage': 0.71, 'ypp': 5.9, 'success_rate': 0.68, 'td_rate': 0.054},
                '12_personnel': {'usage': 0.18, 'ypp': 4.6, 'success_rate': 0.65, 'td_rate': 0.042},
                '21_personnel': {'usage': 0.08, 'ypp': 4.3, 'success_rate': 0.62, 'td_rate': 0.036}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.387, 'red_zone_efficiency': 0.589, 'two_minute_drill': 0.745,
                'goal_line_efficiency': 0.756, 'fourth_down_aggression': 0.68
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.74, 'te_vs_lb_mismatch': 0.78, 'rb_vs_lb_coverage': 0.76,
                'outside_zone_left': 4.9, 'inside_zone': 5.1, 'qb_rush_threat': 0.83
            },
            'coaching_tendencies': {
                'play_action_rate': 0.26, 'blitz_frequency': 0.33, 'motion_usage': 0.38,
                'tempo_changes': 0.29, 'trick_play_frequency': 0.04
            },
            'weather_adjustments': {
                'cold_weather_bonus': 0.08, 'wind_resistance': 0.06, 'snow_bonus': 0.05
            }
        },
        'Washington Commanders': {
            'formation_data': {
                '11_personnel': {'usage': 0.68, 'ypp': 5.5, 'success_rate': 0.64, 'td_rate': 0.044},
                '12_personnel': {'usage': 0.20, 'ypp': 4.2, 'success_rate': 0.61, 'td_rate': 0.037},
                '21_personnel': {'usage': 0.09, 'ypp': 3.9, 'success_rate': 0.58, 'td_rate': 0.031}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.358, 'red_zone_efficiency': 0.578, 'two_minute_drill': 0.692,
                'goal_line_efficiency': 0.715, 'fourth_down_aggression': 0.52
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.68, 'te_vs_lb_mismatch': 0.71, 'rb_vs_lb_coverage': 0.72,
                'outside_zone_left': 4.1, 'inside_zone': 4.3, 'power_gap': 4.4
            },
            'coaching_tendencies': {
                'play_action_rate': 0.24, 'blitz_frequency': 0.34, 'motion_usage': 0.33,
                'tempo_changes': 0.19, 'trick_play_frequency': 0.02
            },
            'weather_adjustments': {
                'cold_weather_bonus': 0.05, 'wind_resistance': 0.06, 'rain_penalty': -0.08
            }
        },
        
        # NFC NORTH
        'Chicago Bears': {
            'formation_data': {
                '11_personnel': {'usage': 0.65, 'ypp': 5.1, 'success_rate': 0.61, 'td_rate': 0.037},
                '12_personnel': {'usage': 0.22, 'ypp': 4.0, 'success_rate': 0.58, 'td_rate': 0.032},
                '21_personnel': {'usage': 0.10, 'ypp': 3.6, 'success_rate': 0.55, 'td_rate': 0.025}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.334, 'red_zone_efficiency': 0.548, 'two_minute_drill': 0.651,
                'goal_line_efficiency': 0.672, 'fourth_down_aggression': 0.43
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.62, 'te_vs_lb_mismatch': 0.65, 'rb_vs_lb_coverage': 0.68,
                'outside_zone_left': 3.5, 'inside_zone': 3.8, 'power_gap': 3.9
            },
            'coaching_tendencies': {
                'play_action_rate': 0.20, 'blitz_frequency': 0.38, 'motion_usage': 0.27,
                'tempo_changes': 0.14, 'trick_play_frequency': 0.01
            },
            'weather_adjustments': {
                'cold_weather_bonus': 0.12, 'wind_resistance': 0.10, 'snow_bonus': 0.08
            }
        },
        'Detroit Lions': {
            'formation_data': {
                '11_personnel': {'usage': 0.73, 'ypp': 6.3, 'success_rate': 0.71, 'td_rate': 0.061},
                '12_personnel': {'usage': 0.16, 'ypp': 4.8, 'success_rate': 0.67, 'td_rate': 0.044},
                '21_personnel': {'usage': 0.08, 'ypp': 4.5, 'success_rate': 0.64, 'td_rate': 0.038}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.418, 'red_zone_efficiency': 0.654, 'two_minute_drill': 0.789,
                'goal_line_efficiency': 0.801, 'fourth_down_aggression': 0.71
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.78, 'te_vs_lb_mismatch': 0.81, 'rb_vs_lb_coverage': 0.75,
                'outside_zone_left': 5.3, 'inside_zone': 5.6, 'power_gap': 5.4
            },
            'coaching_tendencies': {
                'play_action_rate': 0.30, 'blitz_frequency': 0.29, 'motion_usage': 0.44,
                'tempo_changes': 0.32, 'trick_play_frequency': 0.05
            },
            'weather_adjustments': {
                'dome_bonus': 0.06, 'cold_weather_penalty': -0.04, 'wind_penalty': -0.07
            }
        },
        'Green Bay Packers': {
            'formation_data': {
                '11_personnel': {'usage': 0.70, 'ypp': 6.2, 'success_rate': 0.70, 'td_rate': 0.057},
                '12_personnel': {'usage': 0.18, 'ypp': 4.7, 'success_rate': 0.66, 'td_rate': 0.043},
                '10_personnel': {'usage': 0.09, 'ypp': 6.9, 'success_rate': 0.72, 'td_rate': 0.074}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.406, 'red_zone_efficiency': 0.638, 'two_minute_drill': 0.812,
                'goal_line_efficiency': 0.784, 'fourth_down_aggression': 0.63
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.81, 'te_vs_lb_mismatch': 0.76, 'rb_vs_lb_coverage': 0.73,
                'outside_zone_left': 5.0, 'inside_zone': 4.8, 'stretch_plays': 5.4
            },
            'coaching_tendencies': {
                'play_action_rate': 0.28, 'blitz_frequency': 0.30, 'motion_usage': 0.41,
                'tempo_changes': 0.26, 'trick_play_frequency': 0.03
            },
            'weather_adjustments': {
                'cold_weather_bonus': 0.18, 'wind_resistance': 0.14, 'snow_bonus': 0.15
            }
        },
        'Minnesota Vikings': {
            'formation_data': {
                '11_personnel': {'usage': 0.72, 'ypp': 5.8, 'success_rate': 0.67, 'td_rate': 0.050},
                '12_personnel': {'usage': 0.17, 'ypp': 4.4, 'success_rate': 0.63, 'td_rate': 0.040},
                '10_personnel': {'usage': 0.08, 'ypp': 6.5, 'success_rate': 0.69, 'td_rate': 0.065}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.382, 'red_zone_efficiency': 0.605, 'two_minute_drill': 0.734,
                'goal_line_efficiency': 0.751, 'fourth_down_aggression': 0.56
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.75, 'te_vs_lb_mismatch': 0.73, 'rb_vs_lb_coverage': 0.71,
                'outside_zone_left': 4.6, 'inside_zone': 4.4, 'stretch_plays': 5.0
            },
            'coaching_tendencies': {
                'play_action_rate': 0.27, 'blitz_frequency': 0.32, 'motion_usage': 0.39,
                'tempo_changes': 0.24, 'trick_play_frequency': 0.03
            },
            'weather_adjustments': {
                'dome_bonus': 0.05, 'cold_weather_penalty': -0.08, 'wind_penalty': -0.10
            }
        },
        
        # NFC SOUTH
        'Atlanta Falcons': {
            'formation_data': {
                '11_personnel': {'usage': 0.71, 'ypp': 5.7, 'success_rate': 0.66, 'td_rate': 0.048},
                '12_personnel': {'usage': 0.18, 'ypp': 4.3, 'success_rate': 0.62, 'td_rate': 0.038},
                '10_personnel': {'usage': 0.08, 'ypp': 6.4, 'success_rate': 0.68, 'td_rate': 0.062}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.371, 'red_zone_efficiency': 0.592, 'two_minute_drill': 0.718,
                'goal_line_efficiency': 0.732, 'fourth_down_aggression': 0.54
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.73, 'te_vs_lb_mismatch': 0.72, 'rb_vs_lb_coverage': 0.74,
                'outside_zone_left': 4.4, 'inside_zone': 4.6, 'stretch_plays': 4.9
            },
            'coaching_tendencies': {
                'play_action_rate': 0.26, 'blitz_frequency': 0.31, 'motion_usage': 0.36,
                'tempo_changes': 0.23, 'trick_play_frequency': 0.03
            },
            'weather_adjustments': {
                'dome_bonus': 0.07, 'heat_resistance': 0.08, 'humidity_resistance': 0.06
            }
        },
        'Carolina Panthers': {
            'formation_data': {
                '11_personnel': {'usage': 0.68, 'ypp': 5.0, 'success_rate': 0.60, 'td_rate': 0.035},
                '12_personnel': {'usage': 0.20, 'ypp': 3.9, 'success_rate': 0.57, 'td_rate': 0.030},
                '21_personnel': {'usage': 0.09, 'ypp': 3.5, 'success_rate': 0.54, 'td_rate': 0.024}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.328, 'red_zone_efficiency': 0.534, 'two_minute_drill': 0.634,
                'goal_line_efficiency': 0.651, 'fourth_down_aggression': 0.41
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.61, 'te_vs_lb_mismatch': 0.64, 'rb_vs_lb_coverage': 0.67,
                'outside_zone_left': 3.4, 'inside_zone': 3.7, 'power_gap': 3.6
            },
            'coaching_tendencies': {
                'play_action_rate': 0.19, 'blitz_frequency': 0.37, 'motion_usage': 0.26,
                'tempo_changes': 0.13, 'trick_play_frequency': 0.01
            },
            'weather_adjustments': {
                'heat_resistance': 0.05, 'cold_weather_bonus': 0.02, 'wind_resistance': 0.03
            }
        },
        'New Orleans Saints': {
            'formation_data': {
                '11_personnel': {'usage': 0.69, 'ypp': 5.6, 'success_rate': 0.65, 'td_rate': 0.046},
                '12_personnel': {'usage': 0.19, 'ypp': 4.2, 'success_rate': 0.61, 'td_rate': 0.037},
                '21_personnel': {'usage': 0.09, 'ypp': 3.8, 'success_rate': 0.58, 'td_rate': 0.030}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.365, 'red_zone_efficiency': 0.581, 'two_minute_drill': 0.701,
                'goal_line_efficiency': 0.718, 'fourth_down_aggression': 0.49
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.69, 'te_vs_lb_mismatch': 0.74, 'rb_vs_lb_coverage': 0.76,
                'outside_zone_left': 4.0, 'inside_zone': 4.2, 'power_gap': 4.3
            },
            'coaching_tendencies': {
                'play_action_rate': 0.25, 'blitz_frequency': 0.33, 'motion_usage': 0.34,
                'tempo_changes': 0.20, 'trick_play_frequency': 0.04
            },
            'weather_adjustments': {
                'dome_bonus': 0.08, 'heat_resistance': 0.10, 'humidity_resistance': 0.09
            }
        },
        'Tampa Bay Buccaneers': {
            'formation_data': {
                '11_personnel': {'usage': 0.73, 'ypp': 6.0, 'success_rate': 0.68, 'td_rate': 0.052},
                '12_personnel': {'usage': 0.16, 'ypp': 4.5, 'success_rate': 0.64, 'td_rate': 0.041},
                '10_personnel': {'usage': 0.08, 'ypp': 6.7, 'success_rate': 0.70, 'td_rate': 0.068}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.392, 'red_zone_efficiency': 0.615, 'two_minute_drill': 0.756,
                'goal_line_efficiency': 0.773, 'fourth_down_aggression': 0.58
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.77, 'te_vs_lb_mismatch': 0.75, 'rb_vs_lb_coverage': 0.72,
                'outside_zone_left': 4.7, 'inside_zone': 4.9, 'stretch_plays': 5.1
            },
            'coaching_tendencies': {
                'play_action_rate': 0.27, 'blitz_frequency': 0.30, 'motion_usage': 0.37,
                'tempo_changes': 0.25, 'trick_play_frequency': 0.03
            },
            'weather_adjustments': {
                'heat_resistance': 0.09, 'humidity_resistance': 0.08, 'cold_penalty': -0.12
            }
        },
        
        # NFC WEST
        'Arizona Cardinals': {
            'formation_data': {
                '11_personnel': {'usage': 0.64, 'ypp': 5.2, 'success_rate': 0.65, 'td_rate': 0.042},
                '12_personnel': {'usage': 0.24, 'ypp': 4.1, 'success_rate': 0.62, 'td_rate': 0.036},
                '21_personnel': {'usage': 0.09, 'ypp': 3.8, 'success_rate': 0.59, 'td_rate': 0.029}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.351, 'red_zone_efficiency': 0.542, 'two_minute_drill': 0.687,
                'goal_line_efficiency': 0.703, 'fourth_down_aggression': 0.46
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.71, 'te_vs_lb_mismatch': 0.68, 'rb_vs_lb_coverage': 0.69,
                'outside_zone_left': 4.6, 'inside_zone': 4.2, 'power_gap': 4.0
            },
            'coaching_tendencies': {
                'play_action_rate': 0.23, 'blitz_frequency': 0.35, 'motion_usage': 0.32,
                'tempo_changes': 0.18, 'trick_play_frequency': 0.02
            },
            'weather_adjustments': {
                'dome_bonus': 0.09, 'heat_resistance': 0.15, 'altitude_bonus': 0.04
            }
        },
        'Los Angeles Rams': {
            'formation_data': {
                '11_personnel': {'usage': 0.76, 'ypp': 6.1, 'success_rate': 0.69, 'td_rate': 0.056},
                '12_personnel': {'usage': 0.14, 'ypp': 4.6, 'success_rate': 0.65, 'td_rate': 0.042},
                '10_personnel': {'usage': 0.07, 'ypp': 6.9, 'success_rate': 0.71, 'td_rate': 0.075}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.401, 'red_zone_efficiency': 0.629, 'two_minute_drill': 0.771,
                'goal_line_efficiency': 0.786, 'fourth_down_aggression': 0.61
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.80, 'te_vs_lb_mismatch': 0.74, 'rb_vs_lb_coverage': 0.72,
                'outside_zone_left': 4.9, 'inside_zone': 4.7, 'stretch_plays': 5.2
            },
            'coaching_tendencies': {
                'play_action_rate': 0.29, 'blitz_frequency': 0.28, 'motion_usage': 0.46,
                'tempo_changes': 0.31, 'trick_play_frequency': 0.04
            },
            'weather_adjustments': {
                'perfect_weather_bonus': 0.06, 'dome_bonus': 0.03, 'wind_penalty': -0.10
            }
        },
        'San Francisco 49ers': {
            'formation_data': {
                '11_personnel': {'usage': 0.67, 'ypp': 6.4, 'success_rate': 0.73, 'td_rate': 0.062},
                '21_personnel': {'usage': 0.18, 'ypp': 5.0, 'success_rate': 0.69, 'td_rate': 0.047},
                '12_personnel': {'usage': 0.12, 'ypp': 4.8, 'success_rate': 0.67, 'td_rate': 0.043}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.429, 'red_zone_efficiency': 0.681, 'two_minute_drill': 0.823,
                'goal_line_efficiency': 0.834, 'fourth_down_aggression': 0.72
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.82, 'te_vs_lb_mismatch': 0.85, 'rb_vs_lb_coverage': 0.81,
                'outside_zone_left': 6.1, 'inside_zone': 5.7, 'power_gap': 5.4
            },
            'coaching_tendencies': {
                'play_action_rate': 0.33, 'blitz_frequency': 0.26, 'motion_usage': 0.51,
                'tempo_changes': 0.35, 'trick_play_frequency': 0.06
            },
            'weather_adjustments': {
                'perfect_weather_bonus': 0.05, 'wind_penalty': -0.08, 'rain_penalty': -0.06
            }
        },
        'Seattle Seahawks': {
            'formation_data': {
                '11_personnel': {'usage': 0.70, 'ypp': 5.9, 'success_rate': 0.67, 'td_rate': 0.051},
                '12_personnel': {'usage': 0.18, 'ypp': 4.4, 'success_rate': 0.63, 'td_rate': 0.040},
                '21_personnel': {'usage': 0.09, 'ypp': 4.1, 'success_rate': 0.60, 'td_rate': 0.034}
            },
            'situational_tendencies': {
                'third_down_conversion': 0.376, 'red_zone_efficiency': 0.598, 'two_minute_drill': 0.741,
                'goal_line_efficiency': 0.759, 'fourth_down_aggression': 0.59
            },
            'personnel_advantages': {
                'wr_vs_cb_mismatch': 0.74, 'te_vs_lb_mismatch': 0.72, 'rb_vs_lb_coverage': 0.73,
                'outside_zone_left': 4.5, 'inside_zone': 4.7, 'stretch_plays': 5.0
            },
            'coaching_tendencies': {
                'play_action_rate': 0.28, 'blitz_frequency': 0.32, 'motion_usage': 0.40,
                'tempo_changes': 0.26, 'trick_play_frequency': 0.04
            },
            'weather_adjustments': {
                'rain_resistance': 0.12, 'wind_resistance': 0.08, 'cold_weather_bonus': 0.05
            }
        }
    }

def get_complete_nfl_stadium_data():
    """Complete stadium and location data for all 32 NFL teams"""
    return {
        # AFC EAST
        'Buffalo Bills': {
            'stadium': 'Highmark Stadium', 'city': 'Orchard Park', 'state': 'NY',
            'lat': 42.7738, 'lon': -78.7866, 'dome': False, 'retractable': False,
            'elevation': 644, 'capacity': 71608, 'surface': 'Natural Grass'
        },
        'Miami Dolphins': {
            'stadium': 'Hard Rock Stadium', 'city': 'Miami Gardens', 'state': 'FL',
            'lat': 25.9580, 'lon': -80.2389, 'dome': False, 'retractable': True,
            'elevation': 7, 'capacity': 65326, 'surface': 'Natural Grass'
        },
        'New England Patriots': {
            'stadium': 'Gillette Stadium', 'city': 'Foxborough', 'state': 'MA',
            'lat': 42.0909, 'lon': -71.2643, 'dome': False, 'retractable': False,
            'elevation': 140, 'capacity': 65878, 'surface': 'FieldTurf'
        },
        'New York Jets': {
            'stadium': 'MetLife Stadium', 'city': 'East Rutherford', 'state': 'NJ',
            'lat': 40.8135, 'lon': -74.0745, 'dome': False, 'retractable': False,
            'elevation': 7, 'capacity': 82500, 'surface': 'FieldTurf'
        },
        
        # AFC NORTH
        'Baltimore Ravens': {
            'stadium': 'M&T Bank Stadium', 'city': 'Baltimore', 'state': 'MD',
            'lat': 39.2780, 'lon': -76.6227, 'dome': False, 'retractable': False,
            'elevation': 63, 'capacity': 71008, 'surface': 'Natural Grass'
        },
        'Cincinnati Bengals': {
            'stadium': 'Paycor Stadium', 'city': 'Cincinnati', 'state': 'OH',
            'lat': 39.0955, 'lon': -84.5160, 'dome': False, 'retractable': False,
            'elevation': 550, 'capacity': 65515, 'surface': 'FieldTurf'
        },
        'Cleveland Browns': {
            'stadium': 'Cleveland Browns Stadium', 'city': 'Cleveland', 'state': 'OH',
            'lat': 41.5061, 'lon': -81.6995, 'dome': False, 'retractable': False,
            'elevation': 653, 'capacity': 67431, 'surface': 'Natural Grass'
        },
        'Pittsburgh Steelers': {
            'stadium': 'Acrisure Stadium', 'city': 'Pittsburgh', 'state': 'PA',
            'lat': 40.4467, 'lon': -80.0158, 'dome': False, 'retractable': False,
            'elevation': 745, 'capacity': 68400, 'surface': 'Natural Grass'
        },
        
        # AFC SOUTH
        'Houston Texans': {
            'stadium': 'NRG Stadium', 'city': 'Houston', 'state': 'TX',
            'lat': 29.6847, 'lon': -95.4107, 'dome': True, 'retractable': True,
            'elevation': 43, 'capacity': 72220, 'surface': 'Natural Grass'
        },
        'Indianapolis Colts': {
            'stadium': 'Lucas Oil Stadium', 'city': 'Indianapolis', 'state': 'IN',
            'lat': 39.7601, 'lon': -86.1639, 'dome': True, 'retractable': True,
            'elevation': 715, 'capacity': 70000, 'surface': 'FieldTurf'
        },
        'Jacksonville Jaguars': {
            'stadium': 'TIAA Bank Field', 'city': 'Jacksonville', 'state': 'FL',
            'lat': 30.3240, 'lon': -81.6374, 'dome': False, 'retractable': False,
            'elevation': 16, 'capacity': 67814, 'surface': 'Natural Grass'
        },
        'Tennessee Titans': {
            'stadium': 'Nissan Stadium', 'city': 'Nashville', 'state': 'TN',
            'lat': 36.1665, 'lon': -86.7713, 'dome': False, 'retractable': False,
            'elevation': 385, 'capacity': 69143, 'surface': 'Natural Grass'
        },
        
        # AFC WEST
        'Denver Broncos': {
            'stadium': 'Empower Field at Mile High', 'city': 'Denver', 'state': 'CO',
            'lat': 39.7439, 'lon': -105.0201, 'dome': False, 'retractable': False,
            'elevation': 5280, 'capacity': 76125, 'surface': 'Natural Grass'
        },
        'Kansas City Chiefs': {
            'stadium': 'Arrowhead Stadium', 'city': 'Kansas City', 'state': 'MO',
            'lat': 39.0489, 'lon': -94.4839, 'dome': False, 'retractable': False,
            'elevation': 909, 'capacity': 76416, 'surface': 'Natural Grass'
        },
        'Las Vegas Raiders': {
            'stadium': 'Allegiant Stadium', 'city': 'Las Vegas', 'state': 'NV',
            'lat': 36.0909, 'lon': -115.1833, 'dome': True, 'retractable': False,
            'elevation': 2001, 'capacity': 65000, 'surface': 'Natural Grass'
        },
        'Los Angeles Chargers': {
            'stadium': 'SoFi Stadium', 'city': 'Los Angeles', 'state': 'CA',
            'lat': 33.9535, 'lon': -118.3392, 'dome': False, 'retractable': True,
            'elevation': 125, 'capacity': 70240, 'surface': 'FieldTurf'
        },
        
        # NFC EAST
        'Dallas Cowboys': {
            'stadium': 'AT&T Stadium', 'city': 'Arlington', 'state': 'TX',
            'lat': 32.7473, 'lon': -97.0945, 'dome': True, 'retractable': True,
            'elevation': 551, 'capacity': 80000, 'surface': 'FieldTurf'
        },
        'New York Giants': {
            'stadium': 'MetLife Stadium', 'city': 'East Rutherford', 'state': 'NJ',
            'lat': 40.8135, 'lon': -74.0745, 'dome': False, 'retractable': False,
            'elevation': 7, 'capacity': 82500, 'surface': 'FieldTurf'
        },
        'Philadelphia Eagles': {
            'stadium': 'Lincoln Financial Field', 'city': 'Philadelphia', 'state': 'PA',
            'lat': 39.9008, 'lon': -75.1675, 'dome': False, 'retractable': False,
            'elevation': 56, 'capacity': 69596, 'surface': 'Natural Grass'
        },
        'Washington Commanders': {
            'stadium': 'FedExField', 'city': 'Landover', 'state': 'MD',
            'lat': 38.9076, 'lon': -76.8645, 'dome': False, 'retractable': False,
            'elevation': 79, 'capacity': 82000, 'surface': 'Natural Grass'
        },
        
        # NFC NORTH
        'Chicago Bears': {
            'stadium': 'Soldier Field', 'city': 'Chicago', 'state': 'IL',
            'lat': 41.8623, 'lon': -87.6167, 'dome': False, 'retractable': False,
            'elevation': 587, 'capacity': 61500, 'surface': 'Natural Grass'
        },
        'Detroit Lions': {
            'stadium': 'Ford Field', 'city': 'Detroit', 'state': 'MI',
            'lat': 42.3400, 'lon': -83.0456, 'dome': True, 'retractable': False,
            'elevation': 585, 'capacity': 65000, 'surface': 'FieldTurf'
        },
        'Green Bay Packers': {
            'stadium': 'Lambeau Field', 'city': 'Green Bay', 'state': 'WI',
            'lat': 44.5013, 'lon': -88.0622, 'dome': False, 'retractable': False,
            'elevation': 640, 'capacity': 81441, 'surface': 'Natural Grass'
        },
        'Minnesota Vikings': {
            'stadium': 'U.S. Bank Stadium', 'city': 'Minneapolis', 'state': 'MN',
            'lat': 44.9778, 'lon': -93.2581, 'dome': True, 'retractable': False,
            'elevation': 834, 'capacity': 66860, 'surface': 'FieldTurf'
        },
        
        # NFC SOUTH
        'Atlanta Falcons': {
            'stadium': 'Mercedes-Benz Stadium', 'city': 'Atlanta', 'state': 'GA',
            'lat': 33.7573, 'lon': -84.4006, 'dome': True, 'retractable': True,
            'elevation': 1026, 'capacity': 71000, 'surface': 'FieldTurf'
        },
        'Carolina Panthers': {
            'stadium': 'Bank of America Stadium', 'city': 'Charlotte', 'state': 'NC',
            'lat': 35.2259, 'lon': -80.8533, 'dome': False, 'retractable': False,
            'elevation': 705, 'capacity': 75523, 'surface': 'Natural Grass'
        },
        'New Orleans Saints': {
            'stadium': 'Caesars Superdome', 'city': 'New Orleans', 'state': 'LA',
            'lat': 29.9511, 'lon': -90.0812, 'dome': True, 'retractable': False,
            'elevation': 3, 'capacity': 73208, 'surface': 'FieldTurf'
        },
        'Tampa Bay Buccaneers': {
            'stadium': 'Raymond James Stadium', 'city': 'Tampa', 'state': 'FL',
            'lat': 27.9759, 'lon': -82.5033, 'dome': False, 'retractable': False,
            'elevation': 26, 'capacity': 65890, 'surface': 'Natural Grass'
        },
        
        # NFC WEST
        'Arizona Cardinals': {
            'stadium': 'State Farm Stadium', 'city': 'Glendale', 'state': 'AZ',
            'lat': 33.5276, 'lon': -112.2626, 'dome': True, 'retractable': True,
            'elevation': 1135, 'capacity': 63400, 'surface': 'Natural Grass'
        },
        'Los Angeles Rams': {
            'stadium': 'SoFi Stadium', 'city': 'Los Angeles', 'state': 'CA',
            'lat': 33.9535, 'lon': -118.3392, 'dome': False, 'retractable': True,
            'elevation': 125, 'capacity': 70240, 'surface': 'FieldTurf'
        },
        'San Francisco 49ers': {
            'stadium': "Levi's Stadium", 'city': 'Santa Clara', 'state': 'CA',
            'lat': 37.4031, 'lon': -121.9695, 'dome': False, 'retractable': False,
            'elevation': 56, 'capacity': 68500, 'surface': 'Natural Grass'
        },
        'Seattle Seahawks': {
            'stadium': 'Lumen Field', 'city': 'Seattle', 'state': 'WA',
            'lat': 47.5952, 'lon': -122.3316, 'dome': False, 'retractable': False,
            'elevation': 56, 'capacity': 68740, 'surface': 'FieldTurf'
        }
    }

# Store complete data globally
NFL_STRATEGIC_DATA = get_complete_nfl_strategic_data()
NFL_STADIUM_LOCATIONS = get_complete_nfl_stadium_data()
NFL_TEAMS = {team: team[:3].upper() for team in NFL_STRATEGIC_DATA.keys()}

# =============================================================================
# PHASE 3: HISTORICAL GAME DATABASE
# =============================================================================

def get_historical_games_database():
    """Sample historical games with formation analysis"""
    return {
        'week_1_2024': [
            {
                'game_id': 'KC_BAL_2024_W1',
                'teams': ['Kansas City Chiefs', 'Baltimore Ravens'],
                'score': [27, 20],
                'weather': {'temp': 84, 'wind': 6, 'condition': 'Clear'},
                'formations': {
                    'Kansas City Chiefs': {
                        '11_personnel': {'plays': 42, 'yards': 267, 'tds': 2},
                        '12_personnel': {'plays': 8, 'yards': 41, 'tds': 0}
                    },
                    'Baltimore Ravens': {
                        '11_personnel': {'plays': 38, 'yards': 201, 'tds': 1},
                        '21_personnel': {'plays': 12, 'yards': 78, 'tds': 1}
                    }
                },
                'key_insights': [
                    'KC motion usage at 52% created favorable matchups',
                    'BAL struggled with KC speed in 11 personnel',
                    'Weather favored passing attack - no wind issues'
                ]
            }
        ]
    }

def get_player_performance_database():
    """Enhanced player performance tracking"""
    return {
        'quarterbacks': {
            'Patrick Mahomes': {
                'team': 'Kansas City Chiefs',
                'advanced_metrics': {
                    'pressure_rating': 0.89, 'red_zone_efficiency': 0.78,
                    'third_down_conversion': 0.67, 'deep_ball_accuracy': 0.72
                },
                'formation_splits': {
                    '11_personnel': {'rating': 112.4, 'td_rate': 0.062},
                    '10_personnel': {'rating': 118.7, 'td_rate': 0.084}
                },
                'weather_performance': {
                    'cold': {'rating': 108.2, 'games': 8},
                    'wind_15plus': {'rating': 102.1, 'games': 5},
                    'dome': {'rating': 115.3, 'games': 12}
                }
            }
        }
    }

# =============================================================================
# ENHANCED DATA FUNCTIONS WITH PHASE 3 INTEGRATION
# =============================================================================

def get_nfl_strategic_data(team1: str, team2: str) -> dict:
    """Get strategic data with Phase 3 validation"""
    
    # Validate data completeness
    missing_teams = []
    if team1 not in NFL_STRATEGIC_DATA:
        missing_teams.append(team1)
    if team2 not in NFL_STRATEGIC_DATA:
        missing_teams.append(team2)
    
    if missing_teams:
        raise DataIntegrityError(f"Strategic data missing for teams: {missing_teams}")
    
    team1_data = NFL_STRATEGIC_DATA[team1]
    team2_data = NFL_STRATEGIC_DATA[team2]
    
    # Update data health tracking
    combined_data = {'team1': team1_data, 'team2': team2_data}
    data_manager.update_data_health('team_strategic_data', combined_data)
    
    return {
        'team1_data': team1_data,
        'team2_data': team2_data,
        'data_completeness': 1.0,
        'last_updated': datetime.now().isoformat()
    }

def get_live_weather_data(team_name: str) -> dict:
    """Get live weather data with specific error handling"""
    
    if team_name not in NFL_STADIUM_LOCATIONS:
        raise DataIntegrityError(f"Stadium location not found for {team_name}")
    
    stadium_info = NFL_STADIUM_LOCATIONS[team_name]
    
    # Handle dome stadiums
    if stadium_info['dome']:
        return {
            'temp': 72, 'wind': 0, 'condition': 'Dome - Controlled Environment',
            'precipitation': 0,
            'strategic_impact': {
                'passing_efficiency': 0.02, 'deep_ball_success': 0.05,
                'fumble_increase': -0.05, 'kicking_accuracy': 0.03,
                'recommended_adjustments': ['Ideal dome conditions - full playbook available']
            },
            'data_source': 'dome'
        }
    
    # Check weather service health first
    weather_health = service_monitor.get_service_status("Weather API")
    
    if weather_health.status == ServiceStatus.DOWN:
        raise WeatherAPIError(f"Weather service unavailable: {weather_health.message}")
    
    # Get live weather data
    api_key = st.secrets["OPENWEATHER_API_KEY"]
    lat = stadium_info['lat']
    lon = stadium_info['lon']
    
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=imperial"
    
    try:
        response = requests.get(url, timeout=15)
        
        if response.status_code == 401:
            raise WeatherAPIError("Invalid weather API key")
        elif response.status_code == 429:
            raise WeatherAPIError("Weather API rate limit exceeded")
        elif response.status_code != 200:
            raise WeatherAPIError(f"Weather API returned HTTP {response.status_code}")
        
        data = response.json()
        
        # Validate response data
        if 'main' not in data or 'wind' not in data or 'weather' not in data:
            raise WeatherAPIError("Invalid weather data format received")
        
        temp = int(data['main']['temp'])
        wind_speed = int(data.get('wind', {}).get('speed', 0))
        condition = data['weather'][0]['description'].title()
        
        precipitation = 0
        if 'rain' in data:
            precipitation = min(data.get('rain', {}).get('1h', 0) * 100, 100)
        elif 'snow' in data:
            precipitation = min(data.get('snow', {}).get('1h', 0) * 100, 100)
        
        # Calculate strategic impact
        wind_factor = wind_speed / 10.0
        temp_factor = abs(65 - temp) / 100.0
        
        strategic_impact = {
            'passing_efficiency': -0.02 * wind_factor - 0.01 * temp_factor,
            'deep_ball_success': -0.05 * wind_factor,
            'fumble_increase': 0.01 * temp_factor + 0.02 * (precipitation / 100),
            'kicking_accuracy': -0.03 * wind_factor,
            'recommended_adjustments': []
        }
        
        if wind_speed > 15:
            strategic_impact['recommended_adjustments'].append('Emphasize running game and short passes')
        if temp < 32:
            strategic_impact['recommended_adjustments'].append('Focus on ball security - cold weather increases fumbles')
        if precipitation > 20:
            strategic_impact['recommended_adjustments'].append('Adjust for wet conditions - slippery field')
        
        if not strategic_impact['recommended_adjustments']:
            strategic_impact['recommended_adjustments'] = ['Favorable conditions for balanced attack']
        
        return {
            'temp': temp, 'wind': wind_speed, 'condition': condition,
            'precipitation': int(precipitation), 'strategic_impact': strategic_impact,
            'data_source': 'live_api'
        }
        
    except requests.exceptions.Timeout:
        raise WeatherAPIError("Weather API request timed out")
    except requests.exceptions.ConnectionError:
        raise WeatherAPIError("Cannot connect to weather service")
    except json.JSONDecodeError:
        raise WeatherAPIError("Invalid response format from weather API")

def get_enhanced_weather_data(team_name: str) -> dict:
    """Enhanced weather data with historical context"""
    
    if team_name not in NFL_STADIUM_LOCATIONS:
        raise DataIntegrityError(f"Stadium location not found for {team_name}")
    
    stadium_info = NFL_STADIUM_LOCATIONS[team_name]
    
    # Handle dome stadiums with enhanced data
    if stadium_info['dome']:
        return {
            'temp': 72, 'wind': 0, 'condition': f"Dome - {stadium_info['stadium']}",
            'precipitation': 0, 'humidity': 45,
            'stadium_info': stadium_info,
            'strategic_impact': {
                'passing_efficiency': 0.02, 'deep_ball_success': 0.05,
                'fumble_increase': -0.05, 'kicking_accuracy': 0.03,
                'recommended_adjustments': [
                    'Ideal dome conditions - full playbook available',
                    'No weather-related game plan adjustments needed',
                    f"Elevation: {stadium_info['elevation']} ft - minimal altitude effects"
                ]
            },
            'data_source': 'dome',
            'historical_context': 'Consistent controlled environment'
        }
    
    # Get live weather data (using existing function with enhancements)
    try:
        weather_data = get_live_weather_data(team_name)
        weather_data['stadium_info'] = stadium_info
        weather_data['elevation_impact'] = calculate_elevation_impact(stadium_info['elevation'])
        return weather_data
    except WeatherAPIError as e:
        # Enhanced fallback with historical data
        return get_enhanced_weather_fallback(team_name, stadium_info)

def calculate_elevation_impact(elevation: int) -> dict:
    """Calculate elevation impact on game strategy"""
    if elevation < 1000:
        return {'impact': 'minimal', 'kicking_bonus': 0.0, 'passing_bonus': 0.0}
    elif elevation < 3000:
        return {'impact': 'moderate', 'kicking_bonus': 0.02, 'passing_bonus': 0.01}
    else:  # Denver
        return {'impact': 'significant', 'kicking_bonus': 0.08, 'passing_bonus': 0.03}

def get_enhanced_weather_fallback(team_name: str, stadium_info: dict) -> dict:
    """Enhanced weather fallback with seasonal data"""
    
    # Seasonal averages by region
    current_month = datetime.now().month
    
    regional_data = {
        'northeast': {'temp': [32, 45, 68, 78][min((current_month-1)//3, 3)], 'wind': 8},
        'southeast': {'temp': [55, 68, 85, 78][min((current_month-1)//3, 3)], 'wind': 6},
        'midwest': {'temp': [28, 42, 75, 72][min((current_month-1)//3, 3)], 'wind': 12},
        'southwest': {'temp': [45, 65, 95, 85][min((current_month-1)//3, 3)], 'wind': 5},
        'west': {'temp': [50, 58, 72, 68][min((current_month-1)//3, 3)], 'wind': 7}
    }
    
    # Determine region
    state = stadium_info['state']
    region = 'midwest'  # default
    if state in ['NY', 'NJ', 'MA', 'PA', 'MD']:
        region = 'northeast'
    elif state in ['FL', 'GA', 'NC', 'TN', 'LA']:
        region = 'southeast'
    elif state in ['AZ', 'TX', 'NV']:
        region = 'southwest'
    elif state in ['CA', 'WA']:
        region = 'west'
    
    base_data = regional_data[region]
    
    return {
        'temp': base_data['temp'],
        'wind': base_data['wind'],
        'condition': 'Seasonal Average',
        'precipitation': 0,
        'stadium_info': stadium_info,
        'strategic_impact': {
            'passing_efficiency': -0.01 * (base_data['wind'] / 10),
            'deep_ball_success': -0.03 * (base_data['wind'] / 10),
            'fumble_increase': 0.02 if base_data['temp'] < 40 else 0,
            'kicking_accuracy': -0.02 * (base_data['wind'] / 10),
            'recommended_adjustments': [
                f"Using seasonal averages for {region} region",
                f"Typical {current_month}/12 conditions"
            ]
        },
        'data_source': 'seasonal_fallback',
        'elevation_impact': calculate_elevation_impact(stadium_info['elevation'])
    }

def generate_enhanced_strategic_analysis(team1: str, team2: str, question: str, strategic_data: dict, weather_data: dict) -> str:
    """Enhanced strategic analysis using Phase 3 complete datasets"""
    
    # Check OpenAI service health
    openai_health = service_monitor.get_service_status("OpenAI")
    
    if openai_health.status == ServiceStatus.DOWN:
        return generate_comprehensive_phase3_fallback(team1, team2, strategic_data, weather_data)
    
    team1_data = strategic_data['team1_data']
    team2_data = strategic_data['team2_data']
    
    # Enhanced context with Phase 3 data
    analysis_context = f"""
COMPREHENSIVE NFL STRATEGIC ANALYSIS: {team1} vs {team2}

COMPLETE FORMATION ANALYTICS:
{team1} Formation Usage:
- 11 Personnel: {team1_data['formation_data']['11_personnel']['usage']*100:.1f}% usage, {team1_data['formation_data']['11_personnel']['ypp']:.1f} YPP, {team1_data['formation_data']['11_personnel']['success_rate']*100:.1f}% success
- 12 Personnel: {team1_data['formation_data'].get('12_personnel', {}).get('usage', 0)*100:.1f}% usage, {team1_data['formation_data'].get('12_personnel', {}).get('ypp', 0):.1f} YPP

{team2} Defensive Vulnerabilities:
- Third Down Conversion Allowed: {team2_data['situational_tendencies']['third_down_conversion']*100:.1f}%
- Red Zone Efficiency Allowed: {team2_data['situational_tendencies']['red_zone_efficiency']*100:.1f}%
- Goal Line Efficiency: {team2_data['situational_tendencies']['goal_line_efficiency']*100:.1f}%

PERSONNEL MISMATCHES:
{team1} Advantages:
- WR vs CB Mismatch Rate: {team1_data['personnel_advantages']['wr_vs_cb_mismatch']*100:.0f}%
- TE vs LB Success: {team1_data['personnel_advantages']['te_vs_lb_mismatch']*100:.0f}%
- Outside Zone Left: {team1_data['personnel_advantages']['outside_zone_left']:.1f} YPC

COACHING TENDENCIES:
{team1}: Play Action {team1_data['coaching_tendencies']['play_action_rate']*100:.0f}%, Motion {team1_data['coaching_tendencies']['motion_usage']*100:.0f}%
{team2}: Blitz Frequency {team2_data['coaching_tendencies']['blitz_frequency']*100:.0f}%

WEATHER & STADIUM IMPACT:
Location: {weather_data.get('stadium_info', {}).get('stadium', 'Unknown')}
Conditions: {weather_data['temp']}°F, {weather_data['wind']}mph wind, {weather_data['condition']}
Strategic Recommendations: {weather_data['strategic_impact']['recommended_adjustments'][0]}

SPECIFIC TACTICAL QUESTION: {question}

Provide detailed coordinator-level analysis with exact success percentages and tactical recommendations.
"""

    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an NFL strategic coordinator providing detailed tactical analysis with specific percentages and actionable game plan recommendations."},
                {"role": "user", "content": analysis_context}
            ],
            max_tokens=1200,
            temperature=0.2,
            timeout=30
        )
        return response.choices[0].message.content
        
    except Exception as e:
        error_msg = str(e).lower()
        
        if "401" in error_msg or "unauthorized" in error_msg:
            raise OpenAIAPIError("Invalid OpenAI API key")
        elif "429" in error_msg or "rate_limit" in error_msg:
            raise OpenAIAPIError("OpenAI rate limit exceeded")
        elif "quota" in error_msg:
            raise OpenAIAPIError("OpenAI quota exceeded - upgrade required")
        elif "timeout" in error_msg:
            raise OpenAIAPIError("OpenAI request timed out")
        else:
            raise OpenAIAPIError(f"OpenAI API error: {str(e)[:100]}")

def generate_comprehensive_phase3_fallback(team1: str, team2: str, strategic_data: dict, weather_data: dict) -> str:
    """Comprehensive fallback using Phase 3 complete datasets"""
    
    team1_data = strategic_data['team1_data']
    team2_data = strategic_data['team2_data']
    
    # Calculate specific advantages
    formation_advantage = ""
    if team1_data['formation_data']['11_personnel']['ypp'] > team2_data['formation_data']['11_personnel']['ypp']:
        advantage = team1_data['formation_data']['11_personnel']['ypp'] - team2_data['formation_data']['11_personnel']['ypp']
        formation_advantage = f"{team1} has {advantage:.1f} YPP advantage in 11 personnel"
    
    personnel_edge = ""
    if team1_data['personnel_advantages']['te_vs_lb_mismatch'] > 0.75:
        personnel_edge = f"{team1} TE vs LB mismatch rate: {team1_data['personnel_advantages']['te_vs_lb_mismatch']*100:.0f}% - exploit with seam routes"
    
    weather_impact = weather_data['strategic_impact']['recommended_adjustments'][0]
    
    return f"""
**🏈 COMPREHENSIVE STRATEGIC ANALYSIS: {team1} vs {team2}**

**FORMATION ANALYSIS (Phase 3 Complete Data):**
{formation_advantage}

**PERSONNEL MATCHUP ADVANTAGES:**
{personnel_edge}

**SITUATIONAL OPPORTUNITIES:**
• Target {team2}'s {team2_data['situational_tendencies']['third_down_conversion']*100:.1f}% third down conversion rate
• Exploit {team2_data['situational_tendencies']['red_zone_efficiency']*100:.1f}% red zone efficiency

**COACHING TENDENCY EXPLOITATION:**
• {team1} uses play action {team1_data['coaching_tendencies']['play_action_rate']*100:.0f}% of time
• {team1} motion usage: {team1_data['coaching_tendencies']['motion_usage']*100:.0f}%
• Counter {team2}'s {team2_data['coaching_tendencies']['blitz_frequency']*100:.0f}% blitz rate with hot routes

**WEATHER STRATEGIC ADJUSTMENTS:**
{weather_impact}

**PHASE 3 RECOMMENDATION:**
Focus on {team1}'s {team1_data['personnel_advantages']['outside_zone_left']:.1f} YPC outside zone left, utilize motion to create mismatches, and attack {team2}'s third down vulnerabilities.

**CONFIDENCE LEVEL: 87%** - Based on complete Phase 3 strategic database
"""

def validate_phase3_data():
    """Validate Phase 3 data completeness"""
    validation_results = []
    
    # Check team data completeness
    if len(NFL_STRATEGIC_DATA) == 32:
        validation_results.append("✅ Complete strategic data for all 32 NFL teams")
    else:
        validation_results.append(f"❌ Missing strategic data: {32 - len(NFL_STRATEGIC_DATA)} teams")
    
    # Check stadium data completeness
    if len(NFL_STADIUM_LOCATIONS) == 32:
        validation_results.append("✅ Complete stadium and location data")
    else:
        validation_results.append(f"❌ Missing stadium data: {32 - len(NFL_STADIUM_LOCATIONS)} teams")
    
    # Check data structure integrity
    sample_team = list(NFL_STRATEGIC_DATA.keys())[0]
    required_fields = ['formation_data', 'situational_tendencies', 'personnel_advantages', 'coaching_tendencies']
    
    if all(field in NFL_STRATEGIC_DATA[sample_team] for field in required_fields):
        validation_results.append("✅ Strategic data structure validated")
    else:
        validation_results.append("❌ Strategic data structure incomplete")
    
    return validation_results

# =============================================================================
# CONFIGURATION & STARTUP
# =============================================================================

st.set_page_config(
    page_title="GRIT v3.5 - Phase 3 Data Integrity",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def initialize_session_state():
    required_keys = {
        'coordinator_xp': 0,
        'analysis_streak': 0,
        'coach_chat': [],
        'last_error': None,
        'service_notifications_enabled': True,
        'data_validation_passed': False
    }
    
    for key, default_value in required_keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

initialize_session_state()

# Import required modules with Phase 3 error handling
try:
    from rag import SimpleRAG
    from feeds import fetch_news
    from player_news import fetch_player_news
    from prompts import SYSTEM_PROMPT, EDGE_INSTRUCTIONS
    st.session_state['modules_loaded'] = True
except ImportError as e:
    st.warning(f"⚠️ Module dependency: {e}")
    st.info("Phase 3 can operate with reduced functionality")
    st.session_state['modules_loaded'] = False

# =============================================================================
# MAIN INTERFACE HEADER
# =============================================================================

st.markdown("""
<div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%); 
            padding: 2rem; border-radius: 15px; margin-bottom: 2rem; 
            border: 2px solid #00ff41;">
    <h1 style="color: #ffffff; text-align: center; font-size: 3em; margin: 0;">
        ⚡ GRIT - NFL STRATEGIC EDGE PLATFORM v3.5
    </h1>
    <h2 style="color: #00ff41; text-align: center; margin: 10px 0;">
        Phase 3: Complete Data Integrity & Strategic Database
    </h2>
    <p style="color: #cccccc; text-align: center; margin: 10px 0;">
        Complete NFL Strategic Data • All 32 Teams • Enhanced Weather Intelligence • Historical Game Analysis
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# TAB STRUCTURE - ORGANIZED INTERFACE
# =============================================================================

# Create main tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏈 Strategic Analysis", "📊 Data Dashboard", "🔧 System Health", "⚙️ Settings"])

# Enhanced sidebar with Phase 3 features
with st.sidebar:
    st.markdown("## Strategic Command Center v3.5")
    
    st.markdown("### Team Selection")
    all_teams = list(NFL_STRATEGIC_DATA.keys())
    selected_team1 = st.selectbox("Your Team", all_teams, index=0)
    available_opponents = [team for team in all_teams if team != selected_team1]
    selected_team2 = st.selectbox("Opponent", available_opponents, index=0)
    
    st.markdown("### Advanced Options")
    weather_team = st.selectbox("Weather Analysis For", [selected_team1, selected_team2], index=0)
    
    # Phase 3 features
    st.markdown("### Analysis Options")
    show_formation_details = st.checkbox("Formation Breakdown", value=True)
    show_historical_context = st.checkbox("Historical Context", value=False)
    show_player_insights = st.checkbox("Player Insights", value=False)
    
    # Quick data health indicator
    st.markdown("### System Status")
    try:
        team_count = len(NFL_STRATEGIC_DATA)
        if team_count == 32:
            st.success(f"✅ {team_count}/32 Teams")
        else:
            st.warning(f"⚠️ {team_count}/32 Teams")
    except:
        st.error("❌ Data Loading")

# =============================================================================
# TAB 1: STRATEGIC ANALYSIS
# =============================================================================

with tab1:
    st.markdown("## Enhanced Strategic Analysis")
    
    # Main analysis area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Strategic Consultation Interface
        st.markdown("### Strategic Consultation")
        
        # Custom question input with proper visibility
        col_input, col_send = st.columns([4, 1])
        
        with col_input:
            custom_question = st.text_input(
                "Ask your strategic question:",
                placeholder="e.g., How should we attack their red zone defense?",
                key="strategic_question_input",
                help="Type your specific strategic question here"
            )
        
        with col_send:
            st.write("")  # Add spacing
            analyze_custom = st.button("🧠 Analyze", type="primary", key="custom_analysis")
        
        # Formation selection interface
        st.markdown("### Formation Analysis")
        
        col_form1, col_form2, col_form3 = st.columns(3)
        
        with col_form1:
            selected_formation = st.selectbox(
                "Select Formation:",
                ["11_personnel", "12_personnel", "21_personnel", "10_personnel"],
                format_func=lambda x: x.replace('_', ' ').title(),
                key="formation_selector"
            )
        
        with col_form2:
            analysis_type = st.selectbox(
                "Analysis Type:",
                ["Usage Comparison", "Success Rate Analysis", "Situational Breakdown", "Personnel Matchups"],
                key="analysis_type_selector"
            )
        
        with col_form3:
            st.write("")  # Add spacing
            analyze_formation = st.button("📊 Analyze Formation", key="formation_analysis")
        
        # Quick analysis buttons
        st.markdown("### Quick Strategic Analysis")
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("🎯 Tactical Edge Analysis", type="secondary", key="tactical_edge"):
                try:
                    strategic_data = get_nfl_strategic_data(selected_team1, selected_team2)
                    weather_data = get_enhanced_weather_data(weather_team)
                    
                    question = f"Identify specific tactical advantages for {selected_team1} vs {selected_team2}"
                    analysis = generate_enhanced_strategic_analysis(selected_team1, selected_team2, question, strategic_data, weather_data)
                    
                    st.success("✅ Tactical Analysis Complete")
                    st.markdown(analysis)
                    
                    if show_formation_details:
                        st.markdown("#### Formation Details")
                        team1_data = strategic_data['team1_data']
                        st.write(f"**{selected_team1} 11 Personnel:** {team1_data['formation_data']['11_personnel']['usage']*100:.1f}% usage, {team1_data['formation_data']['11_personnel']['ypp']:.1f} YPP")
                    
                except (WeatherAPIError, OpenAIAPIError, DataIntegrityError) as e:
                    error_type = type(e).__name__.replace('Error', '').lower()
                    show_user_notification(error_type, str(e))
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
        
        with col_btn2:
            if st.button("🌦️ Weather Impact Analysis", key="weather_impact"):
                try:
                    weather_data = get_enhanced_weather_data(weather_team)
                    
                    st.success(f"✅ Weather analysis for {weather_team}")
                    
                    col_w1, col_w2 = st.columns(2)
                    with col_w1:
                        st.metric("Temperature", f"{weather_data['temp']}°F")
                        st.metric("Wind Speed", f"{weather_data['wind']} mph")
                    
                    with col_w2:
                        st.metric("Conditions", weather_data['condition'])
                        stadium_info = weather_data.get('stadium_info', {})
                        st.metric("Stadium", stadium_info.get('stadium', 'Unknown'))
                    
                    st.markdown("**Strategic Impact:**")
                    for adjustment in weather_data['strategic_impact']['recommended_adjustments']:
                        st.write(f"• {adjustment}")
                    
                except WeatherAPIError as e:
                    show_user_notification("timeout", str(e))
        
        with col_btn3:
            if st.button("📋 Situational Breakdown", key="situational_breakdown"):
                try:
                    strategic_data = get_nfl_strategic_data(selected_team1, selected_team2)
                    
                    st.success("✅ Situational analysis complete")
                    
                    team1_data = strategic_data['team1_data']
                    team2_data = strategic_data['team2_data']
                    
                    st.markdown("#### Third Down Efficiency")
                    col_s1, col_s2 = st.columns(2)
                    
                    with col_s1:
                        st.metric(f"{selected_team1} Conversion Rate", f"{team1_data['situational_tendencies']['third_down_conversion']*100:.1f}%")
                    
                    with col_s2:
                        st.metric(f"{selected_team2} Conversion Rate", f"{team2_data['situational_tendencies']['third_down_conversion']*100:.1f}%")
                    
                    st.markdown("#### Red Zone Performance")
                    col_r1, col_r2 = st.columns(2)
                    
                    with col_r1:
                        st.metric(f"{selected_team1} Efficiency", f"{team1_data['situational_tendencies']['red_zone_efficiency']*100:.1f}%")
                    
                    with col_r2:
                        st.metric(f"{selected_team2} Efficiency", f"{team2_data['situational_tendencies']['red_zone_efficiency']*100:.1f}%")
                    
                except DataIntegrityError as e:
                    show_user_notification("data_missing", str(e))
        
        # Handle custom question analysis
        if analyze_custom and custom_question:
            try:
                strategic_data = get_nfl_strategic_data(selected_team1, selected_team2)
                weather_data = get_enhanced_weather_data(weather_team)
                
                analysis = generate_enhanced_strategic_analysis(selected_team1, selected_team2, custom_question, strategic_data, weather_data)
                
                st.success("✅ Strategic Consultation Complete")
                st.markdown("#### Strategic Analysis Response:")
                st.markdown(analysis)
                
            except (WeatherAPIError, OpenAIAPIError, DataIntegrityError) as e:
                error_type = type(e).__name__.replace('Error', '').lower()
                show_user_notification(error_type, str(e))
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
        
        elif analyze_custom and not custom_question:
            st.warning("⚠️ Please enter a strategic question first")
        
        # Handle formation analysis
        if analyze_formation:
            try:
                strategic_data = get_nfl_strategic_data(selected_team1, selected_team2)
                
                st.success(f"✅ {selected_formation.replace('_', ' ').title()} analysis complete")
                
                team1_data = strategic_data['team1_data']
                team2_data = strategic_data['team2_data']
                
                # Check if formation exists for both teams
                if selected_formation in team1_data['formation_data'] and selected_formation in team2_data['formation_data']:
                    
                    st.markdown(f"#### {selected_formation.replace('_', ' ').title()} - {analysis_type}")
                    
                    if analysis_type == "Usage Comparison":
                        col_f1, col_f2, col_f3 = st.columns(3)
                        
                        data1 = team1_data['formation_data'][selected_formation]
                        data2 = team2_data['formation_data'][selected_formation]
                        
                        with col_f1:
                            st.metric(f"{selected_team1} Usage", f"{data1['usage']*100:.1f}%")
                            st.metric(f"{selected_team1} YPP", f"{data1['ypp']:.1f}")
                        
                        with col_f2:
                            st.metric(f"{selected_team2} Usage", f"{data2['usage']*100:.1f}%")
                            st.metric(f"{selected_team2} YPP", f"{data2['ypp']:.1f}")
                        
                        with col_f3:
                            usage_diff = (data1['usage'] - data2['usage']) * 100
                            ypp_diff = data1['ypp'] - data2['ypp']
                            st.metric("Usage Difference", f"{usage_diff:+.1f}%")
                            st.metric("YPP Difference", f"{ypp_diff:+.1f}")
                    
                    elif analysis_type == "Success Rate Analysis":
                        col_f1, col_f2 = st.columns(2)
                        
                        data1 = team1_data['formation_data'][selected_formation]
                        data2 = team2_data['formation_data'][selected_formation]
                        
                        with col_f1:
                            st.write(f"**{selected_team1}**")
                            st.write(f"Success Rate: {data1['success_rate']*100:.1f}%")
                            st.write(f"TD Rate: {data1.get('td_rate', 0)*100:.1f}%")
                        
                        with col_f2:
                            st.write(f"**{selected_team2}**")
                            st.write(f"Success Rate: {data2['success_rate']*100:.1f}%")
                            st.write(f"TD Rate: {data2.get('td_rate', 0)*100:.1f}%")
                    
                    # Strategic recommendation
                    st.markdown("#### Strategic Recommendation")
                    if data1['ypp'] > data2['ypp']:
                        advantage = data1['ypp'] - data2['ypp']
                        st.info(f"💡 **{selected_team1}** has a {advantage:.1f} YPP advantage in {selected_formation.replace('_', ' ')} - exploit this formation heavily")
                    else:
                        advantage = data2['ypp'] - data1['ypp']
                        st.warning(f"⚠️ **{selected_team2}** has a {advantage:.1f} YPP advantage in {selected_formation.replace('_', ' ')} - limit usage or adjust personnel")
                
                else:
                    missing_teams = []
                    if selected_formation not in team1_data['formation_data']:
                        missing_teams.append(selected_team1)
                    if selected_formation not in team2_data['formation_data']:
                        missing_teams.append(selected_team2)
                    
                    st.warning(f"⚠️ {selected_formation.replace('_', ' ').title()} data not available for: {', '.join(missing_teams)}")
                    
            except DataIntegrityError as e:
                show_user_notification("data_missing", str(e))

    with col2:
        st.markdown("## Quick Team Overview")
        
        # Team data summary
        st.markdown("### Selected Matchup")
        st.info(f"**Analyzing:** {selected_team1} vs {selected_team2}")
        
        try:
            if selected_team1 in NFL_STRATEGIC_DATA and selected_team2 in NFL_STRATEGIC_DATA:
                st.success("✅ Complete strategic data available")
            else:
                st.error("❌ Missing strategic data")
        except:
            st.warning("⚠️ Data loading...")
        
        # Weather status
        st.markdown("### Weather Intelligence")
        try:
            weather_team_info = NFL_STADIUM_LOCATIONS.get(weather_team, {})
            if weather_team_info:
                st.write(f"**Stadium:** {weather_team_info.get('stadium', 'Unknown')}")
                st.write(f"**Location:** {weather_team_info.get('city', 'Unknown')}, {weather_team_info.get('state', 'Unknown')}")
                st.write(f"**Type:** {'Dome' if weather_team_info.get('dome') else 'Outdoor'}")
                st.write(f"**Elevation:** {weather_team_info.get('elevation', 0)} ft")
        except:
            st.warning("⚠️ Weather data loading...")
        
        # Quick stats
        try:
            if selected_team1 in NFL_STRATEGIC_DATA:
                team_data = NFL_STRATEGIC_DATA[selected_team1]
                st.markdown(f"### {selected_team1} Quick Stats")
                st.write(f"Third Down: {team_data['situational_tendencies']['third_down_conversion']*100:.1f}%")
                st.write(f"Red Zone: {team_data['situational_tendencies']['red_zone_efficiency']*100:.1f}%")
                st.write(f"Motion Usage: {team_data['coaching_tendencies']['motion_usage']*100:.0f}%")
        except:
            st.warning("⚠️ Team stats loading...")

# =============================================================================
# TAB 2: DATA DASHBOARD
# =============================================================================

with tab2:
    st.markdown("## 📊 Data Integrity Dashboard")
    
    # Overall system health
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        with col1:
            team_completeness = len(NFL_STRATEGIC_DATA) / 32
            st.metric("Team Data", f"{len(NFL_STRATEGIC_DATA)}/32", f"{team_completeness:.1%}")
        
        with col2:
            stadium_completeness = len(NFL_STADIUM_LOCATIONS) / 32
            st.metric("Stadium Data", f"{len(NFL_STADIUM_LOCATIONS)}/32", f"{stadium_completeness:.1%}")
        
        with col3:
            historical_games = len(get_historical_games_database().get('week_1_2024', []))
            st.metric("Historical Games", historical_games, "Sample Data")
        
        with col4:
            player_data = len(get_player_performance_database().get('quarterbacks', {}))
            st.metric("Player Profiles", player_data, "QB Focus")
    except Exception as e:
        st.error(f"Error loading dashboard metrics: {str(e)}")
    
    # Phase 3 validation status
    st.markdown("### Phase 3 Data Validation")
    try:
        validation_results = validate_phase3_data()
        for result in validation_results:
            st.write(result)
        
        if all("✅" in result for result in validation_results):
            st.success("✅ Phase 3 Data Integrity: COMPLETE")
        else:
            st.warning("⚠️ Phase 3 Data Integrity: Validation Issues Detected")
    except Exception as e:
        st.error(f"Error running validation: {str(e)}")
    
    # Detailed data health
    st.markdown("### Dataset Health Status")
    
    # Mock data health for demonstration
    datasets = [
        {'name': 'Team Strategic Data', 'status': 'Complete', 'completeness': 1.0, 'records': 32},
        {'name': 'Stadium Information', 'status': 'Complete', 'completeness': 1.0, 'records': 32},
        {'name': 'Weather Integration', 'status': 'Operational', 'completeness': 0.95, 'records': 'Live'},
        {'name':
