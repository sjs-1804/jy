import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image

# -------------------- CONFIG --------------------
LEADERBOARD_FILE = "leaderboard.csv"

# -------------------- SIMULATION LOGIC --------------------
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

# -------------------- SUGGESTIONS --------------------
def generate_suggestions(habits):
    suggestions = []
    images = []

    if habits["sleep_hours"] < 6:
        suggestions.append("🛌 You should sleep 6–8 hours per day.")
        images.append("images/low_sleep.jpg")

    if habits["food_quality"] <= 2:
        suggestions.append("🥦 Eat more whole foods, fruits, and vegetables.")

    if habits["screen_time"] > 6:
        suggestions.append("📱 Try to limit screen time below 6 hours.")

    if habits["stress_level"] >= 4:
        suggestions.append("😟 Practice meditation or deep breathing daily.")

    if habits["activity_minutes"] < 30:
        suggestions.append("🏃‍♀️ Exercise at least 30 minutes per day.")
        images.append("images/low_activity.jpg")

    if habits["caffeine_intake"] > 2:
        suggestions.append("☕ Try limiting caffeine to 1–2 cups/day.")

    if habits["water_glasses"] < 6:
        suggestions.append("💧 Hydrate better – aim for 6–8 glasses of water.")

    if not suggestions:
        suggestions.append("✅ Great job! Your habits are healthy.")

    return suggestions, images

# -------------------- LEADERBOARD --------------------
def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        return pd.read_csv(LEADERBOARD_FILE)
    else:
        return pd.DataFrame(columns=["Name", "Score"])

def save_score(name, score):
    df = load_leaderboard()
    new_row = pd.DataFrame([[name, score]], columns=["Name", "Score"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(LEADERBOARD_FILE, index=False)

# -------------------- STREAMLIT APP --------------------
st.set_page_config(page_title="Future Me Score", layout="wide")

st.title("🧬 Future Me Score Simulator")
st.subheader("Visualize your future based on your current lifestyle.")

tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Simulation", "🏆 Leaderboard"])

# -------------------- HOME --------------------
with tab1:
    st.image("https://images.unsplash.com/photo-1613892202132-d8175c67b11d", use_column_width=True)
    st.markdown("""
    Welcome to the **Future Me Score** app.

    Enter your lifestyle habits and we’ll simulate your health over 3, 5, and 10 years,
    give personalized suggestions, and let you compare with friends on the leaderboard!
    """)

# -------------------- SIMULATION --------------------
with tab2:
    with st.form("habit_form"):
        st.markdown("### ✍️ Enter Your Daily Habits")

        name = st.text_input("Your Name")

        col1, col2 = st.columns(2)
        with col1:
            sleep_hours = st.slider("Sleep (hours per day)", 0.0, 12.0, 6.0, 0.5)
            food_quality = st.slider("Food Quality (1=Poor, 5=Excellent)", 1, 5, 3)
            screen_time = st.slider("Screen Time (hours per day)", 0.0, 15.0, 6.0, 0.5)
            stress_level = st.slider("Stress Level (1=Low, 5=High)", 1, 5, 3)

        with col2:
            activity_minutes = st.slider("Physical Activity (minutes/day)", 0, 120, 30, 5)
            caffeine_intake = st.slider("Caffeine (cups per day)", 0, 6, 2)
            water_glasses = st.slider("Water Intake (glasses/day)", 0, 12, 6)

        submitted = st.form_submit_button("Run Simulation")

    if submitted and name.strip():
        habits = {
            "sleep_hours": sleep_hours,
            "food_quality": food_quality,
            "screen_time": screen_time,
            "stress_level": stress_level,
            "activity_minutes": activity_minutes,
            "caffeine_intake": caffeine_intake,
            "water_glasses": water_glasses
        }

        results = [simulate_future(habits, y) for y in [3, 5, 10]]
        st.write("### 📈 Health Projection")
        df = pd.DataFrame(results)
        st.dataframe(df)

        # Leaderboard score from year=5
        score_5yr = (df.loc[1, "predicted_energy"] + df.loc[1, "predicted_focus"]) / 2
        st.success(f"🎯 Your Future Me Score (Year 5): {round(score_5yr, 2)}")

        # Save to leaderboard
        save_score(name.strip(), round(score_5yr, 2))

        st.write("### 📌 Personalized Suggestions")
        suggestions, img_paths = generate_suggestions(habits)
        for s in suggestions:
            st.markdown(f"- {s}")

        st.write("### 🎨 Visual Insights")
        for img_path in img_paths:
            try:
                st.image(Image.open(img_path), width=300)
            except:
                st.warning(f"⚠️ Image not found: {img_path}")
    elif submitted:
        st.warning("⚠️ Please enter your name to continue.")

# -------------------- LEADERBOARD --------------------
with tab3:
    st.markdown("### 🏆 Friend Leaderboard (Year 5 Score)")
    leaderboard_df = load_leaderboard()
    if not leaderboard_df.empty:
        leaderboard_df = leaderboard_df.sort_values(by="Score", ascending=False).reset_index(drop=True)
        st.dataframe(leaderboard_df)
    else:
        st.info("No scores yet. Go to the Simulation tab to add your first score.")
