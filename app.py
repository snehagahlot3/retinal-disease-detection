import streamlit as st
from database import init_db
from auth import show_auth

st.set_page_config(page_title="RetinalScan", layout="wide", initial_sidebar_state="collapsed")
st.markdown('<style>[data-testid="stSidebarNav"]{display:none}</style>', unsafe_allow_html=True)

# Global styles - Modern Futuristic Dark Theme with Glassmorphism
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { 
    font-family: 'Inter', sans-serif; 
}

/* Dark gradient background with glowing shapes */
.stApp {
    background: 
        radial-gradient(ellipse at 20% 20%, rgba(79, 70, 229, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(6, 182, 212, 0.12) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(124, 58, 237, 0.08) 0%, transparent 60%),
        linear-gradient(180deg, #0a0a1a 0%, #0f0f2a 50%, #0a0a1a 100%);
    background-attachment: fixed;
    color: #e2e8f0;
    min-height: 100vh;
}

/* Animated gradient orbs in background */
.stApp::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: 
        radial-gradient(circle at 30% 30%, rgba(99, 102, 241, 0.03) 0%, transparent 40%),
        radial-gradient(circle at 70% 70%, rgba(6, 182, 212, 0.03) 0%, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.02) 0%, transparent 50%);
    animation: float 20s ease-in-out infinite;
    z-index: -1;
    pointer-events: none;
}

@keyframes float {
    0%, 100% { transform: translate(0, 0) rotate(0deg); }
    50% { transform: translate(-2%, 2%) rotate(1deg); }
}

/* Glassmorphism container */
.block-container {
    padding-top: 2rem; max-width: 1000px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 24px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 
        0 25px 50px -12px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(15, 15, 35, 0.95) 0%, rgba(10, 10, 25, 0.98) 100%) !important;
    border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    width: 280px !important;
}

/* Sidebar buttons */
.stSidebar .stButton > button {
    background: rgba(99, 102, 241, 0.1) !important;
    border: 1px solid rgba(99, 102, 241, 0.2) !important;
    color: #c7d2fe !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
    margin-bottom: 8px !important;
}

.stSidebar .stButton > button:hover {
    background: rgba(99, 102, 241, 0.25) !important;
    border-color: rgba(129, 140, 248, 0.5) !important;
    transform: translateX(4px);
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.3) !important;
}

/* Primary buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%) !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    color: white !important;
    padding: 0.875rem 1.5rem !important;
    box-shadow: 
        0 4px 15px rgba(99, 102, 241, 0.4),
        0 0 30px rgba(139, 92, 246, 0.2) !important;
    transition: all 0.3s ease !important;
}

.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 
        0 8px 25px rgba(99, 102, 241, 0.5),
        0 0 40px rgba(139, 92, 246, 0.3) !important;
}

/* Input fields */
.stTextInput > div > div {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(99, 102, 241, 0.2) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div:focus-within {
    border-color: rgba(139, 92, 246, 0.5) !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.2) !important;
}

.stTextInput input::placeholder {
    color: rgba(226, 232, 240, 0.4) !important;
}

/* File uploader */
div[data-testid="stFileUploader"] {
    border: 2px dashed rgba(99, 102, 241, 0.3) !important;
    border-radius: 16px !important;
    padding: 2rem !important;
    background: rgba(99, 102, 241, 0.03) !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stFileUploader"]:hover {
    border-color: rgba(139, 92, 246, 0.5) !important;
    background: rgba(99, 102, 241, 0.08) !important;
    box-shadow: 0 0 30px rgba(139, 92, 246, 0.15) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(255, 255, 255, 0.03);
    border-radius: 12px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 10px !important;
    color: rgba(226, 232, 240, 0.6) !important;
    font-weight: 500 !important;
    padding: 0.75rem 1.25rem !important;
    border: none !important;
    transition: all 0.3s ease !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
}

/* Headings */
h1, h2, h3, h4 {
    font-weight: 600 !important;
    color: #f1f5f9 !important;
    letter-spacing: -0.02em !important;
}

h1 { font-size: 2.25rem !important; }
h2 { font-size: 1.75rem !important; }
h3 { font-size: 1.25rem !important; }

/* Cards and panels */
.disease-card, .result-card, .action-box {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    transition: all 0.3s ease !important;
}

.disease-card:hover, .result-card:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
    box-shadow: 0 8px 30px rgba(99, 102, 241, 0.2) !important;
    transform: translateY(-2px);
}

/* Spinner */
.stSpinner {
    color: #8b5cf6 !important;
}

/* Progress bars */
.stProgress > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4) !important;
    border-radius: 10px !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    color: #c7d2fe !important;
    font-weight: 500 !important;
}

.streamlit-expanderHeader:hover {
    background: rgba(99, 102, 241, 0.1) !important;
    border-color: rgba(139, 92, 246, 0.3) !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.3);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(139, 92, 246, 0.5);
}

/* Selection */
::selection {
    background: rgba(139, 92, 246, 0.4);
    color: white;
}
</style>
""", unsafe_allow_html=True)

init_db()

if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

if not st.session_state.user:
    show_auth()
else:
    # Sidebar navigation
    with st.sidebar:
        user = st.session_state.user
        initials = "".join([n[0].upper() for n in user["name"].split()[:2]])

        st.markdown("""
        <div style='display:flex;align-items:center;gap:12px;padding:1rem 1rem 1.5rem;border-bottom:1px solid rgba(99,102,241,0.15);margin-bottom:1rem;'>
            <div style='width:40px;height:40px;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:12px;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:1.1rem;box-shadow:0 4px 15px rgba(99,102,241,0.4);'>R</div>
            <span style='font-weight:700;font-size:1.15rem;color:white;letter-spacing:-0.02em;'>RetinalScan</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
        if st.button("New Scan", use_container_width=True):
            st.session_state.page = "predict"
            st.rerun()
        if st.button("History", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()

        st.markdown("<br>"*6, unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.1));border:1px solid rgba(139,92,246,0.2);border-radius:16px;padding:1rem;'>
            <div style='display:flex;align-items:center;gap:12px;'>
                <div style='width:40px;height:40px;background:linear-gradient(135deg,#8b5cf6,#06b6d4);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:0.9rem;box-shadow:0 4px 15px rgba(139,92,246,0.4);'>{initials}</div>
                <div>
                    <div style='font-size:0.9rem;font-weight:600;color:white;'>{user["name"]}</div>
                    <div style='font-size:0.75rem;color:rgba(199,210,254,0.7);'>{user["email"]}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = "home"
            st.rerun()

    # Page routing
    page = st.session_state.page
    if page == "home":
        from pages.home import show
        show()
    elif page == "predict":
        from pages.predict import show
        show()
    elif page == "history":
        from pages.history import show
        show()