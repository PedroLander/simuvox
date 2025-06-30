import math
from world.voxel import Voxel

def get_voxel_in_crosshair(camera, voxels, max_dist=50, step=0.05):
    """
    Raycast from camera position in view direction to find the first voxel hit.
    Returns the Voxel object or None if nothing is hit.
    Uses floor to match voxel min-corner logic.
    """
    x, y, z = camera.x, camera.y, camera.z
    dx, dy, dz = camera.get_direction()
    for t in range(int(max_dist / step)):
        px = x + dx * t * step
        py = y + dy * t * step
        pz = z + dz * t * step
        vx, vy, vz = int(math.floor(px)), int(math.floor(py)), int(math.floor(pz))
        v = Voxel(vx, vy, vz)
        if v in voxels:
            return v
    return None
