import streamlit as st
import random
import pandas as pd
import sqlite3
import plotly.express as px
from typing import List, Tuple
from datetime import datetime

# Configure page theme for dark mode
st.set_page_config(
    page_title="Growth Mindset Coach",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply dark theme
st.markdown("""
    <style>
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput input {
        background-color: #2D2D2D;
        color: white;
    }
    .stTextArea textarea {
        background-color: #2D2D2D;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Constants
QUOTES = [
    "Believe you can and you're halfway there.",
    "The only way to do great work is to love what you do.",
    "Your limitation—it's only your imagination.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones.",
    "Mistakes are proof that you are trying.",
    "Success is not the key to happiness. Happiness is the key to success."
]

class DatabaseManager:
    def __init__(self, database_name: str = "growth_mindset.db"):
        self.conn = sqlite3.connect(database_name, check_same_thread=False)
        self.migrate_database()

    def migrate_database(self):
        """Create or migrate database tables"""
        with self.conn:
            # Check if tables exist
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='challenges'")
            table_exists = cursor.fetchone() is not None

            if not table_exists:
                # Create new tables
                self.conn.execute("""
                    CREATE TABLE challenges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        challenge TEXT NOT NULL,
                        status TEXT CHECK(status IN ('In Progress', 'Completed')) NOT NULL DEFAULT 'In Progress'
                    )
                """)
                self.conn.execute("""
                    CREATE TABLE mistakes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mistake TEXT NOT NULL,
                        lesson TEXT NOT NULL
                    )
                """)
            else:
                # Check if we need to add created_at column
                cursor.execute("PRAGMA table_info(challenges)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'created_at' in columns:
                    # Drop the created_at column by recreating the table
                    self.conn.execute("""
                        CREATE TABLE challenges_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            challenge TEXT NOT NULL,
                            status TEXT CHECK(status IN ('In Progress', 'Completed')) NOT NULL DEFAULT 'In Progress'
                        )
                    """)
                    self.conn.execute("""
                        INSERT INTO challenges_new (id, challenge, status)
                        SELECT id, challenge, status FROM challenges
                    """)
                    self.conn.execute("DROP TABLE challenges")
                    self.conn.execute("ALTER TABLE challenges_new RENAME TO challenges")

    def execute_query(self, query: str, params: Tuple = ()):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            self.conn.commit()
            return None

    def __del__(self):
        self.conn.close()

class AppFeatures:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_random_quote(self) -> str:
        return random.choice(QUOTES)

    def add_challenge(self, challenge: str):
        if not challenge.strip():
            st.error("Please enter a challenge description!")
            return
        
        self.db.execute_query(
            "INSERT INTO challenges (challenge, status) VALUES (?, ?)",
            (challenge.strip(), "In Progress")
        )
        st.success("✅ Challenge added successfully!")

    def display_challenges(self):
        challenges = self.db.execute_query(
            "SELECT id, challenge, status FROM challenges ORDER BY id DESC"
        )
        
        if not challenges:
            st.info("No challenges found. Add your first challenge!")
            return

        for id, challenge, status in challenges:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{challenge}**")
            
            with col2:
                new_status = st.selectbox(
                    "Status",
                    ["In Progress", "Completed"],
                    index=0 if status == "In Progress" else 1,
                    key=f"status_{id}"
                )
                if new_status != status:
                    self.update_challenge_status(id, new_status)
            
            with col3:
                if st.button("Delete", key=f"del_{id}"):
                    self.delete_challenge(id)
                    st.rerun()

    def update_challenge_status(self, challenge_id: int, status: str):
        self.db.execute_query(
            "UPDATE challenges SET status = ? WHERE id = ?",
            (status, challenge_id)
        )
        st.success("✅ Challenge status updated!")

    def delete_challenge(self, challenge_id: int):
        self.db.execute_query(
            "DELETE FROM challenges WHERE id = ?",
            (challenge_id,)
        )
        st.warning("❌ Challenge deleted!")

    def log_mistake(self, mistake: str, lesson: str):
        if not mistake.strip() or not lesson.strip():
            st.error("Please fill in both mistake and lesson fields!")
            return
            
        self.db.execute_query(
            "INSERT INTO mistakes (mistake, lesson) VALUES (?, ?)",
            (mistake.strip(), lesson.strip())
        )
        st.success("✅ Mistake logged successfully!")

    def display_mistakes(self):
        mistakes = self.db.execute_query(
            "SELECT id, mistake, lesson FROM mistakes ORDER BY id DESC"
        )
        
        if not mistakes:
            st.info("No mistakes logged yet. Use mistakes as learning opportunities!")
            return

        for id, mistake, lesson in mistakes:
            with st.expander(f"📝 {mistake[:50]}{'...' if len(mistake) > 50 else ''}", expanded=False):
                st.write("**Mistake:**")
                st.write(mistake)
                st.write("**Lesson Learned:**")
                st.write(lesson)
                if st.button("Delete Entry", key=f"del_mistake_{id}"):
                    self.delete_mistake(id)
                    st.rerun()

    def delete_mistake(self, mistake_id: int):
        self.db.execute_query(
            "DELETE FROM mistakes WHERE id = ?",
            (mistake_id,)
        )
        st.warning("❌ Mistake entry deleted!")

    def plot_progress(self):
        challenges = self.db.execute_query(
            "SELECT status, COUNT(*) FROM challenges GROUP BY status"
        )
        
        if not challenges:
            st.info("No challenges found. Add some to track your progress!")
            return

        df = pd.DataFrame(challenges, columns=['Status', 'Count'])
        
        fig = px.pie(
            df,
            names='Status',
            values='Count',
            title="Challenge Progress Distribution",
            color_discrete_sequence=["#4CAF50", "#FFA726"],
            hole=0.3
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)

        total_challenges = df['Count'].sum()
        completed = df[df['Status'] == 'Completed']['Count'].sum() if 'Completed' in df['Status'].values else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Challenges", total_challenges)
        with col2:
            st.metric("Completed", completed)
        with col3:
            completion_rate = (completed / total_challenges * 100) if total_challenges > 0 else 0
            st.metric("Completion Rate", f"{completion_rate:.1f}%")

    def export_data(self):
        col1, col2 = st.columns(2)
        
        with col1:
            challenges_df = pd.read_sql("SELECT * FROM challenges", self.db.conn)
            st.download_button(
                label="📥 Download Challenges Data",
                data=challenges_df.to_csv(index=False),
                file_name="challenges_data.csv",
                mime="text/csv",
            )
        
        with col2:
            mistakes_df = pd.read_sql("SELECT * FROM mistakes", self.db.conn)
            st.download_button(
                label="📥 Download Mistakes Data",
                data=mistakes_df.to_csv(index=False),
                file_name="mistakes_data.csv",
                mime="text/csv",
            )

def main():
    db = DatabaseManager()
    features = AppFeatures(db)

    # Sidebar
    with st.sidebar:
        st.title("🌱 Growth Navigator")
        menu = st.radio("Menu", [
            "Dashboard",
            "Challenge Tracker",
            "Mistake Journal",
            "Progress Analytics"
        ])
        
        st.markdown("---")
        st.markdown(f"### Today's Motivation\n💬 {features.get_random_quote()}")

    # Main content
    if menu == "Dashboard":
        st.header("🎯 Personal Growth Dashboard")
        
        # Quick Add Section
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Quick Add Challenge")
            new_challenge = st.text_input("Enter a new challenge:")
            if st.button("Add Challenge"):
                features.add_challenge(new_challenge)
                
        with col2:
            st.subheader("Quick Add Mistake")
            new_mistake = st.text_input("What did you learn from today?")
            new_lesson = st.text_input("What's the lesson?")
            if st.button("Log Mistake"):
                features.log_mistake(new_mistake, new_lesson)
        
        # Progress Overview
        st.subheader("Progress Overview")
        features.plot_progress()

    elif menu == "Challenge Tracker":
        st.header("📌 Challenge Tracker")
        new_challenge = st.text_input("Add a new challenge:")
        if st.button("Add Challenge"):
            features.add_challenge(new_challenge)
        
        st.markdown("---")
        features.display_challenges()

    elif menu == "Mistake Journal":
        st.header("📝 Mistake Journal")
        mistake = st.text_input("What happened?")
        lesson = st.text_area("What did you learn from this?")
        if st.button("Log Mistake"):
            features.log_mistake(mistake, lesson)
            
        st.markdown("---")
        features.display_mistakes()

    elif menu == "Progress Analytics":
        st.header("📊 Progress Analytics")
        features.plot_progress()
        
        st.markdown("---")
        st.subheader("Export Data")
        features.export_data()

if __name__ == "__main__":
    main()