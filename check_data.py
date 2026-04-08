import pandas as pd
import os

df = pd.read_csv('data/odir5k/full_df.csv')
image_dir = 'data/odir5k/preprocessed_images/'
available_images = set(os.listdir(image_dir))

print(f"Available images: {len(available_images)}")

X, y = [], []
disease_cols = ['N', 'D', 'G', 'C', 'A', 'H', 'M', 'O']

missing = 0
for idx, row in df.iterrows():
    for eye in ['Left-Fundus', 'Right-Fundus']:
        img_name = row[eye]
        if img_name in available_images:
            X.append(img_name)
            y.append([row[col] for col in disease_cols])
        else:
            missing += 1

print(f"Loaded: {len(X)} images")
print(f"Missing: {missing} images")
