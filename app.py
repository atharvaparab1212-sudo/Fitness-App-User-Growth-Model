import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Fitness App Growth Model", layout="wide")

st.title("🏃‍♂️ Fitness App User Growth & Retention Model")
st.markdown("Predict DAU by balancing exponential acquisition against churn.")

# --- Sidebar Inputs ---
st.sidebar.header("Acquisition Parameters")
initial_users = st.sidebar.number_input("Initial Daily New Users", value=100)
growth_rate = st.sidebar.slider("Daily Growth Rate of New Signups (%)", 0.0, 5.0, 0.5) / 100
projection_days = st.sidebar.slider("Projection Horizon (Days)", 30, 365, 180)

st.sidebar.header("Retention Parameters")
day_1_retention = st.sidebar.slider("Day 1 Retention (%)", 10, 90, 40) / 100
retention_decay = st.sidebar.slider("Retention Decay (Curve Sensitivity)", 0.1, 1.0, 0.4)

# --- The Logic ---
def calculate_projection(days, initial_n, g_rate, d1_ret, decay):
    active_users = np.zeros(days)
    new_subs_history = []
    
    for t in range(days):
        # 1. Calculate new subscribers for the day (Exponential Growth)
        new_subs = initial_n * ((1 + g_rate) ** t)
        new_subs_history.append(new_subs)
        
        # 2. Calculate how many users from all previous cohorts are still active
        current_active = 0
        for age in range(len(new_subs_history)):
            cohort_size = new_subs_history[-(age+1)]
            if age == 0:
                current_active += cohort_size # Day 0 users are 100% active
            else:
                # Power-law retention curve: Day1 * (age^-decay)
                retention_factor = d1_ret * (age ** -decay)
                current_active += cohort_size * retention_factor
        
        active_users[t] = current_active
        
    return active_users, new_subs_history

dau_projection, new_subs_projection = calculate_projection(
    projection_days, initial_users, growth_rate, day_1_retention, retention_decay
)

# --- Visualization ---
fig = go.Figure()
fig.add_trace(go.Scatter(y=dau_projection, name="Total Active Users (DAU)", line=dict(color='#00CC96', width=4)))
fig.add_trace(go.Scatter(y=new_subs_projection, name="Daily New Subscribers", line=dict(dash='dash', color='#636EFA')))

fig.update_layout(
    title="Projected User Growth Over Time",
    xaxis_title="Days",
    yaxis_title="Users",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# --- Retention Strategies Section ---
st.divider()
st.header("📈 Retention Improvement Strategies")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Short-Term (Day 1-7)")
    st.write("""
    *   *Personalized Onboarding:* Quiz users on fitness goals immediately.
    *   *Push Notification Priming:* Get permission to send reminders for tomorrow's workout.
    *   *The 'Quick Win':* Ensure users complete a 5-minute activity on Day 0.
    """)

with col2:
    st.subheader("Long-Term (Day 30+)")
    st.write("""
    *   *Gamification:* Streaks, badges, and community challenges.
    *   *Social Loops:* Allow users to follow friends or join "Clubs."
    *   *Dynamic Content:* Fresh workout plans to prevent "boredom churn."
    """)

# --- Summary Metrics ---
st.sidebar.divider()
st.sidebar.metric("Final DAU", f"{int(dau_projection[-1]):,}")
st.sidebar.metric("Total New Signups", f"{int(sum(new_subs_projection)):,}")
