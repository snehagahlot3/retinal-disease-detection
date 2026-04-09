# RetinalScan — AI-Powered Retinal Disease Detection

A deep learning web application that detects retinal diseases from fundus photographs using computer vision and transfer learning. Built as a non-invasive screening tool for early detection of diabetic retinopathy and 8 other ocular conditions.

---

## Features

- **Diabetic Retinopathy Grading** — classifies DR severity into 5 stages (No DR, Mild, Moderate, Severe, Proliferative) using EfficientNetB3 trained on APTOS 2019
- **Multi-Disease Detection** — detects 8 ocular conditions (Diabetic Retinopathy, Glaucoma, Cataract, AMD, Hypertensive Retinopathy, Myopia, and more) using ODIR-5K dataset
- **Grad-CAM Heatmaps** — visual explanation of which retinal regions influenced the model's prediction
- **Clinical Explanations** — plain-language description of each condition and recommended next steps
- **User Authentication** — secure login and registration with bcrypt password hashing
- **Scan History** — all previous scans saved per user with full results


## Models

The trained model files are too large for GitHub. Download them from Google Drive and place them in the `models/` folder.

| Model | Description | Download |
|---|---|---|
| `best_model.h5` | DR Grading — EfficientNetB3, APTOS 2019, 82% accuracy | [Download](https://drive.google.com/uc?export=download&id=1aqRJ2hO_61yAPfkZNpGHYHOEr_AmDWcp) |
| `odir_model.keras` | Multi-Disease — EfficientNetB3, ODIR-5K, 8 conditions | [Download](https://drive.google.com/uc?export=download&id=1eRfhg71wIWV7AW-2kt-kOoixy3U2eWyA) |

---

## Project Structure

```
retinal-disease-detection/
├── app.py                  # Main Streamlit app, routing, sidebar
├── auth.py                 # Login and registration UI
├── database.py             # SQLite setup, user and prediction queries
├── class_names.json        # DR model class labels
├── requirements.txt        # Python dependencies
├── retinal.db              # Auto-generated SQLite database
├── models/
│   ├── best_model.h5       # DR grading model (download required)
│   ├── odir_model.keras    # Multi-disease model (download required)
│   └── odir_labels.json    # ODIR model class labels
└── pages/
    ├── home.py             # Landing page after login
    ├── predict.py          # Scan upload and prediction page
    └── history.py          # User scan history page
```

---

## Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/snehagahlot3/retinal-disease-detection.git
cd retinal-disease-detection
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Download the models
Download both model files from the links in the table above and place them in the `models/` folder:
```
models/
├── best_model.h5
└── odir_model.keras
```

### 4. Run the app
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Datasets

| Dataset | Used For | Source |
|---|---|---|
| APTOS 2019 Blindness Detection | DR Grading model training | [Kaggle](https://www.kaggle.com/competitions/aptos2019-blindness-detection) |
| ODIR-5K Ocular Disease Recognition | Multi-disease model training | [Kaggle](https://www.kaggle.com/datasets/andrewmvd/ocular-disease-recognition-odir5k) |

---

## Model Architecture

Both models use **EfficientNetB3** pretrained on ImageNet as the backbone with transfer learning:

```
Input (224×224×3)
    ↓
EfficientNetB3 (pretrained backbone)
    ↓
GlobalAveragePooling2D
    ↓
Dropout (0.5)
    ↓
Dense output
  → DR model:   5 units, softmax  (multi-class)
  → ODIR model: 8 units, sigmoid  (multi-label)
```

**Preprocessing:** CLAHE (Contrast Limited Adaptive Histogram Equalization) applied to enhance retinal vessel visibility before feeding to the model.

**Training:**
- Optimizer: Adam (lr=1e-4)
- Loss: Sparse Categorical Crossentropy (DR) / Binary Crossentropy (ODIR)
- Callbacks: EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

---

## Results

| Model | Accuracy | Val Accuracy |
|---|---|---|
| DR Grading (EfficientNetB3) | 97.7% train | 82.2% val |
| Multi-Disease (EfficientNetB3) | 88% train | 86% val (AUC) |

---

## Tech Stack

- **Language:** Python 3.12
- **Deep Learning:** TensorFlow 2.19, Keras
- **Model:** EfficientNetB3 (transfer learning)
- **Frontend:** Streamlit
- **Image Processing:** OpenCV, Pillow
- **Explainability:** Grad-CAM
- **Database:** SQLite
- **Auth:** bcrypt
- **Visualization:** Matplotlib

---

## Disease Classes

### DR Grading Model (APTOS 2019)
| Grade | Label | Description |
|---|---|---|
| 0 | No DR | No diabetic retinopathy |
| 1 | Mild | Microaneurysms only |
| 2 | Moderate | More than just microaneurysms |
| 3 | Severe | Extensive hemorrhages, venous beading |
| 4 | Proliferative | Neovascularization, high risk of blindness |

### Multi-Disease Model (ODIR-5K)
`Normal` · `Diabetic Retinopathy` · `Glaucoma` · `Cataract` · `Age-related Macular Degeneration` · `Hypertensive Retinopathy` · `Myopia` · `Other`

---

## Important Notice

> ⚠️ RetinalScan is intended for **educational and screening purposes only**. It is not a substitute for professional medical diagnosis. Always consult a qualified ophthalmologist for clinical evaluation.

---



**Sneha**  
B.Sc | Machine Learning Internship Project  
GitHub: [@snehagahlot3](https://github.com/snehagahlot3)
