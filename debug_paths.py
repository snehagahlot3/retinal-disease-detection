import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("=" * 50)
print("DEBUGGING DATASET PATHS")
print("=" * 50)

# Check /kaggle/input exists
print("Step 1: /kaggle/input contents:")
print(os.listdir('/kaggle/input/'))

# Try all possible dataset paths
paths_to_try = [
    '/kaggle/input/ocular-disease-recognition-odir5k',
    '/kaggle/input/odir5k',
    '/kaggle/input/ODIR-5K',
    '/kaggle/input/ocular-disease-recognition',
]

for p in paths_to_try:
    print(f"\nStep 2: Checking {p}")
    if os.path.exists(p):
        print(f"  EXISTS! Contents: {os.listdir(p)}")
        
        # Go deeper
        for sub in os.listdir(p):
            full = os.path.join(p, sub)
            print(f"    {sub}: {os.listdir(full)[:3] if os.path.isdir(full) else 'file'}")
    else:
        print(f"  Does NOT exist")

print("\nDone.")