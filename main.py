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



import random
import copy
import json
import os
from camera import Camera
from world import Terrain
from world.utils import clamp_voxel_properties, recalc_voxel_masses
from processes import update_environment
from frontend.ui import set_simulation, run_ui

# All frontend/UI, OpenGL, GLUT, camera, and input code has been moved to frontend/ui.py
# This file now only coordinates simulation setup and launches the UI.

# --- Main script ---
if __name__ == '__main__':
    def load_json_data(filename):
        with open(os.path.join(os.path.dirname(__file__), 'data', filename), 'r') as f:
            return json.load(f)

    MINERALS = load_json_data('minerals.json')
    INORGANIC = load_json_data('inorganic_molecules.json')
    ORGANIC = load_json_data('organic_matter.json')

    GRID_SIZE = 10
    VOXEL_COUNT = 1000
    VOXEL_SIZE = 1.0

    # --- Densities and volume ---
    VOXEL_VOLUME = 1.0  # m^3
    DENSITY = {
        'water': 1000.0,   # kg/m^3
        'soil': 1600.0,    # kg/m^3
        'rock': 2600.0,    # kg/m^3
        'organic': 1300.0, # kg/m^3 (example)
    }

    # Initial world
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
        # Logical composition assignment
        # Minerals: random fractions, sum to minerals
        mineral_ids = [m['id'] for m in MINERALS]
        mineral_fracs = [random.random() for _ in mineral_ids]
        mineral_sum = sum(mineral_fracs)
        minerals_comp = {mid: minerals * (f/mineral_sum) for mid, f in zip(mineral_ids, mineral_fracs)}
        # Inorganic: always water, plus random others, sum to (1-minerals-organic)
        inorg_ids = [m['id'] for m in INORGANIC]
        inorg_fracs = [random.random() for _ in inorg_ids]
        inorg_sum = sum(inorg_fracs)
        inorg_total = max(0.0, 1.0 - minerals - organic)
        inorganic_comp = {iid: inorg_total * (f/inorg_sum) for iid, f in zip(inorg_ids, inorg_fracs)}
        # Set water to match water property
        if 'water' in inorganic_comp:
            inorganic_comp['water'] = water
        # Organic: random fractions, sum to organic
        org_ids = [m['id'] for m in ORGANIC]
        org_fracs = [random.random() for _ in org_ids]
        org_sum = sum(org_fracs)
        organic_comp = {oid: organic * (f/org_sum) for oid, f in zip(org_ids, org_fracs)}
        props = {
            'humidity': humidity,
            'heat': 0.5,
            'water': water,
            'nutrient': 0.5,
            'type': vtype,
            'minerals': minerals,
            'organic': organic,
            'minerals_comp': minerals_comp,
            'inorganic_comp': inorganic_comp,
            'organic_comp': organic_comp
        }
        props['mass'] = get_voxel_mass(props)
        property_map[(v.x, v.y, v.z)] = props

    # --- Precompute simulation steps ---
    sim_states = []
    for step in range(24):
        terrain_copy = copy.deepcopy(terrain)
        property_map_copy = copy.deepcopy(property_map)
        clamp_voxel_properties(property_map_copy, VOXEL_VOLUME, DENSITY)
        recalc_voxel_masses(property_map_copy, VOXEL_VOLUME, DENSITY)
        sim_states.append((terrain_copy, property_map_copy, step*3600.0))
        if step < 23:
            update_environment(terrain_copy.voxels, property_map_copy, dt=3600.0)
            clamp_voxel_properties(property_map_copy, VOXEL_VOLUME, DENSITY)
            recalc_voxel_masses(property_map_copy, VOXEL_VOLUME, DENSITY)
            terrain = copy.deepcopy(terrain_copy)
            property_map = copy.deepcopy(property_map_copy)

    set_simulation(sim_states, camera, 24, VOXEL_VOLUME, DENSITY)
    run_ui()
