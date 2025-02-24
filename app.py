import streamlit as st
import random
from datetime import datetime

# App configuration

st.set_page_config(
    page_title="Growth Mindset Companion",
    page_icon="🌱",
    layout="centered"
)

# Session state initialization

if 'progress' not in st.session_state:
    st.session_state.progress = []

if 'challenge' not in st.session_state:
    st.session_state.challenge = ""

# Custom CSS for navigation

st.markdown("""
<style>
/* Sidebar styling */
.css-1d391kg {
    padding-top: 2rem;
    padding-bottom: 2rem;
    background-color: #f8f9fa;
    border-right: 1px solid #dee2e6;
}

/* Navigation buttons */
.stButton>button {
    width: 100%;
    border-radius: 5px;
    padding: 10px;
    margin: 5px 0;
    transition: all 0.3s ease;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Active page indicator */
.active-page {
    background-color: #0d6efd !important;
    color: white !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Header Section

st.title("🌱 Growth Mindset Companion")

st.subheader("Empower Your Learning Journey")

# Professional Navigation

def create_nav_button(label, page):

    if st.sidebar.button(label):
        st.session_state.page = page

# Initialize session state for page navigation

if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Sidebar Navigation

st.sidebar.title("Navigation")

pages = {
    "🏠 Home": "Home",
    "🧠 Mindset Quiz": "Mindset Quiz",
    "📈 Progress Tracker": "Progress Tracker",
    "💪 Daily Challenge": "Daily Challenge"
}

for label, page in pages.items():

    if st.session_state.page == page:

        st.sidebar.button(label, key=label, disabled=True, 
                          
                         help="You're on this page", 
                         type="primary")
        
    else:
        
        if st.sidebar.button(label, key=label):
            st.session_state.page = page

# Attribution

st.sidebar.markdown("---")

st.sidebar.markdown("### Made by [Ps Qasim]()")

st.sidebar.markdown("Version 1.0.0")

# Content Sections

if st.session_state.page == "Home":

    st.header("Welcome to Your Growth Journey!")
    
    with st.expander("What is Growth Mindset?"):

        st.write("""
        *A growth mindset* is the belief that your abilities can be developed through:
        - Hard work
        - Perseverance
        - Learning from mistakes
        - Embracing challenges
        """)

        st.image("https://cdn-icons-png.flaticon.com/512/3281/3281306.png", width=200)
    
    with st.expander("Why Adopt Growth Mindset?"):

        st.write("""
        - 🚀 Overcome challenges effectively
        - 📈 Improve academic performance
        - 💡 Enhance creativity and problem-solving
        - 🧠 Build resilience and adaptability
        """)
    
    with st.expander("5 Daily Practices"):

        st.write("""
        1. Embrace learning opportunities
        2. Reframe challenges as opportunities
        3. Celebrate small wins
        4. Learn from feedback
        5. Practice positive self-talk
        """)

elif st.session_state.page == "Mindset Quiz":

    st.header("🧠 Growth Mindset Assessment")
    
    questions = {
        "q1": {
            "question": "When facing a difficult problem, you:",
            "options": [
                "Avoid it to prevent failure",
                "Try it immediately without fear",
                "Feel nervous but attempt it anyway"
            ],
            "correct": 2
        },

        "q2": {
            "question": "When receiving feedback, you:",
            "options": [
                "Take it personally",
                "See it as valuable input",
                "Ignore it completely"
            ],
            "correct": 1
        }
    }
    
    score = 0
    for q_id, q in questions.items():

        answer = st.selectbox(q["question"], q["options"])

        if q["options"].index(answer) == q["correct"]:
            score += 1
            st.success("Correct! This reflects a growth mindset!")

        else:
            st.error("Consider reframing this perspective")
    
    st.metric("Your Growth Score", f"{score}/{len(questions)}")

elif st.session_state.page == "Progress Tracker":

    st.header("📈 Progress Tracker")
    
    today = datetime.today().strftime("%Y-%m-%d")

    achievement = st.text_area(f"Today's Growth ({today})", 
                              "Today I learned...")
    
    
    if st.button("Save Entry"):

        st.session_state.progress.append({
            "date": today,
            "entry": achievement
        })

        st.success("Progress saved!")
    
    st.subheader("Growth Journal")

    for entry in reversed(st.session_state.progress):

        st.write(f"{entry['date']}: {entry['entry']}")

elif st.session_state.page == "Daily Challenge":

    st.header("💪 Daily Growth Challenge")
    
    challenges = [

        "Learn something new outside your comfort zone",
        "Reframe a recent mistake as a learning opportunity",
        "Ask for constructive feedback from someone",
        "Teach a concept you learned to someone else",
        "Try a different approach to a problem you're facing"
    ]
    
    if st.button("Generate New Challenge"):

        st.session_state.challenge = random.choice(challenges)
    
    if st.session_state.challenge:

        st.subheader("Today's Challenge")

        st.info(f"🌟 {st.session_state.challenge}")

        st.write("Share your experience in the progress tracker!")

# Footer

st.markdown("---")
st.markdown("Built with ❤ using Streamlit ")
st.markdown("© 2025 Ps Qasim. All rights reserved.")