import streamlit as st
import sys
import os
from pathlib import Path

# --- 1. PAGE CONFIG (Must be first) ---
st.set_page_config(layout="wide", page_title="Math Exam System", page_icon="📐")

# --- 2. SETUP PATHS ---
# Ensure we can import from 'scripts' regardless of where 'streamlit run' is called
current_file = Path(__file__).resolve()
PROJECT_ROOT = current_file.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Now we can safely import
from scripts.db_manager import DBManager
from scripts.build_exam import generate_exam, render_node_preview

# --- 3. SESSION STATE ---
if "selected_questions" not in st.session_state:
    st.session_state.selected_questions = []
if "last_preview" not in st.session_state:
    st.session_state.last_preview = None 
if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = None
if "key_ready" not in st.session_state:
    st.session_state.key_ready = None

# --- 4. DATA LOADING ---
@st.cache_data
def get_db():
    # Defensive: Check if data dir exists
    data_path = PROJECT_ROOT / "data"
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found at: {data_path}")
    return DBManager(data_path)

try:
    db = get_db()
except Exception as e:
    st.error(f"❌ **Database Initialization Failed**\n\n{e}")
    st.stop()

# --- 5. SIDEBAR ---
st.sidebar.title("🎛️ Controls")
st.sidebar.info(f"Loaded {len(db.questions)} Questions.")
if st.sidebar.button("Refresh Database"):
    st.cache_data.clear()
    st.rerun()

# --- 6. PREVIEW HELPER ---
def show_preview(node):
    """Handles logic to call the renderer and update state"""
    with st.spinner(f"Generating preview for {node.id}..."):
        img_path, error_msg = render_node_preview(node)
        
        if img_path:
            st.session_state.last_preview = img_path
        else:
            st.error(f"Rendering failed:\n{error_msg}")

# --- 7. TABS ---
tab1, tab2 = st.tabs(["📝 Exam Builder", "📚 Knowledge Base"])

# === TAB 1: EXAM BUILDER ===
with tab1:
    col_left, col_right = st.columns([0.6, 0.4])

    with col_left:
        st.subheader("Question Bank")
        filter_topic = st.text_input("🔍 Filter by Topic", "")
        
        candidates = list(db.questions.values())
        if filter_topic:
            candidates = [q for q in candidates if filter_topic.lower() in (q.topic or "").lower()]

        st.caption(f"Showing {len(candidates)} questions")
        
        # Scrollable container
        with st.container(height=500):
            for q in candidates:
                c1, c2, c3 = st.columns([0.1, 0.7, 0.2])
                
                # Checkbox for selection
                is_selected = q.id in st.session_state.selected_questions
                
                # Update state based on interaction
                if c1.checkbox("Select", key=f"chk_{q.id}", value=is_selected, label_visibility="collapsed"):
                    if q.id not in st.session_state.selected_questions:
                        st.session_state.selected_questions.append(q.id)
                else:
                     if q.id in st.session_state.selected_questions:
                        st.session_state.selected_questions.remove(q.id)
                
                c2.markdown(f"**{q.topic}** ({q.year or 'N/A'})  \n`{q.id}`")
                
                if c3.button("👁️", key=f"btn_prev_{q.id}"):
                    show_preview(q)
                st.divider()

    with col_right:
        st.subheader("Your Exam")
        if not st.session_state.selected_questions:
            st.info("No questions selected. Check boxes on the left.")
        else:
            st.write(f"Selected **{len(st.session_state.selected_questions)}** questions.")
            with st.expander("View Selected IDs"):
                st.write(st.session_state.selected_questions)
            
            if st.button("🚀 Compile Exam & Key"):
                with st.spinner("Compiling PDF..."):
                    path_std, path_key = generate_exam(
                        filename="final_exam",
                        specific_ids=st.session_state.selected_questions
                    )
                    if path_std and path_key:
                        st.session_state.pdf_ready = str(path_std)
                        st.session_state.key_ready = str(path_key)
                        st.success("Compilation Successful!")
                    else:
                        st.error("Compilation Failed. Check console logs.")

            # DOWNLOAD BUTTONS
            if st.session_state.pdf_ready and os.path.exists(st.session_state.pdf_ready):
                with open(st.session_state.pdf_ready, "rb") as f:
                    st.download_button(
                        label="📄 Download Student Version",
                        data=f,
                        file_name="Math_Exam.pdf",
                        mime="application/pdf"
                    )

            if st.session_state.key_ready and os.path.exists(st.session_state.key_ready):
                with open(st.session_state.key_ready, "rb") as f:
                    st.download_button(
                        label="🔑 Download Solution Key",
                        data=f,
                        file_name="Math_Exam_Key.pdf",
                        mime="application/pdf"
                    )

        st.subheader("Live Preview")
        if st.session_state.last_preview and os.path.exists(st.session_state.last_preview):
            st.image(st.session_state.last_preview, caption="Rendered Output", use_container_width=True)
        else:
            st.caption("Click the eye icon 👁️ to preview a question.")

# === TAB 2: KNOWLEDGE BASE ===
with tab2:
    st.markdown("### 📖 Knowledge Base Explorer")
    kb_type = st.radio("Select Category:", ["Definitions", "Tools", "Mistakes"], horizontal=True)
    
    if kb_type == "Definitions":
        items = list(db.definitions.values())
    elif kb_type == "Tools":
        items = list(db.tools.values())
    else:
        items = list(db.mistakes.values())
        
    kb_search = st.text_input("Filter Items by Content", "")
    if kb_search:
        items = [i for i in items if kb_search.lower() in str(i.__dict__).lower()]

    k_col1, k_col2 = st.columns([0.5, 0.5])
    
    with k_col1:
        st.caption(f"Found {len(items)} items")
        with st.container(height=600):
            for item in items:
                label = getattr(item, 'name', getattr(item, 'description', item.id))
                
                kc1, kc2 = st.columns([0.8, 0.2])
                kc1.markdown(f"**{item.id}**")
                kc1.caption(f"{str(label)[:60]}...")
                
                if kc2.button("👁️", key=f"kb_prev_{item.id}"):
                    show_preview(item)
                st.divider()

    with k_col2:
        st.subheader("Rendered View")
        if st.session_state.last_preview and os.path.exists(st.session_state.last_preview):
            st.image(st.session_state.last_preview, use_container_width=True)
        else:
            st.info("Select an item on the left to view.")