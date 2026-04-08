import streamlit as st

def show():
    st.markdown("""
    <style>
    .hero { padding: 3rem 0 2rem; text-align: center; }
    .hero h1 { 
        font-size: 2.75rem; font-weight: 700; color: #f1f5f9; line-height: 1.2; margin-bottom: 1rem; 
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #818cf8 0%, #22d3ee 50%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero p { font-size: 1.1rem; color: rgba(199, 210, 254, 0.7); max-width: 580px; margin: 0 auto 2rem; line-height: 1.7; }
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
        border: 1px solid rgba(139, 92, 246, 0.3); 
        color: #a5b4fc;
        padding: 8px 20px; border-radius: 999px; font-size: 0.8rem;
        font-weight: 600; margin-bottom: 1.5rem; letter-spacing: 0.1em;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.2);
    }
    .feature-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem; 
        height: 100%;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(139, 92, 246, 0.3);
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.15);
    }
    .feature-icon {
        width: 48px; height: 48px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3), rgba(139, 92, 246, 0.2));
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.3rem;
        margin-bottom: 1rem;
    }
    .feature-title { font-weight: 600; color: #f1f5f9; font-size: 1.05rem; margin-bottom: 0.5rem; }
    .feature-desc { color: rgba(199, 210, 254, 0.6); font-size: 0.9rem; line-height: 1.6; }
    .stat-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.05));
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 20px; 
        padding: 1.5rem; 
        text-align: center;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }
    .stat-card:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.2);
    }
    .stat-num { 
        font-size: 2rem; font-weight: 700; 
        background: linear-gradient(135deg, #818cf8, #22d3ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .stat-label { color: rgba(199, 210, 254, 0.7); font-size: 0.85rem; margin-top: 0.5rem; letter-spacing: 0.02em; }
    .section-title {
        font-size: 1.4rem; font-weight: 600; color: #e2e8f0;
        margin: 2.5rem 0 1.5rem; text-align: center; letter-spacing: -0.01em;
    }
    .disclaimer {
        margin-top: 3rem; 
        padding: 1.25rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        text-align: center;
    }
    .disclaimer-text { 
        font-size: 0.85rem; 
        color: rgba(199, 210, 254, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

    name = st.session_state.user["name"].split()[0]

    st.markdown(f"""
    <div class="hero">
        <div class="badge">AI-POWERED SCREENING</div>
        <h1>Hello, {name}.<br>Early detection saves vision.</h1>
        <p>Upload a retinal fundus image and get instant AI-powered analysis for 8 different eye diseases including diabetic retinopathy, glaucoma, cataract, and more.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start New Scan", type="primary", use_container_width=False):
        st.session_state.page = "predict"
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    stats = [("82%", "Accuracy"), ("8", "Disease Classes"), ("6,393", "Training Images"), ("< 3s", "Scan Time")]
    for col, (num, label) in zip([c1,c2,c3,c4], stats):
        col.markdown(f"""
        <div class="stat-card">
            <div class="stat-num">{num}</div>
            <div class="stat-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>How it works</div>", unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("Upload", "Drag and drop your retinal fundus photograph."),
        ("Analyze", "EfficientNetB3 model processes the image instantly."),
        ("Results", "Get diagnosis for 8 conditions with confidence scores."),
        ("History", "All your scans are saved for future reference."),
    ]
    for col, (title, desc) in zip([f1,f2,f3,f4], features):
        col.markdown(f"""
        <div class="feature-card">
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
        <div class="disclaimer-text">RetinalScan is for educational and screening purposes only. Always consult a qualified ophthalmologist.</div>
    </div>
    """, unsafe_allow_html=True)