import streamlit as st
import pandas as pd
import numpy as np

# ---------- USER HABITS INPUT -------------
def get_user_habits():
    st.write("### ✍️ Enter Your Current Lifestyle Habits")

    name = st.text_input("Enter your nickname for leaderboard", value="You")
    age = st.slider("Your age", 10, 80, 30)
    height = st.slider("Your height (cm)", 140, 200, 170)
    gender = st.radio("Gender", ["Male", "Female"])
    sleep_hours = st.slider("How many hours do you sleep per day?", 0.0, 12.0, 8.0)
    food_quality = st.selectbox("Food quality? (1 = Poor, 5 = Excellent)", [1, 2, 3, 4, 5], index=4)
    screen_time = st.slider("Average screen time (hours)", 0.0, 16.0, 2.0)
    stress_level = st.selectbox("Stress level (1 = Low, 5 = High)", [1, 2, 3, 4, 5], index=0)
    activity_minutes = st.slider("Minutes of physical activity per day", 0, 120, 60)
    caffeine_intake = st.slider("Cups of caffeine per day", 0, 10, 0)
    water_glasses = st.slider("Glasses of water per day", 0, 12, 12)

    return {
        "name": name,
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

    # BMR
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

    # Energy
    energy_change = (
        1.5 * (habits["sleep_hours"] - 7) +
        -1.5 * (habits["stress_level"] - 3) +
        -0.5 * (2 if habits["water_glasses"] < 6 else 0)
    )
    energy_future = np.clip(base_energy + energy_change * years, 0, 100)

    # Focus
    focus_change = (
        -1.0 * (habits["screen_time"] - 6) +
        0.8 * (habits["sleep_hours"] - 7) +
        -1.0 * (habits["stress_level"] - 3)
    )
    focus_future = np.clip(base_focus + focus_change * years, 0, 100)

    return {
        "name": habits["name"],
        "years": years,
        "predicted_weight": round(weight_future, 1),
        "predicted_energy": round(energy_future, 1),
        "predicted_focus": round(focus_future, 1)
    }

# ---------- SUGGESTIONS + REFERENCES -------------
def generate_suggestions(habits):
    suggestions = []
    images = []

    if habits["sleep_hours"] < 6:
        suggestions.append("🛌 You should sleep 6–8 hours/day. ([CDC](https://www.cdc.gov/sleep))")

    if habits["food_quality"] <= 2:
        suggestions.append("🥦 Improve food quality: more vegetables/fruits. ([Harvard](https://www.hsph.harvard.edu/nutritionsource/))")

    if habits["screen_time"] > 6:
        suggestions.append("📱 Reduce screen time to <6 hrs/day to prevent fatigue. ([NIH](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8410649/))")

    if habits["stress_level"] >= 4:
        suggestions.append("😟 High stress. Try mindfulness. ([APA](https://www.apa.org/topics/stress))")

    if habits["activity_minutes"] < 30:
        suggestions.append("🏃‍♂️ Do 30+ min of activity/day. ([WHO](https://www.who.int/news-room/fact-sheets/detail/physical-activity))")

    if habits["caffeine_intake"] > 2:
        suggestions.append("☕ Too much caffeine. Limit to 1–2 cups. ([FDA](https://www.fda.gov/food/food-additives-petitions/caffeine))")

    if habits["water_glasses"] < 6:
        suggestions.append("💧 Drink 6–8 glasses of water/day. ([Mayo Clinic](https://www.mayoclinic.org/)))")

    if not suggestions:
        suggestions.append("✅ Excellent habits! Keep it up!")

    return suggestions

# ---------- AI FUTURE SELF IMAGE ----------
def get_future_self_image(score):
    if score >= 80:
        return "https://cdn.pixabay.com/photo/2020/09/06/09/51/businessman-5547144_1280.jpg"
    elif score >= 50:
        return "https://cdn.pixabay.com/photo/2016/03/31/20/36/man-1298238_1280.png"
    else:
        return "https://cdn.pixabay.com/photo/2017/01/30/12/32/depression-2025607_1280.jpg"

# ---------- LEADERBOARD DUMMY DATA ----------
def generate_leaderboard(user_score):
    data = {
        "User": ["Alice", "Bob", "Cara", "Dev", "Eva", user_score["name"]],
        "Focus Score": [62, 74, 81, 49, 91, user_score["predicted_focus"]]
    }
    df = pd.DataFrame(data)
    df = df.sort_values(by="Focus Score", ascending=False).reset_index(drop=True)
    return df

# ---------- MAIN APP ----------
st.set_page_config(page_title="Future Me Score", layout="wide")

st.title("🧬 Future Me Score")
st.subheader("Simulate your health 3, 5, or 10 years into the future based on today's lifestyle!")

tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Simulation", "🏆 Leaderboard"])

# ---------- HOME ----------
with tab1:
    st.image("https://images.unsplash.com/photo-1613892202132-d8175c67b11d", use_column_width=True)
    st.markdown("""
    Welcome to **Future Me Score** 🎯

    This tool uses your lifestyle to simulate future:
    - Body weight
    - Energy level
    - Focus level

    And shows a portrait of your **future self** 🧠
    """)

# ---------- SIMULATION ----------
with tab2:
    habits = get_user_habits()
    results = [simulate_future(habits, y) for y in [3, 5, 10]]

    df = pd.DataFrame(results)
    st.write("### 📈 Predicted Outcomes")
    st.dataframe(df)

    st.write("### 🤖 AI-Predicted Future Self")
    img = get_future_self_image(results[-1]["predicted_focus"])
    st.image(img, width=300)

    st.write("### 💡 Personalized Suggestions")
    for s in generate_suggestions(habits):
        st.markdown(f"- {s}")

# ---------- LEADERBOARD ----------
with tab3:
    st.write("### 🏆 Focus Score Leaderboard")
    lb = generate_leaderboard(results[-1])
    st.dataframe(lb.style.highlight_max(axis=0, color='lightgreen'))
