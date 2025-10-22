import argparse
import pathlib
import os
import time

import numpy as np

from general_motion_retargeting import GeneralMotionRetargeting as GMR
from general_motion_retargeting import RobotMotionViewer
from general_motion_retargeting.utils.smpl import load_smplx_file, get_smplx_data_offline_fast
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from rich import print


import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def parse_urdf(urdf_file_path):
    tree = ET.parse(urdf_file_path)
    root = tree.getroot()

    # Collect joints: name, parent, child, origin
    joints = {}
    for joint in root.findall('joint'):
        name = joint.get('name')
        parent = joint.find('parent').get('link')
        child = joint.find('child').get('link')
        origin = joint.find('origin')
        if origin is not None:
            xyz = origin.get('xyz', '0 0 0').split()
            xyz = np.array([float(x) for x in xyz])
        else:
            xyz = np.zeros(3)
        joints[name] = {
            'parent': parent,
            'child': child,
            'xyz': xyz
        }

    # Collect links
    links = [link.get('name') for link in root.findall('link')]

    return joints, links

def compute_link_positions(joints, key_links, root_link='pelvis'):
    positions = {}
    visited = set()

    def traverse(link, parent_pos=np.zeros(3)):
        for joint_name, joint in joints.items():
            if joint['parent'] == link:
                child_link = joint['child']
                if child_link not in visited:
                    pos = parent_pos + joint['xyz']
                    positions[child_link] = pos
                    visited.add(child_link)
                    traverse(child_link, pos)

    positions[root_link] = np.zeros(3)
    visited.add(root_link)
    traverse(root_link)

    # Keep only key_links
    positions = {link: positions[link] for link in key_links if link in positions}
    return positions

def compute_bone_lengths(positions, skeleton_edges):
    bone_lengths = {}
    for a, b in skeleton_edges:
        if a in positions and b in positions:
            bone_lengths[f"{a}-{b}"] = np.linalg.norm(positions[b] - positions[a])
    return bone_lengths

def plot_skeleton(positions, skeleton_edges, title="Humanoid Skeleton"):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot joints
    for link, pos in positions.items():
        ax.scatter(pos[0], pos[1], pos[2], c='r', s=40)
        ax.text(pos[0], pos[1], pos[2], link, size=8)

    # Plot bones
    for a, b in skeleton_edges:
        if a in positions and b in positions:
            pos_a = positions[a]
            pos_b = positions[b]
            xs = [pos_a[0], pos_b[0]]
            ys = [pos_a[1], pos_b[1]]
            zs = [pos_a[2], pos_b[2]]
            ax.plot(xs, ys, zs, c='b', linewidth=2)

    ax.set_box_aspect([1, 1, 1])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.title(title)
    plt.show()


if __name__ == "__main__":
    
    HERE = pathlib.Path(__file__).parent

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smplx_file",
        help="SMPLX motion file to load.",
        type=str,
        # required=True,
        default= "/home/wang/GMR/assets/body_models/ACCAD/Male2Running_c3d/C1_-_stand_to_run_stageii.npz",
        # default="/home/yanjieze/projects/g1_wbc/GMR/motion_data/ACCAD/Male1General_c3d/General_A1_-_Stand_stageii.npz",
        # default="/home/yanjieze/projects/g1_wbc/GMR/motion_data/ACCAD/Male2MartialArtsKicks_c3d/G8_-__roundhouse_left_stageii.npz"
        # default="/home/yanjieze/projects/g1_wbc/TWIST-dev/motion_data/AMASS/KIT_572_dance_chacha11_stageii.npz"
        # default="/home/yanjieze/projects/g1_wbc/GMR/motion_data/ACCAD/Male2MartialArtsPunches_c3d/E1_-__Jab_left_stageii.npz",
        # default="/home/yanjieze/projects/g1_wbc/GMR/motion_data/ACCAD/Male1Running_c3d/Run_C24_-_quick_side_step_left_stageii.npz",
    )
    
    parser.add_argument(
        "--robot",
        choices=["unitree_g1", "unitree_g1_with_hands", "unitree_h1", "unitree_h1_2",
                 "booster_t1", "booster_t1_29dof","stanford_toddy", "fourier_n1", 
                "engineai_pm01", "kuavo_s45", "hightorque_hi", "galaxea_r1pro", "berkeley_humanoid_lite", "booster_k1",
                "pnd_adam_lite", "openloong", "tienkung", "urdf0924"],
        default="unitree_g1",
    )
    
    parser.add_argument(
        "--save_path",
        default=None,
        help="Path to save the robot motion.",
    )
    
    parser.add_argument(
        "--loop",
        default=False,
        action="store_true",
        help="Loop the motion.",
    )

    parser.add_argument(
        "--record_video",
        default=False,
        action="store_true",
        help="Record the video.",
    )

    parser.add_argument(
        "--rate_limit",
        default=False,
        action="store_true",
        help="Limit the rate of the retargeted robot motion to keep the same as the human motion.",
    )

    args = parser.parse_args()


    SMPLX_FOLDER = HERE / ".." / "assets" / "body_models"
    
    
    # Load SMPLX trajectory
    smplx_data, body_model, smplx_output, actual_human_height = load_smplx_file(
        args.smplx_file, SMPLX_FOLDER
    )
    
    # align fps
        # "pelvis": 0.9,
        # "spine3": 0.9,

        # "left_hip": 0.9,
        # "right_hip": 0.9,
        # "left_knee": 0.9,
        # "right_knee": 0.9,
        # "left_foot": 0.9,
        # "right_foot": 0.9,

        # "left_shoulder": 0.8,
        # "right_shoulder": 0.8,
        # "left_elbow": 0.8,
        # "right_elbow": 0.8,
        # "left_wrist": 0.8,
        # "right_wrist": 0.8    
    tgt_fps = 30
    smplx_data_frames, aligned_fps = get_smplx_data_offline_fast(smplx_data, body_model, smplx_output, tgt_fps=tgt_fps)
    
    # Suppose smplx_data_frames[0] is a dict or similar structure
    frame0 = smplx_data_frames[0]

    # Create a human pose dictionary
    human_pose = {
        'pelvis': frame0['pelvis'],
        'spine3': frame0['spine3'],
        'left_hip': frame0['left_hip'],
        'right_hip': frame0['right_hip'],
        'left_knee': frame0['left_knee'],
        'right_knee': frame0['right_knee'],
        'left_foot': frame0['left_foot'],
        'right_foot': frame0['right_foot'],
        'left_shoulder': frame0['left_shoulder'],
        'right_shoulder': frame0['right_shoulder'],
        'left_elbow': frame0['left_elbow'],
        'right_elbow': frame0['right_elbow'],
        'left_wrist': frame0['left_wrist'],
        'right_wrist': frame0['right_wrist']
    }
    print("Human pose (positions in meters):\n")
    for joint, pos in human_pose.items():
        # pos[0] if pos contains multiple frames, or just pos if it's a single 3D vector
        joint_pos = pos[0] if isinstance(pos, np.ndarray) and pos.ndim > 1 else pos
        print(f"{joint}: {joint_pos}")

    # Example: frame0 joints (positions only)
    frame0_positions = {joint: frame0[joint][0] for joint in frame0}  # extract positions only

    # Define the connections (edges) between joints to form a skeleton
    skeleton_edges = [
        ('pelvis', 'spine3'),
        ('pelvis', 'left_hip'), ('pelvis', 'right_hip'),
        ('left_hip', 'left_knee'), ('left_knee', 'left_foot'),
        ('right_hip', 'right_knee'), ('right_knee', 'right_foot'),
        ('spine3', 'left_shoulder'), ('spine3', 'right_shoulder'),
        ('left_shoulder', 'left_elbow'), ('left_elbow', 'left_wrist'),
        ('right_shoulder', 'right_elbow'), ('right_elbow', 'right_wrist')
    ]
    # Compute bone lengths
    bone_lengths = {}
    for joint_a, joint_b in skeleton_edges:
        pos_a = frame0_positions[joint_a]
        pos_b = frame0_positions[joint_b]
        length = np.linalg.norm(pos_b - pos_a)
        bone_lengths[f"{joint_a}-{joint_b}"] = length

    # # Print results
    # for bone, length in bone_lengths.items():
    #     print(f"{bone}: {length:.4f} meters")


    # Compute bone vectors (relative positions)
    bone_vectors = {}
    for joint_a, joint_b in skeleton_edges:
        pos_a = frame0_positions[joint_a]
        pos_b = frame0_positions[joint_b]
        vec = pos_b - pos_a  # relative vector from joint_a to joint_b
        bone_vectors[f"{joint_a}->{joint_b}"] = vec

    # # Print relative vectors
    # print("\nRelative bone vectors (meters):")
    # for bone, vec in bone_vectors.items():
    #     print(f"{bone}: {vec}")



    # # Prepare the 3D plot
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')

    # # Plot joints
    # for joint, pos in frame0_positions.items():
    #     ax.scatter(pos[0], pos[1], pos[2], c='r', s=40)
    #     ax.text(pos[0], pos[1], pos[2], joint, size=8)

    # # Plot bones
    # for joint_a, joint_b in skeleton_edges:
    #     pos_a = frame0_positions[joint_a]
    #     pos_b = frame0_positions[joint_b]
    #     xs = [pos_a[0], pos_b[0]]
    #     ys = [pos_a[1], pos_b[1]]
    #     zs = [pos_a[2], pos_b[2]]
    #     ax.plot(xs, ys, zs, c='b')

    # # Set equal aspect ratio
    # ax.set_box_aspect([1,1,1])
    # ax.set_xlabel('X')
    # ax.set_ylabel('Y')
    # ax.set_zlabel('Z')
    # plt.title("SMPLX Skeleton Frame 0")
    # plt.show()
    urdf_path = "/home/wang/URDFly/descriptions/urdf0924/urdf/urdf0924.urdf"
    key_links = [
        "pelvis",
        "left_hip_roll_link", "left_knee_link", "left_ankle_pitch_link",
        "right_hip_roll_link", "right_knee_link", "right_ankle_pitch_link",
        "torso_link",
        "left_shoulder_yaw_link", "left_elbow_link", "left_wrist_yaw_link",
        "right_shoulder_yaw_link", "right_elbow_link", "right_wrist_yaw_link"
    ]

    skeleton_edges = [
        ('pelvis', 'torso_link'),
        ('pelvis', 'left_hip_roll_link'), ('pelvis', 'right_hip_roll_link'),
        ('left_hip_roll_link', 'left_knee_link'), ('left_knee_link', 'left_ankle_pitch_link'),
        ('right_hip_roll_link', 'right_knee_link'), ('right_knee_link', 'right_ankle_pitch_link'),
        ('torso_link', 'left_shoulder_yaw_link'), ('torso_link', 'right_shoulder_yaw_link'),
        ('left_shoulder_yaw_link', 'left_elbow_link'), ('left_elbow_link', 'left_wrist_yaw_link'),
        ('right_shoulder_yaw_link', 'right_elbow_link'), ('right_elbow_link', 'right_wrist_yaw_link')
    ]

    joints, links = parse_urdf(urdf_path)
    positions = compute_link_positions(joints, key_links)
    bone_lengths = compute_bone_lengths(positions, skeleton_edges)

    print("Link positions (meters):")
    for link, pos in positions.items():
        print(f"{link}: {pos}")

    # print("\nSkeleton bone lengths (meters):")
    # for bone, length in bone_lengths.items():
    #     print(f"{bone}: {length:.4f}")


    # Compute relative bone vectors (child relative to parent)
    bone_vectors = {}
    for a, b in skeleton_edges:
        if a in positions and b in positions:
            vec = positions[b] - positions[a]  # vector from parent to child
            bone_vectors[f"{a}->{b}"] = vec

    # print("\nRelative bone vectors (meters):")
    # for bone, vec in bone_vectors.items():
    #     print(f"{bone}: {vec}")


    
    
