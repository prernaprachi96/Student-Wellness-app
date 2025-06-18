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

st.set_page_config(page_title="Mood Predictor App", layout="centered", page_icon="🌿")

# ---------- Dark Mode (only) Theming ----------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# default dark mode on
mode = option_menu(
    menu_title=None,
    options=["🌙 Dark Mode"],  # Removed Light mode option as requested
    orientation="horizontal",
    icons=["moon"],
    default_index=0,
    key="mode_option",
)

st.session_state.dark_mode = True  # Always dark mode now

# Apply CSS for dark mode & custom colors
bg_color = "#121212"
text_color = "white"
card_bg = "#1e1e1e"
button_bg = "#BB86FC"
button_text = "#121212"
accent_color = "#03DAC6"

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
        background-color: #3700B3 !important;
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
    .suggestion-card {{
        background-color: {card_bg};
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 4px solid {accent_color};
    }}
    .quote-card {{
        background-color: {card_bg};
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        font-style: italic;
        border-left: 4px solid {button_bg};
    }}
    .routine-card {{
        background-color: {card_bg};
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #FF7597;
    }}
    .video-card {{
        background-color: {card_bg};
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #4CC9F0;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Pages list - use exact strings everywhere
pages = ["👤 User Info", "📊 Dashboard", "✨ Wellness Guide", "📝 Feedback"]

# Initialize session state for current page
if 'page' not in st.session_state or st.session_state.page not in pages:
    st.session_state.page = pages[0]

# Sidebar Navigation (locked step-by-step)
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

# ========== Page 1: User Info ==========
if st.session_state.page == "👤 User Info":
    st.title("🌱 Welcome to MindGarden")
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

            # Save user info
            with open("data/user_info.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([name, age, gender])

            go_next()
        else:
            st.warning("Please enter your name to continue.")

# ========== Page 2: Dashboard ==========
elif st.session_state.page == "📊 Dashboard":
    st.title("🌼 Mood Dashboard")
    st.write(f"Welcome back, {st.session_state.get('name', 'User')}! Let's check in with yourself today.")
    st.markdown("### ✏️ Your Daily Reflection")
    journal_entry = st.text_area("Write your thoughts, feelings, or anything on your mind:", height=200)

    sleep_hours = st.slider("😴 How many hours did you sleep last night?", 0, 12, 6)
    screen_time = st.slider("📱 Daily Screen Time (in hours)", 0, 16, 6)
    workout_done = st.selectbox("🏋️ Did you move your body today?", ["Yes", "No"])

    if 'mood_analyzed' not in st.session_state:
        st.session_state.mood_analyzed = False

    if st.button("🌻 Analyze My Mood"):
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
                mood = "Blossoming 🌸"
                risk = "Low"
                mood_icon = "🌞"
                mood_color = "#4CAF50"
            elif mood_score > 0.1:
                mood = "Balanced 🌿"
                risk = "Moderate"
                mood_icon = "🌤️"
                mood_color = "#FFC107"
            else:
                mood = "Needs Nourishment 🍂"
                risk = "High"
                mood_icon = "🌧️"
                mood_color = "#F44336"

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div style='background-color:{card_bg}; padding:15px; border-radius:10px; border-left:4px solid {mood_color}'>"
                            f"<h3 style='color:{mood_color}; margin-top:0;'>Your Mood</h3>"
                            f"<p style='font-size:24px; margin-bottom:0;'>{mood_icon} {mood}</p>"
                            "</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<div style='background-color:{card_bg}; padding:15px; border-radius:10px; border-left:4px solid {accent_color}'>"
                            f"<h3 style='color:{accent_color}; margin-top:0;'>Mood Score</h3>"
                            f"<p style='font-size:24px; margin-bottom:0;'>{mood_score:.2f}</p>"
                            "</div>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"<div style='background-color:{card_bg}; padding:15px; border-radius:10px; border-left:4px solid {button_bg}'>"
                            f"<h3 style='color:{button_bg}; margin-top:0;'>Wellness Level</h3>"
                            f"<p style='font-size:24px; margin-bottom:0;'>{risk}</p>"
                            "</div>", unsafe_allow_html=True)

            st.session_state.avg_mood = mood_score
            st.session_state.risk = risk
            st.session_state.mood_analyzed = True

            if risk == "Low":
                flower_animation = load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_touohxv0.json")
                if flower_animation:
                    st_lottie(flower_animation, height=150, key="flower_animation")
                else:
                    st.warning("⚠️ Flower animation failed to load.")
        else:
            st.warning("Please enter something in your journal to analyze.")

    if st.session_state.mood_analyzed:
        if st.button("Continue to Wellness Guide"):
            go_next()

# ========== Page 3: Wellness Guide ==========
elif st.session_state.page == "✨ Wellness Guide":
    st.title("🌿 Your Personalized Wellness Guide")
    
    risk = st.session_state.get('risk', 'Moderate')
    name = st.session_state.get('name', 'Friend')
    
    # Beautiful header with animation
    header_col1, header_col2 = st.columns([3,1])
    with header_col1:
        st.markdown(f"### 🌈 Hello {name}, here's your wellness guide")
    with header_col2:
        wellness_anim = load_lottie_url("https://assets1.lottiefiles.com/packages/lf20_yo4lqexz.json")
        if wellness_anim:
            st_lottie(wellness_anim, height=80, key="wellness_header")

    # Motivational quote card
    quotes = {
        "Low": [
            "Your positive energy is contagious! Keep shining your light ✨",
            "Happiness is not something ready-made. It comes from your own actions. - Dalai Lama",
            "You're doing amazing! Remember to celebrate your wins, big and small 🎉"
        ],
        "Moderate": [
            "This too shall pass. Be gentle with yourself today 🌿",
            "You don't have to be perfect to be worthy of love and belonging. - Brené Brown",
            "Small steps still move you forward. Celebrate your progress, not perfection 🌱"
        ],
        "High": [
            "Even the darkest night will end and the sun will rise. - Victor Hugo",
            "You are stronger than you think. This feeling is temporary 🌤️",
            "Be kind to yourself. Growth is a process, not a destination 🌻"
        ]
    }
    
    selected_quote = quotes[risk][0]  # You could randomize this
    st.markdown(f"""
    <div class="quote-card">
        <p style="font-size:18px; margin-bottom:0;">{selected_quote}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk-specific suggestions
    if risk == "Moderate":
        st.markdown("""
        <div class="suggestion-card">
            <h3 style="color:#FFC107; margin-top:0;">🌱 Nurture Your Balance</h3>
            <p>You're doing well, but could use some extra care. Here are gentle ways to restore your equilibrium:</p>
            <ul>
                <li>🌿 Try a 5-minute mindfulness break today</li>
                <li>💧 Stay hydrated - your brain needs water to function optimally</li>
                <li>📵 Schedule 30 minutes of screen-free time before bed</li>
                <li>🌅 Start your morning with 3 deep breaths before checking your phone</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Suggested Routine
        st.markdown("""
        <div class="routine-card">
            <h3 style="color:#FF7597; margin-top:0;">🌸 Suggested Daily Rhythm</h3>
            <p>A balanced routine can help maintain your wellbeing:</p>
        </div>
        """, unsafe_allow_html=True)
        
        routine = [
            {"Time": "6:30 AM", "Activity": "🌅 Gentle wake-up, stretch in sunlight"},
            {"Time": "7:00 AM", "Activity": "🍵 Hydrate + light movement (yoga/walk)"},
            {"Time": "8:00 AM", "Activity": "🧠 Deep work session (90 min)"},
            {"Time": "9:30 AM", "Activity": "☕ Break with herbal tea"},
            {"Time": "10:00 AM", "Activity": "📚 Creative work/learning"},
            {"Time": "12:00 PM", "Activity": "🥗 Nourishing lunch away from screens"},
            {"Time": "1:00 PM", "Activity": "🌳 Nature walk or rest (20 min)"},
            {"Time": "2:00 PM", "Activity": "✍️ Light tasks/emails"},
            {"Time": "4:00 PM", "Activity": "🏃‍♀️ Movement (dance, walk, yoga)"},
            {"Time": "6:00 PM", "Activity": "🍲 Light dinner with veggies"},
            {"Time": "7:30 PM", "Activity": "📖 Reading or creative hobby"},
            {"Time": "9:00 PM", "Activity": "🛀 Wind-down routine (no screens)"},
            {"Time": "10:00 PM", "Activity": "🌙 Sleep with gratitude reflection"},
        ]
        
        # Create a beautiful timeline
        for item in routine:
            st.markdown(f"""
            <div style="display: flex; margin-bottom: 10px;">
                <div style="width: 80px; font-weight: bold; color: {accent_color};">{item['Time']}</div>
                <div style="flex-grow: 1; padding-left: 15px; border-left: 2px solid {button_bg};">{item['Activity']}</div>
            </div>
            """, unsafe_allow_html=True)

    elif risk == "High":
        st.markdown("""
        <div class="suggestion-card">
            <h3 style="color:#F44336; margin-top:0;">💖 Gentle Self-Care Plan</h3>
            <p>You might be feeling overwhelmed. Here are some nourishing suggestions:</p>
            <ul>
                <li>🌬️ Practice box breathing: 4 sec inhale, 4 sec hold, 6 sec exhale</li>
                <li>🛌 Prioritize sleep - try a warm bath before bed</li>
                <li>📵 Schedule digital detox periods today</li>
                <li>🤗 Reach out to a friend or loved one</li>
                <li>🌱 Spend 10 minutes in nature if possible</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Recovery Routine
        st.markdown("""
        <div class="routine-card">
            <h3 style="color:#FF7597; margin-top:0;">🌿 Recovery Day Plan</h3>
            <p>When feeling drained, this gentle routine can help restore your energy:</p>
        </div>
        """, unsafe_allow_html=True)
        
        recovery_routine = [
            {"Time": "7:00 AM", "Activity": "🌅 Wake without alarm, gentle stretches"},
            {"Time": "7:30 AM", "Activity": "🍋 Warm lemon water + 5 min meditation"},
            {"Time": "8:00 AM", "Activity": "🚶‍♀️ Short walk in nature (even just outside)"},
            {"Time": "9:00 AM", "Activity": "📝 Journal or free-write for 10 minutes"},
            {"Time": "10:00 AM", "Activity": "🍵 Herbal tea + light reading (no news)"},
            {"Time": "12:00 PM", "Activity": "🥑 Nourishing meal with protein & veggies"},
            {"Time": "1:00 PM", "Activity": "😴 Optional 20-min rest (no guilt)"},
            {"Time": "2:30 PM", "Activity": "🎨 Creative activity (draw, craft, music)"},
            {"Time": "4:00 PM", "Activity": "🧘‍♀️ Gentle yoga or stretching"},
            {"Time": "6:00 PM", "Activity": "🍲 Light dinner (comfort foods okay)"},
            {"Time": "7:30 PM", "Activity": "📵 Screen-free time (bath, music, book)"},
            {"Time": "9:00 PM", "Activity": "🛀 Warm bath or shower"},
            {"Time": "9:30 PM", "Activity": "🌙 Gratitude journal + early sleep"},
        ]
        
        for item in recovery_routine:
            st.markdown(f"""
            <div style="display: flex; margin-bottom: 10px;">
                <div style="width: 80px; font-weight: bold; color: {accent_color};">{item['Time']}</div>
                <div style="flex-grow: 1; padding-left: 15px; border-left: 2px solid {button_bg};">{item['Activity']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Emergency resources
        st.markdown("""
        <div class="suggestion-card" style="border-left-color: #F44336;">
            <h3 style="color:#F44336; margin-top:0;">🆘 Immediate Support</h3>
            <p>If you're struggling, these resources can help:</p>
            <ul>
                <li>📞 <a href="tel:988" style="color:{accent_color};">988 Suicide & Crisis Lifeline</a> (US)</li>
                <li>🌐 <a href="https://www.crisistextline.org/" target="_blank" style="color:{accent_color};">Crisis Text Line</a> (Text HOME to 741741)</li>
                <li>💙 <a href="https://www.mentalhealth.gov/get-help/immediate-help" target="_blank" style="color:{accent_color};">International Resources</a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Low risk - celebration
        st.markdown("""
        <div class="suggestion-card" style="border-left-color: #4CAF50;">
            <h3 style="color:#4CAF50; margin-top:0;">🌟 You're Thriving!</h3>
            <p>Your wellness is blossoming! Keep up these nourishing habits:</p>
            <ul>
                <li>🌻 Share your positive energy with others</li>
                <li>📚 Explore a new hobby or skill</li>
                <li>🙏 Practice gratitude journaling</li>
                <li>🌳 Spend time in nature to maintain balance</li>
                <li>💞 Connect with loved ones</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Celebration animation
        celebration_anim = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_sk5h1kfn.json")
        if celebration_anim:
            st_lottie(celebration_anim, height=200, key="celebration")
        
        st.markdown("""
        <div class="quote-card">
            <h4 style="margin-top:0;">🌼 Growth Opportunities</h4>
            <p>While you're doing well, consider these wellness boosters:</p>
            <ul>
                <li>Try a digital detox weekend</li>
                <li>Experiment with a new meditation style</li>
                <li>Volunteer or help someone in your community</li>
                <li>Start a creative project you've been putting off</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Video recommendations section
    st.markdown("""
    <div class="video-card">
        <h3 style="color:#4CC9F0; margin-top:0;">🎥 Mindful Moments</h3>
        <p>Select a video to nourish your mind:</p>
    </div>
    """, unsafe_allow_html=True)
    
    video_options = {
        "🌿 The Power of Vulnerability": "https://www.youtube.com/watch?v=iCvmsMzlF7o",
        "💪 Motivational Speech": "https://www.youtube.com/watch?v=mgmVOuLgFB0",
        "🧘 Guided Meditation": "https://www.youtube.com/watch?v=inpok4MKVLM",
        "🌊 Calming Nature Sounds": "https://www.youtube.com/watch?v=OdIJ2x3nxzQ",
        "😊 The Science of Happiness": "https://www.youtube.com/watch?v=GXy__kBVq1M"
    }
    
    selected_title = st.selectbox("Choose a video:", options=list(video_options.keys()))
    custom_url = st.text_input("Or enter your own YouTube URL:")
    video_url = custom_url.strip() if custom_url.strip() else video_options[selected_title]
    
    try:
        st.video(video_url)
    except:
        st.warning("Failed to load video. Please check the URL.")
    
    # Additional resources
    st.markdown("""
    <div class="suggestion-card">
        <h3 style="color:#BB86FC; margin-top:0;">📚 Further Reading</h3>
        <ul>
            <li><a href="https://www.mindful.org/" target="_blank" style="color:{accent_color};">Mindful.org</a> - Mindfulness practices</li>
            <li><a href="https://www.headspace.com/" target="_blank" style="color:{accent_color};">Headspace</a> - Meditation resources</li>
            <li><a href="https://www.ted.com/topics/mental_health" target="_blank" style="color:{accent_color};">TED Talks on Mental Health</a></li>
        </ul>
    </div>
    """.format(accent_color=accent_color), unsafe_allow_html=True)
        
    if st.button("Continue to Feedback"):
        st.session_state.page = "📝 Feedback"
        st.rerun()

# ========== Page 4: Feedback ===========
elif st.session_state.page == "📝 Feedback":
    st.title("💌 Share Your Thoughts")
    st.write("Thank you for using MindGarden! Your feedback helps us grow.")
    
    # Load animation
    feedback_animation = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_tutvdkg0.json")
    if feedback_animation:
        st_lottie(feedback_animation, height=200, key="feedback_anim")
    
    with st.form("feedback_form"):
        feedback = st.text_area("How was your experience with MindGarden?", height=150)
        rating = st.slider("How likely are you to recommend us to a friend?", 1, 10, 5)
        
        submitted = st.form_submit_button("🌻 Submit Feedback")
        if submitted:
            with open("data/feedback.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([st.session_state.get("name", "Anonymous"), feedback, rating])
            
            # Beautiful thank you message
            st.markdown(f"""
            <div style="background-color:{card_bg}; padding:30px; border-radius:10px; text-align:center; margin-top:20px;">
                <h2 style="color:{accent_color};">Thank You! 🌸</h2>
                <p>Your feedback is deeply appreciated.</p>
                <p>Remember: <i>"You yourself, as much as anybody in the entire universe, deserve your love and affection."</i> - Buddha</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Confetti animation
            confetti_anim = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_obhph3sh.json")
            if confetti_anim:
                st_lottie(confetti_anim, height=200, key="confetti")
