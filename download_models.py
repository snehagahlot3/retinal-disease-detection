import urllib.request
import os

MODELS = {
    "models/odir_model.keras": "https://drive.google.com/uc?export=download&id=1eRfhg71wIWV7AW-2kt-kOoixy3U2eWyA",
    "models/best_model.h5": "https://drive.google.com/uc?export=download&id=1aqRJ2hO_61yAPfkZNpGHYHOEr_AmDWcp"
}

def download_models():
    os.makedirs("models", exist_ok=True)
    for path, url in MODELS.items():
        if os.path.exists(path):
            print(f"{path} already exists")
            continue
        print(f"Downloading {path}...")
        urllib.request.urlretrieve(url, path)
        print(f"Downloaded {path}")

if __name__ == "__main__":
    download_models()
    print("All models downloaded!")