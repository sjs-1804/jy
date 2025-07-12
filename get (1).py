import streamlit as st
import pandas as pd
import numpy as np
import openai
import os

# ------------ API Key (Secure Setup) ---------------
openai.api_key = st.secrets.get("OPENAI_API_KEY", "your-api-key-here")

# ------------ Prompt Builder for AI Portrait ---------------
def build_ai_portrait_prompt(habits):
    prompt = f"Portrait of a {habits['age']}-year-old {habits['gender'].lower()}, "

    if habits["sleep_hours"] < 6:
        prompt += "tired eyes, dark circles, "
    else:
        prompt += "well-rested and refreshed, "

    if habits["food_quality"] >= 4:
        prompt += "healthy glowing skin, "
    else:
        prompt += "dull and unhealthy skin, "

    if habits["stress_level"] >= 4:
        prompt += "stressed facial expression, "
    elif habits["stress_level"] <= 2:
        prompt += "calm and relaxed appearance, "

    if habits["screen_time"] > 6:
        prompt += "slightly strained eyes, "

    if habits["activity_minutes"] >= 45:
        prompt += "fit and active look, defined face, "
    else:
        prompt += "low-energy posture, "

    if habits["water_glasses"] < 6:
        prompt += "dry skin, "

    if habits["caffeine_intake"] > 3:
        prompt += "restless or anxious expression, "

    prompt += "realistic digital portrait, professional lighting."
    return prompt.strip()

# ------------ Generate AI Image with OpenAI DALL·E ---------------
def generate_ai_image(prompt):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        return response['data'][0]['url']
    except Exception as e:
        st.error(f"Image generation failed: {e}")
        return None

# ------------ Collect Lifestyle Habits from User ---------------
def get_user_habits():
    st.write("### ✍️ Enter Your Current Lifestyle Habits")

    name = st.text_input("Your name (optional)", value="You")
    age = st.slider("Age", 10, 80, 30)
    height = st.slider("Height (cm)", 140, 200, 170)
    gender = st.radio("Gender", ["Male", "Female"])
    sleep_hours = st.slider("Sleep hours per day", 0.0, 12.0, 8.0)
    food_quality = st.selectbox("Food quality (1 = Poor, 5 = Excellent)", [1, 2, 3, 4, 5], index=4)
    screen_time = st.slider("Screen time (hrs/day)", 0.0, 16.0, 2.0)
    stress_level = st.selectbox("Stress level (1 = Low, 5 = High)", [1, 2, 3, 4, 5], index=1)
    activity_minutes = st.slider("Physical activity (min/day)", 0, 120, 60)
    caffeine_intake = st.slider("Cups of caffeine/day", 0, 10, 0)
    water_glasses = st.slider("Water intake (glasses/day)", 0, 12, 8)

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

# ------------ Future Simulation ---------------
def simulate_future(habits, years):
    base_weight = 70
    base_energy = 70
    base_focus = 70

    weight = base_weight
    if habits["gender"] == "Male":
        bmr = 10 * weight + 6.25 * habits["height"] - 5 * habits["age"] + 5
    else:
        bmr = 10 * weight + 6.25 * habits["height"] - 5 * habits["age"] - 161

    activity_factor = 1.2 + (habits["activity_minutes"] / 120)
    calorie_surplus = (
        (5 - habits["food_quality"]) * 100 +
        (habits["screen_time"] - 6) * 50 -
        (habits["activity_minutes"] - 30) * 5
    )
    weight_change = (calorie_surplus * 365 * years) / 7700
    weight_future = np.clip(weight + weight_change, 45, 120)

    energy_change = (
        1.5 * (habits["sleep_hours"] - 7) -
        1.5 * (habits["stress_level"] - 3) -
        0.5 * (2 if habits["water_glasses"] < 6 else 0)
    )
    energy_future = np.clip(base_energy + energy_change * years, 0, 100)

    focus_change = (
        -1.0 * (habits["screen_time"] - 6) +
        0.8 * (habits["sleep_hours"] - 7) -
        1.0 * (habits["stress_level"] - 3)
    )
    focus_future = np.clip(base_focus + focus_change * years, 0, 100)

    return {
        "name": habits["name"],
        "years": years,
        "predicted_weight": round(weight_future, 1),
        "predicted_energy": round(energy_future, 1),
        "predicted_focus": round(focus_future, 1)
    }

# ------------ Streamlit App Layout ---------------
st.set_page_config(page_title="Future Me Score", layout="wide")
st.title("🧬 Future Me Score")
st.subheader("Simulate your future health and see your AI-generated future self")

tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Simulation", "🤖 AI Portrait"])

# ------------ Home Tab ---------------
with tab1:
    st.image("https://images.unsplash.com/photo-1613892202132-d8175c67b11d", use_column_width=True)
    st.markdown("This app lets you simulate future **weight**, **energy**, and **focus** — and generate your **AI Future Self** based on your lifestyle.")

# ------------ Simulation Tab ---------------
with tab2:
    habits = get_user_habits()
    results = [simulate_future(habits, y) for y in [3, 5, 10]]
    df = pd.DataFrame(results)
    st.write("### 📈 Future Health Predictions")
    st.dataframe(df)

# ------------ AI Portrait Tab ---------------
with tab3:
    st.write("### 🧠 Your AI-Generated 'Future You' Image")
    prompt = build_ai_portrait_prompt(habits)
    st.text_area("Prompt used:", value=prompt, height=120)

    if st.button("🎨 Generate Image"):
        image_url = generate_ai_image(prompt)
        if image_url:
            st.image(image_url, caption="AI-Generated Future You", width=512)
        else:
            st.error("❌ Failed to generate image. Check your OpenAI API key.")
