
#!/usr/bin/env python3

import argparse
import math
import numpy as np

def rotation_matrix(roll, pitch, yaw):
    """Build rotation matrix from roll, pitch, yaw in radians."""
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)

    Rx = np.array([
        [1, 0, 0],
        [0, cr, -sr],
        [0, sr, cr],
    ])

    Ry = np.array([
        [cp, 0, sp],
        [0, 1, 0],
        [-sp, 0, cp],
    ])

    Rz = np.array([
        [cy, -sy, 0],
        [sy, cy, 0],
        [0, 0, 1],
    ])

    return Rz @ Ry @ Rx

def matrix_to_rpy(R):
    """Extract URDF roll, pitch, yaw from R = Rz(yaw) Ry(pitch) Rx(roll)."""
    sin_pitch = max(-1.0, min(1.0, -R[2, 0]))
    pitch = math.asin(sin_pitch)

    if abs(math.cos(pitch)) > 1e-8:
        roll = math.atan2(R[2, 1], R[2, 2])
        yaw = math.atan2(R[1, 0], R[0, 0])
    else:
        # Gimbal lock: choose roll = 0
        roll = 0.0
        yaw = math.atan2(-R[0, 1], R[1, 1])

    return roll, pitch, yaw

def calculate_origin(parent_pos, parent_rpy, child_pos, child_rpy):
    """Calculate the child pose relative to the parent link."""
    Rp = rotation_matrix(*parent_rpy)
    Rc = rotation_matrix(*child_rpy)

    # Relative translation expressed in parent coordinates
    relative_pos = Rp.T @ (np.array(child_pos) - np.array(parent_pos))

    # Relative orientation
    relative_R = Rp.T @ Rc
    relative_rpy = matrix_to_rpy(relative_R)

    # Convert millimetres to metres
    xyz_m = relative_pos / 1000.0

    return xyz_m, relative_rpy

def main():
    parser = argparse.ArgumentParser(
        description="Calculate URDF joint origin from FreeCAD link poses."
    )

    parser.add_argument(
        "--parent-pos", nargs=3, type=float, required=True,
        metavar=("X", "Y", "Z"),
        help="Parent world position in mm"
    )
    parser.add_argument(
        "--parent-rpy", nargs=3, type=float, required=True,
        metavar=("ROLL", "PITCH", "YAW"),
        help="Parent world RPY in degrees"
    )
    parser.add_argument(
        "--child-pos", nargs=3, type=float, required=True,
        metavar=("X", "Y", "Z"),
        help="Child world position in mm"
    )
    parser.add_argument(
        "--child-rpy", nargs=3, type=float, required=True,
        metavar=("ROLL", "PITCH", "YAW"),
        help="Child world RPY in degrees"
    )

    args = parser.parse_args()

    parent_rpy = np.radians(args.parent_rpy)
    child_rpy = np.radians(args.child_rpy)

    xyz, rpy = calculate_origin(
        args.parent_pos,
        parent_rpy,
        args.child_pos,
        child_rpy,
    )

    print("\nCalculated URDF joint origin:")
    print(
        '<origin rpy="{:.6f} {:.6f} {:.6f}" xyz="{:.4f} {:.4f} {:.4f}"/>'.format(*rpy, *xyz)
    )

if __name__ == "__main__":
    main()
