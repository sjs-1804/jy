import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from datetime import date
import random

LEADERBOARD_FILE = "leaderboard.csv"
HABIT_TRACKER_FILE = "habit_data.csv"
HABIT_GOALS_FILE = "habit_goals.csv"

# Daily tips
TIPS = [
    "💡 Small habits create big results.",
    "🏃 A 30-minute walk can boost your mood instantly.",
    "💧 Hydrate to focus better. Drink 6–8 glasses daily.",
    "🛌 Sleep is the best recovery tool. Aim for 7–8 hours.",
    "🌿 Deep breathing reduces stress instantly.",
    "📴 Less screen time, more life time."
]

# Load CSV

def load_csv(file, cols):
    if os.path.exists(file):
        return pd.read_csv(file)
    else:
        return pd.DataFrame(columns=cols)

# Save data

def save_score(name, score):
    df = load_csv(LEADERBOARD_FILE, ["Name", "Score"])
    df = df[df["Name"] != name]
    new_row = pd.DataFrame([[name, score]], columns=["Name", "Score"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(LEADERBOARD_FILE, index=False)

def save_habit_entry(entry_dict):
    df = load_csv(HABIT_TRACKER_FILE, ["Date", "Sleep", "Food", "Screen", "Stress", "Activity", "Caffeine", "Water"])
    today = str(date.today())
    entry = pd.DataFrame([[today] + list(entry_dict.values())], columns=df.columns)
    df = df[df["Date"] != today]
    df = pd.concat([df, entry], ignore_index=True)
    df.to_csv(HABIT_TRACKER_FILE, index=False)

def save_goals(goals):
    df = pd.DataFrame([goals])
    df.to_csv(HABIT_GOALS_FILE, index=False)

# Simulation

def simulate_future(h, years):
    base_weight = 70
    base_energy = 70
    base_focus = 70
    
    weight_change = -0.4 * (h["Activity"] / 30) + 0.7 * (h["Screen"] / 5) + 1.0 * (5 - h["Food"])
    energy_change = 1.2 * (h["Sleep"] - 7) - 1.1 * (h["Stress"] - 3) - 0.4 * h["Caffeine"]
    focus_change = -0.8 * (h["Screen"] - 6) + 0.5 * (h["Sleep"] - 6) - 0.7 * (h["Stress"] - 3)

    return {
        "years": years,
        "predicted_weight": np.clip(base_weight + weight_change * years, 45, 120),
        "predicted_energy": np.clip(base_energy + energy_change * years, 0, 100),
        "predicted_focus": np.clip(base_focus + focus_change * years, 0, 100)
    }

# Recommendations

def smart_recommendations(h):
    recs = []
    if h["Water"] < 4:
        recs.append("💧 Try lemon water in the morning.")
    if h["Screen"] > 8:
        recs.append("📴 Use screen time limits or take digital breaks.")
    if h["Activity"] < 20:
        recs.append("🏃 Evening walks for 10 minutes can improve circulation.")
    return recs if recs else ["👍 Keep up the good habits!"]

# App Config
st.set_page_config("Future Me Score", layout="wide")
st.title("🧪 Future Me Score Simulator")
st.subheader("Simulate your future based on daily habits")

# Tabs
t1, t2, t3, t4, t5 = st.tabs(["Home", "Simulation", "Goals", "Trend Graphs", "Leaderboard"])

# Home
t1.image("https://images.unsplash.com/photo-1613892202132-d8175c67b11d", use_column_width=True)
t1.success(random.choice(TIPS))
t1.markdown("Visualize your future health and improve with simple daily habits.")

# Simulation
t2.markdown("### Enter Habits")
with t2.form("habit_form"):
    name = st.text_input("Name")
    sleep = st.slider("Sleep (hrs)", 0.0, 12.0, 7.0, 0.5)
    food = st.slider("Food Quality (1–5)", 1, 5, 3)
    screen = st.slider("Screen Time (hrs)", 0.0, 12.0, 6.0, 0.5)
    stress = st.slider("Stress Level (1–5)", 1, 5, 3)
    activity = st.slider("Activity (mins)", 0, 120, 30, 5)
    caffeine = st.slider("Caffeine (cups)", 0, 5, 2)
    water = st.slider("Water (glasses)", 0, 12, 6)
    submit = st.form_submit_button("Simulate")

    if submit and name:
        habits = {"Sleep": sleep, "Food": food, "Screen": screen, "Stress": stress, "Activity": activity, "Caffeine": caffeine, "Water": water}
        save_habit_entry(habits)
        result = [simulate_future(habits, y) for y in [3, 5, 10]]
        df = pd.DataFrame(result)
        t2.dataframe(df)
        score = round((df.loc[1, "predicted_focus"] + df.loc[1, "predicted_energy"]) / 2, 2)
        t2.success(f"Your Future Me Score (5 yrs): {score}")
        save_score(name, score)
        t2.markdown("### Smart Suggestions")
        for r in smart_recommendations(habits):
            t2.markdown(f"- {r}")

# Goals
t3.markdown("### Set Your Daily Habit Goals")
with t3.form("goals"):
    g_sleep = st.slider("Goal Sleep (hrs)", 0.0, 12.0, 7.0, 0.5)
    g_water = st.slider("Goal Water Intake (glasses)", 0, 12, 8)
    g_activity = st.slider("Goal Activity (mins)", 0, 120, 45)
    g_submit = st.form_submit_button("Save Goals")
    if g_submit:
        save_goals({"Sleep": g_sleep, "Water": g_water, "Activity": g_activity})
        t3.success("Goals saved successfully!")

t3.markdown("### Current Goals")
goals_df = load_csv(HABIT_GOALS_FILE, ["Sleep", "Water", "Activity"])
if not goals_df.empty:
    t3.dataframe(goals_df)

# Trend Graphs
t4.markdown("### Habit Trends")
data = load_csv(HABIT_TRACKER_FILE, ["Date", "Sleep", "Food", "Screen", "Stress", "Activity", "Caffeine", "Water"])
if not data.empty:
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.sort_values("Date")
    fig, ax = plt.subplots(3, 1, figsize=(10, 6))
    ax[0].plot(data["Date"], data["Sleep"], label="Sleep", marker="o")
    ax[1].plot(data["Date"], data["Screen"], label="Screen Time", marker="o", color="orange")
    ax[2].plot(data["Date"], data["Water"], label="Water Intake", marker="o", color="green")
    for i in ax:
        i.legend()
        i.set_ylabel("Hours / Glasses")
    plt.tight_layout()
    t4.pyplot(fig)
else:
    t4.info("No habit data yet.")

# Leaderboard
t5.markdown("### Leaderboard")
lead = load_csv(LEADERBOARD_FILE, ["Name", "Score"])
if not lead.empty:
    lead = lead.sort_values("Score", ascending=False).reset_index(drop=True)
    t5.dataframe(lead)
else:
    t5.info("No scores yet.")
