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

# Configure OpenAI - replace with your API key
openai.api_key = "YOUR_OPENAI_API_KEY"

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

# ========= Theme & Styles ========
# Nature-inspired color palette
bg_color = "#0a1a0f"  # Deep forest green
card_bg = "#1a2a1a"   # Medium forest green
text_color = "#e0f0e0" # Soft mint
accent_color = "#4cc9a8" # Teal
warning_color = "#ff7597" # Coral
button_bg = "#3a8a5f"  # Sage green
button_text = "#ffffff"

# Apply CSS
st.markdown(
    f"""
    <style>
    body {{ background-color: {bg_color}; color: {text_color}; }}
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: {card_bg};
        color: {text_color};
        border-color: {accent_color};
    }}
    .stSelectbox>div>div>select {{
        background-color: {card_bg};
        color: {text_color};
    }}
    .stSlider>div>div>div>div {{
        background-color: {accent_color};
    }}
    .stButton>button {{
        background-color: {button_bg};
        color: {button_text};
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
    }}
    .stButton>button:hover {{
        background-color: #2a6a4f;
        color: white;
    }}
    .chat-message {{
        padding: 12px;
        border-radius: 12px;
        margin: 6px 0;
        max-width: 80%;
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
    }}
    .warning-card {{
        background-color: {card_bg};
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        border-left: 4px solid {warning_color};
    }}
    .routine-item {{
        display: flex;
        margin-bottom: 10px;
        align-items: center;
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
    <div style="background-color:{card_bg}; padding:20px; border-radius:12px;">
        <p>Find your balance with our nature-inspired wellness companion. 
        Track your mood, get personalized suggestions, and chat with Terra, 
        your friendly plant-based guide.</p>
    </div>
    """, unsafe_allow_html=True)
    
    anim = load_lottie_url("https://assets5.lottiefiles.com/packages/lf20_yo4lqexz.json")
    if anim:
        st_lottie(anim, height=200, key="welcome_anim")
    
    with st.form("user_info"):
        st.subheader("Let's get started")
        name = st.text_input("What's your name?")
        age = st.slider("Your age", 10, 100, 25)
        lifestyle = st.selectbox("How would you describe your lifestyle?", 
                              ["Mostly indoors", "Balanced", "Very active outdoors"])
        
        if st.form_submit_button("Continue to Mood Check"):
            if name:
                st.session_state.name = name
                st.session_state.age = age
                st.session_state.lifestyle = lifestyle
                st.session_state.page = pages[1]
                st.rerun()
            else:
                st.warning("Please enter your name")

# ========= Page 2: Mood Check ========
elif st.session_state.page == "📊 Mood Check":
    st.title("🌼 Mood Check-In")
    st.write(f"Hello, {st.session_state.get('name', 'friend')}! Let's see how you're doing today.")
    
    # Initialize variables with default values
    mood = "Not analyzed yet"
    mood_score = 0
    risk = "Not analyzed yet"
    mood_color = accent_color
    
    # Check if mood analysis has been done
    if st.session_state.mood_analyzed:
        # Get values from session state
        mood = st.session_state.get("mood", mood)
        mood_score = st.session_state.get("mood_score", mood_score)
        risk = st.session_state.get("risk", risk)
        mood_color = st.session_state.get("mood_color", mood_color)
        
        st.success("Analysis complete!")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="background-color:{card_bg}; padding:15px; border-radius:10px; border-left:4px solid {mood_color}">
                <h3 style="color:{mood_color}">Your Mood</h3>
                <p style="font-size:24px; margin-bottom:0;">{mood}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background-color:{card_bg}; padding:15px; border-radius:10px; border-left:4px solid {accent_color}">
                <h3 style="color:{accent_color}">Wellness Score</h3>
                <p style="font-size:24px; margin-bottom:0;">{mood_score:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background-color:{card_bg}; padding:15px; border-radius:10px; border-left:4px solid {mood_color}">
                <h3 style="color:{mood_color}">Burnout Risk</h3>
                <p style="font-size:24px; margin-bottom:0;">{risk}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Show appropriate animation
        if risk == "Low":
            anim = load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_yo4lqexz.json")
        elif risk == "Moderate":
            anim = load_lottie_url("https://assets1.lottiefiles.com/packages/lf20_yo4lqexz.json")
        else:
            anim = load_lottie_url("https://assets3.lottiefiles.com/packages/lf20_yo4lqexz.json")
        
        if anim:
            st_lottie(anim, height=150, key="mood_anim")
        
        # Move the quiz button outside of any form
        if risk == "High":
            st.markdown(f"""
            <div class="warning-card">
                <h3>Let's check in with a quick wellness quiz</h3>
                <p>This will help us provide more personalized suggestions for you.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Take the Wellness Quiz"):
                st.session_state.page = "🌿 Wellness Guide"
                st.rerun()
        else:
            if st.button("View Wellness Suggestions"):
                st.session_state.page = "🌿 Wellness Guide"
                st.rerun()
    
    # Form for mood input
    with st.form("mood_form"):
        st.subheader("Daily Reflection")
        journal_entry = st.text_area("How are you feeling today? What's on your mind?", height=150)
        
        st.subheader("Lifestyle Factors")
        col1, col2 = st.columns(2)
        with col1:
            sleep_hours = st.slider("😴 Hours slept", 0, 12, 7)
            screen_time = st.slider("📱 Screen time (hours)", 0, 16, 5)
        with col2:
            outdoor_time = st.slider("🌳 Time in nature (minutes)", 0, 240, 30)
            exercise = st.selectbox("🏃 Movement today", ["None", "Light", "Moderate", "Intense"])
        
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
                    0.4 * polarity +
                    0.2 * sleep_score +
                    0.15 * nature_score +
                    0.15 * exercise_score -
                    0.1 * (1 - screen_score)
                )
                
                # Determine risk level
                if mood_score > 0.4:
                    mood = "Thriving 🌸"
                    risk = "Low"
                    mood_color = accent_color
                elif mood_score > 0.1:
                    mood = "Balanced 🌿"
                    risk = "Moderate"
                    mood_color = "#FFC107"
                else:
                    mood = "Needs Care 🍂"
                    risk = "High"
                    mood_color = warning_color
                
                # Store results
                st.session_state.mood_score = mood_score
                st.session_state.risk = risk
                st.session_state.mood = mood
                st.session_state.mood_color = mood_color
                st.session_state.mood_analyzed = True
                
                # Rerun to show results
                st.rerun()
            else:
                st.warning("Please share how you're feeling to get your mood analysis")

# ========= Page 3: Wellness Guide ========
elif st.session_state.page == "🌿 Wellness Guide":
    st.title("🌱 Personalized Wellness Guide")
    
    risk = st.session_state.get("risk", "Moderate")
    name = st.session_state.get("name", "friend")
    
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
        
        # Remove the form wrapper and use individual components
        st.write("1. How has your energy level been lately?")
        energy = st.radio(
            "Energy level",
            ["Normal", "Somewhat low", "Very low"],
            index=1,
            key="energy",
            label_visibility="collapsed"
        )
        
        st.write("2. How has your sleep been?")
        sleep = st.radio(
            "Sleep quality",
            ["Restful", "Occasionally restless", "Frequently disrupted"],
            index=1,
            key="sleep",
            label_visibility="collapsed"
        )
        
        st.write("3. How is your ability to concentrate?")
        concentration = st.radio(
            "Concentration",
            ["Normal", "Somewhat difficult", "Very difficult"],
            index=1,
            key="concentration",
            label_visibility="collapsed"
        )
        
        st.write("4. How is your motivation for daily activities?")
        motivation = st.radio(
            "Motivation",
            ["Normal", "Somewhat reduced", "Very reduced"],
            index=1,
            key="motivation",
            label_visibility="collapsed"
        )
        
        st.write("5. How would you describe your stress levels?")
        stress = st.radio(
            "Stress levels",
            ["Manageable", "Sometimes overwhelming", "Constantly overwhelming"],
            index=1,
            key="stress",
            label_visibility="collapsed"
        )
        
        # Store answers in session state
        st.session_state.quiz_answers = {
            "energy": energy,
            "sleep": sleep,
            "concentration": concentration,
            "motivation": motivation,
            "stress": stress
        }
        
        # Move the button outside of any form context
        if st.button("Get My Recommendations"):
            st.session_state.quiz_complete = True
            st.rerun()
    
    elif risk == "High" and "quiz_complete" in st.session_state:
        # Analyze quiz results
        score = sum([
            0 if ans in ["Normal", "Restful", "Manageable"] else
            1 if ans in ["Somewhat low", "Occasionally restless", "Somewhat difficult", "Somewhat reduced", "Sometimes overwhelming"] else
            2 for ans in st.session_state.quiz_answers.values()
        ])
        
        if score >= 8:
            recommendation = "professional"
        elif score >= 5:
            recommendation = "intensive_self_care"
        else:
            recommendation = "self_care"
        
        # Show recommendations based on quiz
        st.markdown(f"""
        <div class="warning-card">
            <h3>🌿 Your Personalized Recovery Plan</h3>
            <p>Based on your responses, here's what we recommend:</p>
        </div>
        """, unsafe_allow_html=True)
        
        if recommendation == "professional":
            st.markdown(f"""
            <div class="suggestion-card">
                <h4>🧠 Consider Professional Support</h4>
                <p>Your responses suggest you might benefit from professional support. Here are some resources:</p>
                <ul>
                    <li>📞 <a href="tel:988" style="color:{accent_color};">988 Suicide & Crisis Lifeline</a> (US)</li>
                    <li>🌐 <a href="https://www.psychologytoday.com/" style="color:{accent_color};" target="_blank">Find a Therapist</a></li>
                    <li>📱 <a href="https://www.betterhelp.com/" style="color:{accent_color};" target="_blank">Online Therapy Options</a></li>
                </ul>
                <p>In the meantime, these gentle practices may help:</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="suggestion-card">
            <h4>🌱 Gentle Recovery Routine</h4>
            <p>Try this nurturing daily rhythm:</p>
        </div>
        """, unsafe_allow_html=True)
        
        recovery_routine = [
            {"time": "Morning", "activities": [
                "🌅 Wake without alarm, stretch gently",
                "🍵 Warm herbal tea with 5 min meditation",
                "📝 Journal 3 things you're grateful for"
            ]},
            {"time": "Midday", "activities": [
                "🚶‍♀️ Short walk in nature (even just outside)",
                "🥑 Nourishing meal with protein & veggies",
                "😴 20-min rest (no screens)"
            ]},
            {"time": "Evening", "activities": [
                "🧘‍♀️ Gentle yoga or stretching",
                "📵 Screen-free time after dinner",
                "🛀 Warm bath before bed"
            ]}
        ]
        
        for part in recovery_routine:
            st.markdown(f"""
            <div style="background-color:{card_bg}; padding:12px; border-radius:8px; margin-bottom:12px;">
                <h5 style="color:{accent_color}; margin:0 0 8px 0;">{part['time']}</h5>
                <ul style="margin:0;">
                    {''.join([f"<li>{act}</li>" for act in part['activities']])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="suggestion-card">
            <h4>🌼 Additional Resources</h4>
            <ul>
                <li>📖 <a href="https://www.mindful.org/" style="color:{accent_color};" target="_blank">Mindfulness Practices</a></li>
                <li>🎧 <a href="https://www.headspace.com/" style="color:{accent_color};" target="_blank">Guided Meditations</a></li>
                <li>🌳 <a href="https://www.nature.org/" style="color:{accent_color};" target="_blank">Find Nature Near You</a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
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
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="suggestion-card">
            <h4>🌸 Sample Balanced Day</h4>
        </div>
        """, unsafe_allow_html=True)
        
        balanced_routine = [
            {"time": "7:00 AM", "activity": "🌞 Gentle wake-up, sunlight exposure"},
            {"time": "7:30 AM", "activity": "🧘 Morning stretch or yoga"},
            {"time": "8:30 AM", "activity": "🍳 Nourishing breakfast"},
            {"time": "9:00 AM", "activity": "📚 Focused work (90 min)"},
            {"time": "10:30 AM", "activity": "☕ Break with herbal tea"},
            {"time": "12:30 PM", "activity": "🥗 Lunch away from screens"},
            {"time": "1:30 PM", "activity": "🚶‍♀️ 15-min walk outside"},
            {"time": "4:00 PM", "activity": "🏃‍♀️ Movement break (dance, walk)"},
            {"time": "6:30 PM", "activity": "🍲 Light dinner with veggies"},
            {"time": "8:00 PM", "activity": "📖 Reading or creative hobby"},
            {"time": "9:30 PM", "activity": "🌙 Wind-down routine"}
        ]
        
        for item in balanced_routine:
            st.markdown(f"""
            <div class="routine-item">
                <div class="routine-time">{item['time']}</div>
                <div class="routine-activity">{item['activity']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    else:  # Low risk
        st.markdown(f"""
        <div class="suggestion-card">
            <h3>🌟 You're Thriving!</h3>
            <p>Your wellness is blossoming, {name}! Here's how to maintain it:</p>
            <ul>
                <li>🌻 Share your positive energy with others</li>
                <li>🌎 Explore new outdoor activities</li>
                <li>🙏 Keep a gratitude practice</li>
                <li>💞 Nurture your relationships</li>
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
    
    if st.button("💬 Chat with Terra for more help"):
        st.session_state.page = "💬 Terra Chat"
        st.rerun()

# ========= Page 4: Chatbot ========
elif st.session_state.page == "💬 Terra Chat":
    st.title("💬 Chat with Terra")
    st.markdown(f"""
    <div style="background-color:{card_bg}; padding:15px; border-radius:12px; margin-bottom:20px;">
        <p>Hi {st.session_state.get('name', 'friend')}! I'm Terra, your plant-inspired wellness guide. 
        Ask me about self-care, mindfulness, or anything else on your mind.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize OpenAI client
    if "openai_client" not in st.session_state:
        from openai import OpenAI
        st.session_state.openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    # Initialize chat history if not exists
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": f"Hi {st.session_state.get('name', 'friend')}! I'm Terra, your plant-inspired wellness guide. How can I help you today?"}
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
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        try:
            # Generate response using the new API
            response = st.session_state.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Terra, a friendly, nature-inspired wellness assistant. Use plant/animal metaphors and keep responses under 3 sentences."},
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
    
    # Suggested questions
    st.markdown("""
    <div class="suggestion-card">
        <h4>🌿 Try asking me:</h4>
        <ul>
            <li>"What's a simple mindfulness exercise?"</li>
            <li>"How can I reduce screen time?"</li>
            <li>"Suggest a calming nature activity"</li>
            <li>"Help me create a bedtime routine"</li>
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
        <div style="background-color:{card_bg}; padding:15px; border-radius:12px;">
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
