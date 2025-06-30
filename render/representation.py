"""
Rendering logic for the voxel world simulation.
Handles drawing of voxels and visible faces using OpenGL.
"""
from OpenGL.GL import *
from OpenGL.GLUT import glutBitmapCharacter, GLUT_BITMAP_HELVETICA_18
from world.voxel import Voxel

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
    """
    Returns a list of face names that are visible for a given voxel.
    Only faces not adjacent to another voxel are considered visible.

    Args:
        voxel: The voxel object for which to determine visible faces.
        voxels: The set of all voxels in the world, used to check adjacency.

    Returns:
        A list of strings, each representing a visible face ('right', 'left', 'top', 'bottom', 'front', 'back').
    """
    faces = []
    x, y, z = voxel.x, voxel.y, voxel.z
    for (dx, dy, dz), name in FACE_DIRS:
        neighbor = Voxel(x+dx, y+dy, z+dz)
        if neighbor not in voxels:
            faces.append(name)
    return faces

def get_voxel_color(voxel, property_map):
    props = property_map.get((voxel.x, voxel.y, voxel.z), {})
    vtype = props.get('type', 'soil')
    humidity = props.get('humidity', 0.5)
    water = props.get('water', 0.2)
    minerals = props.get('minerals', 0.5)
    organic = props.get('organic', 0.1)
    # Dynamic color blending
    if vtype == 'soil' or vtype == 'organic':
        # Soil: brown, more organic = darker, more water = bluer, more minerals = lighter
        base = [0.55, 0.27, 0.07]  # brown
        # Blend: minerals lighten, organic darkens, water adds blue
        r = base[0] * (1-organic) + 0.2*minerals
        g = base[1] * (1-organic) + 0.3*minerals
        b = base[2] * (1-organic) + 0.5*water + 0.1*minerals
        # Clamp
        color = [min(max(r,0),1), min(max(g,0),1), min(max(b,0),1)]
    elif vtype == 'rock':
        # Rock: gray, minerals lighten
        base = [0.5, 0.5, 0.5]
        r = base[0] + 0.3*minerals
        g = base[1] + 0.3*minerals
        b = base[2] + 0.3*minerals
        color = [min(r,1), min(g,1), min(b,1)]
    elif vtype == 'water':
        # Water: blue, organic darkens, minerals add green
        r = 0.1 + 0.1*minerals
        g = 0.3 + 0.3*minerals
        b = 0.7 + 0.2*water - 0.2*organic
        color = [min(r,1), min(g,1), min(b,1)]
    else:
        color = [0.7, 0.7, 0.7]
    return color

def draw_voxel(voxel, voxels, wireframe_mode=None, property_map=None):
    """
    Draws a voxel's visible faces and edges using OpenGL.

    Args:
        voxel: Voxel object to draw.
        voxels: Set of all voxels (for visibility check).
        wireframe_mode: 'continuous' for continuous edge lines, None or other values for standard wireframe.
        property_map: dict for coloring by composition.
    """
    faces = get_visible_faces(voxel, voxels)
    if not faces:
        return
    x, y, z = voxel.x, voxel.y, voxel.z
    for face in faces:
        verts = [CUBE_VERTS[i] for i in FACE_VERTS[face]]
        if property_map is not None:
            glColor3fv(get_voxel_color(voxel, property_map))
        else:
            glColor3fv(FACE_COLORS[face])
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

def draw_voxel_wireframe(voxel, size=1.0, color=(1,1,0), linewidth=4):
    """
    Draws a wireframe box matching the voxel's position and size (min corner at x,y,z).
    """
    x, y, z = voxel.x, voxel.y, voxel.z
    corners = [
        (x, y, z), (x+size, y, z), (x+size, y+size, z), (x, y+size, z),
        (x, y, z+size), (x+size, y, z+size), (x+size, y+size, z+size), (x, y+size, z+size)
    ]
    edges = [
        (0,1),(1,2),(2,3),(3,0), # bottom
        (4,5),(5,6),(6,7),(7,4), # top
        (0,4),(1,5),(2,6),(3,7)  # sides
    ]
    glPushAttrib(GL_ENABLE_BIT | GL_LINE_BIT)
    glDisable(GL_LIGHTING)
    glColor3f(*color)
    glLineWidth(linewidth)
    glBegin(GL_LINES)
    for a, b in edges:
        glVertex3f(*corners[a])
        glVertex3f(*corners[b])
    glEnd()
    glLineWidth(1)
    glPopAttrib()

def draw_highlighted_voxel(voxel, size=1.0):
    """
    Draws a thick yellow wireframe box around the given voxel, matching the solid voxel exactly.
    """
    draw_voxel_wireframe(voxel, size=size, color=(1,1,0), linewidth=4)

def draw_crosshair():
    # Draw a + in the center of the screen
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glColor3f(0,0,0)
    glLineWidth(2)
    glBegin(GL_LINES)
    glVertex2f(-0.025, 0)
    glVertex2f(0.025, 0)
    glVertex2f(0, -0.03)
    glVertex2f(0, 0.03)
    glEnd()
    glLineWidth(1)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_text(x, y, text):
    """
    Draws text at normalized device coordinates (x, y) in [-1, 1].
    """
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glColor3f(0,0,0)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
