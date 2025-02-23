import streamlit as st
import random
import pandas as pd
import sqlite3
import plotly.express as px
from typing import List, Tuple

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

# Database Setup
class DatabaseManager:
    def __init__(self, database_name: str = "growth_mindset.db"):
        self.conn = sqlite3.connect(database_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS challenges (
                    id INTEGER PRIMARY KEY,
                    challenge TEXT NOT NULL,
                    status TEXT CHECK(status IN ('In Progress', 'Completed')) NOT NULL
                )""")
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS mistakes (
                    id INTEGER PRIMARY KEY,
                    mistake TEXT NOT NULL,
                    lesson TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""")

    def execute_query(self, query: str, params: Tuple = None):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(query, params or ())
            return cursor

    def __del__(self):
        self.conn.close()

# Core Functionality
class AppFeatures:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_random_quote(self) -> str:
        return random.choice(QUOTES)

    def add_challenge(self, challenge: str):
        self.db.execute_query(
            "INSERT INTO challenges (challenge, status) VALUES (?, ?)",
            (challenge, "In Progress")
        )
        st.success("✅ Challenge added successfully!")
        st.rerun()

    def update_challenge_status(self, challenge_id: int, status: str):
        self.db.execute_query(
            "UPDATE challenges SET status = ? WHERE id = ?",
            (status, challenge_id)
        )
        st.success("✅ Challenge status updated!")
        st.rerun()

    def get_challenges(self) -> List[Tuple]:
        return self.db.execute_query(
            "SELECT id, challenge, status FROM challenges ORDER BY id DESC"
        ).fetchall()

    def delete_challenge(self, challenge_id: int):
        self.db.execute_query(
            "DELETE FROM challenges WHERE id = ?", (challenge_id,)
        )
        st.warning("❌ Challenge deleted!")
        st.rerun()

    def log_mistake(self, mistake: str, lesson: str):
        self.db.execute_query(
            "INSERT INTO mistakes (mistake, lesson) VALUES (?, ?)",
            (mistake, lesson)
        )
        st.success("✅ Mistake logged successfully!")
        st.rerun()

    def get_mistakes(self) -> List[Tuple]:
        return self.db.execute_query(
            "SELECT id, mistake, lesson, created_at FROM mistakes ORDER BY created_at DESC"
        ).fetchall()

    def delete_mistake(self, mistake_id: int):
        self.db.execute_query(
            "DELETE FROM mistakes WHERE id = ?", (mistake_id,)
        )
        st.warning("❌ Mistake deleted!")
        st.rerun()

    def export_data(self, table_name: str):
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, self.db.conn)
        st.download_button(
            label=f"📥 Download {table_name.capitalize()} Data",
            data=df.to_csv(index=False),
            file_name=f"{table_name}_data.csv",
            mime="text/csv",
        )

    def plot_progress(self):
        challenges = self.get_challenges()
        if not challenges:
            st.info("No challenges found. Add some to track your progress!")
            return

        status_counts = {"Completed": 0, "In Progress": 0}
        for _, _, status in challenges:
            status_counts[status] += 1

        fig = px.pie(
            names=list(status_counts.keys()),
            values=list(status_counts.values()),
            title="Challenge Progress Distribution",
            color_discrete_sequence=["#28a745", "#ff851b"]
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

# Streamlit UI Components
def main():
    st.set_page_config(
        page_title="Growth Mindset Coach",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    db = DatabaseManager()
    features = AppFeatures(db)

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

        dark_mode = st.toggle("🌙 Dark Mode")
        if dark_mode:
            st.markdown(
                """
                <style>
                body { background-color: #121212; color: white; }
                .stApp { background-color: #121212; }
                .css-1aumxhk { background-color: #121212 !important; }
                </style>
                """, unsafe_allow_html=True
            )

    if menu == "Dashboard":
        st.header("Personal Growth Dashboard")
        st.subheader("Recent Challenges")
        challenges = features.get_challenges()
        if not challenges:
            st.info("No challenges found. Add your first challenge!")

    elif menu == "Challenge Tracker":
        st.header("📌 Challenge Tracker")
        new_challenge = st.text_input("Add a new challenge:")
        if st.button("Add Challenge"):
            features.add_challenge(new_challenge)

    elif menu == "Mistake Journal":
        st.header("📝 Mistake Journal")
        mistake = st.text_input("Log a mistake:")
        lesson = st.text_area("Lesson learned:")
        if st.button("Log Mistake"):
            features.log_mistake(mistake, lesson)

    elif menu == "Progress Analytics":
        st.header("📊 Progress Analytics")
        features.plot_progress()
        st.subheader("Export Data")
        features.export_data("challenges")
        features.export_data("mistakes")

if __name__ == "__main__":
    main()
