import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from openai import OpenAI

# ✅ Use a user API key only (not a project-scoped one)
client = OpenAI(api_key="sk-your-user-secret-key-here")  # Replace with your real key

# -------------------- USER INPUT --------------------
def get_user_habits():
    return {
        "gender": "female",
        "age": 27,
        "sleep_hours": 5,
        "food_quality": 2,
        "screen_time": 9.0,
        "stress_level": 4,
        "activity_minutes": 20,
        "caffeine_intake": 3,
        "water_glasses": 3
    }

# -------------------- SIMULATION --------------------
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

# -------------------- AI IMAGE --------------------
def generate_ai_image(habits):
    prompt = f"A portrait of a {habits['gender']} in her {habits['age']}s living a lifestyle with "
    prompt += f"{habits['sleep_hours']} hrs sleep, high stress, poor diet, "
    prompt += f"{habits['screen_time']} hrs screen time, low activity, low water intake."

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="512x512"
    )
    return response.data[0].url

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

# -------------------- STREAMLIT APP --------------------
st.set_page_config(page_title="Future Me Score", layout="wide")

st.title("🧬 Future Me Score Simulator")
st.subheader("Visualize your future based on your current lifestyle.")

tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Simulation", "🤖 AI Portrait"])

with tab1:
    st.image("https://images.unsplash.com/photo-1613892202132-d8175c67b11d", use_column_width=True)
    st.markdown("""
    Welcome to the **Future Me Score** app.

    Enter your lifestyle habits and we’ll simulate your health over 3, 5, and 10 years,
    along with tips to improve and an AI-generated **future portrait**.
    """)

with tab2:
    habits = get_user_habits()
    results = [simulate_future(habits, y) for y in [3, 5, 10]]
    st.write("### 📈 Health Projection")
    st.dataframe(pd.DataFrame(results))

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

with tab3:
    st.write("### 👁️ AI-Generated Future You")
    if st.button("🎨 Generate Image"):
        with st.spinner("Creating your future portrait..."):
            try:
                image_url = generate_ai_image(habits)
                st.image(image_url, caption="Your Future Self", use_column_width=True)
            except Exception as e:
                st.error(f"Image generation failed: {e}")
