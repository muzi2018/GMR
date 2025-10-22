import numpy as np

file_path = "/home/wang/GMR/assets/body_models/ACCAD/Male2Running_c3d/C1_-_stand_to_run_stageii.npz"

data = np.load(file_path, allow_pickle=True)
print("Keys in the file:", data.files)

# ACCAD data usually contains:
# 'poses' : joint rotations (n_frames, n_joints, 3)
# 'trans' : root joint translation (n_frames, 3)
# other info like 'gender', 'betas' may also exist

poses = data['poses']
trans = data['trans']

print("poses shape:", poses.shape)
print("trans shape:", trans.shape)

from smplx import SMPLX
import torch

# Assuming you have an SMPL or AMASS skeleton
smpl_model = SMPLX(model_path='/home/wang/GMR/assets/body_models/smplx', gender='MALE', use_pca=False, batch_size=1)

# Take the first frame
pose = torch.tensor(poses[0:1], dtype=torch.float32)
trans_root = torch.tensor(trans[0:1], dtype=torch.float32)

global_orient = pose[:, :3]
body_pose = pose[:, 3:66]
left_hand_pose = pose[:, 66:111]
right_hand_pose = pose[:, 111:156]
jaw_pose = pose[:, 156:159]
leye_pose = pose[:, 159:162]
reye_pose = pose[:, 162:165]

output = smpl_model(
    global_orient=global_orient,
    body_pose=body_pose,
    left_hand_pose=left_hand_pose,
    right_hand_pose=right_hand_pose,
    jaw_pose=jaw_pose,
    leye_pose=leye_pose,
    reye_pose=reye_pose,
    transl=trans_root
)

vertices = output.vertices.detach().numpy()
joints = output.joints.detach().numpy()


