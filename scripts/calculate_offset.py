import argparse
import pathlib
import os
import time

import numpy as np

from general_motion_retargeting import GeneralMotionRetargeting as GMR
from general_motion_retargeting import RobotMotionViewer
from general_motion_retargeting.utils.smpl import load_smplx_file, get_smplx_data_offline_fast
import numpy as np
# import trimesh
# import pyrender
from rich import print

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

    
    exit()
    