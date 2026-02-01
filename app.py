import streamlit as st
import sys
from pathlib import Path

# Add project root to path so we can import scripts
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

from scripts.db_manager import DBManager
from scripts.build_exam import generate_exam

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Math Exam Cockpit",
    page_icon="🎓",
    layout="wide"
)

# --- SIDEBAR: SETTINGS ---
st.sidebar.title("🎛️ Exam Controls")
exam_title = st.sidebar.text_input("Exam Title", "Final Examination 2026")
filter_topic = st.sidebar.text_input("Filter by Topic", "")

# --- MAIN: DATA LOADING ---
st.title("🎓 Professor's Cockpit")
st.markdown("Select questions below to build your exam.")

@st.cache_data
def load_data():
    """Cached loader to prevent re-reading YAML on every click."""
    db = DBManager(PROJECT_ROOT / "data")
    return db

try:
    db = load_data()
    questions = list(db.questions.values())
    
    # Filter Logic
    if filter_topic:
        questions = [q for q in questions if q.topic and filter_topic.lower() in q.topic.lower()]
        
    st.info(f"Loaded {len(questions)} questions from the database.")
    
except Exception as e:
    st.error(f"Failed to load database: {e}")
    st.stop()

# --- QUESTION BROWSER (THE SHOPPING CART) ---
# We use a form to batch the selection
with st.form("exam_builder"):
    selected_ids = []
    
    # Create a nice grid
    for q in questions:
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            # unique key needed for every checkbox
            if st.checkbox("", key=q.id):
                selected_ids.append(q.id)
        with col2:
            st.markdown(f"**{q.topic}** ({q.year})")
            # Show a preview of the content (stripping the block scalar |)
            preview = q.given[:100] + "..." if q.given and len(q.given) > 100 else q.given
            st.caption(f"{q.id} | {preview}")
        st.divider()
    
    # --- ACTION BUTTON ---
    submitted = st.form_submit_button("🚀 Compile Exam PDF")

# --- COMPILATION LOGIC ---
if submitted:
    if not selected_ids:
        st.warning("Please select at least one question!")
    else:
        with st.spinner("Compiling Typst Document..."):
            # Call the backend script
            pdf_path = generate_exam(
                filename="web_exam",
                specific_ids=selected_ids
            )
            
            if pdf_path and pdf_path.exists():
                st.success("Exam Generated Successfully!")
                
                # Read PDF for download
                with open(pdf_path, "rb") as f:
                    pdf_data = f.read()
                    
                st.download_button(
                    label="📥 Download Exam PDF",
                    data=pdf_data,
                    file_name="my_exam.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Compilation failed. Check the terminal logs.")
