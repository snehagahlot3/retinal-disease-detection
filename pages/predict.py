import streamlit as st
import tensorflow as tf
import numpy as np
import json
import cv2
from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess
from tensorflow.keras import backend as K
from PIL import Image
from database import save_prediction

@st.cache_resource
def load_dr_model():
    model = tf.keras.models.load_model('models/best_model.h5', compile=False)
    model.compile(optimizer='adam', loss='categorical_crossentropy')
    with open('class_names.json') as f:
        classes = json.load(f)
    return model, classes

@st.cache_resource
def load_odir_model():
    model = tf.keras.models.load_model('models/odir_model.keras')
    with open('models/odir_labels.json') as f:
        labels = json.load(f)
    return model, labels

def preprocess_dr(img):
    img = img.convert('RGB').resize((224, 224))
    arr = np.array(img).astype(np.float32)
    arr = efficientnet_preprocess(arr)
    return np.expand_dims(arr, axis=0)

def preprocess_odir(img):
    img = img.convert('RGB').resize((224, 224))
    arr = np.array(img).astype(np.float32)
    arr = efficientnet_preprocess(arr)
    return np.expand_dims(arr, axis=0)

def get_gradcam_heatmap(model, img_array, target_class_idx=0):
    try:
        arr_tf = tf.constant(img_array, dtype=tf.float32)
        
        preds = model(arr_tf, training=False)
        
        if target_class_idx == 0:
            target_class_idx = int(tf.argmax(preds[0]))
        
        with tf.GradientTape() as tape:
            tape.watch(arr_tf)
            preds = model(arr_tf, training=False)
            loss = preds[0, target_class_idx]
        
        grads_input = tape.gradient(loss, arr_tf)
        
        if grads_input is None:
            return None
        
        # Average across RGB channels to get single channel heatmap
        heatmap = tf.reduce_mean(grads_input, axis=-1).numpy()
        heatmap = heatmap[0]  # Remove batch dimension
        
        # Resize to original image size
        heatmap = cv2.resize(heatmap, (224, 224))
        
        heatmap = np.maximum(heatmap, 0)
        heatmap /= (heatmap.max() + 1e-8)
        
        return heatmap
    except Exception as e:
        return None

def overlay_heatmap(img_pil, heatmap, alpha=0.4):
    img = img_pil.convert('RGB').resize((224, 224))
    img_arr = np.array(img)
    
    heatmap_resized = cv2.resize(heatmap, (224, 224))
    heatmap_uint8 = np.uint8(255 * heatmap_resized)
    
    heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)
    
    overlay = np.uint8(alpha * heatmap_color + (1 - alpha) * img_arr)
    
    return Image.fromarray(overlay)

dr_descriptions = {
    "No DR": {
        "desc": "No diabetic retinopathy detected. The retina appears healthy with normal vessel structure.",
        "findings": ["Normal vessel structure", "No microaneurysms detected", "Healthy optic disc"],
        "action": "Continue routine annual eye examinations. Maintain healthy blood sugar levels."
    },
    "Mild": {
        "desc": "Early-stage diabetic retinopathy detected. Small microaneurysms are present in the retinal vasculature.",
        "findings": ["Microaneurysms present", "No significant vessel changes", "Early signs of retinal stress"],
        "action": "Schedule an ophthalmology visit within 3-6 months. Monitor blood sugar closely and maintain glycemic control."
    },
    "Moderate": {
        "desc": "Moderate diabetic retinopathy detected. Some retinal blood vessels show damage and leakage.",
        "findings": ["Multiple microaneurysms", "Hard exudates detected", "Retinal vessel abnormalities"],
        "action": "Consult an ophthalmologist within 1-3 months. Treatment options may include laser therapy or anti-VEGF injections."
    },
    "Severe": {
        "desc": "Severe diabetic retinopathy detected. Significant vessel blockage and retinal ischemia present.",
        "findings": ["Extensive hemorrhages", "Venous beading present", "Significant retinal ischemia"],
        "action": "Seek urgent medical attention. Prompt treatment with laser photocoagulation or anti-VEGF therapy is recommended."
    },
    "Proliferative": {
        "desc": "Proliferative diabetic retinopathy detected. Abnormal new blood vessel growth is present on the retina.",
        "findings": ["Neovascularization detected", "High risk of vision loss", "Possible vitreous hemorrhage risk"],
        "action": "Immediate specialist referral required. Pan-retinal photocoagulation or vitrectomy surgery may be necessary."
    }
}

odir_descriptions = {
    "Normal": {
        "desc": "The retina appears healthy with no detectable abnormalities.",
        "action": "Continue routine annual eye examinations."
    },
    "Diabetic Retinopathy": {
        "desc": "Damage to retinal blood vessels caused by prolonged high blood sugar levels, leading to leakage and abnormal vessel growth.",
        "action": "Consult an endocrinologist and ophthalmologist. Tight glycemic control and possible laser or anti-VEGF treatment."
    },
    "Glaucoma": {
        "desc": "A group of eye conditions that damage the optic nerve, often associated with elevated intraocular pressure, leading to progressive vision loss.",
        "action": "See an ophthalmologist promptly for intraocular pressure measurement and possible medicated eye drops or surgery."
    },
    "Cataract": {
        "desc": "Clouding of the eye's natural lens, causing blurred vision and light sensitivity. Commonly age-related.",
        "action": "Schedule an eye examination. Cataract surgery may be recommended if vision is significantly impaired."
    },
    "Age-related Macular Degeneration": {
        "desc": "Progressive deterioration of the macula, the central part of the retina responsible for sharp central vision.",
        "action": "Consult a retinal specialist. Anti-VEGF injections or AREDS supplements may be recommended depending on the type."
    },
    "Hypertensive Retinopathy": {
        "desc": "Retinal damage caused by chronic high blood pressure, resulting in narrowed vessels, hemorrhages, and optic disc swelling.",
        "action": "Consult a physician for blood pressure management and an ophthalmologist for retinal evaluation."
    },
    "Myopia": {
        "desc": "Nearsightedness caused by an elongated eyeball or overly curved cornea, causing distant objects to appear blurred.",
        "action": "Schedule a refraction exam for corrective lenses. Regular monitoring for myopic retinal changes is advised."
    },
    "Other": {
        "desc": "An abnormality was detected that does not fit the standard categories. Further clinical evaluation is needed.",
        "action": "Consult an ophthalmologist for a comprehensive eye examination and differential diagnosis."
    }
}

odir_colors = {
    "Normal": "#16a34a",
    "Diabetic Retinopathy": "#ea580c",
    "Glaucoma": "#dc2626",
    "Cataract": "#2563eb",
    "Age-related Macular Degeneration": "#9333ea",
    "Hypertensive Retinopathy": "#0891b2",
    "Myopia": "#059669",
    "Other": "#6b7280"
}

def show():
    st.markdown("""
    <style>
    .predict-title { font-size: 2rem; font-weight: 700; color: #f1f5f9; margin-bottom: 0.5rem; letter-spacing: -0.02em; }
    .predict-sub { color: rgba(199, 210, 254, 0.6); margin-bottom: 2rem; font-size: 1rem; }
    .section-heading { font-size: 1.1rem; font-weight: 600; color: #e2e8f0; margin: 1.5rem 0 1rem; letter-spacing: -0.01em; }
    .result-card {
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 20px;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .result-card:hover {
        border-color: rgba(139, 92, 246, 0.4);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.2);
        transform: translateY(-2px);
    }
    .diag-label { font-size: 0.7rem; font-weight: 600; color: rgba(199, 210, 254, 0.6); letter-spacing: 0.1em; text-transform: uppercase; }
    .diag-value { font-size: 2rem; font-weight: 700; margin: 0.5rem 0; background: linear-gradient(135deg, #818cf8, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
    .conf-score { font-size: 1rem; color: rgba(199, 210, 254, 0.7); }
    .finding-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; color: rgba(226, 232, 240, 0.85); font-size: 0.9rem; }
    .finding-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; background: linear-gradient(135deg, #6366f1, #8b5cf6); box-shadow: 0 0 10px rgba(139, 92, 246, 0.5); }
    .prob-bar-bg { flex: 1; background: rgba(255, 255, 255, 0.1); height: 8px; border-radius: 8px; overflow: hidden; }
    .action-box { background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 14px; padding: 1rem; margin-top: 1rem; }
    .action-label { font-size: 0.75rem; font-weight: 600; color: rgba(199, 210, 254, 0.7); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.5rem; }
    .action-text { font-size: 0.9rem; color: #e2e8f0; line-height: 1.6; }
    .disease-card {
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 0.75rem;
        border-left: 4px solid;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .disease-card:hover {
        background: rgba(255, 255, 255, 0.08);
        transform: translateX(4px);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
    }
    .disease-name { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.25rem; color: #f1f5f9; }
    .disease-conf { font-size: 0.85rem; color: rgba(199, 210, 254, 0.7); font-weight: 500; }
    .disease-desc { font-size: 0.85rem; color: rgba(226, 232, 240, 0.7); line-height: 1.5; margin-top: 0.5rem; }
    .disease-action { font-size: 0.85rem; color: #22d3ee; margin-top: 0.75rem; font-weight: 500; }
    .disclaimer { margin-top: 1.5rem; padding: 1rem; background: rgba(255, 255, 255, 0.03); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); }
    .disclaimer-text { font-size: 0.8rem; color: rgba(199, 210, 254, 0.5); text-align: center; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="predict-title">New Scan</div>', unsafe_allow_html=True)
    st.markdown('<div class="predict-sub">Upload a retinal fundus photograph for AI analysis.</div>', unsafe_allow_html=True)

    model_choice = st.radio(
        "Select analysis type",
        options=["Diabetic Retinopathy Grading", "Multi-Disease Detection (ODIR)"],
        horizontal=True,
        label_visibility="collapsed"
    )

    uploaded = st.file_uploader(
        "Drag and drop a retinal image here, or click to browse",
        type=["png", "jpg", "jpeg"],
        label_visibility="collapsed"
    )

    if not uploaded:
        return

    image = Image.open(uploaded)

    if model_choice == "Diabetic Retinopathy Grading":
        model, classes = load_dr_model()
        img_input = preprocess_dr(image)

        with st.spinner("Analyzing retinal scan..."):
            raw_preds = model.predict(img_input, verbose=0)[0]
            if not np.isclose(raw_preds.sum(), 1.0, atol=1e-3):
                preds = tf.nn.softmax(raw_preds).numpy()
            else:
                preds = raw_preds

            pred_idx = int(np.argmax(preds))
            pred_class = classes.get(str(pred_idx), classes.get(pred_idx, "Unknown"))
            confidence = float(preds[pred_idx]) * 100
            info = dr_descriptions[pred_class]

            save_prediction(
                st.session_state.user["id"],
                f"DR: {pred_class}",
                round(confidence, 2),
                {classes[str(i)]: round(float(preds[i]) * 100, 2) for i in range(5)},
                uploaded.name
            )

        left, right = st.columns([1, 1])

        with left:
            st.markdown("#### Original Scan")
            st.image(image, use_container_width=True, clamp=True)
            
            with st.expander("View AI Attention Heatmap"):
                st.markdown("""
                <div style="font-size: 0.85rem; color: rgba(199, 210, 254, 0.6); margin-bottom: 0.5rem;">
                The heatmap shows which regions the model focused on when making its prediction.
                Red/orange areas indicate high importance, blue areas indicate low importance.
                </div>
                """, unsafe_allow_html=True)
                
                heatmap = get_gradcam_heatmap(model, img_input, pred_idx)
                if heatmap is not None:
                    heatmap_img = overlay_heatmap(image, heatmap)
                    st.image(heatmap_img, use_container_width=True, caption="Grad-CAM Attention Map")
                else:
                    st.info("Heatmap visualization not available for this model.")

        with right:
            st.markdown(f"""
            <div class="result-card">
                <div class="diag-label">AI Classification</div>
                <div class="diag-value">{pred_class}</div>
                <div class="conf-score">{confidence:.1f}% confidence</div>
                <hr style="border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 1rem 0;">
                <div style="font-size: 0.9rem; color: rgba(226, 232, 240, 0.8); line-height: 1.6;">{info['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-heading">Key Findings</div>', unsafe_allow_html=True)
            for f in info["findings"]:
                st.markdown(f'<div class="finding-item"><div class="finding-dot"></div>{f}</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-heading">Class Probabilities</div>', unsafe_allow_html=True)
            for i in range(5):
                cls = classes[str(i)]
                prob = float(preds[i]) * 100
                bar_color = "#818cf8" if i == pred_idx else "#4b5563"
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:12px;margin:8px 0;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:10px;border:1px solid rgba(255,255,255,0.05);'>
                    <div style='width:140px;font-size:0.85rem;color:#e2e8f0;font-weight:500;'>{cls}</div>
                    <div style='flex:1;background:rgba(255,255,255,0.1);border-radius:8px;height:8px;'>
                        <div style='width:{prob}%;background:linear-gradient(90deg,{bar_color},#22d3ee);height:8px;border-radius:8px;'></div>
                    </div>
                    <div style='width:50px;text-align:right;font-size:0.85rem;color:#818cf8;font-weight:600;'>{prob:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="action-box">
                <div class="action-label">Recommended Next Action</div>
                <div class="action-text">{info['action']}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="disclaimer" style="margin-top: 1rem;">
                <div class="disclaimer-text" style="color: #0f172a; background: white; padding: 0.5rem; border-radius: 8px;">This result is AI-generated and intended for screening only. Always consult a qualified ophthalmologist for clinical diagnosis.</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        model, labels = load_odir_model()
        img_input = preprocess_odir(image)

        with st.spinner("Analyzing retinal scan..."):
            raw_preds = model.predict(img_input, verbose=0)[0]
            preds = tf.nn.sigmoid(raw_preds).numpy()

            detected = []
            for key, name in labels.items():
                idx = list(labels.keys()).index(key)
                score = float(preds[idx])
                if score >= 0.65:
                    detected.append((name, score))

            if not detected:
                max_score = max(float(preds[list(labels.keys()).index(k)]) for k in labels)
                max_idx = int(np.argmax(preds))
                max_name = labels[list(labels.keys())[max_idx]]
                detected = [(max_name, max_score)]

            all_probs = {labels[k]: round(float(preds[list(labels.keys()).index(k)]) * 100, 2) for k in labels}

            diag_text = ", ".join([f"{n} ({s:.0f}%)" for n, s in detected])
            save_prediction(
                st.session_state.user["id"],
                f"ODIR: {diag_text}",
                round(max(s for _, s in detected) * 100, 2),
                all_probs,
                uploaded.name
            )

        left, right = st.columns([1, 1])

        with left:
            st.markdown("**Original Scan**")
            st.image(image, use_container_width=True)
            
            with st.expander("View AI Attention Heatmap"):
                st.markdown("""
                <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 0.5rem;">
                The heatmap shows which regions the model focused on when making its prediction.
                Red/orange areas indicate high importance, blue areas indicate low importance.
                </div>
                """, unsafe_allow_html=True)
                
                heatmap = get_gradcam_heatmap(model, img_input, 0)
                if heatmap is not None:
                    heatmap_img = overlay_heatmap(image, heatmap)
                    st.image(heatmap_img, use_container_width=True, caption="Grad-CAM Attention Map")
                else:
                    st.info("Heatmap visualization not available for this model.")

        with right:
            st.markdown('<div class="section-heading">Detected Conditions</div>', unsafe_allow_html=True)

            for disease_name, score in sorted(detected, key=lambda x: x[1], reverse=True):
                color = odir_colors.get(disease_name, "#818cf8")
                info = odir_descriptions.get(disease_name, {"desc": "Further evaluation needed.", "action": "Consult an ophthalmologist."})
                pct = score * 100

                st.markdown(f"""
                <div class="disease-card" style="border-left-color: {color};">
                    <div class="disease-name" style="color: {color};">{disease_name}</div>
                    <div class="disease-conf">{pct:.1f}% confidence</div>
                    <div class="disease-desc">{info['desc']}</div>
                    <div class="disease-action">→ {info['action']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="section-heading" style="margin-top: 1.5rem;">Recommended Actions</div>', unsafe_allow_html=True)
            for disease_name, score in sorted(detected, key=lambda x: x[1], reverse=True):
                info = odir_descriptions.get(disease_name, {"action": "Consult an ophthalmologist."})
                st.markdown(f"""
                <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
                    <div style="color: #22d3ee; font-weight: 500;">{disease_name}: {info['action']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<div class="section-heading">All Condition Scores</div>', unsafe_allow_html=True)
            for name, prob in sorted(all_probs.items(), key=lambda x: x[1], reverse=True):
                color = odir_colors.get(name, "#4b5563")
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:12px;margin:8px 0;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:10px;border:1px solid rgba(255,255,255,0.05);'>
                    <div style='width:180px;font-size:0.85rem;color:#e2e8f0;font-weight:500;'>{name}</div>
                    <div style='flex:1;background:rgba(255,255,255,0.1);border-radius:8px;height:8px;'>
                        <div style='width:{prob}%;background:linear-gradient(90deg,{color},#22d3ee);height:8px;border-radius:8px;'></div>
                    </div>
                    <div style='width:50px;text-align:right;font-size:0.85rem;color:#818cf8;font-weight:600;'>{prob:.1f}%</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div class="disclaimer">
                <div class="disclaimer-text">This result is AI-generated and intended for screening only. Always consult a qualified ophthalmologist for clinical diagnosis.</div>
            </div>
            """, unsafe_allow_html=True)
