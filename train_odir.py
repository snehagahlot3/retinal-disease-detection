import numpy as np
import pandas as pd
import cv2
import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.applications import EfficientNetB3
from sklearn.model_selection import train_test_split
import json
import warnings
warnings.filterwarnings('ignore')

tf.get_logger().setLevel('ERROR')

print("=" * 50)
print("ODIR MODEL TRAINING")
print("=" * 50)

BASE = 'data/odir5k'
IMAGE_DIR = f'{BASE}/preprocessed_images/'

df = pd.read_csv(f'{BASE}/full_df.csv')
print(f"Dataset: {df.shape[0]} patients")

disease_cols = ['N', 'D', 'G', 'C', 'A', 'H', 'M', 'O']
disease_names = {
    'N': 'Normal', 'D': 'Diabetic Retinopathy', 'G': 'Glaucoma',
    'C': 'Cataract', 'A': 'Age-related Macular Degeneration',
    'H': 'Hypertensive Retinopathy', 'M': 'Myopia', 'O': 'Other'
}

print("\nLabel distribution:")
for col in disease_cols:
    print(f"  {disease_names[col]}: {df[col].sum()}")

IMG_SIZE = 224
available_images = set(os.listdir(IMAGE_DIR))

print("\nLoading images...")
X, y = [], []

for idx, row in df.iterrows():
    for eye in ['Left-Fundus', 'Right-Fundus']:
        img_name = row[eye]
        if img_name in available_images:
            img_path = os.path.join(IMAGE_DIR, img_name)
            img = cv2.imread(img_path)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
                X.append(img)
                y.append([row[col] for col in disease_cols])
    if idx % 500 == 0:
        print(f"  Processed {idx}/{len(df)} - Loaded {len(X)} images")

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.float32)
print(f"\nTotal loaded: {X.shape[0]} images")

X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

del X, y, X_temp, y_temp

print(f"Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")

X_train = X_train / 255.0
X_val = X_val / 255.0
X_test = X_test / 255.0

print("\nBuilding model...")

base = EfficientNetB3(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
for layer in base.layers[:100]:
    layer.trainable = False

inputs = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
x = base(inputs, training=True)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.4)(x)
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(8, activation='sigmoid')(x)

model = keras.Model(inputs, outputs)
model.summary()

model.compile(
    optimizer=keras.optimizers.Adam(1e-4),
    loss='binary_crossentropy',
    metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
)

callbacks = [
    keras.callbacks.ModelCheckpoint('models/odir_model.keras', save_best_only=True, monitor='val_auc', mode='max'),
    keras.callbacks.EarlyStopping(patience=10, monitor='val_auc', mode='max', restore_best_weights=True),
    keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5, monitor='val_auc', mode='max')
]

print("\n" + "=" * 50)
print("STARTING TRAINING")
print("=" * 50)

history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=30,
    batch_size=32,
    callbacks=callbacks,
    verbose=1
)

print("\n" + "=" * 50)
print("EVALUATING")
print("=" * 50)

model.load_weights('models/odir_model.keras')
preds = model.predict(X_test, verbose=1)
preds_binary = (preds > 0.5).astype(int)

from sklearn.metrics import classification_report
print("\nClassification Report:")
print(classification_report(y_test, preds_binary, target_names=list(disease_names.values()), zero_division=0))

model.save('models/odir_model.keras')
print("\nModel saved!")

with open('models/odir_labels.json', 'w') as f:
    json.dump(disease_names, f)
print("Labels saved!")

print("\n" + "=" * 50)
print("TRAINING COMPLETE")
print("=" * 50)
