"""
Transfer process module for the voxel world simulation.
Handles humidity, heat, water, and nutrient transfer between adjacent blocks.
"""

def get_transfer_coeff(prop, props):
    """
    Return a transfer coefficient for the property based on block composition.
    - For heat: higher for water and minerals (esp. quartz), lower for organic.
    - For humidity: higher for water, clay, organic.
    - For nutrient: higher for water, organic, clay.
    """
    minerals = props.get('minerals_comp', {})
    inorg = props.get('inorganic_comp', {})
    organic = props.get('organic_comp', {})
    # Example: use quartz, clay, water, organic fractions
    quartz = minerals.get('quartz', 0)
    clay = minerals.get('clay', 0)
    water = inorg.get('water', 0)
    humus = organic.get('humus', 0)
    if prop == 'heat':
        # Thermal conductivity: quartz > water > clay > organic
        return 0.2 + 0.6*quartz + 0.4*water + 0.2*clay + 0.05*humus
    elif prop == 'humidity':
        # Water diffusivity: water > clay > organic > quartz
        return 0.1 + 0.5*water + 0.3*clay + 0.2*humus + 0.05*quartz
    elif prop == 'nutrient':
        # Nutrient mobility: water > organic > clay > quartz
        return 0.1 + 0.5*water + 0.3*humus + 0.2*clay + 0.05*quartz
    else:
        return 0.1


def transfer_property(voxels, property_map, prop, rate=0.1, dt=1.0):
    """
    Simulate transfer of a property (e.g., humidity, heat, water, nutrient) between adjacent voxels.
    Args:
        voxels: set of Voxel objects representing the world.
        property_map: dict mapping (x, y, z) to property dicts.
        prop: property name to transfer.
        rate: transfer rate (float).
        dt: time step in seconds.
    """
    from collections import defaultdict
    from world.voxel import Voxel
    deltas = defaultdict(float)
    for (x, y, z) in voxels:
        props = property_map.get((x, y, z), {})
        val = props.get(prop, 0)
        coeff = get_transfer_coeff(prop, props) * rate * dt
        for dx, dy, dz in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]:
            n = Voxel(x+dx, y+dy, z+dz)
            if n in voxels:
                nprops = property_map.get((n.x, n.y, n.z), {})
                nval = nprops.get(prop, 0)
                ncoeff = get_transfer_coeff(prop, nprops) * rate * dt
                # Use harmonic mean for interface
                eff_coeff = 2 * coeff * ncoeff / (coeff + ncoeff) if (coeff + ncoeff) > 0 else 0
                diff = (val - nval) * eff_coeff
                deltas[(x, y, z)] -= diff
                deltas[(n.x, n.y, n.z)] += diff
    for k, d in deltas.items():
        if k not in property_map:
            property_map[k] = {'humidity': 0.5, 'heat': 0.5, 'water': 0.5, 'nutrient': 0.5}
        property_map[k][prop] = property_map[k].get(prop, 0) + d
