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
openai.api_key = st.secrets["OPENAI_API_KEY"]

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

def generate_chat_response(prompt):
    """Generate chatbot response using OpenAI"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly, nature-inspired wellness assistant named Terra. You speak in warm, compassionate tones with occasional plant/animal metaphors. Keep responses under 3 sentences."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I'm having trouble connecting right now. Please try again later. ({str(e)})"

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
pages = ["🌱 Welcome", "📊 Mood Check", "🌿 Wellness Guide", "💬 Terra Chat", "📝 Feedback"]

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
                st.session_state.page = "🌿 Wellness Guide"
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
                        mood = "Thriving 🌸"
                        risk = "Low"
                        mood_color = accent_color
                    elif mood_score > 0.1:
                        mood = "Balanced 🌿"
                        risk = "Moderate"
                        mood_color = "#FFC107"  # Yellow
                    else:
                        mood = "Needs Care 🍂"
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
elif st.session_state.page == "🌿 Wellness Guide":
    st.title("🌱 Personalized Wellness Guide")
    
    # Get user data
    name = st.session_state.get("name", "friend")
    risk = st.session_state.mood_data.get("risk", "Moderate")
    gender = st.session_state.get("gender", "Prefer not to say")
    
    # Header with animation
    anim = load_lottie_url("https://assets1.lottiefiles.com/packages/lf20_yo4lqexz.json")
    if anim:
        st_lottie(anim, height=120, key="guide_header")
    
    # Burnout quiz for high risk users
    if risk == "High" and "quiz_complete" not in st.session_state:
        st.markdown(f"""
        <div class="warning-card">
            <h3>🌻 Wellness Check-In Quiz</h3>
            <p>Let's understand what areas need attention, {name}.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quiz questions
        questions = [
            ("1. How has your energy level been lately?", "energy", ["Normal", "Somewhat low", "Very low"]),
            ("2. How has your sleep been?", "sleep", ["Restful", "Occasionally restless", "Frequently disrupted"]),
            ("3. How is your ability to concentrate?", "concentration", ["Normal", "Somewhat difficult", "Very difficult"]),
            ("4. How is your motivation for daily activities?", "motivation", ["Normal", "Somewhat reduced", "Very reduced"]),
            ("5. How would you describe your stress levels?", "stress", ["Manageable", "Sometimes overwhelming", "Constantly overwhelming"])
        ]
        
        # Initialize quiz answers if not exists
        if "quiz_answers" not in st.session_state:
            st.session_state.quiz_answers = {q[1]: None for q in questions}
        
        # Display quiz questions
        for q_text, q_key, options in questions:
            st.write(q_text)
            selected = st.radio(
                q_text,
                options,
                index=options.index(st.session_state.quiz_answers[q_key]) if st.session_state.quiz_answers[q_key] else 0,
                key=q_key,
                label_visibility="collapsed"
            )
            st.session_state.quiz_answers[q_key] = selected
        
        # Submit button
        if st.button("Get My Recommendations"):
            st.session_state.quiz_complete = True
            st.rerun()
    
    elif risk == "High" and "quiz_complete" in st.session_state:
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
        
        # Professional support recommendations
        if recommendation_level == "professional":
            st.markdown(f"""
            <div class="suggestion-card">
                <h4>🧠 Consider Professional Support</h4>
                <p>Your responses suggest you might benefit from professional support:</p>
                <ul>
                    <li>📞 <a href="tel:988" style="color:{accent_color};">988 Suicide & Crisis Lifeline</a></li>
                    <li>🌐 <a href="https://www.psychologytoday.com/" style="color:{accent_color};" target="_blank">Find a Therapist</a></li>
                    <li>📱 <a href="https://www.betterhelp.com/" style="color:{accent_color};" target="_blank">Online Therapy Options</a></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Recovery routine with gender-specific modifications
        st.markdown(f"""
        <div class="suggestion-card">
            <h4>🌱 Gentle Recovery Routine</h4>
            <p>Try this nurturing daily rhythm:</p>
        </div>
        """, unsafe_allow_html=True)
        
        if gender.lower() in ["female", "woman"]:
            recovery_routine = [
                {"time": "Morning", "activities": [
                    "🌅 Wake without alarm, stretch gently",
                    "🍵 Warm herbal tea with 5 min meditation",
                    "📝 Journal 3 things you're grateful for",
                    "💊 Consider magnesium supplement"
                ]},
                {"time": "Midday", "activities": [
                    "🚶‍♀️ Short walk in nature",
                    "🥑 Nourishing meal with protein & healthy fats",
                    "😴 20-min rest (no screens)",
                    "💧 Stay hydrated with electrolytes"
                ]},
                {"time": "Evening", "activities": [
                    "🧘‍♀️ Gentle yoga or stretching",
                    "📵 Screen-free time after dinner",
                    "🛀 Warm bath with Epsom salts",
                    "📖 Read something uplifting"
                ]}
            ]
        else:  # Default/male version
            recovery_routine = [
                {"time": "Morning", "activities": [
                    "🌅 Wake without alarm, stretch",
                    "🍵 Warm tea with deep breathing",
                    "📝 Write down 3 priorities",
                    "💊 Consider vitamin D supplement"
                ]},
                {"time": "Midday", "activities": [
                    "🚶‍♂️ Short walk outside",
                    "🥩 Protein-rich meal with veggies",
                    "😴 20-min power nap (no screens)",
                    "💧 Drink plenty of water"
                ]},
                {"time": "Evening", "activities": [
                    "🏋️‍♂️ Light resistance training",
                    "📵 Reduce screen time",
                    "🚿 Warm shower before bed",
                    "🎧 Listen to calming music"
                ]}
            ]
        
        # Display routine
        for part in recovery_routine:
            st.markdown(f"""
            <div style="background-color:{card_bg}; padding:12px; border-radius:8px; margin-bottom:12px;">
                <h5 style="color:{accent_color}; margin:0 0 8px 0;">{part['time']}</h5>
                <ul style="margin:0;">
                    {''.join([f"<li>{act}</li>" for act in part['activities']])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional resources
        st.markdown(f"""
        <div class="suggestion-card">
            <h4>🌼 Additional Resources</h4>
            <ul>
                <li>📖 <a href="https://www.mindful.org/" style="color:{accent_color};" target="_blank">Mindfulness Practices</a></li>
                <li>🎧 <a href="https://www.headspace.com/" style="color:{accent_color};" target="_blank">Guided Meditations</a></li>
                <li>🌳 <a href="https://www.nature.org/" style="color:{accent_color};" target="_blank">Find Nature Near You</a></li>
                {f'<li>👩‍⚕️ <a href="https://www.womenshealth.gov/" style="color:{accent_color};" target="_blank">Women\'s Health Resources</a></li>' if gender.lower() in ["female", "woman"] else ''}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Moderate risk recommendations
    elif risk == "Moderate":
        st.markdown(f"""
        <div class="suggestion-card">
            <h3>🌿 Balance Boosters</h3>
            <p>Here are some ways to maintain your equilibrium, {name}:</p>
            <ul>
                <li>🌅 Start your day with 5 minutes of sunlight</li>
                <li>💧 Stay hydrated - aim for 2L water daily</li>
                <li>📵 Create tech-free zones in your home</li>
                <li>🌱 Try "forest bathing" - slow walks in nature</li>
                {"<li>🌸 Track your menstrual cycle for patterns</li>" if gender.lower() in ["female", "woman"] else "<li>🏋️‍♂️ Incorporate strength training 2-3x/week</li>"}
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="suggestion-card">
            <h4>🌸 Sample Balanced Day</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Gender-specific daily routine
        if gender.lower() in ["female", "woman"]:
            balanced_routine = [
                {"time": "7:00 AM", "activity": "🌞 Gentle wake-up, sunlight exposure"},
                {"time": "7:30 AM", "activity": "🧘 Morning stretch or yoga"},
                {"time": "8:30 AM", "activity": "🍳 Protein-rich breakfast with healthy fats"},
                {"time": "9:00 AM", "activity": "📚 Focused work (90 min)"},
                {"time": "10:30 AM", "activity": "☕ Break with herbal tea"},
                {"time": "12:30 PM", "activity": "🥗 Lunch with leafy greens & lean protein"},
                {"time": "1:30 PM", "activity": "🚶‍♀️ 15-min walk outside"},
                {"time": "4:00 PM", "activity": "🏃‍♀️ Movement break (dance, walk, yoga)"},
                {"time": "6:30 PM", "activity": "🍲 Light dinner with veggies & whole grains"},
                {"time": "8:00 PM", "activity": "📖 Reading or creative hobby"},
                {"time": "9:30 PM", "activity": "🌙 Wind-down routine with calming tea"}
            ]
        else:
            balanced_routine = [
                {"time": "7:00 AM", "activity": "🌞 Morning sunlight exposure"},
                {"time": "7:30 AM", "activity": "🏋️‍♂️ Short bodyweight workout or stretch"},
                {"time": "8:30 AM", "activity": "🍳 High-protein breakfast with complex carbs"},
                {"time": "9:00 AM", "activity": "📚 Focused work (90 min)"},
                {"time": "10:30 AM", "activity": "☕ Break with green tea"},
                {"time": "12:30 PM", "activity": "🥩 Lunch with protein & vegetables"},
                {"time": "1:30 PM", "activity": "🚶‍♂️ 15-min walk outside"},
                {"time": "4:00 PM", "activity": "🏋️‍♂️ Strength training or cardio"},
                {"time": "6:30 PM", "activity": "🍗 Dinner with lean protein & veggies"},
                {"time": "8:00 PM", "activity": "🎧 Podcast or relaxing activity"},
                {"time": "9:30 PM", "activity": "🌙 Wind-down without screens"}
            ]
        
        for item in balanced_routine:
            st.markdown(f"""
            <div class="routine-item">
                <div class="routine-time">{item['time']}</div>
                <div class="routine-activity">{item['activity']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Low risk recommendations
    else:
        st.markdown(f"""
        <div class="suggestion-card">
            <h3>🌟 You're Thriving!</h3>
            <p>Your wellness is blossoming, {name}! Here's how to maintain it:</p>
            <ul>
                <li>🌻 Share your positive energy with others</li>
                <li>🌎 Explore new outdoor activities</li>
                <li>🙏 Keep a gratitude practice</li>
                <li>💞 Nurture your relationships</li>
                {"<li>🌸 Consider cycle syncing your activities</li>" if gender.lower() in ["female", "woman"] else "<li>🏆 Set new fitness goals</li>"}
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        anim = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_sk5h1kfn.json")
        if anim:
            st_lottie(anim, height=200, key="celebration_anim")
        
        st.markdown("""
        <div class="suggestion-card">
            <h4>🌼 Growth Opportunities</h4>
            <p>While you're doing well, consider these wellness boosters:</p>
            <ul>
                <li>Try a digital detox weekend</li>
                <li>Start a nature journal</li>
                <li>Volunteer in your community</li>
                <li>Learn about forest therapy</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔙 Back to Mood Check", use_container_width=True):
            st.session_state.page = "📊 Mood Check"
            st.rerun()
    with col2:
        if st.button("💬 Chat with Terra", use_container_width=True):
            st.session_state.page = "💬 Terra Chat"
            st.rerun()

# ========= Page 4: Chatbot ========
elif st.session_state.page == "💬 Terra Chat":
    st.title("💬 Wellness Companion")
    
    # Gender toggle
    st.markdown(f"""
    <div class="gender-tabs">
        <div class="gender-tab {'active' if st.session_state.chat_gender == 'female' else ''}" onclick="window.streamlitSessionState.set('chat_gender','female');window.streamlitSessionState.set('rerun',true)">🌸 For Her</div>
        <div class="gender-tab {'active' if st.session_state.chat_gender == 'male' else ''}" onclick="window.streamlitSessionState.set('chat_gender','male');window.streamlitSessionState.set('rerun',true)">🌿 For Him</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show appropriate content based on gender
    if st.session_state.chat_gender == "female":
        st.markdown(f"""
        <div class="result-card">
            <p style="font-size: 16px;">Hello {st.session_state.get('name', 'friend')}! Let's explore wellness topics that matter to you. 
            Select a question or ask your own.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Menstrual cycle phase selector
        cycle_phase = st.selectbox(
            "Select your menstrual cycle phase (optional)",
            ["Not applicable", "Menstruation (Days 1-5)", "Follicular (Days 6-14)", 
             "Ovulation (Days 15-17)", "Luteal (Days 18-28)"],
            index=0
        )
        
        # Common questions for women
        st.subheader("Common Wellness Questions")
        
        tabs = st.tabs(["🌱 General", "🍵 Nutrition", "😴 Sleep", "🧘 Mindfulness", "🩸 Cycle Health"])
        
        with tabs[0]:
            st.markdown("""
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How can I boost my energy naturally during the day?');window.streamlitSessionState.set('rerun',true)">
                <h4>How can I boost my energy naturally during the day?</h4>
                <p>Discover natural ways to combat fatigue</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What are some quick stress-relief techniques I can do at work?');window.streamlitSessionState.set('rerun',true)">
                <h4>What are some quick stress-relief techniques I can do at work?</h4>
                <p>Office-friendly relaxation methods</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How can I create a better morning routine?');window.streamlitSessionState.set('rerun',true)">
                <h4>How can I create a better morning routine?</h4>
                <p>Start your day with intention</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[1]:
            st.markdown("""
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What foods help with hormonal balance?');window.streamlitSessionState.set('rerun',true)">
                <h4>What foods help with hormonal balance?</h4>
                <p>Nutrition for cycle harmony</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','Are there specific nutrients I need more of during my period?');window.streamlitSessionState.set('rerun',true)">
                <h4>Are there specific nutrients I need more of during my period?</h4>
                <p>Eating for menstrual health</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What are good snacks for PCOS management?');window.streamlitSessionState.set('rerun',true)">
                <h4>What are good snacks for PCOS management?</h4>
                <p>Blood sugar balancing ideas</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[2]:
            st.markdown("""
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','Why do I feel more tired before my period?');window.streamlitSessionState.set('rerun',true)">
                <h4>Why do I feel more tired before my period?</h4>
                <p>Understanding progesterone's effects</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How can I sleep better during PMS?');window.streamlitSessionState.set('rerun',true)">
                <h4>How can I sleep better during PMS?</h4>
                <p>Tips for the luteal phase</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What\\'s the ideal sleep temperature for women?');window.streamlitSessionState.set('rerun',true)">
                <h4>What's the ideal sleep temperature for women?</h4>
                <p>Body temperature regulation</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[3]:
            st.markdown("""
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How does meditation affect female hormones?');window.streamlitSessionState.set('rerun',true)">
                <h4>How does meditation affect female hormones?</h4>
                <p>The mind-body connection</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What type of yoga is best for each cycle phase?');window.streamlitSessionState.set('rerun',true)">
                <h4>What type of yoga is best for each cycle phase?</h4>
                <p>Cycle-syncing movement</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How can I practice self-love during menstruation?');window.streamlitSessionState.set('rerun',true)">
                <h4>How can I practice self-love during menstruation?</h4>
                <p>Honoring your body's rhythm</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[4]:
            if cycle_phase != "Not applicable":
                st.markdown(f"""
                <div class="cycle-phase">
                    {cycle_phase} phase selected
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How can I support my body during this phase?');window.streamlitSessionState.set('rerun',true)">
                    <h4>How can I support my body during this phase?</h4>
                    <p>Phase-specific wellness tips</p>
                </div>
                <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What foods are most nourishing right now?');window.streamlitSessionState.set('rerun',true)">
                    <h4>What foods are most nourishing right now?</h4>
                    <p>Nutritional needs for this phase</p>
                </div>
                <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What type of exercise is best during this phase?');window.streamlitSessionState.set('rerun',true)">
                    <h4>What type of exercise is best during this phase?</h4>
                    <p>Movement recommendations</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How can I track my cycle for better wellness?');window.streamlitSessionState.set('rerun',true)">
                    <h4>How can I track my cycle for better wellness?</h4>
                    <p>Understanding your patterns</p>
                </div>
                <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What are signs of hormonal imbalance to watch for?');window.streamlitSessionState.set('rerun',true)">
                    <h4>What are signs of hormonal imbalance to watch for?</h4>
                    <p>When to seek help</p>
                </div>
                <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How does stress affect menstrual health?');window.streamlitSessionState.set('rerun',true)">
                    <h4>How does stress affect menstrual health?</h4>
                    <p>The cortisol connection</p>
                </div>
                """, unsafe_allow_html=True)
    
    else:  # Male content
        st.markdown(f"""
        <div class="result-card">
            <p style="font-size: 16px;">Hello {st.session_state.get('name', 'friend')}! Let's explore wellness topics that matter to you. 
            Select a question or ask your own.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Common questions for men
        st.subheader("Common Wellness Questions")
        
        tabs = st.tabs(["🌱 General", "🍗 Nutrition", "💪 Fitness", "😴 Sleep", "🧠 Mental Health"])
        
        with tabs[0]:
            st.markdown("""
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How can I improve my focus and productivity naturally?');window.streamlitSessionState.set('rerun',true)">
                <h4>How can I improve my focus and productivity naturally?</h4>
                <p>Beyond caffeine solutions</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What are signs of testosterone imbalance?');window.streamlitSessionState.set('rerun',true)">
                <h4>What are signs of testosterone imbalance?</h4>
                <p>Hormonal health awareness</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How can I build a sustainable morning routine?');window.streamlitSessionState.set('rerun',true)">
                <h4>How can I build a sustainable morning routine?</h4>
                <p>Starting strong</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[1]:
            st.markdown("""
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What nutrients are most important for male health?');window.streamlitSessionState.set('rerun',true)">
                <h4>What nutrients are most important for male health?</h4>
                <p>Beyond protein needs</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How does alcohol affect male hormones?');window.streamlitSessionState.set('rerun',true)">
                <h4>How does alcohol affect male hormones?</h4>
                <p>The testosterone connection</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What are good plant-based protein sources?');window.streamlitSessionState.set('rerun',true)">
                <h4>What are good plant-based protein sources?</h4>
                <p>Vegetarian options</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[2]:
            st.markdown("""
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How often should I take rest days?');window.streamlitSessionState.set('rerun',true)">
                <h4>How often should I take rest days?</h4>
                <p>Recovery strategies</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What exercises help prevent common male injuries?');window.streamlitSessionState.set('rerun',true)">
                <h4>What exercises help prevent common male injuries?</h4>
                <p>Prehab routines</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How can I maintain muscle as I age?');window.streamlitSessionState.set('rerun',true)">
                <h4>How can I maintain muscle as I age?</h4>
                <p>Strength preservation</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[3]:
            st.markdown("""
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','Why do men often sleep hotter than women?');window.streamlitSessionState.set('rerun',true)">
                <h4>Why do men often sleep hotter than women?</h4>
                <p>Body temperature regulation</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How does sleep affect testosterone levels?');window.streamlitSessionState.set('rerun',true)">
                <h4>How does sleep affect testosterone levels?</h4>
                <p>The hormone-sleep connection</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What\\'s the best sleep position for back health?');window.streamlitSessionState.set('rerun',true)">
                <h4>What's the best sleep position for back health?</h4>
                <p>Spinal alignment</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[4]:
            st.markdown("""
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How can men recognize signs of depression?');window.streamlitSessionState.set('rerun',true)">
                <h4>How can men recognize signs of depression?</h4>
                <p>Beyond "feeling sad"</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','What are healthy ways to manage stress?');window.streamlitSessionState.set('rerun',true)">
                <h4>What are healthy ways to manage stress?</h4>
                <p>Beyond avoidance</p>
            </div>
            <div class="question-card" onclick="window.streamlitSessionState.set('chat_input','How can I improve emotional communication?');window.streamlitSessionState.set('rerun',true)">
                <h4>How can I improve emotional communication?</h4>
                <p>Building vulnerability</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat interface
    st.markdown("---")
    st.subheader("Ask Terra Anything")
    
    # Initialize chat history if not exists
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": f"Hi {st.session_state.get('name', 'friend')}! I'm Terra, your wellness guide. How can I help you today?"}
        ]
    
    # Display chat messages
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <p><strong>You:</strong> {message["content"]}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <p><strong>Terra:</strong> {message["content"]}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Type your wellness question here...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        try:
            # Generate response
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are Terra, a friendly wellness assistant. You specialize in {st.session_state.chat_gender}-specific health. Use metaphors from nature and keep responses under 3 sentences."},
                    *[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.chat_history]
                ],
                temperature=0.7,
            )
            
            # Get the assistant's reply
            assistant_reply = response.choices[0].message.content
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
            
            # Rerun to update the chat display
            st.rerun()
            
        except Exception as e:
            error_msg = f"I'm having trouble connecting right now. Please try again later. (Error: {str(e)})"
            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            st.rerun()
    
    # Quick suggestions
    st.markdown("""
    <div class="suggestion-card">
        <h4>💡 Quick Wellness Tips</h4>
        <ul>
            <li>Drink water first thing in the morning</li>
            <li>Take 5 deep breaths before meals</li>
            <li>Stand up and stretch every hour</li>
            <li>Write down 3 good things before bed</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ========= Page 5: Feedback ========
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
