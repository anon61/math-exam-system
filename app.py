import streamlit as st
import sys
from pathlib import Path

# Add project root to path so we can import scripts
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

from scripts.db_manager import DBManager
from scripts.build_exam import generate_exam, render_preview

# --- 1. CONFIGURATION & STATE ---
st.set_page_config(page_title="Math Exam Pro", page_icon="✨", layout="wide")

# Initialize session state for selections and previews
if 'selected_ids' not in st.session_state:
    st.session_state['selected_ids'] = []
if 'last_previewed' not in st.session_state:
    st.session_state['last_previewed'] = None
if 'preview_svg' not in st.session_state:
    st.session_state['preview_svg'] = None
if 'preview_error' not in st.session_state:
    st.session_state['preview_error'] = None

# --- 2. DATA LOADING ---
@st.cache_data
def load_data():
    """Cached loader for the question database."""
    db = DBManager(PROJECT_ROOT / "data")
    questions = list(db.questions.values())
    # Sort for consistent display
    return sorted(questions, key=lambda q: (q.year, q.topic, q.id), reverse=True)

try:
    all_questions = load_data()
    topics = sorted(list(set(q.topic for q in all_questions if q.topic)))
    years = sorted(list(set(q.year for q in all_questions if q.year)), reverse=True)
    lecturers = sorted(list(set(q.lecturer for q in all_questions if q.lecturer)))
except Exception as e:
    st.error(f"Failed to load database: {e}")
    st.stop()

# --- 3. SIDEBAR FILTERS ---
st.sidebar.title("🔍 Filter Questions")
selected_topics = st.sidebar.multiselect("Topics", topics, default=st.session_state.get('topics_filter'))
selected_years = st.sidebar.multiselect("Years", years, default=st.session_state.get('years_filter'))
selected_lecturers = st.sidebar.multiselect("Lecturers", lecturers, default=st.session_state.get('lecturers_filter'))

# Persist filters
st.session_state['topics_filter'] = selected_topics
st.session_state['years_filter'] = selected_years
st.session_state['lecturers_filter'] = selected_lecturers


# --- 4. FILTERING LOGIC ---
filtered_questions = all_questions
if selected_topics:
    filtered_questions = [q for q in filtered_questions if q.topic in selected_topics]
if selected_years:
    filtered_questions = [q for q in filtered_questions if q.year in selected_years]
if selected_lecturers:
    filtered_questions = [q for q in filtered_questions if q.lecturer in selected_lecturers]


# --- 5. UI LAYOUT ---
st.title("🚀 Math Exam Pro")
st.markdown("Advanced filtering and live previews.")

col1, col2 = st.columns([0.5, 0.5])

# --- COLUMN 1: QUESTION BROWSER ---
with col1:
    st.header(f"Browse Questions ({len(filtered_questions)})")
    
    for q in filtered_questions:
        with st.container():
            is_selected = q.id in st.session_state.selected_ids
            
            sub_col1, sub_col2, sub_col3 = st.columns([0.1, 0.7, 0.2])
            
            with sub_col1:
                st.checkbox("", value=is_selected, key=f"cb_{q.id}", disabled=True) # Visually disabled, logic is manual

            with sub_col2:
                st.markdown(f"**{q.topic or 'General'}** ({q.year or 'N/A'}) - {q.lecturer or 'N/A'}")
                st.caption(f"`{q.id}`")

            with sub_col3:
                # Preview Button
                if st.button("👁️ Preview", key=f"preview_{q.id}"):
                    st.session_state.last_previewed = q.id
                    with st.spinner("Rendering SVG..."):
                        svg_path, error_msg = render_preview(q, PROJECT_ROOT)
                        if svg_path:
                            st.session_state.preview_svg = str(svg_path)
                            st.session_state.preview_error = None
                        else:
                            st.session_state.preview_svg = None
                            st.session_state.preview_error = error_msg
                
                # Add/Remove Button
                if is_selected:
                    if st.button("➖ Remove", key=f"rem_{q.id}"):
                        st.session_state.selected_ids.remove(q.id)
                        st.rerun()
                else:
                    if st.button("➕ Add", key=f"add_{q.id}"):
                        st.session_state.selected_ids.append(q.id)
                        st.rerun()

            st.divider()

# --- COLUMN 2: CART & PREVIEW ---
with col2:
    # --- Shopping Cart ---
    st.header("🛒 Exam Cart")
    if not st.session_state.selected_ids:
        st.info("Your cart is empty. Add questions from the browser on the left.")
    else:
        st.markdown(f"You have selected **{len(st.session_state.selected_ids)}** questions.")
        for qid in st.session_state.selected_ids:
            st.caption(f"- `{qid}`")
        
        if st.button("🚀 Compile Exam PDF", type="primary"):
            if not st.session_state.selected_ids:
                st.warning("Please select at least one question!")
            else:
                with st.spinner("Compiling Typst Document..."):
                    pdf_path = generate_exam(
                        filename="web_exam",
                        specific_ids=st.session_state.selected_ids
                    )
                    if pdf_path and pdf_path.exists():
                        st.success("Exam Generated Successfully!")
                        with open(pdf_path, "rb") as f:
                            st.download_button("📥 Download PDF", f.read(), "exam.pdf", "application/pdf")
                    else:
                        st.error("Compilation failed. Check terminal logs.")

    st.divider()
    
    # --- Live Preview ---
    st.header("🖼️ Live Preview")
    if st.session_state.last_previewed:
        st.caption(f"Showing preview for: `{st.session_state.last_previewed}`")
        
        if st.session_state.preview_svg:
            st.image(st.session_state.preview_svg)
        elif st.session_state.preview_error:
            st.error("Failed to render preview. Error log:")
            st.code(st.session_state.preview_error, language="bash")
        else:
            st.info("Click a 'Preview' button to see the question here.")
    else:
        st.info("Click 'Preview' on any question to see it here.")