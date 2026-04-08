# 👁️ Retinal Disease Detection

ML model to detect diabetic retinopathy from retinal fundus images using EfficientNetB3.

## Classes
- No DR, Mild, Moderate, Severe, Proliferative DR

## Model
- EfficientNetB3 + Transfer Learning
- 82% validation accuracy
- Trained on APTOS 2019 dataset

## Run locally
```
pip install -r requirements.txt
python download_models.py
streamlit run app.py
```

## Tech Stack
Python, TensorFlow, Streamlit, OpenCV
```

---

Now open the terminal in VS Code and run:
```
pip install -r requirements.txt
streamlit run app.py