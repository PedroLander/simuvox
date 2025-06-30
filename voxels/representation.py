# voxels/representation.py
from OpenGL.GL import *
from .voxel import Voxel

FACE_DIRS = [
    ((1, 0, 0), 'right'),
    ((-1, 0, 0), 'left'),
    ((0, 1, 0), 'top'),
    ((0, -1, 0), 'bottom'),
    ((0, 0, 1), 'front'),
    ((0, 0, -1), 'back'),
]

FACE_COLORS = {
    'right': (1, 0.7, 0.7),
    'left': (0.7, 1, 0.7),
    'top': (0.7, 0.7, 1),
    'bottom': (1, 1, 0.7),
    'front': (0.7, 1, 1),
    'back': (1, 0.7, 1),
}

CUBE_VERTS = [
    (0,0,0), (1,0,0), (1,1,0), (0,1,0), # back
    (0,0,1), (1,0,1), (1,1,1), (0,1,1), # front
]
FACE_VERTS = {
    'right':  [1,2,6,5],
    'left':   [0,4,7,3],
    'top':    [3,7,6,2],
    'bottom': [0,1,5,4],
    'front':  [4,5,6,7],
    'back':   [0,3,2,1],
}

def get_visible_faces(voxel, voxels):
    faces = []
    x, y, z = voxel.x, voxel.y, voxel.z
    for (dx, dy, dz), name in FACE_DIRS:
        neighbor = Voxel(x+dx, y+dy, z+dz)
        if neighbor not in voxels:
            faces.append(name)
    return faces

def draw_voxel(voxel, voxels, wireframe_mode=None):
    faces = get_visible_faces(voxel, voxels)
    if not faces:
        return
    x, y, z = voxel.x, voxel.y, voxel.z
    # Draw faces
    for face in faces:
        verts = [CUBE_VERTS[i] for i in FACE_VERTS[face]]
        color = FACE_COLORS[face]
        glColor3fv(color)
        glBegin(GL_QUADS)
        for vx, vy, vz in verts:
            glVertex3f(x+vx, y+vy, z+vz)
        glEnd()
    # Draw continuous wireframe
    if wireframe_mode == 'continuous':
        edges = set()
        for face in faces:
            idxs = FACE_VERTS[face]
            for i in range(4):
                a = tuple(CUBE_VERTS[idxs[i]])
                b = tuple(CUBE_VERTS[idxs[(i+1)%4]])
                edge = tuple(sorted([a, b]))
                edges.add(edge)
        glDisable(GL_LINE_STIPPLE)
        glLineWidth(1.5)
        glColor3f(0,0,0)
        glBegin(GL_LINES)
        for (a, b) in edges:
            glVertex3f(x+a[0], y+a[1], z+a[2])
            glVertex3f(x+b[0], y+b[1], z+b[2])
        glEnd()
        glLineWidth(1)
    else:
        for face in faces:
            verts = [CUBE_VERTS[i] for i in FACE_VERTS[face]]
            glColor3f(0,0,0)
            glBegin(GL_LINE_LOOP)
            for vx, vy, vz in verts:
                glVertex3f(x+vx, y+vy, z+vz)
            glEnd()
