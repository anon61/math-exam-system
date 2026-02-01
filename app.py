import streamlit as st
import sys
from pathlib import Path

# Setup Path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

from scripts.db_manager import DBManager
from scripts.build_exam import generate_exam, render_node_preview

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="Math Exam System", page_icon="📐")

# --- SESSION STATE ---
if "selected_questions" not in st.session_state:
    st.session_state.selected_questions = []
if "last_preview" not in st.session_state:
    st.session_state.last_preview = None 
if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = None

# --- DATA LOADING ---
@st.cache_data
def get_db():
    return DBManager(PROJECT_ROOT / "data")

try:
    db = get_db()
except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("🎛️ Controls")
st.sidebar.info(f"Database contains {len(db.questions)} Questions.")

# --- HELPER: PREVIEW FUNCTION ---
def show_preview(node):
    with st.spinner(f"Rendering {node.id}..."):
        img_path, error_msg = render_node_preview(node)
        
        if img_path:
            st.session_state.last_preview = img_path
        else:
            st.error(f"Rendering failed:\n{error_msg}")

# --- MAIN TABS ---
tab1, tab2 = st.tabs(["📝 Exam Builder", "📚 Knowledge Base"])

# === TAB 1: EXAM BUILDER ===
with tab1:
    col_left, col_right = st.columns([0.6, 0.4])

    with col_left:
        st.subheader("Question Bank")
        filter_topic = st.text_input("🔍 Search Topic (e.g., 'Calculus')", "")
        
        candidates = list(db.questions.values())
        if filter_topic:
            candidates = [q for q in candidates if filter_topic.lower() in (q.topic or "").lower()]

        with st.container(height=500):
            for q in candidates:
                c1, c2, c3 = st.columns([0.1, 0.7, 0.2])
                
                is_selected = q.id in st.session_state.selected_questions
                # FIX: Added label_visibility to fix warning
                if c1.checkbox("Select", key=f"chk_{q.id}", value=is_selected, label_visibility="collapsed"):
                    if q.id not in st.session_state.selected_questions:
                        st.session_state.selected_questions.append(q.id)
                elif q.id in st.session_state.selected_questions:
                    st.session_state.selected_questions.remove(q.id)
                
                c2.markdown(f"**{q.topic}** ({q.year})  \n`{q.id}`")
                
                if c3.button("👁️", key=f"btn_prev_{q.id}"):
                    show_preview(q)
                st.divider()

    with col_right:
        st.subheader("Your Exam")
        if not st.session_state.selected_questions:
            st.info("No questions selected.")
        else:
            st.write(f"Selected **{len(st.session_state.selected_questions)}** questions.")
            with st.expander("View Selected IDs"):
                st.write(st.session_state.selected_questions)
            
            if st.button("🚀 Compile PDF"):
                pdf_path = generate_exam(
                    filename="final_exam",
                    specific_ids=st.session_state.selected_questions
                )
                if pdf_path:
                    st.session_state.pdf_ready = str(pdf_path)
                    st.success("Compilation Complete!")
                else:
                    st.error("Compilation Failed.")

            if st.session_state.pdf_ready:
                with open(st.session_state.pdf_ready, "rb") as f:
                    st.download_button(
                        label="📥 Download Exam PDF",
                        data=f,
                        file_name="My_Math_Exam.pdf",
                        mime="application/pdf"
                    )

        st.subheader("Live Preview")
        if st.session_state.last_preview:
            # FIX: Fit to container + Fixed width generation = Perfect scaling
            st.image(st.session_state.last_preview, caption="Rendered Output", use_container_width=True)
        else:
            st.caption("Click the eye icon 👁️ to preview a question.")

# === TAB 2: KNOWLEDGE BASE ===
with tab2:
    st.markdown("### 📖 Browse Definitions, Tools & Mistakes")
    kb_type = st.radio("Select Category:", ["Definitions", "Tools", "Mistakes"], horizontal=True)
    
    if kb_type == "Definitions":
        items = list(db.definitions.values())
    elif kb_type == "Tools":
        items = list(db.tools.values())
    else:
        items = list(db.mistakes.values())
        
    kb_search = st.text_input("Filter Items", "")
    if kb_search:
        items = [i for i in items if kb_search.lower() in str(i.__dict__).lower()]

    k_col1, k_col2 = st.columns([0.5, 0.5])
    
    with k_col1:
        st.caption("Select an item to view:")
        for item in items:
            label = getattr(item, 'name', getattr(item, 'description', item.id))
            
            kc1, kc2 = st.columns([0.8, 0.2])
            kc1.write(f"**{item.id}**")
            kc1.caption(label[:60] + "...")
            
            if kc2.button("👁️", key=f"kb_prev_{item.id}"):
                show_preview(item)
            st.divider()

    with k_col2:
        st.subheader("Rendered View")
        if st.session_state.last_preview:
            st.image(st.session_state.last_preview, use_container_width=True)
        else:
            st.info("Select an item on the left.")