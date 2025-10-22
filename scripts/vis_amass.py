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


# Example: calibrate shoulder-to-ankle length
# List of SMPL-X joint names
smpl_joint_names = [
    'pelvis',
    'left_hip',
    'right_hip',
    'spine1',
    'left_knee',
    'right_knee',
    'spine2',
    'left_ankle',
    'right_ankle',
    'spine3',
    'left_foot',
    'right_foot',
    'neck',
    'left_collar',
    'right_collar',
    'head',
    'left_shoulder',
    'right_shoulder',
    'left_elbow',
    'right_elbow',
    'left_wrist',
    'right_wrist',
    'jaw',
    'left_eye_smplhf',
    'right_eye_smplhf',
    # the rest are hand joints
    'left_index1', 'left_index2', 'left_index3',
    'left_middle1', 'left_middle2', 'left_middle3',
    'left_pinky1', 'left_pinky2', 'left_pinky3',
    'left_ring1', 'left_ring2', 'left_ring3',
    'left_thumb1', 'left_thumb2', 'left_thumb3',
    'right_index1', 'right_index2', 'right_index3',
    'right_middle1', 'right_middle2', 'right_middle3',
    'right_pinky1', 'right_pinky2', 'right_pinky3',
    'right_ring1', 'right_ring2', 'right_ring3',
    'right_thumb1', 'right_thumb2', 'right_thumb3',
]


# Build a dictionary mapping name -> index
smpl_joint_index = {name: idx for idx, name in enumerate(smpl_joint_names)}
print("Example:", smpl_joint_index['left_shoulder'], smpl_joint_index['left_ankle'])

left_shoulder = joints[0, smpl_joint_index['LeftShoulder']]
left_ankle = joints[0, smpl_joint_index['LeftAnkle']]

human_limb_length = np.linalg.norm(left_ankle - left_shoulder)

# Robot corresponding joints
robot_l_shoulder_pos = robot_joints_pos['left_shoulder']
robot_l_ankle_pos = robot_joints_pos['left_ankle']

robot_limb_length = np.linalg.norm(robot_l_ankle_pos - robot_l_shoulder_pos)

scale_ratio = robot_limb_length / human_limb_length
print("Calibration scale:", scale_ratio)

# Offset by human root and scale
scaled_human_joints = (joints - joints[0, smpl_joint_index['Hips']]) * scale_ratio
target_robot_positions = robot_root_pos + scaled_human_joints

# Solve IK for your robot
robot_configuration = solve_ik(target_robot_positions)

