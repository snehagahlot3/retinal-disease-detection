import streamlit as st
from database import register_user, login_user

def show_auth():
    st.markdown('<style>[data-testid="stSidebar"]{display:none}</style>', unsafe_allow_html=True)
    st.markdown("""
    <style>
    .auth-container {
        max-width: 420px; margin: 2rem auto; padding: 2.5rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        backdrop-filter: blur(20px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }
    .brand-icon {
        width: 44px; height: 44px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        color: white; font-weight: 700; font-size: 1.2rem;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5);
    }
    .brand-name {
        font-size: 1.5rem; font-weight: 700; color: #f1f5f9;
        letter-spacing: -0.02em;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style='text-align:center;margin:1.5rem 0 2rem;'>
            <div style='display:inline-flex;align-items:center;gap:14px;'>
                <span style='font-size:1.5rem;font-weight:700;color:#f1f5f9;letter-spacing:-0.02em;'>RetinalScan</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Sign In", "Create Account"])

        with tab1:
            st.markdown("#### Welcome Back")
            email = st.text_input("Email address", key="login_email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
            if st.button("Sign In", use_container_width=True, type="primary"):
                if email and password:
                    ok, result = login_user(email, password)
                    if ok:
                        st.session_state.user = result
                        st.session_state.page = "home"
                        st.rerun()
                    else:
                        st.error(result)
                else:
                    st.warning("Please fill in all fields.")

        with tab2:
            st.markdown("#### Create Account")
            name = st.text_input("Full name", key="reg_name", placeholder="Jane Smith")
            email2 = st.text_input("Email address", key="reg_email", placeholder="you@example.com")
            pass2 = st.text_input("Password", type="password", key="reg_pass", placeholder="Min. 6 characters")
            if st.button("Create Account", use_container_width=True, type="primary"):
                if name and email2 and pass2:
                    if len(pass2) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        ok, msg = register_user(name, email2, pass2)
                        if ok:
                            st.success(msg + " Please sign in.")
                        else:
                            st.error(msg)
                else:
                    st.warning("Please fill in all fields.")