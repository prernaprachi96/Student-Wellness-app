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
    st.title(f"🌿 Personalized Wellness Guide for {st.session_state.get('name', 'you')}")
    
    # Get user data
    name = st.session_state.get("name", "friend")
    risk = st.session_state.mood_data.get("risk", "Moderate")
    gender = st.session_state.get("gender", "Prefer not to say")
    age = st.session_state.get("age", 30)
    lifestyle = st.session_state.get("lifestyle", "Balanced")
    
    # Header with animation
    anim = load_lottie_url("https://assets1.lottiefiles.com/packages/lf20_yo4lqexz.json")
    if anim:
        st_lottie(anim, height=120, key="guide_header")
    
    # Wellness Score Dashboard
    st.markdown(f"""
    <div class="result-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3>Your Wellness Dashboard</h3>
                <p>Risk Level: <strong>{risk}</strong></p>
                <p>Age: <strong>{age}</strong> | Lifestyle: <strong>{lifestyle}</strong></p>
            </div>
            <div style="text-align: right;">
                <p style="font-size: 24px; margin: 0; color: {st.session_state.mood_data['mood_color']}">
                    {st.session_state.mood_data['mood_score']:.1f}/10
                </p>
                <p>Wellness Score</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab system for different wellness aspects
    tab1, tab2, tab3, tab4 = st.tabs(["🌱 Daily Routine", "💤 Sleep", "🍎 Nutrition", "🧘 Mindfulness"])
    
    with tab1:
        st.subheader("Personalized Daily Routine")
        
        # Time-based routine suggestions
        st.markdown("""
        <div class="suggestion-card">
            <h4>⏰ Suggested Daily Schedule</h4>
            <p>Based on your risk level and lifestyle, here's an optimal daily routine:</p>
        </div>
        """, unsafe_allow_html=True)
        
        if risk == "High":
            routine = [
                {"time": "7:00 AM", "activity": "Gentle wake-up with sunlight exposure"},
                {"time": "7:15 AM", "activity": "5-minute stretching or yoga"},
                {"time": "8:00 AM", "activity": "Balanced breakfast with protein"},
                {"time": "12:00 PM", "activity": "Short walk in nature (10-15 min)"},
                {"time": "3:00 PM", "activity": "Mindfulness break (5 min deep breathing)"},
                {"time": "6:30 PM", "activity": "Light dinner with vegetables"},
                {"time": "8:30 PM", "activity": "Digital detox (no screens)"},
                {"time": "9:30 PM", "activity": "Relaxing bedtime routine"}
            ]
        elif risk == "Moderate":
            routine = [
                {"time": "6:30 AM", "activity": "Morning sunlight + hydration"},
                {"time": "7:00 AM", "activity": "15-minute movement (yoga/walk)"},
                {"time": "8:00 AM", "activity": "Protein-rich breakfast"},
                {"time": "12:30 PM", "activity": "Balanced lunch with greens"},
                {"time": "3:00 PM", "activity": "Quick stretch or walk"},
                {"time": "6:00 PM", "activity": "Exercise (30-45 min)"},
                {"time": "8:00 PM", "activity": "Screen-free wind down"},
                {"time": "10:00 PM", "activity": "Bedtime routine"}
            ]
        else:
            routine = [
                {"time": "6:00 AM", "activity": "Morning workout or run"},
                {"time": "7:00 AM", "activity": "Healthy breakfast with complex carbs"},
                {"time": "12:00 PM", "activity": "Nutrient-dense lunch"},
                {"time": "5:00 PM", "activity": "Intensive exercise session"},
                {"time": "7:00 PM", "activity": "Light, early dinner"},
                {"time": "9:00 PM", "activity": "Reading or creative activity"},
                {"time": "10:30 PM", "activity": "Relaxation before sleep"}
            ]
        
        for item in routine:
            st.markdown(f"""
            <div class="routine-item">
                <div class="routine-time">{item['time']}</div>
                <div class="routine-activity">{item['activity']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Habit tracker
        st.markdown("""
        <div class="suggestion-card">
            <h4>📊 Weekly Habit Tracker</h4>
            <p>Track these wellness habits throughout your week:</p>
        </div>
        """, unsafe_allow_html=True)
        
        habits = ["Morning sunlight", "Hydration (8 glasses)", "30-min exercise", 
                 "Healthy meals", "Digital detox", "Quality sleep", "Mindfulness"]
        
        if 'habit_tracker' not in st.session_state:
            st.session_state.habit_tracker = {habit: False for habit in habits}
        
        cols = st.columns(3)
        for i, habit in enumerate(habits):
            with cols[i%3]:
                st.session_state.habit_tracker[habit] = st.checkbox(
                    habit, 
                    value=st.session_state.habit_tracker[habit],
                    key=f"habit_{i}"
                )
    
    with tab2:
        st.subheader("Sleep Optimization")
        
        # Sleep quality assessment
        with st.expander("🔍 Assess Your Sleep Quality"):
            sleep_quality = st.slider("How would you rate your sleep quality?", 1, 5, 3)
            sleep_duration = st.number_input("Average hours of sleep:", min_value=4, max_value=12, value=7)
            sleep_issues = st.multiselect(
                "Do you experience any of these?",
                ["Difficulty falling asleep", "Waking up at night", "Not feeling rested", "Snoring"]
            )
            
            if st.button("Get Sleep Recommendations"):
                if sleep_quality <= 2 or sleep_duration < 6 or sleep_issues:
                    st.warning("Your sleep needs improvement. Try these:")
                    st.markdown("""
                    - Maintain consistent sleep schedule
                    - Avoid screens 1 hour before bed
                    - Keep bedroom cool and dark
                    - Limit caffeine after 2pm
                    - Try relaxation techniques before bed
                    """)
                else:
                    st.success("Your sleep habits look good! Keep it up.")
        
        # Sleep tracker visualization
        st.markdown("""
        <div class="suggestion-card">
            <h4>📈 Your Sleep Patterns</h4>
        </div>
        """, unsafe_allow_html=True)
        
        sleep_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Hours": [7, 6.5, 7.5, 6, 7, 8, 8.5],
            "Quality": [3, 2, 4, 3, 3, 4, 5]
        })
        
        chart = alt.Chart(sleep_data).mark_bar().encode(
            x='Day',
            y='Hours',
            color=alt.condition(
                alt.datum.Hours >= 7,
                alt.value(accent_color),
                alt.value(warning_color)
        ).properties(width=600)
        st.altair_chart(chart, use_container_width=True)
    
    with tab3:
        st.subheader("Nutrition Guidance")
        
        # Personalized nutrition plan
        st.markdown(f"""
        <div class="suggestion-card">
            <h4>🍽️ {name}'s Nutrition Plan</h4>
            <p>Based on your age, gender and activity level:</p>
        </div>
        """, unsafe_allow_html=True)
        
        if gender.lower() in ["female", "woman"]:
            st.markdown("""
            - **Breakfast:** Greek yogurt with berries and nuts
            - **Lunch:** Salmon salad with leafy greens and quinoa
            - **Dinner:** Grilled chicken with roasted vegetables
            - **Snacks:** Hummus with veggies, hard-boiled eggs
            - **Hydration:** 2L water + herbal teas
            """)
        else:
            st.markdown("""
            - **Breakfast:** Oatmeal with protein powder and banana
            - **Lunch:** Chicken rice bowl with mixed vegetables
            - **Dinner:** Lean beef with sweet potato and broccoli
            - **Snacks:** Protein shake, mixed nuts
            - **Hydration:** 3L water + green tea
            """)
        
        # Meal planner
        with st.expander("📅 Weekly Meal Planner"):
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Weekend"]
            meal_data = []
            
            for day in days:
                cols = st.columns(3)
                with cols[0]:
                    breakfast = st.text_input(f"Breakfast - {day}", "Oatmeal with fruits")
                with cols[1]:
                    lunch = st.text_input(f"Lunch - {day}", "Grilled chicken salad")
                with cols[2]:
                    dinner = st.text_input(f"Dinner - {day}", "Fish with vegetables")
                meal_data.append({"Day": day, "Breakfast": breakfast, "Lunch": lunch, "Dinner": dinner})
            
            if st.button("Save Meal Plan"):
                st.session_state.meal_plan = meal_data
                st.success("Meal plan saved!")
    
    with tab4:
        st.subheader("Mindfulness & Stress Management")
        
        # Stress assessment
        st.markdown("""
        <div class="suggestion-card">
            <h4>😌 Stress Level Assessment</h4>
        </div>
        """, unsafe_allow_html=True)
        
        stress_level = st.slider("Rate your current stress level (1-10)", 1, 10, 5)
        
        if stress_level >= 7:
            st.warning("High stress detected. Try these techniques:")
            st.markdown("""
            - 5-minute box breathing exercise
            - Progressive muscle relaxation
            - Nature walk without devices
            - Journaling for 10 minutes
            - Guided meditation (try Headspace or Calm)
            """)
        else:
            st.success("Your stress levels seem manageable. Maintenance tips:")
            st.markdown("""
            - Daily 5-minute mindfulness practice
            - Gratitude journaling
            - Regular exercise
            - Social connections
            - Hobby time
            """)
        
        # Guided meditation player
        st.markdown("""
        <div class="suggestion-card">
            <h4>🎧 Quick Meditation</h4>
            <p>Take a 3-minute break with this breathing exercise:</p>
        </div>
        """, unsafe_allow_html=True)
        
        meditation_type = st.radio(
            "Choose meditation type:",
            ["Box Breathing", "Body Scan", "Mindfulness", "Loving-Kindness"],
            horizontal=True
        )
        
        if st.button("Start Guided Meditation"):
            st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")  # Placeholder
            
            with st.expander("Meditation Instructions"):
                if meditation_type == "Box Breathing":
                    st.write("""
                    1. Inhale for 4 seconds
                    2. Hold for 4 seconds
                    3. Exhale for 4 seconds
                    4. Hold for 4 seconds
                    5. Repeat for 3 minutes
                    """)
                elif meditation_type == "Body Scan":
                    st.write("""
                    1. Focus on your toes, notice sensations
                    2. Slowly move attention up through your body
                    3. Notice areas of tension without judgment
                    4. Breathe into tense areas
                    """)
    
    # Progress tracking
    st.markdown("""
    <div class="suggestion-card">
        <h4>📊 Your Wellness Progress</h4>
    </div>
    """, unsafe_allow_html=True)
    
    progress_cols = st.columns(3)
    with progress_cols[0]:
        st.metric("Current Streak", "5 days", "2 days")
    with progress_cols[1]:
        st.metric("Weekly Goals", "3/7 completed")
    with progress_cols[2]:
        st.metric("Improvement", "+12%", "4% from last week")
    
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
