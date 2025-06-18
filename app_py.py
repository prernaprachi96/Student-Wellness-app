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

st.set_page_config(page_title="Mood Predictor App", layout="centered")

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
    </style>
    """,
    unsafe_allow_html=True,
)

# Pages list - use exact strings everywhere
pages = ["👤 User Info", "📊 Dashboard", "✨ Suggestions", "Chatbot" "📝 Feedback"]

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
if st.session_state.current_page == "👤 User Info":
    st.title("User Information")
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
elif st.session_state.current_page == "📊 Dashboard":
    st.title("Mood Dashboard")
    st.write(f"Welcome, {st.session_state.get('name', 'User')}!")
    st.markdown("### ✏️ Write about your day")
    journal_entry = st.text_area("Write your journal entry here:", height=200)

    sleep_hours = st.slider("😴 For what hours did you sleep last night?", 0, 12, 6)
    screen_time = st.slider("📱 Daily Screen Time (in hours)", 0, 16, 6)
    workout_done = st.selectbox("🏋️ Did you work out today?", ["Yes", "No"])

    if 'mood_analyzed' not in st.session_state:
        st.session_state.mood_analyzed = False

    if st.button("Analyze My Mood"):
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
                mood = "Happy 😊"
                risk = "Low"
            elif mood_score > 0.1:
                mood = "Okay 🙂"
                risk = "Moderate"
            else:
                mood = "Stressed 😟"
                risk = "High"

            st.metric("Mood", mood)
            st.metric("Mood Score", f"{mood_score:.2f}")
            st.metric("Burnout Risk", risk)

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
        if st.button("Continue to Suggestions"):
            go_next()

# ========== Page 3: Suggestions ==========
elif st.session_state.page == "✨ Suggestions":
    st.title("🧘 Wellness Suggestions")

    risk = st.session_state.get('risk', 'Moderate')

    if "motivational_shown" not in st.session_state:
        st.session_state.motivational_shown = True
        st.info("💡 Motivation: \"The only way to do great work is to love what you do.\" – Steve Jobs")

    if risk == "Moderate":
        st.subheader("You might be feeling overwhelmed.")
        st.video("https://www.youtube.com/watch?v=2OEL4P1Rz04")
        st.markdown("[Burnout Management Tips from CDC](https://www.cdc.gov/mentalhealth/stress-coping/cope-with-stress/index.html)")

        st.markdown("### 🗓️ Suggested Routine for Moderate Risk:")
        routine = [
            {"Time": "6:30 AM - 7:30 AM", "Activity": "Light exercise (walking, stretching)"},
            {"Time": "7:30 AM - 8:00 AM", "Activity": "Healthy breakfast with fruits and veggies"},
            {"Time": "8:00 AM - 10:00 AM", "Activity": "Focused study/work"},
            {"Time": "10:00 AM - 10:15 AM", "Activity": "Break - meditate or relax"},
            {"Time": "10:15 AM - 12:00 PM", "Activity": "Study or project work"},
            {"Time": "12:00 PM - 1:00 PM", "Activity": "Balanced lunch"},
            {"Time": "1:00 PM - 2:00 PM", "Activity": "Rest or light nap"},
            {"Time": "2:00 PM - 4:00 PM", "Activity": "Study or assignments"},
            {"Time": "4:00 PM - 4:30 PM", "Activity": "Physical activity (walk, cycling)"},
            {"Time": "4:30 PM - 5:00 PM", "Activity": "Healthy snack"},
            {"Time": "5:00 PM - 7:00 PM", "Activity": "Light study/revision"},
            {"Time": "7:00 PM - 8:00 PM", "Activity": "Dinner with veggies"},
            {"Time": "8:00 PM - 9:00 PM", "Activity": "Relaxation and hobbies"},
            {"Time": "9:00 PM - 10:00 PM", "Activity": "Prepare for next day & sleep early"},
        ]
        routine_df = pd.DataFrame(routine)

        st.table(routine_df)

        def parse_time(t):
            return datetime.strptime(t.split(" - ")[0], "%I:%M %p")

        routine_df['Start Time'] = routine_df['Time'].apply(lambda x: parse_time(x))
        routine_df['End Time'] = routine_df['Time'].apply(lambda x: datetime.strptime(x.split(" - ")[1], "%I:%M %p") if " - " in x else parse_time(x))

        chart = alt.Chart(routine_df).mark_bar().encode(
            x=alt.X('Start Time:T', axis=alt.Axis(title='Time of Day', format='%I:%M %p')),
            x2='End Time:T',
            y=alt.Y('Activity:N', sort=None),
            color=alt.Color('Activity:N', legend=None)
        ).properties(
            height=400,
            width=700,
            title='Daily Routine Timeline for Moderate Risk'
        )

        st.altair_chart(chart, use_container_width=True)

    elif risk == "High":
        st.subheader("You might be feeling overwhelmed.")
        st.video("https://www.youtube.com/watch?v=2OEL4P1Rz04")
        st.markdown("[Burnout Management Tips from CDC](https://www.cdc.gov/mentalhealth/stress-coping/cope-with-stress/index.html)")

        st.markdown("### 🗓️ Recommended Daily Routine for You:")
        routine = [
            {"Time": "6:00 AM - 7:00 AM", "Activity": "Wake up & Morning exercise (stretch, yoga)"},
            {"Time": "7:00 AM - 7:30 AM", "Activity": "Healthy breakfast (include green veggies, fruits)"},
            {"Time": "7:30 AM - 9:00 AM", "Activity": "Focused study session"},
            {"Time": "9:00 AM - 9:15 AM", "Activity": "Short break (walk/stretch)"},
            {"Time": "9:15 AM - 11:00 AM", "Activity": "Study / Assignments"},
            {"Time": "11:00 AM - 12:00 PM", "Activity": "Light snack & rest"},
            {"Time": "12:00 PM - 1:00 PM", "Activity": "Lunch (balanced with veggies and protein)"},
            {"Time": "1:00 PM - 2:00 PM", "Activity": "Power nap or relaxation"},
            {"Time": "2:00 PM - 4:00 PM", "Activity": "Study or project work"},
            {"Time": "4:00 PM - 4:30 PM", "Activity": "Physical activity (walk, cycling, sport)"},
            {"Time": "4:30 PM - 5:00 PM", "Activity": "Healthy snack"},
            {"Time": "5:00 PM - 7:00 PM", "Activity": "Study / Revision"},
            {"Time": "7:00 PM - 8:00 PM", "Activity": "Dinner (include green vegetables)"},
            {"Time": "8:00 PM - 9:00 PM", "Activity": "Leisure time (reading, hobbies)"},
            {"Time": "9:00 PM - 10:00 PM", "Activity": "Prepare for next day & relax"},
            {"Time": "10:00 PM", "Activity": "Sleep early for recovery"},
        ]
        routine_df = pd.DataFrame(routine)

        st.table(routine_df)

        def parse_time(t):
            return datetime.strptime(t.split(" - ")[0], "%I:%M %p")

        routine_df['Start Time'] = routine_df['Time'].apply(lambda x: parse_time(x))
        routine_df['End Time'] = routine_df['Time'].apply(lambda x: datetime.strptime(x.split(" - ")[1], "%I:%M %p") if " - " in x else parse_time(x))

        chart = alt.Chart(routine_df).mark_bar().encode(
            x=alt.X('Start Time:T', axis=alt.Axis(title='Time of Day', format='%I:%M %p')),
            x2='End Time:T',
            y=alt.Y('Activity:N', sort=None),
            color=alt.Color('Activity:N', legend=None)
        ).properties(
            height=400,
            width=700,
            title='Daily Routine Timeline for High Risk'
        )

        st.altair_chart(chart, use_container_width=True)

    else:
        st.success("You're doing great! Keep it up 🥳")

    st.markdown("### 🎙️ Talk of the Day")

    video_options = {
        "TEDx - The Power of Vulnerability": "https://www.youtube.com/watch?v=iCvmsMzlF7o",
        "Motivational Speech - Never Give Up": "https://www.youtube.com/watch?v=mgmVOuLgFB0",
        "Mindfulness Meditation": "https://www.youtube.com/watch?v=inpok4MKVLM",
        "Calming Nature Sounds": "https://www.youtube.com/watch?v=OdIJ2x3nxzQ",
    }

    selected_title = st.selectbox("Select a video:", options=list(video_options.keys()))
    custom_url = st.text_input("Or enter a YouTube video URL:")
    video_url = custom_url.strip() if custom_url.strip() else video_options[selected_title]

    try:
        st.video(video_url)
    except:
        st.warning("Failed to load video. Please check the URL.")

    captions = {
        "TEDx - The Power of Vulnerability": "“Vulnerability is the birthplace of innovation, creativity and change.” – Brené Brown",
        "Motivational Speech - Never Give Up": "“Don’t watch the clock; do what it does. Keep going.” – Sam Levenson",
        "Mindfulness Meditation": "Relax your mind and body with this meditation.",
        "Calming Nature Sounds": "Experience calm and tranquility with nature’s sounds.",
    }

    caption_text = captions.get(selected_title, "")
    if caption_text:
        st.caption(caption_text)
        
    if st.button("Chat with Wellness Bot"):
        go_next("Chtbot")







#=========== Page 4: Chatbot ============
if "current_page" not in st.session_state:
    st.session_state.current_page = "Chatbot"  # Set chatbot as default start page


def chatbot_page():
    st.title("🧠 Chat with Your Wellness Buddy")
    st.markdown("Feel free to talk about your day, stress, or anything on your mind 💬")
    st.write("Hi there! I’m your friendly mood bot. Ask me anything or type 'exit' to leave the chat.")
    

    # Get mood score and convert to mood label
    score = st.session_state.mood_score
    mood = "positive" if score > 0.3 else "negative" if score < -0.3 else "neutral"

    # Initialize message history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": f"You are a kind and understanding mental wellness coach. The student is feeling {mood}."}
        ]

    # Display chat history
    for msg in st.session_state.messages[1:]:
        st.chat_message(msg["role"]).markdown(msg["content"])

    # User input
    if prompt := st.chat_input("Say something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        with st.spinner("Thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state.messages
                )
                reply = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.chat_message("assistant").markdown(reply)
            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.current_page == ("Chatbot"):
        chatbot_page()
       
     


# ========== Page 4: Feedback ===========
elif st.session_state.current_page == "📝 Feedback":
        st.title("💬 Feedback")
        st.write("Thank you for using our Mood Prediction App!")
    # Load animation
        feedback_animation = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_tutvdkg0.json")  # You can replace this URL with any other Lottie animation
    
        if feedback_animation:
            st_lottie(feedback_animation, height=200, key="feedback_anim")
        else:
            st.warning("⚠️ Animation failed to load.")
        feedback = st.text_area("How was your experience?")
        if st.button("Submit Feedback"):
            with open("data/feedback.csv", "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([st.session_state.get("name", "Anonymous"), feedback])
            st.success("Thanks for your feedback! 🌟")
             # ✨ Add custom thank-you message
            st.markdown("### 🙏 We appreciate your time!")
            st.info("Your feedback helps us improve. Stay happy and healthy!")

    # Continue button to go to Feedback page
        if st.button("➡️ Continue to Feedback"):
            st.session_state.page = "📝 Feedback"
            st.rerun()



