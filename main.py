import sys
import random
from math import sin, cos, radians
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from camera import Camera
from world import Terrain, Voxel
from world.utils import get_voxel_in_crosshair
from render import draw_voxel
from render.representation import draw_voxel_wireframe, draw_highlighted_voxel, draw_crosshair, draw_text
from processes import update_environment
import time

sim_time = 0.0
last_frame_time = time.time()
frame_count = 0
fps_accum = 0.0
real_fps = 0.0

# --- OpenGL Callbacks ---
def display():
    global sim_time, last_frame_time, frame_count, fps_accum, real_fps
    now = time.time()
    dt = now - last_frame_time
    last_frame_time = now
    frame_count += 1
    fps_accum += 1.0 / max(dt, 1e-6)
    if frame_count >= 10:
        real_fps = fps_accum / frame_count
        frame_count = 0
        fps_accum = 0.0
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
        draw_voxel(voxel, terrain.get_voxels(), wireframe_mode='continuous', property_map=property_map)
    # Draw crosshair
    draw_crosshair()
    # Draw voxel info at crosshair
    v = get_voxel_in_crosshair(camera, terrain.get_voxels())
    if v:
        # Highlight the voxel under the crosshair
        draw_highlighted_voxel(v, size=1.0)
        props = property_map.get((v.x, v.y, v.z), {})
        mass = props.get('mass', 1.0)
        info = (
            f"Voxel ({v.x},{v.y},{v.z})\n"
            f"Lat: {v.lat:.6f}°, Lon: {v.lon:.6f}°, H: {v.height:.2f}m\n"
            f"Type: {props.get('type','soil')} | Mass: {mass:.2f} kg\n"
            f"Water: {props.get('water',0):.2f} | Organic: {props.get('organic',0):.2f} | Minerals: {props.get('minerals',0):.2f}\n"
            f"Humidity: {props.get('humidity',0):.2f} | Heat: {props.get('heat',0):.2f} | Nutrient: {props.get('nutrient',0):.2f}"
        )
        for i, line in enumerate(info.split('\n')):
            draw_text(-0.98, 0.95 - i*0.07, line)
    # Show simulation units and time
    draw_text(-0.98, -0.98, f"Time: {sim_time:.2f}s | Voxel: 1m³ | Time step: 0.05s | FPS: {real_fps:.1f}")
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

def timer(fps=25):
    global sim_time
    update_movement()
    update_environment(terrain.voxels, property_map, dt=0.05)
    sim_time += 0.05
    glutPostRedisplay()
    glutTimerFunc(int(1000/fps), lambda v=0: timer(fps), 0)

def init():
    glClearColor(0.8, 0.9, 1.0, 1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

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
    timer(25)
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

def get_voxel_mass(props, default_density=1600.0):
    """
    Compute the mass of a voxel based on its type and humidity.
    Types: 'soil', 'rock', 'water'. Default is 'soil'.
    Densities: soil=1600kg/m³, rock=2600kg/m³, water=1000kg/m³.
    Humidity increases mass for soil (adds water mass).
    """
    vtype = props.get('type', 'soil')
    humidity = props.get('humidity', 0.5)
    if vtype == 'soil':
        dry_density = 1600.0
        water_density = 1000.0
        # Assume humidity is fraction of pore space filled with water (simple model)
        # Assume 50% pore space for soil
        pore_space = 0.5
        mass = (dry_density * (1-pore_space) + (dry_density * pore_space) * (1-humidity) + water_density * pore_space * humidity)
    elif vtype == 'rock':
        mass = 2600.0
    elif vtype == 'water':
        mass = 1000.0
    else:
        mass = default_density
    return mass

if __name__ == '__main__':
    GRID_SIZE = 10
    VOXEL_COUNT = 1000
    VOXEL_SIZE = 1.0

    terrain = Terrain(GRID_SIZE, VOXEL_COUNT)
    camera = Camera(GRID_SIZE)

    property_map = {}
    for v in terrain.get_voxels():
        # Assign type and properties based on y and randomness
        if v.y == 0:
            vtype = 'soil'
            minerals = 0.7 + 0.2*random.random()
            organic = 0.05 + 0.1*random.random()
            water = 0.1 + 0.1*random.random()
        elif v.y == 1:
            vtype = 'soil'
            minerals = 0.5 + 0.3*random.random()
            organic = 0.1 + 0.2*random.random()
            water = 0.15 + 0.2*random.random()
        elif v.y == 2:
            vtype = 'soil'
            minerals = 0.3 + 0.3*random.random()
            organic = 0.15 + 0.25*random.random()
            water = 0.2 + 0.25*random.random()
        elif random.random() < 0.1:
            vtype = 'water'
            minerals = 0.01
            organic = 0.01
            water = 1.0
        elif random.random() < 0.1:
            vtype = 'rock'
            minerals = 1.0
            organic = 0.01
            water = 0.01
        else:
            vtype = 'soil'
            minerals = 0.2 + 0.3*random.random()
            organic = 0.1 + 0.2*random.random()
            water = 0.2 + 0.2*random.random()
        humidity = water
        props = {
            'humidity': humidity,
            'heat': 0.5,
            'water': water,
            'nutrient': 0.5,
            'type': vtype,
            'minerals': minerals,
            'organic': organic
        }
        props['mass'] = get_voxel_mass(props)
        property_map[(v.x, v.y, v.z)] = props

    main()
