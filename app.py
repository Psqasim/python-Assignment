import streamlit as st
import random
import sqlite3
from typing import List, Tuple
import plotly.express as px



# Constants
QUOTES = [
    "Believe you can and you're halfway there.",
    "The only way to do great work is to love what you do.",
    "Your limitation—it's only your imagination.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones."
]

# Database Setup
class DatabaseManager:
    def __init__(self, database_name: str = "growth_mindset.db"):
        self.conn = sqlite3.connect(database_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS challenges (
                    id INTEGER PRIMARY KEY,
                    challenge TEXT NOT NULL,
                    status TEXT CHECK(status IN ('In Progress', 'Completed')) NOT NULL
                )""")
            
            try:
                result = self.conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='mistakes'
                """).fetchone()
                
                if result:
                    columns = self.conn.execute('PRAGMA table_info(mistakes)').fetchall()
                    has_created_at = any(col[1] == 'created_at' for col in columns)
                    
                    if not has_created_at:
                        self.conn.execute("""
                            CREATE TABLE mistakes_new (
                                id INTEGER PRIMARY KEY,
                                mistake TEXT NOT NULL,
                                lesson TEXT NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )""")
                        
                        self.conn.execute("""
                            INSERT INTO mistakes_new (id, mistake, lesson)
                            SELECT id, mistake, lesson FROM mistakes
                        """)
                        
                        self.conn.execute("DROP TABLE mistakes")
                        self.conn.execute("ALTER TABLE mistakes_new RENAME TO mistakes")
                else:
                    self.conn.execute("""
                        CREATE TABLE mistakes (
                            id INTEGER PRIMARY KEY,
                            mistake TEXT NOT NULL,
                            lesson TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )""")
            
            except sqlite3.Error as e:
                print(f"Database error: {e}")
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

    def update_challenge_status(self, challenge_id: int, status: str):
        self.db.execute_query(
            "UPDATE challenges SET status = ? WHERE id = ?",
            (status, challenge_id)
        )

    def get_challenges(self) -> List[Tuple]:
        return self.db.execute_query(
            "SELECT id, challenge, status FROM challenges ORDER BY id DESC"
        ).fetchall()

    def log_mistake(self, mistake: str, lesson: str):
        self.db.execute_query(
            "INSERT INTO mistakes (mistake, lesson) VALUES (?, ?)",
            (mistake, lesson)
        )

    def get_mistakes(self) -> List[Tuple]:
        return self.db.execute_query(
            "SELECT id, mistake, lesson, created_at FROM mistakes ORDER BY created_at DESC"
        ).fetchall()

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

    def growth_mindset_quiz(self):
        st.subheader("Growth Mindset Assessment")
        questions = [
            {
                "question": "Do you believe intelligence can be developed?",
                "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"],
                "correct": ["Strongly Agree", "Agree"]
            },
            {
                "question": "When faced with a challenge, do you try different strategies?",
                "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
                "correct": ["Always", "Often"]
            },
            {
                "question": "Do you see failure as an opportunity to learn?",
                "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
                "correct": ["Always", "Often"]
            },
            {
                "question": "Do you believe effort leads to improvement?",
                "options": ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"],
                "correct": ["Strongly Agree", "Agree"]
            },
            {
                "question": "When you encounter a difficult task, do you stay persistent?",
                "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
                "correct": ["Always", "Often"]
            }
        ]

        score = 0
        responses = []
        for i, q in enumerate(questions, 1):
            st.markdown(f"{i}. {q['question']}")
            response = st.radio(
                label=q["question"],
                options=q["options"],
                key=f"question_{i}",
                label_visibility="collapsed"
            )
            responses.append(response)
            if response in q["correct"]:
                score += 1

        if st.button("Submit Assessment"):
            max_score = len(questions)
            st.progress(score/max_score)
            
            if score == max_score:
                st.success("🎉 Excellent! You're fully embracing a growth mindset!")
            elif score >= max_score/2:
                st.warning("💪 Good start! Keep working on your growth mindset!")
            else:
                st.info("🌟 Awareness is the first step! Let's grow together!")

# Streamlit UI Components
def main():
    st.set_page_config(
        page_title="Growth Mindset Coach",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize components
    db = DatabaseManager()
    features = AppFeatures(db)

    # Sidebar
    with st.sidebar:
        st.title("🌱 Growth Navigator")
        menu = st.radio("Menu", [
            "Dashboard", 
            "Challenge Tracker", 
            "Mistake Journal", 
            "Progress Analytics", 
            "Mindset Assessment"
        ])
        
        st.markdown("---")
        st.markdown(f"### Today's Motivation\n💬 {features.get_random_quote()}")

    # Main Content
    if menu == "Dashboard":
        st.header("Personal Growth Dashboard")
        st.subheader("Recent Challenges")
        challenges = features.get_challenges()
        if not challenges:
            st.info("No challenges found. Add your first challenge!")

if __name__ == "__main__":
    main()
