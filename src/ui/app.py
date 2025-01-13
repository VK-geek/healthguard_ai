import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
import json

# Page config
st.set_page_config(
    page_title="Your Health Companion",
    page_icon="🫀",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 20px;
        padding: 10px 30px;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title and intro
st.title("👋 Welcome to Your Health Dashboard!")
st.markdown("""
Let's keep an eye on your health together! This dashboard helps you:
- Track your vital signs
- Get personalized health insights
- Stay on top of your daily activity
""")

# Sidebar for inputs
with st.sidebar:
    st.header("📊 Your Health Metrics")
    st.markdown("Share your current health numbers with us:")
    
    heart_rate = st.number_input(
        "Heart Rate (bpm)",
        min_value=30,
        max_value=220,
        value=75,
        help="Your heart rate in beats per minute"
    )
    
    spo2 = st.number_input(
        "Blood Oxygen (%)",
        min_value=70,
        max_value=100,
        value=98,
        help="Your blood oxygen saturation level"
    )
    
    steps = st.number_input(
        "Steps Today",
        min_value=0,
        value=5000,
        help="Number of steps you've taken today"
    )
    
    if st.button("Get Insights!", use_container_width=True):
        with st.spinner("Analyzing your health data..."):
            try:
                response = requests.post(
                    "http://localhost:7000/metrics",
                    json={
                        "heart_rate": heart_rate,
                        "spo2": spo2,
                        "steps": steps
                    }
                )
                if response.status_code == 200:
                    st.session_state.latest_insights = response.json()
                    st.success("Got your insights! Check out the main panel →")
                else:
                    st.error("Oops! Something went wrong. Please try again!")
            except Exception as e:
                st.error("Couldn't connect to the health service. Is it running?")

# Main panel
col1, col2, col3 = st.columns(3)

# Display current metrics if available
if hasattr(st.session_state, 'latest_insights'):
    insights = st.session_state.latest_insights
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(
            "Heart Rate",
            f"{heart_rate} bpm",
            delta=None,
            delta_color="normal"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(
            "Blood Oxygen",
            f"{spo2}%",
            delta=None,
            delta_color="normal"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric(
            "Steps",
            f"{steps:,}",
            delta=f"{10000 - steps:,} to goal",
            delta_color="normal"
        )
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display insights
    st.markdown("### 🧠 Your Personal Health Insights")
    st.markdown(insights['data']['insights']['analysis'])
    
    # Display relevant guidelines
    st.markdown("### 📚 Relevant Health Tips")
    for guideline in insights['data']['insights']['relevant_guidelines']:
        st.info(guideline)
    
    # Add a fun visualization
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = steps,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Daily Step Progress"},
        gauge = {
            'axis': {'range': [None, 10000]},
            'bar': {'color': "#ff4b4b"},
            'steps': [
                {'range': [0, 5000], 'color': "lightgray"},
                {'range': [5000, 7500], 'color': "gray"},
                {'range': [7500, 10000], 'color': "darkgray"}
            ],
            'threshold': {
                'line': {'color': "green", 'width': 4},
                'thickness': 0.75,
                'value': 10000
            }
        }
    ))
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("👈 Start by entering your health metrics in the sidebar!")
