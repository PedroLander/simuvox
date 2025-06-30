"""
Camera module for the voxel world simulation.
Handles camera position, orientation, and movement.
"""

from math import sin, cos, radians
from OpenGL.GLU import gluLookAt

class Camera:
    """
    Camera object for 3D navigation and view control.
    Attributes:
        x, y, z: Position in world space.
        yaw, pitch: Orientation angles.
        speed: Movement speed.
    Methods:
        get_direction: Returns forward direction vector.
        get_right: Returns right direction vector (perpendicular to forward and up).
        move: Moves camera relative to orientation.
        rotate: Rotates camera by yaw/pitch deltas.
        apply: Applies view transformation (gluLookAt).
    """
    def __init__(self, grid_size):
        self.x, self.y, self.z = grid_size/2, 2, grid_size*1.5
        self.yaw, self.pitch = 0, 0
        self.speed = 0.2
    def get_direction(self):
        rad_yaw = radians(self.yaw)
        rad_pitch = radians(self.pitch)
        dx = cos(rad_pitch) * sin(rad_yaw)
        dy = sin(rad_pitch)
        dz = -cos(rad_pitch) * cos(rad_yaw)
        return dx, dy, dz
    def get_right(self):
        fx, fy, fz = self.get_direction()
        upx, upy, upz = 0, 1, 0
        rx = upy * fz - upz * fy
        ry = upz * fx - upx * fz
        rz = upx * fy - upy * fx
        norm = (rx**2 + ry**2 + rz**2) ** 0.5
        if norm == 0:
            return 1, 0, 0
        return rx/norm, ry/norm, rz/norm
    def move(self, forward, right, up):
        dx, dy, dz = self.get_direction()
        rx, ry, rz = self.get_right()
        self.x += forward * dx * self.speed + right * rx * self.speed
        self.y += forward * dy * self.speed + right * ry * self.speed + up * self.speed
        self.z += forward * dz * self.speed + right * rz * self.speed
    def rotate(self, dyaw, dpitch):
        self.yaw = (self.yaw + dyaw) % 360
        self.pitch = max(-89, min(89, self.pitch - dpitch))
    def apply(self):
        dx, dy, dz = self.get_direction()
        gluLookAt(self.x, self.y, self.z, self.x+dx, self.y+dy, self.z+dz, 0, 1, 0)
