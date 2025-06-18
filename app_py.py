import streamlit as st
import pandas as pd
from textblob import TextBlob
import os
import csv
from streamlit_lottie import st_lottie
import requests
import random
import time
from datetime import datetime

# Create folders if not exist
os.makedirs("data", exist_ok=True)

# Set page config with nature theme
st.set_page_config(
    page_title="MindGarden",
    page_icon="🌿",
    layout="centered",
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

# Nature-themed color palette
colors = {
    "primary": "#2E8B57",  # Sea Green
    "secondary": "#3CB371",  # Medium Sea Green
    "accent": "#20B2AA",  # Light Sea Green
    "background": "#F5FFFA",  # Mint Cream
    "text": "#2F4F4F",  # Dark Slate Gray
    "card": "#E0F7E0",  # Very Light Green
    "warning": "#FF6347",  # Tomato
    "positive": "#4CAF50"  # Green
}

# Apply nature-themed CSS
st.markdown(
    f"""
    <style>
    body {{ background-color: {colors['background']}; color: {colors['text']}; }}
    .stApp {{ background-color: {colors['background']}; color: {colors['text']}; }}
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: white;
        border: 1px solid {colors['primary']};
    }}
    .stButton>button {{
        background-color: {colors['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
    }}
    .stButton>button:hover {{
        background-color: {colors['secondary']};
        color: white;
    }}
    .chatbot-message {{
        background-color: {colors['card']};
        border-radius: 15px;
        padding: 12px;
        margin: 5px 0;
        border-left: 5px solid {colors['accent']};
    }}
    .user-message {{
        background-color: {colors['primary']};
        color: white;
        border-radius: 15px;
        padding: 12px;
        margin: 5px 0;
    }}
    .suggestion-card {{
        background-color: {colors['card']};
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid {colors['accent']};
    }}
    .warning-card {{
        background-color: #FFEBEE;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid {colors['warning']};
    }}
    .positive-card {{
        background-color: #E8F5E9;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid {colors['positive']};
    }}
    .routine-item {{
        display: flex;
        margin-bottom: 10px;
        align-items: center;
    }}
    .routine-time {{
        font-weight: bold;
        color: {colors['primary']};
        width: 80px;
    }}
    .routine-activity {{
        flex-grow: 1;
        padding-left: 15px;
        border-left: 2px solid {colors['accent']};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ========== Chatbot Functionality ==========
class MindGardenChatbot:
    def __init__(self):
        self.responses = {
            "greeting": [
                "Hello! I'm Willow, your MindGarden guide. How can I help you grow today? 🌱",
                "Welcome back to your MindGarden! What's on your mind? 🌸",
                "Hi there! Ready to nurture your wellbeing? 🌿"
            ],
            "mood": [
                "I hear you. Emotions are like weather in your MindGarden - sometimes sunny, sometimes rainy. Both are important for growth. 🌦️",
                "Thank you for sharing. Remember, every feeling is valid in your MindGarden. 🌈",
                "I understand. Let's tend to these feelings together. What would help right now? 🌻"
            ],
            "stress": [
                "When stress feels overwhelming, try the 5-4-3-2-1 grounding technique: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, and 1 you taste. 🌍",
                "Stress is like a storm in your garden - temporary and necessary for growth. Try some deep breathing with me: Inhale for 4, hold for 4, exhale for 6. 🌬️",
                "Let's plant some calm. Would you like a guided meditation or some nature sounds? 🎧"
            ],
            "sleep": [
                "Sleep is the water that nourishes your MindGarden. Try a digital sunset - no screens 1 hour before bed. 🌙",
                "Having trouble sleeping? A warm cup of chamomile tea and some gentle stretches might help. 🍵",
                "Your sleep garden needs tending. Consistent bedtime routines help your body's natural rhythms. ⏰"
            ],
            "unknown": [
                "I'm still growing my knowledge! Could you tell me more about what you need? 🌱",
                "That's an interesting question for this garden. Let me think how best to help... 🌷",
                "I want to make sure I understand. Could you rephrase that for me? 🌼"
            ],
            "farewell": [
                "Remember to tend to your MindGarden daily. You're doing great! 🌟",
                "Wishing you peace and growth until we chat again. 🌿",
                "Thank you for nurturing your wellbeing today. Come back anytime! 🌸"
            ]
        }
    
    def respond(self, message):
        message = message.lower()
        if any(word in message for word in ["hi", "hello", "hey"]):
            return random.choice(self.responses["greeting"])
        elif any(word in message for word in ["feel", "mood", "emotion"]):
            return random.choice(self.responses["mood"])
        elif any(word in message for word in ["stress", "overwhelm", "anxious"]):
            return random.choice(self.responses["stress"])
        elif any(word in message for word in ["sleep", "tired", "rest"]):
            return random.choice(self.responses["sleep"])
        elif any(word in message for word in ["bye", "goodbye", "thanks"]):
            return random.choice(self.responses["farewell"])
        else:
            return random.choice(self.responses["unknown"])

# Initialize chatbot
if "chatbot" not in st.session_state:
    st.session_state.chatbot = MindGardenChatbot()
    st.session_state.chat_history = []

# ========== Burnout Quiz ==========
def burnout_quiz():
    questions = [
        {
            "question": "How often do you feel exhausted, even after resting?",
            "options": ["Rarely", "Sometimes", "Often", "Almost always"]
        },
        {
            "question": "How difficult do you find it to concentrate on tasks?",
            "options": ["Not difficult", "Somewhat difficult", "Very difficult", "Extremely difficult"]
        },
        {
            "question": "How often do you feel detached or cynical about your work/daily activities?",
            "options": ["Rarely", "Sometimes", "Often", "Almost always"]
        },
        {
            "question": "How would you rate your sleep quality recently?",
            "options": ["Excellent", "Good", "Fair", "Poor"]
        },
        {
            "question": "How often do you experience physical symptoms like headaches or stomachaches?",
            "options": ["Rarely", "Sometimes", "Often", "Almost always"]
        }
    ]
    
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = [None] * len(questions)
        st.session_state.current_question = 0
    
    if st.session_state.current_question < len(questions):
        q = questions[st.session_state.current_question]
        st.subheader(f"Question {st.session_state.current_question + 1}/{len(questions)}")
        st.markdown(f"### {q['question']}")
        
        cols = st.columns(2)
        for i, option in enumerate(q["options"]):
            with cols[i % 2]:
                if st.button(option, key=f"q{st.session_state.current_question}_o{i}"):
                    st.session_state.quiz_answers[st.session_state.current_question] = i
                    st.session_state.current_question += 1
                    st.rerun()
    else:
        # Calculate score (higher = more burnout risk)
        score = sum(st.session_state.quiz_answers)
        
        st.subheader("Your Burnout Assessment")
        if score <= 5:
            st.markdown(f"""
            <div class="positive-card">
                <h3>🌱 Mild Burnout Risk</h3>
                <p>Your garden is thriving! You're managing stress well, but here are some tips to maintain balance:</p>
                <ul>
                    <li>Continue your healthy routines</li>
                    <li>Practice gratitude journaling</li>
                    <li>Take regular nature breaks</li>
                    <li>Share your energy with others</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        elif score <= 10:
            st.markdown(f"""
            <div class="suggestion-card">
                <h3>🌿 Moderate Burnout Risk</h3>
                <p>Your garden needs some attention. Consider these nurturing practices:</p>
                <ul>
                    <li>Set clearer boundaries between work and rest</li>
                    <li>Schedule regular digital detox periods</li>
                    <li>Practice the 20-20-20 rule (every 20 mins, look at something 20 feet away for 20 seconds)</li>
                    <li>Connect with supportive friends or family</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="warning-card">
                <h3>⚠️ High Burnout Risk</h3>
                <p>Your garden needs immediate care. Please consider:</p>
                <ul>
                    <li>Taking a mental health day if possible</li>
                    <li>Speaking with a healthcare professional</li>
                    <li>Implementing daily relaxation practices</li>
                    <li>Reducing non-essential commitments</li>
                </ul>
                <p><strong>Immediate support:</strong> <a href="tel:988">988 Suicide & Crisis Lifeline</a> (US) or <a href="https://www.crisistextline.org/" target="_blank">Crisis Text Line</a></p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("Back to Wellness Guide"):
            del st.session_state.quiz_answers
            del st.session_state.current_question
            st.session_state.page = "✨ Wellness Guide"
            st.rerun()

# ========== Pages ==========
pages = ["👤 User Info", "📊 Mood Garden", "✨ Wellness Guide", "💬 Chat with Willow"]

# Initialize session state for current page
if 'page' not in st.session_state or st.session_state.page not in pages:
    st.session_state.page = pages[0]

# Sidebar Navigation
st.sidebar.title("🌿 MindGarden")
st.sidebar.markdown("Nurture your mental wellbeing")

for page in pages:
    if st.sidebar.button(page):
        st.session_state.page = page

# Page Navigator
def go_next():
    current_idx = pages.index(st.session_state.page)
    if current_idx + 1 < len(pages):
        st.session_state.page = pages[current_idx + 1]

# ========== Page 1: User Info ==========
if st.session_state.page == "👤 User Info":
    st.title("🌱 Welcome to MindGarden")
    st.markdown("Let's get to know each other before we start nurturing your wellbeing garden.")
    
    animation = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_1pxqjqps.json")
    if animation:
        st_lottie(animation, height=220, key="character_animation")
    
    with st.form("user_info"):
        name = st.text_input("Your Name")
        age = st.number_input("Your Age", min_value=10, max_value=100, step=1)
        gender = st.selectbox("Gender Identity", ["Female", "Male", "Non-binary", "Other", "Prefer not to say"])
        
        if st.form_submit_button("Plant Your Garden"):
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
    st.title("🌸 Your Mood Garden")
    st.write(f"Welcome, {st.session_state.get('name', 'Gardener')}! Let's check in with your emotional landscape today.")
    
    with st.expander("📝 Journal Entry"):
        journal_entry = st.text_area("What's growing in your mind today? What needs watering or pruning?", height=150)
    
    col1, col2 = st.columns(2)
    with col1:
        sleep_hours = st.slider("🌙 Sleep last night (hours)", 0, 12, 7)
    with col2:
        screen_time = st.slider("📱 Screen time today (hours)", 0, 16, 4)
    
    workout_done = st.selectbox("💪 Movement today", ["Not yet", "Light activity", "Moderate exercise", "Intense workout"])
    social_interaction = st.selectbox("👥 Social connection", ["Little/none", "Some", "Plenty"])
    
    if st.button("🌻 Analyze My Garden"):
        if journal_entry.strip():
            polarity = TextBlob(journal_entry).sentiment.polarity
            
            # Calculate scores
            sleep_score = min(sleep_hours / 8, 1.5)  # Max 1.5 for 12 hours
            workout_score = {"Not yet": 0, "Light activity": 0.5, "Moderate exercise": 1, "Intense workout": 1.2}[workout_done]
            screen_score = max(0, (screen_time - 2) / 10)  # More than 2 hours starts reducing score
            social_score = {"Little/none": 0, "Some": 0.5, "Plenty": 1}[social_interaction]
            
            mood_score = (
                (0.4 * polarity) +
                (0.3 * sleep_score) +
                (0.2 * workout_score) -
                (0.2 * screen_score) +
                (0.1 * social_score)
            )
            
            if mood_score > 0.6:
                mood = "Blossoming 🌸"
                risk = "Low"
                color = colors["positive"]
                animation_url = "https://assets4.lottiefiles.com/packages/lf20_touohxv0.json"
            elif mood_score > 0.3:
                mood = "Growing 🌿"
                risk = "Moderate"
                color = colors["secondary"]
                animation_url = "https://assets1.lottiefiles.com/packages/lf20_yo4lqexz.json"
            else:
                mood = "Needs Care 🍂"
                risk = "High"
                color = colors["warning"]
                animation_url = "https://assets3.lottiefiles.com/packages/lf20_qpsnmykx.json"
            
            # Display results
            st.markdown(f"""
            <div style="background-color: {colors['card']}; border-radius: 15px; padding: 20px; margin: 15px 0; border-left: 5px solid {color};">
                <h2 style="color: {color}; margin-top: 0;">Your Garden Status: {mood}</h2>
                <p>Mood Score: <strong>{mood_score:.2f}/1.0</strong></p>
                <p>Wellness Level: <strong>{risk}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Load appropriate animation
            anim = load_lottie_url(animation_url)
            if anim:
                st_lottie(anim, height=150, key="mood_anim")
            
            st.session_state.avg_mood = mood_score
            st.session_state.risk = risk
            st.session_state.mood_analyzed = True
            
            if risk == "High":
                st.markdown(f"""
                <div class="warning-card">
                    <h3>Your Garden Needs Extra Care</h3>
                    <p>Let's assess your needs with a quick wellness check-in.</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Begin Wellness Check-in"):
                    st.session_state.page = "✨ Wellness Guide"
                    st.rerun()
        else:
            st.warning("Please share something about your day to analyze.")

# ========== Page 3: Wellness Guide ==========
elif st.session_state.page == "✨ Wellness Guide":
    if "risk" in st.session_state and st.session_state.risk == "High" and "quiz_answers" not in st.session_state:
        burnout_quiz()
    else:
        st.title("🌿 Your Wellness Guide")
        st.write(f"Welcome, {st.session_state.get('name', 'Gardener')}! Here's your personalized wellbeing plan.")
        
        # Header with animation
        header_col1, header_col2 = st.columns([3,1])
        with header_col1:
            st.markdown("### Nurture Your MindGarden")
        with header_col2:
            wellness_anim = load_lottie_url("https://assets1.lottiefiles.com/packages/lf20_yo4lqexz.json")
            if wellness_anim:
                st_lottie(wellness_anim, height=80, key="wellness_header")
        
        risk = st.session_state.get("risk", "Moderate")
        
        # Motivational quote
        quotes = {
            "Low": "Your garden is thriving! Keep nurturing it with love and attention. 🌸",
            "Moderate": "Every garden needs care. Small, consistent actions create lasting growth. 🌱",
            "High": "Even the most neglected garden can bloom again with care and patience. 🌻"
        }
        st.markdown(f"""
        <div class="suggestion-card">
            <p style="font-size: 18px; font-style: italic;">"{quotes.get(risk, 'Growth takes time. Be gentle with yourself.')}"</p>
        </div>
        """, unsafe_allow_html=True)
        
        if risk == "High":
            st.markdown(f"""
            <div class="warning-card">
                <h3>🌱 Recovery Plan</h3>
                <p>Your garden needs extra nourishment. Try these gentle steps:</p>
                <ul>
                    <li><strong>Morning:</strong> 5 minutes of deep breathing outdoors</li>
                    <li><strong>Midday:</strong> Hydrate with herbal tea and a short walk</li>
                    <li><strong>Afternoon:</strong> Digital detox for 30 minutes</li>
                    <li><strong>Evening:</strong> Warm bath and gratitude reflection</li>
                </ul>
                <p>Would you like to talk with Willow about specific concerns?</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("💬 Chat with Willow"):
                st.session_state.page = "💬 Chat with Willow"
                st.rerun()
        
        elif risk == "Moderate":
            st.markdown(f"""
            <div class="suggestion-card">
                <h3>🌿 Balance Boosters</h3>
                <p>Your garden could use some tending. Try these practices:</p>
                <ul>
                    <li>Nature breaks every 2 hours (even looking out a window helps)</li>
                    <li>Evening digital sunset (no screens 1 hour before bed)</li>
                    <li>Weekly "forest bathing" - spend time mindfully in nature</li>
                    <li>Gratitude journaling each morning or evening</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Nature sound player
            st.markdown("### 🎶 Nature Sounds for Relaxation")
            sound_options = {
                "Forest Rain": "https://www.youtube.com/watch?v=H9I3VnFvp8M",
                "Ocean Waves": "https://www.youtube.com/watch?v=aBkTkxKDduc",
                "Mountain Stream": "https://www.youtube.com/watch?v=Yxq7Q1QY1Q4",
                "Birdsong": "https://www.youtube.com/watch?v=6S3OqQXk3vA"
            }
            selected_sound = st.selectbox("Choose a soundscape:", list(sound_options.keys()))
            st.video(sound_options[selected_sound])
        
        else:  # Low risk
            st.markdown(f"""
            <div class="positive-card">
                <h3>🌸 Flourishing Practices</h3>
                <p>Your garden is blooming! Keep up these habits:</p>
                <ul>
                    <li>Share your positive energy with others</li>
                    <li>Try new growth experiences (learn a skill, explore nature)</li>
                    <li>Maintain your healthy routines</li>
                    <li>Practice mindful appreciation of your progress</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Celebration animation
            celebration_anim = load_lottie_url("https://assets6.lottiefiles.com/packages/lf20_sk5h1kfn.json")
            if celebration_anim:
                st_lottie(celebration_anim, height=200, key="celebration")
        
        # Guided meditation section
        st.markdown("### � Guided Practices")
        meditations = {
            "5-Minute Breathing": "https://www.youtube.com/watch?v=SEfs5TJZ6Nk",
            "Body Scan Relaxation": "https://www.youtube.com/watch?v=86HUcX8ZtAk",
            "Mindful Walking": "https://www.youtube.com/watch?v=6p_yaNFSYao",
            "Loving-Kindness Meditation": "https://www.youtube.com/watch?v=sz7cpV7ERsM"
        }
        selected_meditation = st.selectbox("Choose a guided practice:", list(meditations.keys()))
        st.video(meditations[selected_meditation])

# ========== Page 4: Chat with Willow ==========
elif st.session_state.page == "💬 Chat with Willow":
    st.title("💬 Chat with Willow")
    st.markdown("Your friendly MindGarden guide is here to help you grow.")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "assistant":
            st.markdown(f"""
            <div class="chatbot-message">
                <strong>Willow 🌿</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="user-message">
                <strong>You</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Type your message to Willow...", key="chat_input")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get bot response
        bot_response = st.session_state.chatbot.respond(user_input)
        
        # Add typing animation delay
        with st.spinner("Willow is thinking..."):
            time.sleep(1)  # Simulate typing delay
            st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
            st.rerun()
    
    if st.button("Back to Wellness Guide"):
        st.session_state.page = "✨ Wellness Guide"
        st.rerun()

# Add footer
st.markdown("---")
st.markdown("🌻 MindGarden - Nurturing your mental wellbeing daily")
