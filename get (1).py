import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

# ---------- USER HABITS FROM INPUT -------------
def get_user_habits():
    st.write("### ✍️ Enter Your Current Lifestyle Habits")

    age = st.slider("Your age", 10, 80, 30)
    height = st.slider("Your height (cm)", 140, 200, 170)
    gender = st.radio("Gender", ["Male", "Female"])
    sleep_hours = st.slider("How many hours do you sleep per day?", 0.0, 12.0, 8.0)
    food_quality = st.selectbox("How would you rate your food quality? (1 = Poor, 5 = Excellent)", [1, 2, 3, 4, 5], index=4)
    screen_time = st.slider("Average screen time (hours)", 0.0, 16.0, 2.0)
    stress_level = st.selectbox("Your current stress level (1 = Low, 5 = High)", [1, 2, 3, 4, 5], index=0)
    activity_minutes = st.slider("Minutes of physical activity per day", 0, 120, 60)
    caffeine_intake = st.slider("Cups of caffeine per day", 0, 10, 0)
    water_glasses = st.slider("Glasses of water per day", 0, 12, 12)

    return {
        "age": age,
        "height": height,
        "gender": gender,
        "sleep_hours": sleep_hours,
        "food_quality": food_quality,
        "screen_time": screen_time,
        "stress_level": stress_level,
        "activity_minutes": activity_minutes,
        "caffeine_intake": caffeine_intake,
        "water_glasses": water_glasses
    }

# ---------- SIMULATOR -------------
def simulate_future(habits, years):
    base_weight = 70
    base_energy = 70
    base_focus = 70

    # Estimate BMR (Mifflin-St Jeor Equation)
    weight = base_weight
    if habits["gender"] == "Male":
        bmr = 10 * weight + 6.25 * habits["height"] - 5 * habits["age"] + 5
    else:
        bmr = 10 * weight + 6.25 * habits["height"] - 5 * habits["age"] - 161

    activity_factor = 1.2 + (habits["activity_minutes"] / 120)
    tdee = bmr * activity_factor

    calorie_surplus = (
        (5 - habits["food_quality"]) * 100 +
        (habits["screen_time"] - 6) * 50 -
        (habits["activity_minutes"] - 30) * 5
    )

    weight_change_kg = (calorie_surplus * 365 * years) / 7700
    weight_future = np.clip(weight + weight_change_kg, 45, 120)

    # Energy level (based on sleep, stress, hydration)
    energy_change = (
        1.5 * (habits["sleep_hours"] - 7) +
        -1.5 * (habits["stress_level"] - 3) +
        -0.5 * (2 if habits["water_glasses"] < 6 else 0)
    )
    energy_future = np.clip(base_energy + energy_change * years, 0, 100)

    # Focus level (based on screen time, sleep, stress)
    focus_change = (
        -1.0 * (habits["screen_time"] - 6) +
        0.8 * (habits["sleep_hours"] - 7) +
        -1.0 * (habits["stress_level"] - 3)
    )
    focus_future = np.clip(base_focus + focus_change * years, 0, 100)

    return {
        "years": years,
        "predicted_weight": round(weight_future, 1),
        "predicted_energy": round(energy_future, 1),
        "predicted_focus": round(focus_future, 1)
    }

# ---------- SUGGESTIONS + IMAGES -------------
def generate_suggestions(habits):
    suggestions = []
    images = []

    if habits["sleep_hours"] < 6:
        suggestions.append("🛌 You should sleep 6–8 hours per day. Your sleep time is very low.")
        images.append("https://cdn.pixabay.com/photo/2020/02/05/19/13/sleep-4825687_1280.jpg")

    if habits["food_quality"] <= 2:
        suggestions.append("🥦 Improve your food quality by eating more fruits and vegetables.")

    if habits["screen_time"] > 6:
        suggestions.append("📱 Your screen time is high. Reduce it to less than 6 hours per day.")
        images.append("https://cdn.pixabay.com/photo/2017/08/07/23/57/smartphone-2604479_1280.jpg")

    if habits["stress_level"] >= 4:
        suggestions.append("😟 Your stress level is high. Try relaxation techniques like meditation.")

    if habits["activity_minutes"] < 30:
        suggestions.append("🏃‍♂️ Increase physical activity to at least 30 minutes per day.")
        images.append("https://cdn.pixabay.com/photo/2016/03/27/22/22/running-1280256_1280.jpg")

    if habits["caffeine_intake"] > 2:
        suggestions.append("☕ Reduce caffeine to 1–2 cups a day.")

    if habits["water_glasses"] < 6:
        suggestions.append("💧 Your water intake is low. Aim for 6–8 glasses daily.")
        images.append("https://cdn.pixabay.com/photo/2016/04/20/18/41/water-1343141_1280.jpg")

    if not suggestions:
        suggestions.append("✅ Your habits look balanced. Keep it up!")

    return suggestions, images

# ---------- MAIN PAGE ----------
st.set_page_config(page_title="Future Me Score", layout="wide")

st.title("🧬 Future Me Score")
st.subheader("Simulate your health 3, 5, or 10 years into the future based on today's lifestyle!")

tab1, tab2 = st.tabs(["🏠 Home", "📊 Simulation & Suggestions"])

# ---------- TAB 1: HOME ----------
with tab1:
    st.image("https://images.unsplash.com/photo-1613892202132-d8175c67b11d", caption="Visualize Your Future Self", use_column_width=True)
    st.markdown("""
    Welcome to the **Future Me Score Simulator**.

    This tool helps you visualize your future health, energy, and focus based on your current lifestyle habits.

    > Small habits today, big impact tomorrow!
    """)

# ---------- TAB 2: SIMULATION ----------
with tab2:
    habits = get_user_habits()
    results = []
    for year in [3, 5, 10]:
        results.append(simulate_future(habits, year))

    df = pd.DataFrame(results)
    st.write("### 📈 Predicted Health Outcomes")
    st.dataframe(df)

    st.write("### 📌 Personalized Suggestions")
    suggestions, img_urls = generate_suggestions(habits)
    for s in suggestions:
        st.markdown(f"- {s}")

    st.write("### 🎨 Visual Insights")
    for url in img_urls:
        st.image(url, width=300)
