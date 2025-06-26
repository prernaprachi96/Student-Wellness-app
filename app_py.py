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

# ========= Theme & Styles ========
# Nature-inspired color palette
bg_color = "#f5faf5"  # Soft greenish white
card_bg = "#ffffff"   # White
text_color = "#1a3b2a" # Dark green
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
    body {{ background-color: {bg_color}; color: {text_color}; }}
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
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
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    .warning-card {{
        background-color: {card_bg};
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        border-left: 4px solid {warning_color};
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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
    .gender-tab {{
        display: flex;
        margin-bottom: 20px;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .gender-tab button {{
        flex: 1;
        padding: 10px;
        border: none;
        background-color: {card_bg};
        color: {text_color};
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s;
    }}
    .gender-tab button.active {{
        background-color: {accent_color};
        color: white;
    }}
    .question-card {{
        background-color: {card_bg};
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s;
        cursor: pointer;
        border-left: 4px solid {accent_color};
    }}
    .question-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .cycle-phase {{
        background-color: {female_color}20;
        padding: 8px 12px;
        border-radius: 20px;
        display: inline-block;
        margin: 4px 0;
        font-size: 0.8rem;
        color: {text_color};
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
    st.session_state.chat_gender = "female"  # Default to female view

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
    <div style="background-color:{card_bg}; padding:20px; border-radius:12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
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

# ========= Page 4: Chatbot ========
elif st.session_state.page == "💬 Terra Chat":
    st.title("💬 Wellness Companion")
    
    # Gender toggle for chat
    st.markdown("""
    <div class="gender-tab">
        <button class="active">For Her</button>
        <button>For Him</button>
    </div>
    """, unsafe_allow_html=True)
    
    # Handle gender selection
    cols = st.columns(2)
    with cols[0]:
        if st.button("🌸 For Her", use_container_width=True):
            st.session_state.chat_gender = "female"
    with cols[1]:
        if st.button("🌿 For Him", use_container_width=True):
            st.session_state.chat_gender = "male"
    
    # Show appropriate content based on gender
    if st.session_state.chat_gender == "female":
        st.markdown(f"""
        <div style="background-color:{card_bg}; padding:15px; border-radius:12px; margin-bottom:20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
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
        
        # Questions organized by categories
        tabs = st.tabs(["🌱 General", "🍵 Nutrition", "😴 Sleep", "🧘 Mindfulness", "🩸 Cycle Health"])
        
        with tabs[0]:
            st.markdown("""
            <div class="question-card" onclick="alert('Question selected')">
                <h4>How can I boost my energy naturally during the day?</h4>
                <p>Discover natural ways to combat fatigue</p>
            </div>
            <div class="question-card">
                <h4>What are some quick stress-relief techniques I can do at work?</h4>
                <p>Office-friendly relaxation methods</p>
            </div>
            <div class="question-card">
                <h4>How can I create a better morning routine?</h4>
                <p>Start your day with intention</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[1]:
            st.markdown("""
            <div class="question-card">
                <h4>What foods help with hormonal balance?</h4>
                <p>Nutrition for cycle harmony</p>
            </div>
            <div class="question-card">
                <h4>Are there specific nutrients I need more of during my period?</h4>
                <p>Eating for menstrual health</p>
            </div>
            <div class="question-card">
                <h4>What are good snacks for PCOS management?</h4>
                <p>Blood sugar balancing ideas</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[2]:
            st.markdown("""
            <div class="question-card">
                <h4>Why do I feel more tired before my period?</h4>
                <p>Understanding progesterone's effects</p>
            </div>
            <div class="question-card">
                <h4>How can I sleep better during PMS?</h4>
                <p>Tips for the luteal phase</p>
            </div>
            <div class="question-card">
                <h4>What's the ideal sleep temperature for women?</h4>
                <p>Body temperature regulation</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[3]:
            st.markdown("""
            <div class="question-card">
                <h4>How does meditation affect female hormones?</h4>
                <p>The mind-body connection</p>
            </div>
            <div class="question-card">
                <h4>What type of yoga is best for each cycle phase?</h4>
                <p>Cycle-syncing movement</p>
            </div>
            <div class="question-card">
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
                <div class="question-card">
                    <h4>How can I support my body during this phase?</h4>
                    <p>Phase-specific wellness tips</p>
                </div>
                <div class="question-card">
                    <h4>What foods are most nourishing right now?</h4>
                    <p>Nutritional needs for this phase</p>
                </div>
                <div class="question-card">
                    <h4>What type of exercise is best during this phase?</h4>
                    <p>Movement recommendations</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="question-card">
                    <h4>How can I track my cycle for better wellness?</h4>
                    <p>Understanding your patterns</p>
                </div>
                <div class="question-card">
                    <h4>What are signs of hormonal imbalance to watch for?</h4>
                    <p>When to seek help</p>
                </div>
                <div class="question-card">
                    <h4>How does stress affect menstrual health?</h4>
                    <p>The cortisol connection</p>
                </div>
                """, unsafe_allow_html=True)
    
    else:  # Male content
        st.markdown(f"""
        <div style="background-color:{card_bg}; padding:15px; border-radius:12px; margin-bottom:20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <p style="font-size: 16px;">Hello {st.session_state.get('name', 'friend')}! Let's explore wellness topics that matter to you. 
            Select a question or ask your own.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Common questions for men
        st.subheader("Common Wellness Questions")
        
        tabs = st.tabs(["🌱 General", "🍗 Nutrition", "💪 Fitness", "😴 Sleep", "🧠 Mental Health"])
        
        with tabs[0]:
            st.markdown("""
            <div class="question-card">
                <h4>How can I improve my focus and productivity naturally?</h4>
                <p>Beyond caffeine solutions</p>
            </div>
            <div class="question-card">
                <h4>What are signs of testosterone imbalance?</h4>
                <p>Hormonal health awareness</p>
            </div>
            <div class="question-card">
                <h4>How can I build a sustainable morning routine?</h4>
                <p>Starting strong</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[1]:
            st.markdown("""
            <div class="question-card">
                <h4>What nutrients are most important for male health?</h4>
                <p>Beyond protein needs</p>
            </div>
            <div class="question-card">
                <h4>How does alcohol affect male hormones?</h4>
                <p>The testosterone connection</p>
            </div>
            <div class="question-card">
                <h4>What are good plant-based protein sources?</h4>
                <p>Vegetarian options</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[2]:
            st.markdown("""
            <div class="question-card">
                <h4>How often should I take rest days?</h4>
                <p>Recovery strategies</p>
            </div>
            <div class="question-card">
                <h4>What exercises help prevent common male injuries?</h4>
                <p>Prehab routines</p>
            </div>
            <div class="question-card">
                <h4>How can I maintain muscle as I age?</h4>
                <p>Strength preservation</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[3]:
            st.markdown("""
            <div class="question-card">
                <h4>Why do men often sleep hotter than women?</h4>
                <p>Body temperature regulation</p>
            </div>
            <div class="question-card">
                <h4>How does sleep affect testosterone levels?</h4>
                <p>The hormone-sleep connection</p>
            </div>
            <div class="question-card">
                <h4>What's the best sleep position for back health?</h4>
                <p>Spinal alignment</p>
            </div>
            """, unsafe_allow_html=True)
        
        with tabs[4]:
            st.markdown("""
            <div class="question-card">
                <h4>How can men recognize signs of depression?</h4>
                <p>Beyond "feeling sad"</p>
            </div>
            <div class="question-card">
                <h4>What are healthy ways to manage stress?</h4>
                <p>Beyond avoidance</p>
            </div>
            <div class="question-card">
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

# [Rest of your existing code for other pages remains unchanged...]
