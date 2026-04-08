import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import numpy as np
import pandas as pd
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
print("ODIR MODEL TRAINING - GPU OPTIMIZED")
print("=" * 50)

BASE = '/kaggle/input/datasets/andrewmvd/ocular-disease-recognition-odir5k'
IMAGE_DIR = f'{BASE}/preprocessed_images/'
CSV_PATH = f'{BASE}/full_df.csv'

print(f"Base: {BASE}")
print(f"Images: {IMAGE_DIR}")
print(f"CSV: {CSV_PATH}")

df = pd.read_csv(CSV_PATH)
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
BATCH_SIZE = 32

available_images = set(os.listdir(IMAGE_DIR))
print(f"Available images: {len(available_images)}")

data = []
for idx, row in df.iterrows():
    for eye in ['Left-Fundus', 'Right-Fundus']:
        img_name = row[eye]
        if img_name in available_images:
            label = [row[c] for c in disease_cols]
            data.append((img_name, label))

print(f"Total samples: {len(data)}")

train_data, temp_data = train_test_split(data, test_size=0.3, random_state=42)
val_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)

print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")

def data_generator(data_list, image_dir, img_size, batch_size, shuffle=True):
    while True:
        if shuffle:
            np.random.shuffle(data_list)
        
        images, labels = [], []
        for img_name, label in data_list:
            img_path = os.path.join(image_dir, img_name)
            img = keras.preprocessing.image.load_img(img_path, target_size=(img_size, img_size))
            img = keras.preprocessing.image.img_to_array(img) / 255.0
            images.append(img)
            labels.append(label)
            
            if len(images) == batch_size:
                yield np.array(images), np.array(labels, dtype=np.float32)
                images, labels = [], []
        
        if images:
            yield np.array(images), np.array(labels, dtype=np.float32)

train_gen = data_generator(train_data, IMAGE_DIR, IMG_SIZE, BATCH_SIZE)
val_gen = data_generator(val_data, IMAGE_DIR, IMG_SIZE, BATCH_SIZE, shuffle=False)

steps_per_epoch = len(train_data) // BATCH_SIZE
validation_steps = len(val_data) // BATCH_SIZE

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
    keras.callbacks.EarlyStopping(patience=5, monitor='val_auc', mode='max', restore_best_weights=True),
    keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3, monitor='val_auc', mode='max')
]

print("\n" + "=" * 50)
print("STARTING TRAINING")
print("=" * 50)

history = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=20,
    steps_per_epoch=steps_per_epoch,
    validation_steps=validation_steps,
    callbacks=callbacks,
    verbose=1
)

print("\n" + "=" * 50)
print("EVALUATING")
print("=" * 50)

test_gen = data_generator(test_data, IMAGE_DIR, IMG_SIZE, BATCH_SIZE, shuffle=False)
test_steps = len(test_data) // BATCH_SIZE

model.load_weights('models/odir_model.keras')
preds = model.predict(test_gen, steps=test_steps, verbose=1)

test_labels = np.array([label for _, label in test_data[:len(preds)]])
preds_binary = (preds > 0.5).astype(int)

from sklearn.metrics import classification_report
print("\nClassification Report:")
print(classification_report(test_labels, preds_binary, target_names=list(disease_names.values()), zero_division=0))

model.save('models/odir_model.keras')
print("\nModel saved!")

with open('models/odir_labels.json', 'w') as f:
    json.dump(disease_names, f)
print("Labels saved!")

print("\n" + "=" * 50)
print("TRAINING COMPLETE")
print("=" * 50)