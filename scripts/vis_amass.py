import numpy as np

# Path to your .npz file
file_path = "/home/wang/GMR/assets/body_models/ACCAD/Male2Running_c3d/C1_-_stand_to_run_stageii.npz"

# Load the file
data = np.load(file_path, allow_pickle=True)

# Check what arrays are inside
print("Keys in the npz file:", data.files)

# Access a specific array, e.g., 'poses'
# Replace 'poses' with the actual key you find in data.files
poses = data['poses']
print("Shape of poses:", poses.shape)

# If you want to see the first few entries
print(poses[:5])
