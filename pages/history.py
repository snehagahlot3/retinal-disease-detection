import streamlit as st
import json
from database import get_history
from datetime import datetime

colors = {
    "No DR": "#22c55e", "Mild": "#facc15",
    "Moderate": "#f97316", "Severe": "#ef4444", "Proliferative": "#dc2626",
    "Normal": "#22c55e", "Diabetic Retinopathy": "#f97316", "Glaucoma": "#ef4444",
    "Cataract": "#3b82f6", "Age-related Macular Degeneration": "#a855f7",
    "Hypertensive Retinopathy": "#06b6d4", "Myopia": "#14b8a6", "Other": "#6b7280"
}

def show():
    st.markdown("""
    <style>
    .hist-header { 
        font-size: 2rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.5rem; 
        letter-spacing: -0.02em;
    }
    .hist-sub { color: rgba(199, 210, 254, 0.6); margin-bottom: 2rem; font-size: 1rem; }
    .hist-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.25rem 1.5rem; margin-bottom: 0.75rem;
        display: flex; align-items: center; justify-content: space-between;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }
    .hist-card:hover {
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(139, 92, 246, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
    }
    .hist-diag { font-weight: 600; font-size: 1.05rem; color: #f1f5f9; }
    .hist-meta { font-size: 0.85rem; color: rgba(199, 210, 254, 0.5); margin-top: 4px; }
    .hist-badge {
        padding: 6px 16px; border-radius: 999px;
        font-size: 0.85rem; font-weight: 600; color: white;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        background: rgba(255, 255, 255, 0.02);
        border: 2px dashed rgba(99, 102, 241, 0.2);
        border-radius: 20px;
    }
    .empty-icon { font-size: 3rem; margin-bottom: 1rem; }
    .empty-text { color: rgba(199, 210, 254, 0.5); font-size: 1rem; }
    .prob-row {
        display: flex; align-items: center; gap: 12px; margin: 8px 0;
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
    }
    .prob-label { width: 180px; font-size: 0.85rem; color: #e2e8f0; font-weight: 500; }
    .prob-bar-bg { flex: 1; background: rgba(255, 255, 255, 0.1); height: 8px; border-radius: 8px; }
    .prob-val { width: 50px; text-align: right; font-size: 0.85rem; color: #818cf8; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="hist-header">Scan History</div>', unsafe_allow_html=True)
    st.markdown('<div class="hist-sub">All your previous retinal scans.</div>', unsafe_allow_html=True)

    rows = get_history(st.session_state.user["id"])

    if not rows:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">Scan</div>
            <div class="empty-text">No scans yet. Upload your first retinal image to get started.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start First Scan", type="primary"):
            st.session_state.page = "predict"
            st.rerun()
        return

    st.markdown(f"**{len(rows)} scan(s) found**")
    st.markdown("<br>", unsafe_allow_html=True)

    for row in rows:
        _, user_id, diagnosis, confidence, probs_json, image_name, created_at = row
        color = colors.get(diagnosis, "#818cf8")
        try:
            dt = datetime.fromisoformat(created_at).strftime("%b %d, %Y at %I:%M %p")
        except:
            dt = created_at

        st.markdown(f"""
        <div class="hist-card">
            <div>
                <div class="hist-diag">{diagnosis}</div>
                <div class="hist-meta">{image_name} · {dt}</div>
            </div>
            <div class="hist-badge">{confidence:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("View probabilities"):
            probs = json.loads(probs_json)
            for cls, prob in probs.items():
                clr = colors.get(cls, "#4b5563")
                pct = prob
                st.markdown(f"""
                <div class="prob-row">
                    <div class="prob-label">{cls}</div>
                    <div class="prob-bar-bg">
                        <div style="width:{pct}%;background:linear-gradient(90deg,{clr},#22d3ee);height:8px;border-radius:8px;"></div>
                    </div>
                    <div class="prob-val">{pct:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)