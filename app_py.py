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
import random
import json

# Create folders if not exist
os.makedirs("data", exist_ok=True)

# Set page config with nature theme
st.set_page_config(
    page_title="NatureMind Wellness",
    layout="centered",
    page_icon="🌿",
    initial_sidebar_state="expanded"
)

# ========== Helper Functions ==========
@st.cache_data(ttl=3600)
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Nature-themed colors
nature_colors = {
    "bg": "#f0f7f4",
    "card": "#ffffff",
    "text": "#1a3e34",
    "accent": "#4a7c59",
    "button": "#3a5a40",
    "button_text": "#ffffff",
    "chat_user": "#e3f0e8",
    "chat_bot": "#c8dad3"
}

# Apply nature theme CSS
st.markdown(
    f"""
    <style>
    body {{ background-color: {nature_colors['bg']}; color: {nature_colors['text']}; }}
    .stApp {{ background-color: {nature_colors['bg']}; color: {nature_colors['text']}; }}
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: {nature_colors['card']};
        border: 1px solid {nature_colors['accent']};
    }}
    .stSelectbox>div>div>select {{
        background-color: {nature_colors['card']};
        border: 1px solid {nature_colors['accent']};
    }}
    .stSlider>div>div>div>div {{
        background-color: {nature_colors['accent']};
    }}
    button[kind="primary"] {{
        background-color: {nature_colors['button']} !important;
        color: {nature_colors['button_text']} !important;
        border: none !important;
    }}
    button[kind="primary"]:hover {{
        background-color: {nature_colors['accent']} !important;
    }}
    .chat-user {{
        background-color: {nature_colors['chat_user']};
        padding: 10px;
        border-radius: 15px 15px 0 15px;
        margin: 5px 0;
        max-width: 80%;
        margin-left: auto;
        border: 1px solid {nature_colors['accent']};
    }}
    .chat-bot {{
        background-color: {nature_colors['chat_bot']};
        padding: 10px;
        border-radius: 15px 15px 15px 0;
        margin: 5px 0;
        max-width: 80%;
        margin-right: auto;
        border: 1px solid {nature_colors['accent']};
    }}
    .nature-card {{
        background-color: {nature_colors['card']};
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 5px solid {nature_colors['accent']};
    }}
    .st-emotion-cache-1kyxreq {{
        justify-content: center;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Pages list
pages = ["🌱 User Info", "📊 Mood Garden", "💬 Nature Guide", "📝 Feedback"]

# Initialize session state for current page
if 'page' not in st.session_state or st.session_state.page not in pages:
    st.session_state.page = pages[0]

# Initialize chat history if not exists
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize quiz state if not exists
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

# Sidebar Navigation
st.sidebar.title("🌿 Navigation")
current_idx = pages.index(st.session_state.page)

for i, page in enumerate(pages):
    if i <= current_idx:
        if st.sidebar.button(f"{page}", key=page):
            st.session_state.page = page
    else:
        st.sidebar.markdown(f"{page} 🔒")

# Page Navigator
def go_next():
    next_idx = pages.index(st.session_state.page) + 1
    if next_idx < len(pages):
        st.session_state.page = pages[next_idx]

# ========== Nature Chatbot ==========
def nature_chatbot_response(user_input):
    """Generate responses for the nature-themed chatbot"""
    greetings = ["hello", "hi", "hey", "greetings"]
    feelings = ["sad", "stress", "anxious", "overwhelm", "tired", "exhaust"]
    happy = ["happy", "good", "great", "wonderful", "awesome"]
    nature = ["plant", "tree", "flower", "garden", "nature", "outdoor"]
    
    user_input_lower = user_input.lower()
    
    if any(word in user_input_lower for word in greetings):
        return random.choice([
            "Hello friend! 🌸 How can I help you grow today?",
            "Greetings! 🌿 What's on your mind?",
            "Welcome to NatureMind! 🌻 How are you feeling?"
        ])
    
    elif any(word in user_input_lower for word in feelings):
        return random.choice([
            "I hear you. Even the mightiest oak was once a little nut that stood its ground. 🌳 What's been challenging for you?",
            "Nature teaches us that storms pass and sunshine returns. ☀️ Would you like to share more?",
            "Like a river, our emotions flow and change. 💧 How can I support you right now?"
        ])
    
    elif any(word in user_input_lower for word in happy):
        return random.choice([
            "Your joy is like sunshine after rain! ☀️🌈 What's bringing you happiness today?",
            "Wonderful! Like a blooming flower, your positivity is contagious! 🌺",
            "I'm so glad to hear that! Nature celebrates with you! 🍃"
        ])
    
    elif any(word in user_input_lower for word in nature):
        return random.choice([
            "Nature is the best healer. Have you spent time outside today? 🌳",
            "Plants teach us patience and resilience. What's your favorite plant? 🌱",
            "Even in the smallest seed lies great potential. What's growing in your life? 🌻"
        ])
    
    elif "thank" in user_input_lower:
        return random.choice([
            "You're welcome! Remember, kindness grows like wildflowers. 🌼",
            "It's my pleasure! Like a tree, I'm rooted in helping you. 🌲",
            "Gratitude is the memory of the heart. Thank YOU for being here! 💚"
        ])
    
    else:
        return random.choice([
            "Interesting! Tell me more about that. 🍂",
            "Nature reminds us that every perspective is valuable. Could you elaborate? 🌿",
            "Like the changing seasons, our conversations evolve. What else is on your mind? 🍁"
        ])

# ========== Burnout Quiz ==========
def burnout_quiz():
    """Display burnout risk assessment quiz"""
    questions = {
        "q1": "How often do you feel tired or lacking energy?",
        "q2": "How often do you feel distant or cynical about your work/daily activities?",
        "q3": "How often do you have difficulty concentrating?",
        "q4": "How often do you feel ineffective or like you're not accomplishing much?",
        "q5": "How often do you feel irritable or impatient with others?"
    }
    
    options = [
        "Never",
        "Rarely",
        "Sometimes",
        "Often",
        "Always"
    ]
    
    st.markdown("### 🌧️ Burnout Risk Assessment")
    st.write("Let's understand how you're feeling with this quick assessment:")
    
    for q_id, question in questions.items():
        st.session_state.quiz_answers[q_id] = st.radio(
            question,
            options,
            index=2,
            key=q_id
        )
    
    if st.button("🌱 Get My Results"):
        calculate_burnout_score()

def calculate_burnout_score():
    """Calculate and display burnout quiz results"""
    score_map = {"Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Always": 4}
    total = sum(score_map[ans] for ans in st.session_state.quiz_answers.values())
    
    if total <= 5:
        result = "🌤️ Low Risk"
        advice = """
        <div class='nature-card'>
            <h3>You're doing well!</h3>
            <p>Your responses suggest you're managing stress effectively. Keep nurturing your healthy habits:</p>
            <ul>
                <li>🌿 Continue your daily nature connection</li>
                <li>💧 Stay hydrated and nourished</li>
                <li>🌅 Maintain your morning and evening routines</li>
                <li>🔄 Check in with yourself weekly</li>
            </ul>
        </div>
        """
    elif total <= 10:
        result = "⛅ Moderate Risk"
        advice = """
        <div class='nature-card'>
            <h3>Some signs of strain</h3>
            <p>You're showing early signs of stress. Consider these gentle adjustments:</p>
            <ul>
                <li>🌳 Schedule regular breaks in nature</li>
                <li>🧘 Try 5-minute mindfulness sessions</li>
                <li>📵 Set digital boundaries, especially before bed</li>
                <li>💞 Reach out to supportive friends/family</li>
            </ul>
            <p>Remember: Even bamboo needs time to grow strong roots before shooting up.</p>
        </div>
        """
    else:
        result = "🌧️ High Risk"
        advice = """
        <div class='nature-card'>
            <h3>Time for self-care</h3>
            <p>Your responses indicate significant stress. Please prioritize your wellbeing:</p>
            <ul>
                <li>🛌 Ensure 7-9 hours of sleep nightly</li>
                <li>🌱 Start with small, manageable changes</li>
                <li>📞 Consider talking to a professional</li>
                <li>🌄 Create morning and evening rituals</li>
            </ul>
            <p><b>Resources:</b> <a href='https://www.mentalhealth.gov/get-help/immediate-help'>Immediate Help</a> | 
            <a href='https://www.crisistextline.org/'>Crisis Text Line</a></p>
            <p>Like a forest after fire, recovery takes time but new growth always comes.</p>
        </div>
        """
    
    st.session_state.quiz_completed = True
    st.markdown(f"### Your Result: {result}")
    st.markdown(advice, unsafe_allow_html=True)

# ========== Page 1: User Info ==========
if st.session_state.page == "🌱 User Info":
    st.title("🌿 Welcome to NatureMind")
    st.markdown("Let's grow together! Start by sharing some basic information.")
    
    animation = load_lottie_url("https://assets1.lottiefiles.com/packages/lf20_yo4lqexz.json")
    if animation:
        st_lottie(animation, height=220, key="character_animation")
    
    with st.form("user_info"):
        name = st.text_input("Your Name")
        age = st.number_input("Your Age", min_value=10, max_value=100, step=1)
        gender = st.selectbox("Gender", ["Female", "Male", "Non-binary", "Prefer not to say"])
        
        if st.form_submit_button("Continue to Mood Garden"):
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

# ========== Page 2: Mood Garden ==========
elif st.session_state.page == "📊 Mood Garden":
    st.title(f"🌻 {st.session_state.get('name', 'Friend')}'s Mood Garden")
    st.markdown("### ✏️ Plant Your Thoughts")
    
    journal_entry = st.text_area("What's growing in your mind today?", height=200)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        sleep_hours = st.slider("🌙 Sleep hours", 0, 12, 6)
    with col2:
        screen_time = st.slider("📱 Screen time (hrs)", 0, 16, 6)
    with col3:
        workout_done = st.selectbox("🏃‍♀️ Movement today", ["Yes", "No"])
    
    if 'mood_analyzed' not in st.session_state:
        st.session_state.mood_analyzed = False
    
    if st.button("🌱 Analyze My Mood"):
        if journal_entry.strip():
            polarity = TextBlob(journal_entry).sentiment.polarity
            
            sleep_score = sleep_hours / 8  # Normalize to 0-1 scale
            workout_score = 1 if workout_done == "Yes" else 0
            screen_score = screen_time / 16  # Normalize to 0-1 scale
            
            mood_score = (
                (0.5 * polarity) + 
                (0.3 * sleep_score) + 
                (0.2 * workout_score) - 
                (0.2 * screen_score)
            )
            
            if mood_score > 0.4:
                mood = "Blooming 🌸"
                risk = "Low"
                color = "#4CAF50"
                animation_url = "https://assets4.lottiefiles.com/packages/lf20_touohxv0.json"
            elif mood_score > 0.1:
                mood = "Growing 🌱"
                risk = "Moderate"
                color = "#FFC107"
                animation_url = "https://assets1.lottiefiles.com/packages/lf20_yo4lqexz.json"
            else:
                mood = "Needing Sunshine 🌧️"
                risk = "High"
                color = "#F44336"
                animation_url = "https://assets3.lottiefiles.com/packages/lf20_6eii5m.json"
            
            # Display results in nature cards
            st.markdown(f"""
            <div class='nature-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h2 style='color: {color}; margin: 0;'>Your Mood: {mood}</h2>
                    <span style='font-size: 24px;'>{mood.split()[-1]}</span>
                </div>
                <p>Mood Score: <b>{mood_score:.2f}</b> | Burnout Risk: <b style='color: {color};'>{risk}</b></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show appropriate animation
            anim = load_lottie_url(animation_url)
            if anim:
                st_lottie(anim, height=150, key="mood_anim")
            
            st.session_state.avg_mood = mood_score
            st.session_state.risk = risk
            st.session_state.mood_analyzed = True
            
            # If high risk, suggest the quiz
            if risk == "High":
                st.markdown("""
                <div class='nature-card'>
                    <h3>🌧️ We Notice You Might Need Extra Care</h3>
                    <p>Our gentle assessment can help identify areas for support. Would you like to take a quick quiz?</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Take the Burnout Assessment"):
                    st.session_state.show_quiz = True
        else:
            st.warning("Please write something in your journal to analyze.")
    
    # Show quiz if high risk and user opted in
    if st.session_state.get('show_quiz', False) and not st.session_state.quiz_completed:
        burnout_quiz()
    
    if st.session_state.mood_analyzed and not st.session_state.get('show_quiz', False):
        if st.button("Continue to Nature Guide"):
            go_next()

# ========== Page 3: Nature Guide ==========
elif st.session_state.page == "💬 Nature Guide":
    st.title("🌿 Nature Guide")
    st.markdown(f"### Hello {st.session_state.get('name', 'Friend')}, your personal wellness companion")
    
    # Display risk-specific header
    risk = st.session_state.get('risk', 'Moderate')
    if risk == "High":
        st.markdown("""
        <div class='nature-card'>
            <h3 style='color: #F44336;'>🌧️ Stormy Weather Guide</h3>
            <p>When clouds gather, remember even storms nourish the earth. Here's your personalized care plan.</p>
        </div>
        """, unsafe_allow_html=True)
    elif risk == "Moderate":
        st.markdown("""
        <div class='nature-card'>
            <h3 style='color: #FFC107;'>⛅ Partly Sunny Guide</h3>
            <p>Like a garden after rain, you're growing through changes. These tips can help you flourish.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='nature-card'>
            <h3 style='color: #4CAF50;'>☀️ Sunshine Guide</h3>
            <p>Your light is shining bright! Keep nurturing your wellbeing with these ideas.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Nature Chatbot
    st.markdown("### 💬 Talk with Willow (Your Nature Guide)")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"<div class='chat-user'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bot'>🌿 {message['content']}</div>", unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Type your message to Willow...", key="chat_input")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get bot response
        bot_response = nature_chatbot_response(user_input)
        st.session_state.chat_history.append({"role": "bot", "content": bot_response})
        
        # Rerun to update chat display
        st.rerun()
    
    # Risk-specific suggestions
    st.markdown("### 🌱 Personalized Suggestions")
    
    if risk == "High":
        st.markdown("""
        <div class='nature-card'>
            <h4>🌧️ Storm Survival Kit</h4>
            <ul>
                <li><b>Root yourself:</b> Try the 5-4-3-2-1 grounding technique (5 things you see, 4 you feel, etc.)</li>
                <li><b>Create a recovery routine:</b> Gentle morning stretches + evening gratitude</li>
                <li><b>Digital sunset:</b> Stop screens 1 hour before bedtime</li>
                <li><b>Nature therapy:</b> Even 10 minutes outside can help reset your mood</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.video("https://www.youtube.com/watch?v=z6X5oEIg6Ak")  # Grounding technique video
        
    elif risk == "Moderate":
        st.markdown("""
        <div class='nature-card'>
            <h4>⛅ Balance Boosters</h4>
            <ul>
                <li><b>Micro-breaks:</b> Every hour, pause for 1 minute of deep breathing</li>
                <li><b>Green time:</b> Add plants to your workspace or home</li>
                <li><b>Hydration:</b> Keep a water bottle with you and sip regularly</li>
                <li><b>Movement snacks:</b> Short walks or stretches throughout the day</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.video("https://www.youtube.com/watch?v=4pLUleLdwY4")  # Desk yoga video
        
    else:
        st.markdown("""
        <div class='nature-card'>
            <h4>☀️ Flourishing Ideas</h4>
            <ul>
                <li><b>Gratitude garden:</b> Journal 3 things you're grateful for each day</li>
                <li><b>Creative growth:</b> Try a new nature-related hobby (gardening, nature photography)</li>
                <li><b>Community roots:</b> Share your positivity with others</li>
                <li><b>Adventure seeds:</b> Plan a nature outing for the weekend</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.video("https://www.youtube.com/watch?v=wTPL_T6S3Nc")  # Nature sounds video
    
    if st.button("Continue to Feedback"):
        go_next()

# ========== Page 4: Feedback ==========
elif st.session_state.page == "📝 Feedback":
    st.title("🌸 Share Your Thoughts")
    st.markdown("We'd love to hear about your experience with NatureMind")
    
    feedback_animation = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_tutvdkg0.json")
    if feedback_animation:
        st_lottie(feedback_animation, height=200, key="feedback_anim")
    
    with st.form("feedback_form"):
        feedback = st.text_area("What did you find most helpful?", height=150)
        rating = st.slider("How would you rate your experience?", 1, 5, 3)
        
        if st.form_submit_button("Submit Feedback"):
            with open("data/feedback.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    st.session_state.get("name", "Anonymous"),
                    feedback,
                    rating,
                    datetime.now().strftime("%Y-%m-%d")
                ])
            
            st.success("Thank you for helping our garden grow! 🌱")
            
            # Show appreciation animation
            thanks_anim = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_obhph3sh.json")
            if thanks_anim:
                st_lottie(thanks_anim, height=200, key="thanks_anim")
            
            st.markdown("""
            <div class='nature-card'>
                <h3>🌿 One Last Thought</h3>
                <p><i>"Like a tree, stand tall and proud. Go out on a limb. Remember your roots. Drink plenty of water. Be content with your natural beauty. Enjoy the view."</i></p>
                <p>Wishing you continued growth and wellbeing!</p>
            </div>
            """, unsafe_allow_html=True)
