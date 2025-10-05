import streamlit as st
from datetime import date
import pandas as pd
from utils.api_calls import fetch_nasa_power, get_coordinates
from utils.weather_processing import classify_conditions, risk_score
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json

# -------------------- ENHANCED CUSTOM CSS STYLING --------------------
st.markdown("""
<style>
    /* Main background styling with animation */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Header styling with glow effect - SINGLE LINE */
    .main-header {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, #FFD700, #FFA500, #FF8C00, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
        animation: glow 2s ease-in-out infinite alternate;
        white-space: nowrap;
        overflow: hidden;
        line-height: 1.2;
    }
    
    @keyframes glow {
        from { text-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
        to { text-shadow: 0 0 30px rgba(255, 215, 0, 0.8), 0 0 40px rgba(255, 215, 0, 0.6); }
    }
    
    /* Enhanced card styling with blur effect */
    .card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-10px);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
    }
    
    /* Enhanced metric cards - SIGNIFICANTLY INCREASED SIZE */
    .metric-card {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.4);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        height: 280px;  /* Increased from 220px */
        min-width: 250px;  /* Added minimum width */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        overflow: hidden;
        margin: 0.5rem;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        background: rgba(255, 255, 255, 0.25);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    /* Weather condition cards - SIGNIFICANTLY INCREASED SIZE */
    .condition-card {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.4);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        height: 280px;  /* Increased from 240px */
        min-width: 250px;  /* Added minimum width */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        overflow: hidden;
        margin: 0.5rem;
    }
    
    .condition-card:hover {
        transform: translateY(-8px) scale(1.02);
        background: rgba(255, 255, 255, 0.25);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    /* Floating animation for main elements */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .floating {
        animation: float 6s ease-in-out infinite;
    }
    
    /* Sidebar enhancements */
    .css-1d391kg, .css-12oz5g7 {
        background: rgba(20, 20, 40, 0.95) !important;
        backdrop-filter: blur(20px);
    }
    
    /* Enhanced button styling */
    .stButton>button {
        background: linear-gradient(90deg, #FF6B6B, #FF8E53, #FF6B6B);
        background-size: 200% 200%;
        color: white;
        border: none;
        border-radius: 30px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.5s ease;
        width: 100%;
        animation: buttonShine 3s ease-in-out infinite;
    }
    
    @keyframes buttonShine {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 25px rgba(255, 107, 107, 0.6);
    }
    
    /* Risk indicator enhancements - INCREASED SIZE */
    .low-risk {
        background: linear-gradient(135deg, #56ab2f, #a8e063);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        color: black;
        font-weight: bold;
        font-size: 1.3rem;
        box-shadow: 0 15px 30px rgba(86, 171, 47, 0.4);
        animation: pulse 2s infinite;
        height: 280px;  /* Increased from 220px */
        min-width: 250px;  /* Added minimum width */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        overflow: hidden;
        margin: 0.5rem;
    }
    
    .moderate-risk {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        color: black;
        font-weight: bold;
        font-size: 1.3rem;
        box-shadow: 0 15px 30px rgba(247, 151, 30, 0.4);
        animation: pulse 2s infinite;
        height: 280px;  /* Increased from 220px */
        min-width: 250px;  /* Added minimum width */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        overflow: hidden;
        margin: 0.5rem;
    }
    
    .high-risk {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        color: black;
        font-weight: bold;
        font-size: 1.3rem;
        box-shadow: 0 15px 30px rgba(255, 65, 108, 0.4);
        animation: pulse 1s infinite;
        height: 280px;  /* Increased from 220px */
        min-width: 250px;  /* Added minimum width */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        overflow: hidden;
        margin: 0.5rem;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    /* Custom progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 10px;
    }
    
    /* Weather icon animations - LARGER ICONS */
    .weather-icon {
        font-size: 3.5rem;  /* Increased from 2.5rem */
        animation: bounce 2s infinite;
        margin-bottom: 1rem;
    }
    
    .condition-icon {
        font-size: 3rem;  /* Increased from 2.2rem */
        animation: bounce 2s infinite;
        margin-bottom: 1rem;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* Card content styling */
    .card-content {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100%;
        width: 100%;
        position: relative;
        z-index: 2;
    }
    
    .metric-value {
        font-size: 2.2rem;  /* Increased from 1.8rem */
        font-weight: bold;
        margin: 0.5rem 0;
        color: black;
        text-shadow: 0 2px 4px rgba(255,255,255,0.3);
    }
    
    .metric-label {
        font-size: 1.2rem;  /* Increased from 1rem */
        margin: 0.3rem 0;
        color: black;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        line-height: 1.3;
        word-wrap: break-word;
        max-width: 100%;
    }
    
    .metric-unit {
        font-size: 1rem;  /* Increased from 0.9rem */
        color: black;
        margin-top: 0.5rem;
        font-weight: 600;
        line-height: 1.3;
    }
    
    .condition-value {
        font-size: 1.4rem;  /* Increased from 1.2rem */
        font-weight: bold;
        margin: 0.5rem 0;
        color: black;
        text-shadow: 0 2px 4px rgba(255,255,255,0.3);
        line-height: 1.3;
    }
    
    .condition-label {
        font-size: 1.1rem;  /* Increased from 0.9rem */
        margin: 0.3rem 0;
        color: black;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        line-height: 1.3;
        word-wrap: break-word;
        max-width: 100%;
    }
    
    /* Ensure all content stays inside cards */
    .stMarkdown, .stPlotlyChart, .stColumn {
        position: relative;
        z-index: 1;
    }
    
    /* Fix for plotly charts */
    .js-plotly-plot .plotly {
        border-radius: 15px;
        overflow: hidden;
    }
    
    /* Fix for metric card text alignment */
    .metric-card .card-content {
        padding: 0;
        margin: 0;
    }
    
    .metric-card .weather-icon {
        margin-bottom: 1.2rem;
    }
    
    .metric-card .metric-label {
        margin-bottom: 0.8rem;
    }
    
    .metric-card .metric-value {
        margin: 0.5rem 0;
    }
    
    .metric-card .metric-unit {
        margin-top: 0.6rem;
    }
    
    /* Ensure symbols stay within cards */
    .symbol-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        height: 90px;  /* Increased from 70px */
        margin-bottom: 1rem;
    }
    
    /* Fix for overflowing content */
    .stColumn, .element-container {
        overflow: visible !important;
    }
    
    /* Force all content to stay within card boundaries */
    .metric-card * {
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        word-wrap: break-word;
    }
    
    /* Fix column spacing - MORE SPACE */
    .stColumn {
        padding: 1rem;
    }
    
    /* Column container adjustments */
    .row-widget.stColumns {
        gap: 1rem;
    }
    
    /* Global black text for all content */
    .stMarkdown, .stText, .stMetric, .stInfo, .stSuccess, .stWarning, .stError {
        color: black !important;
    }
    
    /* Chart text colors */
    .js-plotly-plot .plotly .infolayer .legend text,
    .js-plotly-plot .plotly .xtitle,
    .js-plotly-plot .plotly .ytitle {
        fill: black !important;
        color: black !important;
    }
    
    /* Sidebar text color */
    .css-1d391kg, .css-12oz5g7 {
        color: black !important;
    }
    
    /* Input fields text color */
    .stTextInput input, .stNumberInput input, .stDateInput input {
        color: black !important;
    }
    
    /* Radio button text color */
    .stRadio label {
        color: black !important;
    }
    
    /* Button text remains white for contrast */
    .stButton>button {
        color: white !important;
    }
    
    /* Ensure full text display */
    .text-full {
        white-space: normal !important;
        word-break: break-word !important;
        overflow-wrap: break-word !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- DYNAMIC BACKGROUND FUNCTION --------------------
def get_dynamic_background(weather_condition):
    """Get background based on weather condition"""
    backgrounds = {
        "sunny": "https://assets.mixkit.co/videos/preview/mixkit-sun-over-hills-118836-large.mp4",
        "rainy": "https://assets.mixkit.co/videos/preview/mixkit-rain-falling-on-the-window-1187-large.mp4",
        "cloudy": "https://assets.mixkit.co/videos/preview/mixkit-white-clouds-in-the-sky-2409-large.mp4",
        "stormy": "https://assets.mixkit.co/videos/preview/mixkit-lightning-storm-in-the-evening-1185-large.mp4",
        "snowy": "https://assets.mixkit.co/videos/preview/mixkit-snow-falling-in-the-forest-1186-large.mp4",
        "default": "https://assets.mixkit.co/videos/preview/mixkit-aerial-view-of-a-fog-over-a-forest-1188-large.mp4"
    }
    
    condition = weather_condition.lower()
    if "rain" in condition or "wet" in condition:
        return backgrounds["rainy"]
    elif "hot" in condition or "sun" in condition:
        return backgrounds["sunny"]
    elif "cloud" in condition:
        return backgrounds["cloudy"]
    elif "storm" in condition or "wind" in condition:
        return backgrounds["stormy"]
    elif "cold" in condition or "snow" in condition:
        return backgrounds["snowy"]
    else:
        return backgrounds["default"]

# -------------------- WEATHER ICONS MAPPING --------------------
def get_weather_icons():
    """Fixed weather icons mapping to handle all possible conditions"""
    return {
        "temp": {
            "Very Hot": "🔥", 
            "Hot": "☀️", 
            "Moderate": "😊", 
            "Comfortable": "🌡️",
            "Cold": "❄️", 
            "Very Cold": "🥶"
        },
        "rain": {
            "Very Wet": "🌧️", 
            "Wet": "🌦️", 
            "Moderate": "☁️", 
            "Dry": "🌤️", 
            "Very Dry": "🏜️"
        },
        "wind": {
            "Very Windy": "💨", 
            "Windy": "💨", 
            "Moderate": "🍃", 
            "Calm": "🌫️", 
            "Very Calm": "🌫️"
        },
        "humidity": {
            "Very Humid": "💦", 
            "Humid": "💧", 
            "Moderate": "😊", 
            "Dry": "🏜️", 
            "Very Dry": "🔥"
        }
    }

# -------------------- STREAMLIT SETUP --------------------
st.markdown('<h1 class="main-header floating">🌦️ Will It Rain On My Parade?</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; color: black; margin-bottom: 2rem; font-weight: bold;">Advanced Weather Intelligence Platform</h3>', unsafe_allow_html=True)

st.markdown("""
<div class="card">
    <div style="text-align: center; color: black;">
        <div class="symbol-container">
            <div class="weather-icon">🌤️</div>
        </div>
        <h3 style="color: black;">Real-time Weather Intelligence</h3>
        <p style="color: black;">Powered by <b>StellarLogic</b> • NASA Space Apps Challenge 2025</p>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------- ENHANCED SIDEBAR INPUTS --------------------

from datetime import date
import streamlit as st

# ---- Optional CSS for white text & dark theme ----
st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background-color: #111827 !important; /* dark sidebar */
    }
    section[data-testid="stSidebar"] input {
        color: white !important;
        background-color: #1f2937 !important;
    }
    section[data-testid="stSidebar"] input::placeholder {
        color: #bfbfbf !important;
    }
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] h2 {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- ENHANCED SIDEBAR INPUTS --------------------
with st.sidebar:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: white;">🎯 Location & Date</h2>', unsafe_allow_html=True)
    
    # Only Latitude and Longitude inputs
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("🌐 Latitude", value=24.8607, format="%.4f")
    with col2:
        lon = st.number_input("🌐 Longitude", value=67.0011, format="%.4f")
    
    # Enhanced date input
    st.markdown("---")
    selected_date = st.date_input("📅 Select Date", value=date(2024, 9, 10))
    
    # Date validation
    if selected_date > date.today():
        st.error("🚫 Only past or present dates available.")
        st.stop()
    
    # Enhanced fetch button
    fetch_data = st.button("🚀 Get Weather Analysis", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# -------------------- MAIN APP LOGIC --------------------
if fetch_data or 'weather_data' in st.session_state:
    if fetch_data:
        with st.spinner("🌤️ Fetching real-time weather data..."):
            weather_data = fetch_nasa_power(lat, lon, selected_date)
            if weather_data is None:
                st.error("❌ Failed to fetch weather data. Try again or pick a different date/location.")
                st.stop()
            st.session_state.weather_data = weather_data
    else:
        weather_data = st.session_state.weather_data
    
    # Get conditions for dynamic background
    conditions = classify_conditions(
        weather_data["temp"], 
        weather_data["rain"], 
        weather_data["wind"], 
        weather_data["humidity"]
    )
    
    # Set dynamic background based on weather
    background_video = get_dynamic_background(conditions["temp"] + " " + conditions["rain"])
    st.markdown(f"""
    <style>
    .stApp video {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        z-index: -1;
        opacity: 0.4;
    }}
    </style>
    <video autoplay muted loop>
        <source src="{background_video}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)
    
    # -------------------- FIXED WEATHER METRICS WITH LARGER CARDS --------------------
    st.markdown("## 📊 Live Weather Dashboard")
    
    # Create animated metric cards with proper content alignment - USING 2x2 GRID FOR LARGER CARDS
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-content">
                <div class="symbol-container">
                    <div class="weather-icon">🌡️</div>
                </div>
                <div class="metric-label text-full">TEMPERATURE</div>
                <div class="metric-value">{round(weather_data['temp'], 1)}°C</div>
                <div class="metric-unit text-full">Current temperature</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-content">
                <div class="symbol-container">
                    <div class="weather-icon">💧</div>
                </div>
                <div class="metric-label text-full">PRECIPITATION</div>
                <div class="metric-value">{round(weather_data['rain'], 1)} mm</div>
                <div class="metric-unit text-full">Rainfall amount</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-content">
                <div class="symbol-container">
                    <div class="weather-icon">💨</div>
                </div>
                <div class="metric-label text-full">WIND SPEED</div>
                <div class="metric-value">{round(weather_data['wind'], 1)} km/h</div>
                <div class="metric-unit text-full">Wind intensity</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-content">
                <div class="symbol-container">
                    <div class="weather-icon">💦</div>
                </div>
                <div class="metric-label text-full">HUMIDITY</div>
                <div class="metric-value">{round(weather_data['humidity'], 1)}%</div>
                <div class="metric-unit text-full">Moisture level</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # -------------------- ENHANCED BAR CHART VISUALIZATION --------------------
    st.markdown("## 📈 Weather Analytics")
    
    # Create bar charts for better data visualization
    metrics_data = {
        'Parameter': ['Temperature', 'Precipitation', 'Wind Speed', 'Humidity'],
        'Value': [
            weather_data["temp"], 
            weather_data["rain"], 
            weather_data["wind"], 
            weather_data["humidity"]
        ],
        'Units': ['°C', 'mm', 'km/h', '%'],
        'Color': ['#FF6B6B', '#4facfe', '#a8e063', '#00f2fe']
    }
    
    df_metrics = pd.DataFrame(metrics_data)
    
    # Bar chart for main metrics
    fig_bar = px.bar(
        df_metrics, 
        x='Parameter', 
        y='Value',
        text='Value',
        color='Parameter',
        color_discrete_sequence=df_metrics['Color'],
        title="<b>Weather Parameters Comparison</b>"
    )
    
    fig_bar.update_traces(
        texttemplate='%{y:.1f}',
        textposition='outside',
        marker_line_color='white',
        marker_line_width=2,
        opacity=0.8
    )
    
    fig_bar.update_layout(
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='black', size=12),
        title_font=dict(size=20, color='black'),
        xaxis=dict(
            title_font=dict(size=14, color='black'),
            tickfont=dict(color='black'),
            title_text=""
        ),
        yaxis=dict(
            title_font=dict(size=14, color='black'),
            tickfont=dict(color='black'),
            title_text="Value"
        )
    )
    
    # Container for the chart to ensure it stays in place
    with st.container():
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # -------------------- WEATHER CLASSIFICATION --------------------
    st.markdown("## 🌦️ Weather Conditions Analysis")
    
    score = risk_score(
        weather_data["temp"], 
        weather_data["rain"], 
        weather_data["wind"], 
        weather_data["humidity"]
    )
    
    # Display enhanced condition cards with FIXED icon mapping
    condition_icons = get_weather_icons()
    
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    # Safe icon retrieval with fallback
    def get_safe_icon(condition_type, condition_value):
        icons = condition_icons.get(condition_type, {})
        return icons.get(condition_value, "🌤️")  # Fallback icon
    
    with col1:
        icon = get_safe_icon("temp", conditions["temp"])
        st.markdown(f"""
        <div class="condition-card">
            <div class="card-content">
                <div class="symbol-container">
                    <div class="condition-icon">{icon}</div>
                </div>
                <div class="condition-label text-full">TEMPERATURE</div>
                <div class="condition-value text-full">{conditions['temp']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        icon = get_safe_icon("rain", conditions["rain"])
        st.markdown(f"""
        <div class="condition-card">
            <div class="card-content">
                <div class="symbol-container">
                    <div class="condition-icon">{icon}</div>
                </div>
                <div class="condition-label text-full">PRECIPITATION</div>
                <div class="condition-value text-full">{conditions['rain']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        icon = get_safe_icon("wind", conditions["wind"])
        st.markdown(f"""
        <div class="condition-card">
            <div class="card-content">
                <div class="symbol-container">
                    <div class="condition-icon">{icon}</div>
                </div>
                <div class="condition-label text-full">WIND</div>
                <div class="condition-value text-full">{conditions['wind']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        icon = get_safe_icon("humidity", conditions["humidity"])
        st.markdown(f"""
        <div class="condition-card">
            <div class="card-content">
                <div class="symbol-container">
                    <div class="condition-icon">{icon}</div>
                </div>
                <div class="condition-label text-full">HUMIDITY</div>
                <div class="condition-value text-full">{conditions['humidity']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # -------------------- ENHANCED RISK ANALYSIS --------------------
    st.markdown("## ⚖️ Event Risk Assessment")
    
    risk_col1, risk_col2 = st.columns([1, 2])
    
    with risk_col1:
        if score <= 1:
            st.markdown("""
            <div class="low-risk">
                <div class="symbol-container">
                    <div style="font-size: 3rem;">✅</div>
                </div>
                <div>LOW RISK</div>
                <div style="font-size: 1rem; margin-top: 0.8rem;">Perfect for your event!</div>
            </div>
            """, unsafe_allow_html=True)
        elif score == 2:
            st.markdown("""
            <div class="moderate-risk">
                <div class="symbol-container">
                    <div style="font-size: 3rem;">⚠️</div>
                </div>
                <div>MODERATE RISK</div>
                <div style="font-size: 1rem; margin-top: 0.8rem;">Have a backup plan</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="high-risk">
                <div class="symbol-container">
                    <div style="font-size: 3rem;">🚨</div>
                </div>
                <div>HIGH RISK</div>
                <div style="font-size: 1rem; margin-top: 0.8rem;">Consider rescheduling</div>
            </div>
            """, unsafe_allow_html=True)
    
    with risk_col2:
        st.markdown(f"**Overall Risk Score: {score}/3**")
        st.progress(score/3)
        
        # Enhanced risk messages
        risk_messages = {
            1: "🎉 Excellent conditions! Perfect for outdoor events and activities.",
            2: "📝 Good conditions with minor concerns. Keep an eye on updates.",
            3: "⚠️ Challenging conditions. Consider indoor alternatives or reschedule."
        }
        
        st.info(risk_messages.get(score, "Check specific conditions for details."))
    
    # -------------------- SMART RECOMMENDATIONS --------------------
    st.markdown("## 💡 Weather Recommendations")
    
    recommendations = []
    if conditions["temp"] in ["Very Hot", "Hot"]:
        recommendations.append("• 🧴 Stay hydrated and use sunscreen")
        recommendations.append("• ⛱️ Seek shade during peak hours (12PM-4PM)")
        recommendations.append("• 👕 Wear light-colored, breathable clothing")
    
    if conditions["temp"] in ["Cold", "Very Cold"]:
        recommendations.append("• 🧥 Dress in layers with thermal protection")
        recommendations.append("• 🔥 Have warm beverages available")
        recommendations.append("• 🧤 Protect extremities with gloves and hat")
    
    if conditions["rain"] in ["Wet", "Very Wet"]:
        recommendations.append("• 🌂 Bring waterproof gear and umbrellas")
        recommendations.append("• 🏠 Have indoor backup venue ready")
        recommendations.append("• 📱 Monitor real-time radar updates")
    
    if conditions["wind"] in ["Windy", "Very Windy"]:
        recommendations.append("• 📌 Secure loose items and decorations")
        recommendations.append("• 🎯 Avoid temporary structures")
        recommendations.append("• 👓 Protect eyes from debris")
    
    if conditions["humidity"] in ["Humid", "Very Humid"]:
        recommendations.append("• 🌀 Use fans or air circulation")
        recommendations.append("• 🧴 Bring extra water and towels")
        recommendations.append("• ⏱️ Schedule breaks in cool areas")
    
    if not recommendations:
        recommendations.append("• 🌟 Perfect weather! No special precautions needed")
        recommendations.append("• 📸 Great day for photography")
        recommendations.append("• 🎉 Ideal for all outdoor activities")
    
    # Display recommendations in a beautiful grid
    cols = st.columns(2)
    for i, rec in enumerate(recommendations):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 15px; margin: 0.8rem 0; border-left: 4px solid #4facfe; color: black; font-size: 1.1rem;">
                {rec}
            </div>
            """, unsafe_allow_html=True)

# -------------------- INITIAL STATE WITH WOW FACTOR --------------------
else:
    st.markdown("""
    <div class="card" style="text-align: center; padding: 4rem; color: black;">
        <div class="symbol-container">
            <div class="weather-icon" style="font-size: 6rem;">🌤️</div>
        </div>
        <h2 style="color: black;">🚀 Ready for Weather Intelligence?</h2>
        <p style="font-size: 1.2rem; color: black;">Enter your location and date to get AI-powered weather insights for perfect event planning!</p>
        <br>
        <div style="display: flex; justify-content: center; gap: 1rem;">
            <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px;">
                <div class="symbol-container">
                    <div style="font-size: 2rem;">🌡️</div>
                </div>
                <small style="color: black;">Temperature Analysis</small>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px;">
                <div class="symbol-container">
                    <div style="font-size: 2rem;">💧</div>
                </div>
                <small style="color: black;">Rain Prediction</small>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 1rem; border-radius: 10px;">
                <div class="symbol-container">
                    <div style="font-size: 2rem;">💨</div>
                </div>
                <small style="color: black;">Wind Assessment</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------- ENHANCED FOOTER --------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: black; padding: 2rem;">
    <div style="display: flex; justify-content: center; gap: 2rem; margin-bottom: 1rem;">
        <div>🌐 <b>Real-time Data</b></div>
        <div>⚡ <b>AI Powered</b></div>
        <div>🎯 <b>Smart Analysis</b></div>
    </div>
    <div>Developed with ❤️ by <b>StellarLogic</b> for NASA Space Apps Challenge 2025</div>
</div>
""", unsafe_allow_html=True)