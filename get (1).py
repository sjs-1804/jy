import streamlit as st
import pandas as pd
import numpy as np
import os
import random
from datetime import date
from PIL import Image

LEADERBOARD_FILE = "leaderboard.csv"
HABIT_TRACKER_FILE = "habit_data.csv"

# ---------------- TIPS / QUOTES ------------------
tips = [
    "💡 Small habits create big results.",
    "🏃 A 30-minute walk can boost your mood instantly.",
    "💧 Hydrate to focus better. Drink 6–8 glasses daily.",
    "🛌 Sleep is the best recovery tool. Aim for 7–8 hours.",
    "🥗 A colorful plate is a healthy plate.",
    "🌿 Deep breathing reduces stress instantly.",
    "📴 Less screen time, more life time."
]

# ---------------- SIMULATION ENGINE ----------------
def simulate_future(habits, years):
    base_weight = 70
    base_energy = 70
    base_focus = 70

    weight_change = (
        -0.4 * (habits["activity_minutes"] / 30) +
        0.7 * (habits["screen_time"] / 5) +
        1.0 * (5 - habits["food_quality"])
    )

    energy_change = (
        1.2 * (habits["sleep_hours"] - 7) +
        -1.1 * (habits["stress_level"] - 3) +
        -0.4 * habits["caffeine_intake"]
    )

    focus_change = (
        -0.8 * (habits["screen_time"] - 6) +
        0.5 * (habits["sleep_hours"] - 6) +
        -0.7 * (habits["stress_level"] - 3)
    )

    weight_future = np.clip(base_weight + weight_change * years, 45, 120)
    energy_future = np.clip(base_energy + energy_change * years, 0, 100)
    focus_future = np.clip(base_focus + focus_change * years, 0, 100)

    return {
        "years": years,
        "predicted_weight": round(weight_future, 1),
        "predicted_energy": round(energy_future, 1),
        "predicted_focus": round(focus_future, 1)
    }

# ---------------- SUGGESTIONS ----------------
def generate_suggestions(habits):
    suggestions = []
    images = []

    if habits["sleep_hours"] < 6:
        suggestions.append("🛌 You should sleep 6–8 hours per day.")
        images.append("images/low_sleep.jpg")
    if habits["food_quality"] <= 2:
        suggestions.append("🥦 Improve your food with more vegetables and fruits.")
    if habits["screen_time"] > 6:
        suggestions.append("📱 Try to reduce screen time below 6 hours.")
    if habits["stress_level"] >= 4:
        suggestions.append("😟 High stress detected. Try meditation or exercise.")
    if habits["activity_minutes"] < 30:
        suggestions.append("🏃 Increase activity to at least 30 minutes daily.")
        images.append("images/low_activity.jpg")
    if habits["caffeine_intake"] > 2:
        suggestions.append("☕ Try reducing caffeine to 1–2 cups a day.")
    if habits["water_glasses"] < 6:
        suggestions.append("💧 Drink at least 6–8 glasses of water daily.")

    if not suggestions:
        suggestions.append("✅ Excellent habits! Keep it up.")
    return suggestions, images

# ---------------- FILE UTILITIES ----------------
def load_csv(file_path, columns):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=columns)

def save_score(name, score):
    df = load_csv(LEADERBOARD_FILE, ["Name", "Score"])
    new_row = pd.DataFrame([[name, score]], columns=["Name", "Score"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(LEADERBOARD_FILE, index=False)

def save_habit_entry(entry_dict):
    df = load_csv(HABIT_TRACKER_FILE, ["Date", "Sleep", "Food", "Screen", "Stress", "Activity", "Caffeine", "Water"])
    today = str(date.today())
    entry = pd.DataFrame([[today] + list(entry_dict.values())], columns=df.columns)
    df = df[df["Date"] != today]  # overwrite today's entry if exists
    df = pd.concat([df, entry], ignore_index=True)
    df.to_csv(HABIT_TRACKER_FILE, index=False)

# ---------------- APP CONFIG ----------------
st.set_page_config(page_title="Future Me Score", layout="wide")
st.title("🧬 Future Me Score Simulator")
st.subheader("Simulate your future health based on daily habits")

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "📊 Simulation", "📅 Habit Tracker", "🏆 Leaderboard"])

# ---------------- HOME ----------------
with tab1:
    st.image("https://images.unsplash.com/photo-1613892202132-d8175c67b11d", use_column_width=True)
    st.markdown("Welcome to your **habit-powered future simulator**. Predict your health and track your habits over time.")
    st.info(random.choice(tips))  # daily tip

# ---------------- SIMULATION ----------------
with tab2:
    with st.form("habit_form"):
        st.markdown("### ✍️ Enter Your Habits")
        name = st.text_input("Your Name")
        sleep = st.slider("Sleep (hrs/day)", 0.0, 12.0, 7.0, 0.5)
        food = st.slider("Food Quality (1–5)", 1, 5, 3)
        screen = st.slider("Screen Time (hrs/day)", 0.0, 12.0, 5.0, 0.5)
        stress = st.slider("Stress Level (1–5)", 1, 5, 3)
        activity = st.slider("Physical Activity (mins/day)", 0, 120, 30, 5)
        caffeine = st.slider("Caffeine Intake (cups)", 0, 6, 2)
        water = st.slider("Water Intake (glasses/day)", 0, 12, 6)
        submitted = st.form_submit_button("Simulate")

    if submitted and name.strip():
        habits = {
            "sleep_hours": sleep,
            "food_quality": food,
            "screen_time": screen,
            "stress_level": stress,
            "activity_minutes": activity,
            "caffeine_intake": caffeine,
            "water_glasses": water
        }
        save_habit_entry(habits)

        projections = [simulate_future(habits, y) for y in [3, 5, 10]]
        df = pd.DataFrame(projections)
        st.write("### 📈 Future Projections")
        st.dataframe(df)

        score = (df.loc[1, "predicted_energy"] + df.loc[1, "predicted_focus"]) / 2
        st.success(f"🎯 Your Future Me Score (Year 5): {round(score, 2)}")
        save_score(name.strip(), round(score, 2))

        st.write("### 📌 Suggestions")
        suggestions, imgs = generate_suggestions(habits)
        for s in suggestions:
            st.markdown(f"- {s}")

        st.write("### 🎨 Visual Insights")
        for img in imgs:
            try:
                st.image(Image.open(img), width=300)
            except:
                st.warning(f"Image not found: {img}")
    elif submitted:
        st.warning("Please enter your name.")

# ---------------- HABIT TRACKER ----------------
with tab3:
    st.markdown("### 📅 Habit Tracker History")
    df = load_csv(HABIT_TRACKER_FILE, ["Date", "Sleep", "Food", "Screen", "Stress", "Activity", "Caffeine", "Water"])
    if df.empty:
        st.info("No habit entries yet. Submit your data from the Simulation tab.")
    else:
        edit_row = st.selectbox("Select entry to edit", options=df["Date"].unique())
        row_data = df[df["Date"] == edit_row].iloc[0]

        with st.form("edit_form"):
            st.write(f"Editing habits for **{edit_row}**:")
            sleep = st.slider("Sleep (hrs)", 0.0, 12.0, float(row_data["Sleep"]), 0.5)
            food = st.slider("Food Quality (1–5)", 1, 5, int(row_data["Food"]))
            screen = st.slider("Screen Time", 0.0, 12.0, float(row_data["Screen"]), 0.5)
            stress = st.slider("Stress", 1, 5, int(row_data["Stress"]))
            activity = st.slider("Activity", 0, 120, int(row_data["Activity"]), 5)
            caffeine = st.slider("Caffeine", 0, 6, int(row_data["Caffeine"]))
            water = st.slider("Water", 0, 12, int(row_data["Water"]))
            update = st.form_submit_button("Update Entry")

        if update:
            df.loc[df["Date"] == edit_row, ["Sleep", "Food", "Screen", "Stress", "Activity", "Caffeine", "Water"]] = \
                [sleep, food, screen, stress, activity, caffeine, water]
            df.to_csv(HABIT_TRACKER_FILE, index=False)
            st.success("Updated successfully!")

        st.dataframe(df.sort_values("Date", ascending=False))

# ---------------- LEADERBOARD ----------------
with tab4:
    st.markdown("### 🏆 Leaderboard (Year 5 Score)")
    df_leader = load_csv(LEADERBOARD_FILE, ["Name", "Score"])
    if not df_leader.empty:
        df_leader = df_leader.sort_values("Score", ascending=False).reset_index(drop=True)
        st.dataframe(df_leader)
    else:
        st.info("No scores yet.")

