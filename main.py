import sys
import random
from math import sin, cos, radians
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from camera import Camera
from world import Terrain, Voxel
from render import draw_voxel
from processes import update_environment

# --- OpenGL Callbacks ---
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    camera.apply()
    glEnable(GL_DEPTH_TEST)
    # Draw axes
    glLineWidth(3)
    glBegin(GL_LINES)
    glColor3f(1,0,0)  # X axis (red)
    glVertex3f(0,0,0)
    glVertex3f(5,0,0)
    glColor3f(0,1,0)  # Y axis (green)
    glVertex3f(0,0,0)
    glVertex3f(0,5,0)
    glColor3f(0,0,1)  # Z axis (blue)
    glVertex3f(0,0,0)
    glVertex3f(0,0,5)
    glEnd()
    glLineWidth(1)
    # Draw voxels
    for voxel in terrain.get_voxels():
        draw_voxel(voxel, terrain.get_voxels(), wireframe_mode='continuous')
    # Draw crosshair
    draw_crosshair()
    glutSwapBuffers()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w/float(h or 1), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    key = key.decode('utf-8').lower()
    forward = right = up = 0
    if key == 'w':
        forward = 1
    elif key == 's':
        forward = -1
    elif key == 'd':
        right = -1
    elif key == 'a':
        right = 1
    elif key == ' ':  # Space for up
        up = 1
    elif key == 'z':  # Z for down
        up = -1
    elif key == '\x1b':
        sys.exit()
    camera.move(forward, right, up)
    glutPostRedisplay()

def special(key, x, y):
    # Remove camera.rotate from arrow keys to avoid conflict with mouse look
    pass

def timer(fps=60):
    update_movement()
    update_environment(terrain.voxels, property_map)
    glutPostRedisplay()
    glutTimerFunc(int(1000/fps), lambda v=0: timer(fps), 0)

def init():
    glClearColor(0.8, 0.9, 1.0, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

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
    glVertex2f(-0.03, 0)
    glVertex2f(0.03, 0)
    glVertex2f(0, -0.03)
    glVertex2f(0, 0.03)
    glEnd()
    glLineWidth(1)
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 700)
    glutCreateWindow(b"Voxel World - PyOpenGL")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard_down)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special)
    glutSetCursor(GLUT_CURSOR_NONE)
    glutPassiveMotionFunc(mouse_look)
    # Center mouse at start
    win_w = glutGet(GLUT_WINDOW_WIDTH)
    win_h = glutGet(GLUT_WINDOW_HEIGHT)
    glutWarpPointer(win_w // 2, win_h // 2)
    timer(60)
    glutMainLoop()

# --- Mouse look state ---
last_mouse = {'x': None, 'y': None}

# --- Mouse look callback ---
def mouse_look(x, y):
    global last_mouse
    win_w = glutGet(GLUT_WINDOW_WIDTH)
    win_h = glutGet(GLUT_WINDOW_HEIGHT)
    cx, cy = win_w // 2, win_h // 2
    # Only process if window is focused and pointer is at center or moved by user
    if (x, y) == (cx, cy):
        return
    if last_mouse['x'] is None or last_mouse['y'] is None:
        last_mouse['x'] = cx
        last_mouse['y'] = cy
        glutWarpPointer(cx, cy)
        return
    dx = x - cx
    dy = y - cy
    sensitivity = 0.15
    camera.rotate(dx * sensitivity, dy * sensitivity)
    last_mouse['x'] = cx
    last_mouse['y'] = cy
    glutWarpPointer(cx, cy)
    glutPostRedisplay()

# --- Key state tracking ---
pressed_keys = set()

def keyboard_down(key, x, y):
    key = key.decode('utf-8').lower()
    pressed_keys.add(key)
    update_movement()

def keyboard_up(key, x, y):
    key = key.decode('utf-8').lower()
    if key in pressed_keys:
        pressed_keys.remove(key)
    update_movement()

def update_movement():
    forward = right = up = 0
    if 'w' in pressed_keys:
        forward += 1
    if 's' in pressed_keys:
        forward -= 1
    if 'a' in pressed_keys:
        right += 1
    if 'd' in pressed_keys:
        right -= 1
    if ' ' in pressed_keys:
        up += 1
    if 'z' in pressed_keys:
        up -= 1
    if forward or right or up:
        camera.move(forward, right, up)

if __name__ == '__main__':
    GRID_SIZE = 20
    VOXEL_COUNT = 1000
    VOXEL_SIZE = 1.0

    terrain = Terrain(GRID_SIZE, VOXEL_COUNT)
    camera = Camera(GRID_SIZE)

    property_map = {}
    for v in terrain.get_voxels():
        property_map[(v.x, v.y, v.z)] = {'humidity': 0.5, 'heat': 0.5, 'water': 0.5, 'nutrient': 0.5}

    main()
