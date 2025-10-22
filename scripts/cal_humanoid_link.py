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

    print("\nSkeleton bone lengths (meters):")
    for bone, length in bone_lengths.items():
        print(f"{bone}: {length:.4f}")

    # Plot
    plot_skeleton(positions, skeleton_edges, title="URDF0924 Skeleton")
