import streamlit as st
import pandas as pd
from textblob import TextBlob
import os
import csv
from streamlit_lottie import st_lottie
import requests
from streamlit_option_menu import option_menu
import altair as alt
from datetime import datetime
import base64
from io import BytesIO
import openai
import random

# Add your OpenAI API key here
openai.api_key = "YOUR_OPENAI_API_KEY"

# =========Helper function Loader=============
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        return None

# ========== Function to Load Animation with cache ==========
@st.cache_data(ttl=3600)
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Create folders if not exist
os.makedirs("data", exist_ok=True)

st.set_page_config(page_title="NatureMind Wellness", layout="centered", page_icon="🌿")

# ---------- Dark Mode Theming ----------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# Apply nature-inspired dark theme
bg_color = "#0a1a0f"  # Dark forest green
text_color = "#e0f7e0"  # Soft greenish white
card_bg = "#1a2b1a"  # Medium forest green
button_bg = "#4a8c4a"  # Nature green
button_text = "#ffffff"  # White
accent_color = "#5dbb63"  # Bright nature green
danger_color = "#ff6b6b"  # For high risk alerts

st.markdown(
    f"""
    <style>
    body {{ background-color: {bg_color}; color: {text_color}; }}
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    div[data-testid="stMetric"] {{
        background-color: {card_bg};
        color: {text_color};
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
    }}
    table {{ color: {text_color}; }}
    button[kind="primary"] {{
        background-color: {button_bg} !important;
        color: {button_text} !important;
        border: none !important;
    }}
    button[kind="primary"]:hover {{
        background-color: #3a6b3a !important;
        color: white !important;
    }}
    .stTextInput>div>div>input {{
        background-color: {card_bg};
        color: {text_color};
    }}
    .stNumberInput>div>div>input {{
        background-color: {card_bg};
        color: {text_color};
    }}
    select {{
        background-color: {card_bg};
        color: {text_color};
    }}
    .chat-message {{
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        max-width: 80%;
    }}
    .chat-message.user {{
        background-color: {card_bg};
        margin-left: auto;
        border-bottom-right-radius: 0;
    }}
    .chat-message.bot {{
        background-color: {button_bg};
        margin-right: auto;
        border-bottom-left-radius: 0;
    }}
    .stChatInput {{
        bottom: 20px;
        position: fixed;
    }}
    .quiz-question {{
        background-color: {card_bg};
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }}
    .quiz-option {{
        background-color: {button_bg};
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        cursor: pointer;
    }}
    .quiz-option:hover {{
        background-color: #3a6b3a;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize chatbot
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.chat_history.append({"role": "bot", "content": "🌿 Welcome to NatureMind! I'm your wellness companion. How can I help you today?"})

if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []
    st.session_state.quiz_complete = False

# Pages list
pages = ["👤 User Info", "📊 Dashboard", "✨ Suggestions", "📝 Feedback"]

# Initialize session state for current page
if 'page' not in st.session_state or st.session_state.page not in pages:
    st.session_state.page = pages[0]

# Sidebar Navigation
st.sidebar.title("Navigation")
current_idx = pages.index(st.session_state.page)

for i, page in enumerate(pages):
    if i <= current_idx:
        if st.sidebar.button(f"{i+1}. {page}", key=page):
            st.session_state.page = page
    else:
        st.sidebar.markdown(f"{i+1}. {page} 🔒")

# Page Navigator
def go_next():
    next_idx = pages.index(st.session_state.page) + 1
    if next_idx < len(pages):
        st.session_state.page = pages[next_idx]

# ========== Chatbot Functions ==========
def handle_chat_input():
    user_input = st.session_state.chat_input
    if user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Simple chatbot responses
        if any(word in user_input.lower() for word in ["hi", "hello", "hey"]):
            response = "🌱 Hello there! How can I assist you with your wellness journey today?"
        elif any(word in user_input.lower() for word in ["stress", "anxious", "overwhelmed"]):
            response = "🍃 I hear you're feeling stressed. Remember to take deep breaths. Would you like a guided breathing exercise?"
        elif any(word in user_input.lower() for word in ["sleep", "tired"]):
            response = "🌙 Sleep is crucial for wellbeing. Try establishing a calming bedtime routine with dim lights and no screens 1 hour before bed."
        elif any(word in user_input.lower() for word in ["thank", "thanks"]):
            response = "🌸 You're welcome! Remember, small steps lead to big changes in wellness."
        else:
            response = "🌿 That's an interesting thought. Could you tell me more about how you're feeling?"
        
        st.session_state.chat_history.append({"role": "bot", "content": response})
        st.session_state.chat_input = ""

# ========== Quiz Functions ==========
def handle_quiz_answer(question_idx, answer):
    st.session_state.quiz_answers[question_idx] = answer
    if None not in st.session_state.quiz_answers:
        st.session_state.quiz_complete = True

def get_quiz_suggestions():
    score = sum(st.session_state.quiz_answers)
    if score <= 5:
        return """
        🌧️ You're showing several signs of burnout. Please consider:
        1. Taking a complete mental health day
        2. Talking to a professional
        3. Reducing your workload where possible
        4. Practicing daily mindfulness
        """
    elif score <= 10:
        return """
        🌤️ You're showing some signs of stress. Try these:
        1. Schedule regular breaks during work
        2. Practice the 20-20-20 rule (every 20 mins, look 20 feet away for 20 seconds)
        3. Start a gratitude journal
        4. Increase physical activity
        """
    else:
        return """
        🌞 You're managing well! To maintain balance:
        1. Keep up your healthy habits
        2. Check in with yourself weekly
        3. Help others with their wellness
        4. Continue learning about self-care
        """

# ========== Page 1: User Info ==========
if st.session_state.page == "👤 User Info":
    st.title("🌱 NatureMind Wellness")
    st.markdown("Please fill in your details to get started")

    animation = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_1pxqjqps.json")
    if animation:
        st_lottie(animation, height=220, key="character_animation")
    else:
        st.warning("⚠️ Animation failed to load. Please check your internet or animation URL.")

    name = st.text_input("Your Name")
    age = st.number_input("Your Age", min_value=10, max_value=100, step=1)
    gender = st.selectbox("Select your gender:", ["Male", "Female", "Other", "Prefer not to say"])

    if st.button("Continue to Dashboard"):
        if name:
            st.session_state.name = name
            st.session_state.age = age
            st.session_state.gender = gender

            with open("data/user_info.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([name, age, gender])

            go_next()
        else:
            st.warning("Please enter your name to continue.")

# ========== Page 2: Dashboard ==========
elif st.session_state.page == "📊 Dashboard":
    st.title("🌿 Wellness Dashboard")
    st.write(f"Welcome, {st.session_state.get('name', 'User')}!")
    st.markdown("### ✏️ Nature Journal")
    journal_entry = st.text_area("Write about your day, thoughts, or feelings:", height=200)

    sleep_hours = st.slider("🌙 Hours slept last night", 0, 12, 6)
    screen_time = st.slider("📱 Daily Screen Time (hours)", 0, 16, 6)
    workout_done = st.selectbox("🏃‍♀️ Physical activity today?", ["Yes", "No"])

    if 'mood_analyzed' not in st.session_state:
        st.session_state.mood_analyzed = False

    if st.button("Analyze My Wellness"):
        if journal_entry.strip():
            polarity = TextBlob(journal_entry).sentiment.polarity

            sleep_score = sleep_hours
            workout_score = 1 if workout_done == "Yes" else 0
            screen_score = screen_time

            mood_score = (
                (0.4 * polarity) +
                (0.3 * (sleep_score / 10)) +
                (0.2 * workout_score) -
                (0.2 * (screen_score / 10))
            )

            if mood_score > 0.4:
                mood = "Thriving 🌸"
                risk = "Low"
            elif mood_score > 0.1:
                mood = "Balanced 🌿"
                risk = "Moderate"
            else:
                mood = "Needs Care 🍂"
                risk = "High"

            st.metric("Current State", mood)
            st.metric("Wellness Score", f"{mood_score:.2f}")
            st.metric("Burnout Risk", risk)

            st.session_state.avg_mood = mood_score
            st.session_state.risk = risk
            st.session_state.mood_analyzed = True

            if risk == "High":
                st.session_state.quiz_answers = [None] * 5  # Reset quiz
                st.session_state.quiz_complete = False

            if risk == "Low":
                flower_animation = load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_touohxv0.json")
                if flower_animation:
                    st_lottie(flower_animation, height=150, key="flower_animation")
        else:
            st.warning("Please enter something in your journal to analyze.")

    if st.session_state.mood_analyzed:
        if st.button("Continue to Suggestions"):
            go_next()

    # Chatbot in Dashboard
    st.markdown("---")
    st.markdown("### 🌱 Wellness Companion")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message user">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message bot">{message["content"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    st.text_input("Message the wellness companion...", key="chat_input", on_change=handle_chat_input)

# ========== Page 3: Suggestions ==========
elif st.session_state.page == "✨ Suggestions":
    st.title("🌻 Personalized Suggestions")
    risk = st.session_state.get('risk', 'Moderate')

    if risk == "High" and not st.session_state.quiz_complete:
        st.markdown("### 🍂 Burnout Risk Assessment")
        st.markdown("Let's understand your situation better with a quick quiz:")
        
        questions = [
            "How often do you feel exhausted?",
            "Do you have trouble concentrating?",
            "How often do you feel irritable?",
            "Do you feel less productive than usual?",
            "How often do you feel detached from work?"
        ]
        
        options = [
            ["Never", "Rarely", "Sometimes", "Often", "Always"],
            ["Not at all", "Slightly", "Moderately", "Quite a bit", "Extremely"],
            ["Never", "Rarely", "Sometimes", "Often", "Always"],
            ["Not at all", "Slightly", "Moderately", "Quite a bit", "Extremely"],
            ["Never", "Rarely", "Sometimes", "Often", "Always"]
        ]
        
        for i, question in enumerate(questions):
            st.markdown(f'<div class="quiz-question">{i+1}. {question}</div>', unsafe_allow_html=True)
            cols = st.columns(5)
            for j, option in enumerate(options[i]):
                with cols[j]:
                    if st.button(option, key=f"quiz_{i}_{j}"):
                        handle_quiz_answer(i, j)
        
        if st.session_state.quiz_complete:
            st.success("Quiz completed! Here are your personalized suggestions:")
            st.markdown(get_quiz_suggestions())
    else:
        if risk == "Moderate":
            st.subheader("🌿 Balance Restoration")
            st.markdown("""
            You're doing okay but could use some extra care:
            - Try a 5-minute nature meditation
            - Schedule screen-free time before bed
            - Take short walking breaks every hour
            """)
        elif risk == "High":
            if st.session_state.quiz_complete:
                st.markdown(get_quiz_suggestions())
            else:
                st.subheader("🍂 Deep Recovery")
                st.markdown("""
                You might be feeling overwhelmed. Consider:
                - Taking a complete mental health day
                - Talking to a professional
                - Practicing daily mindfulness
                - Reducing workload where possible
                """)
        else:
            st.subheader("🌸 Thriving Well")
            st.markdown("""
            You're doing great! To maintain your wellness:
            - Keep up your healthy habits
            - Check in with yourself weekly
            - Help others with their wellness
            - Continue learning about self-care
            """)

        st.markdown("---")
        st.markdown("### 🎧 Nature Sound Therapy")
        sound_options = {
            "Forest Rain": "https://www.youtube.com/watch?v=OdIJ2x3nxzQ",
            "Ocean Waves": "https://www.youtube.com/watch?v=rZ7VVGvrfiA",
            "Mountain Stream": "https://www.youtube.com/watch?v=HiUY9vU-rYQ",
            "Birds Singing": "https://www.youtube.com/watch?v=6D0Q1f1i1x0"
        }
        selected_sound = st.selectbox("Choose a nature sound:", options=list(sound_options.keys()))
        st.video(sound_options[selected_sound])

    if st.button("Continue to Feedback"):
        st.session_state.page = "📝 Feedback"

# ========== Page 4: Feedback ==========
elif st.session_state.page == "📝 Feedback":
    st.title("🍃 Your Feedback")
    st.write("Thank you for using NatureMind Wellness!")
    
    feedback_animation = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_tutvdkg0.json")
    if feedback_animation:
        st_lottie(feedback_animation, height=200, key="feedback_anim")
    
    feedback = st.text_area("How was your experience with NatureMind Wellness?")
    if st.button("Submit Feedback"):
        with open("data/feedback.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([st.session_state.get("name", "Anonymous"), feedback])
        st.success("🌻 Thank you for your feedback! Wishing you continued wellness.")
        
        # Celebration animation
        confetti_anim = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_obhph3sh.json")
        if confetti_anim:
            st_lottie(confetti_anim, height=200, key="confetti")
