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
import openai
import random

# Configure OpenAI - using secrets management
openai.api_key = "OPENAI_API_KEY"

# ========= Helper Functions ========
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

# ========= App Configuration ========
st.set_page_config(
    page_title="NatureMind Wellness",
    layout="centered",
    page_icon="🌿",
    initial_sidebar_state="expanded"
)

# ========= Dark Mode Theme & Styles ========
bg_color = "#0a1a0f"  # Dark forest green
card_bg = "#1a2a1a"   # Darker green
text_color = "#e0f0e0" # Soft mint
accent_color = "#4cc9a8" # Teal
warning_color = "#ff7597" # Coral
button_bg = "#3a8a5f"  # Sage green
button_text = "#ffffff"
female_color = "#ffb6c1" # Light pink
male_color = "#89cff0"   # Light blue

# Apply CSS
st.markdown(
    f"""
    <style>
    :root {{
        --primary-color: {accent_color};
        --background-color: {bg_color};
        --card-bg: {card_bg};
        --text-color: {text_color};
        --warning-color: {warning_color};
        --female-color: {female_color};
        --male-color: {male_color};
    }}
    
    body {{ 
        background-color: {bg_color}; 
        color: {text_color}; 
    }}
    .stApp {{ 
        background-color: {bg_color}; 
        color: {text_color}; 
    }}
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: {card_bg};
        color: {text_color};
        border-color: {accent_color};
        border-radius: 12px;
    }}
    .stSelectbox>div>div>select {{
        background-color: {card_bg};
        color: {text_color};
        border-radius: 12px;
    }}
    .stSlider>div>div>div>div {{
        background-color: {accent_color};
    }}
    .stButton>button {{
        background-color: {button_bg};
        color: {button_text};
        border: none;
        border-radius: 12px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: #2a6a4f;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    .chat-message {{
        padding: 12px;
        border-radius: 12px;
        margin: 6px 0;
        max-width: 80%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }}
    .user-message {{
        background-color: {card_bg};
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }}
    .bot-message {{
        background-color: {bg_color};
        border: 1px solid {accent_color};
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }}
    .suggestion-card {{
        background-color: {card_bg};
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        border-left: 4px solid {accent_color};
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .warning-card {{
        background-color: {card_bg};
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        border-left: 4px solid {warning_color};
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .routine-item {{
        display: flex;
        margin-bottom: 10px;
        align-items: center;
        background-color: {card_bg};
        padding: 10px;
        border-radius: 8px;
    }}
    .routine-time {{
        width: 80px;
        font-weight: bold;
        color: {accent_color};
    }}
    .routine-activity {{
        flex-grow: 1;
        padding-left: 15px;
        border-left: 2px solid {button_bg};
    }}
    .gender-tabs {{
        display: flex;
        margin-bottom: 20px;
        border-radius: 12px;
        overflow: hidden;
        background-color: {card_bg};
    }}
    .gender-tab {{
        flex: 1;
        text-align: center;
        padding: 10px;
        cursor: pointer;
        transition: all 0.3s;
    }}
    .gender-tab.active {{
        background-color: {accent_color};
        color: white;
    }}
    .question-card {{
        background-color: {card_bg};
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: all 0.3s;
        cursor: pointer;
        border-left: 4px solid {accent_color};
    }}
    .question-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.3);
    }}
    .cycle-phase {{
        background-color: {female_color}30;
        padding: 8px 12px;
        border-radius: 20px;
        display: inline-block;
        margin: 4px 0;
        font-size: 0.8rem;
        color: {text_color};
    }}
    .result-card {{
        background-color: {card_bg};
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 4px solid {accent_color};
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ========= Pages & Navigation ========
pages = ["🌱 Welcome", "📊 Mood Check", "Wellness Guide", "📝 Feedback"]

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = pages[0]
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'mood_analyzed' not in st.session_state:
    st.session_state.mood_analyzed = False
if 'gender' not in st.session_state:
    st.session_state.gender = None
if 'chat_gender' not in st.session_state:
    st.session_state.chat_gender = "female"
if 'mood_data' not in st.session_state:
    st.session_state.mood_data = {
        "mood": "Not analyzed yet",
        "mood_score": 0,
        "risk": "Not analyzed yet",
        "mood_color": accent_color,
        "journal_entry": "",
        "sleep_hours": 7,
        "screen_time": 5,
        "outdoor_time": 30,
        "exercise": "Moderate"
    }

# Sidebar Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3197/3197428.png", width=80)
    st.title("NatureMind")
    st.caption("Your natural wellness companion")
    
    for i, page in enumerate(pages):
        if st.button(f"{page}", key=f"nav_{page}"):
            st.session_state.page = page

# ========= Page 1: Welcome ========
if st.session_state.page == "🌱 Welcome":
    st.title("🌿 Welcome to NatureMind")
    st.markdown(f"""
    <div class="result-card">
        <p style="font-size: 16px;">Find your balance with our nature-inspired wellness companion. 
        Track your mood, get personalized suggestions, and discover wellness insights tailored just for you.</p>
    </div>
    """, unsafe_allow_html=True)
    
    anim = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_yo4lqexz.json")
    if anim:
        st_lottie(anim, height=200, key="welcome_anim")
    
    with st.form("user_info"):
        st.subheader("Let's get started")
        name = st.text_input("What's your name?")
        age = st.slider("Your age", 10, 100, 25)
        gender = st.selectbox("Your gender", ["Female", "Male", "Non-binary", "Prefer not to say"])
        lifestyle = st.selectbox("How would you describe your lifestyle?", 
                              ["Mostly indoors", "Balanced", "Very active outdoors"])
        
        if st.form_submit_button("Continue to Mood Check"):
            if name:
                st.session_state.name = name
                st.session_state.age = age
                st.session_state.gender = gender
                st.session_state.lifestyle = lifestyle
                st.session_state.page = pages[1]
                st.rerun()
            else:
                st.warning("Please enter your name")

# ========= Page 2: Mood Check ========
elif st.session_state.page == "📊 Mood Check":
    st.title("🌼 Mood Check-In")
    st.write(f"Hello, {st.session_state.get('name', 'friend')}! Let's see how you're doing today.")
    
    # Check if mood analysis has been done
    if st.session_state.mood_analyzed:
        # Get values from session state
        mood = st.session_state.mood_data["mood"]
        mood_score = st.session_state.mood_data["mood_score"]
        risk = st.session_state.mood_data["risk"]
        mood_color = st.session_state.mood_data["mood_color"]
        
        st.success("Analysis complete!")
        
        # Display results in cards
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="result-card" style="border-left-color: {mood_color}">
                <h3 style="color:{mood_color}">Your Mood</h3>
                <p style="font-size:24px; margin-bottom:0;">{mood}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="result-card">
                <h3 style="color:{accent_color}">Wellness Score</h3>
                <p style="font-size:24px; margin-bottom:0;">{mood_score:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="result-card" style="border-left-color: {mood_color}">
                <h3 style="color:{mood_color}">Burnout Risk</h3>
                <p style="font-size:24px; margin-bottom:0;">{risk}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Show appropriate animation
        anim_urls = {
            "Low": "https://assets4.lottiefiles.com/packages/lf20_yo4lqexz.json",
            "Moderate": "https://assets1.lottiefiles.com/packages/lf20_yo4lqexz.json",
            "High": "https://assets3.lottiefiles.com/packages/lf20_yo4lqexz.json"
        }
        anim = load_lottie_url(anim_urls.get(risk, anim_urls["Moderate"]))
        if anim:
            st_lottie(anim, height=150, key="mood_anim")
        
        # Add navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("View Wellness Suggestions", use_container_width=True):
                st.session_state.page = "Wellness Guide"
                st.rerun()
        with col2:
            if st.button("Do Another Check-In", use_container_width=True):
                st.session_state.mood_analyzed = False
                st.rerun()
    
    # Mood check form (only show if not analyzed or doing another check-in)
    if not st.session_state.mood_analyzed:
        with st.form("mood_form"):
            st.subheader("Daily Reflection")
            journal_entry = st.text_area(
                "How are you feeling today? What's on your mind?",
                height=150,
                value=st.session_state.mood_data["journal_entry"]
            )
            
            st.subheader("Lifestyle Factors")
            col1, col2 = st.columns(2)
            with col1:
                sleep_hours = st.slider(
                    "😴 Hours slept",
                    0, 12, 
                    st.session_state.mood_data["sleep_hours"]
                )
                screen_time = st.slider(
                    "📱 Screen time (hours)",
                    0, 16,
                    st.session_state.mood_data["screen_time"]
                )
            with col2:
                outdoor_time = st.slider(
                    "🌳 Time in nature (minutes)",
                    0, 240,
                    st.session_state.mood_data["outdoor_time"]
                )
                exercise = st.selectbox(
                    "🏃 Movement today",
                    ["None", "Light", "Moderate", "Intense"],
                    index=["None", "Light", "Moderate", "Intense"].index(st.session_state.mood_data["exercise"])
                )
            
            if st.form_submit_button("Analyze My Mood"):
                if journal_entry.strip():
                    # Sentiment analysis
                    polarity = TextBlob(journal_entry).sentiment.polarity
                    
                    # Calculate scores
                    sleep_score = min(sleep_hours / 8, 1.0)
                    screen_score = 1 - min(screen_time / 10, 1.0)
                    exercise_score = {"None": 0, "Light": 0.3, "Moderate": 0.7, "Intense": 1.0}[exercise]
                    nature_score = min(outdoor_time / 120, 1.0)
                    
                    # Weighted mood score
                    mood_score = (
                        0.4 * polarity +  # Journal sentiment
                        0.2 * sleep_score +
                        0.15 * nature_score +
                        0.15 * exercise_score -
                        0.1 * (1 - screen_score)
                    )
                    
                    # Determine mood and risk level
                    if mood_score > 0.4:
                        mood = "Blooming"
                        risk = "Low"
                        mood_color = accent_color
                    elif mood_score > 0.1:
                        mood = "Balanced(Work on youself dude!)"
                        risk = "Moderate"
                        mood_color = "#FFC107"  # Yellow
                    else:
                        mood = "Needs Care"
                        risk = "High"
                        mood_color = warning_color
                    
                    # Store results
                    st.session_state.mood_data = {
                        "mood": mood,
                        "mood_score": mood_score,
                        "risk": risk,
                        "mood_color": mood_color,
                        "journal_entry": journal_entry,
                        "sleep_hours": sleep_hours,
                        "screen_time": screen_time,
                        "outdoor_time": outdoor_time,
                        "exercise": exercise
                    }
                    st.session_state.mood_analyzed = True
                    
                    # Rerun to show results
                    st.rerun()
                else:
                    st.warning("Please share how you're feeling to get your mood analysis")

# ========= Page 3: Wellness Guide ========
elif st.session_state.page == "Wellness Guide":
    st.title("Personalized Wellness Guide")
    
    # Get user data from session state with proper defaults
    name = st.session_state.get("name", "friend")
    risk = st.session_state.mood_data.get("risk", "Moderate")
    gender = st.session_state.get("gender", "Prefer not to say")
    
    # Header with animation
    anim = load_lottie_url("https://assets1.lottiefiles.com/packages/lf20_yo4lqexz.json")
    if anim:
        st_lottie(anim, height=120, key="guide_header")
    
    # Burnout quiz for high risk users
    if risk == "High":
        if "quiz_complete" not in st.session_state or not st.session_state.quiz_complete:
            st.markdown(f"""
            <div class="warning-card">
                <h3>Wellness Check-In Quiz</h3>
                <p>Let's understand what areas need attention, {name}.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Initialize quiz answers if not exists
            if "quiz_answers" not in st.session_state:
                st.session_state.quiz_answers = {
                    "energy": "Normal",
                    "sleep": "Restful", 
                    "concentration": "Normal",
                    "motivation": "Normal",
                    "stress": "Manageable"
                }
            
            # Quiz questions
            questions = [
                ("1. How has your energy level been lately?", "energy", ["Normal", "Somewhat low", "Very low"]),
                ("2. How has your sleep been?", "sleep", ["Restful", "Occasionally restless", "Frequently disrupted"]),
                ("3. How is your ability to concentrate?", "concentration", ["Normal", "Somewhat difficult", "Very difficult"]),
                ("4. How is your motivation for daily activities?", "motivation", ["Normal", "Somewhat reduced", "Very reduced"]),
                ("5. How would you describe your stress levels?", "stress", ["Manageable", "Sometimes overwhelming", "Constantly overwhelming"])
            ]
            
            # Display quiz questions
            for q_text, q_key, options in questions:
                st.write(q_text)
                current_value = st.session_state.quiz_answers.get(q_key, options[0])
                selected = st.radio(
                    q_text,
                    options,
                    index=options.index(current_value),
                    key=f"quiz_{q_key}",
                    label_visibility="collapsed"
                )
                st.session_state.quiz_answers[q_key] = selected
            
            if st.button("Get My Recommendations"):
                st.session_state.quiz_complete = True
                st.rerun()
        
        else:  # Quiz completed - show recommendations
            # Analyze quiz results
            score_mapping = {
                "Normal": 0, "Restful": 0, "Manageable": 0,
                "Somewhat low": 1, "Occasionally restless": 1, "Somewhat difficult": 1, 
                "Somewhat reduced": 1, "Sometimes overwhelming": 1,
                "Very low": 2, "Frequently disrupted": 2, "Very difficult": 2,
                "Very reduced": 2, "Constantly overwhelming": 2
            }
            
            total_score = sum(score_mapping[ans] for ans in st.session_state.quiz_answers.values())
            
            # Determine recommendation level
            if total_score >= 8:
                recommendation_level = "professional"
            elif total_score >= 5:
                recommendation_level = "intensive_self_care"
            else:
                recommendation_level = "self_care"
            
            # Show recommendations
            st.markdown(f"""
            <div class="warning-card">
                <h3>🌿 Your Personalized Recovery Plan</h3>
                <p>Based on your responses, here's what we recommend:</p>
            </div>
            """, unsafe_allow_html=True)
            
            # [Rest of your recommendation code remains the same...]
    
    # [Rest of your Wellness Guide code for Moderate and Low risk remains the same...]
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 Back to Mood Check", use_container_width=True):
            st.session_state.page = "📊 Mood Check"
            st.rerun()
    with col2:
        if st.button("💌 Give Feedback", use_container_width=True):
            st.session_state.page = "📝 Feedback"
            st.rerun()


# ========= Page 4: Feedback ========
elif st.session_state.page == "📝 Feedback":
    st.title("💌 Share Your Thoughts")
    
    anim = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_tutvdkg0.json")
    if anim:
        st_lottie(anim, height=150, key="feedback_anim")
    
    with st.form("feedback_form"):
        st.markdown(f"""
        <div class="result-card">
            <p>Your feedback helps us grow and improve NatureMind.</p>
        </div>
        """, unsafe_allow_html=True)
        
        rating = st.slider("How would you rate your experience?", 1, 5, 4)
        feedback = st.text_area("What did you like or what could be improved?")
        
        if st.form_submit_button("Submit Feedback"):
            with open("data/feedback.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    st.session_state.get("name", "Anonymous"),
                    datetime.now().strftime("%Y-%m-%d"),
                    rating,
                    feedback
                ])
            
            st.success("Thank you for your feedback! 🌸")
            
            confetti_anim = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_obhph3sh.json")
            if confetti_anim:
                st_lottie(confetti_anim, height=200, key="confetti")
