import kubric as kb

def get_material(rng):
    material_keys = [
        'color',
        'metallic', 
        'specular', 
        'specular_tint', 
        'roughness', 
        'transmission', 
        'transmission_roughness'
    ]
    material_kwargs = {}
    for key in material_keys:
        if key == 'color':
            _, random_color = kb.randomness.sample_color("gray", rng)
            material_kwargs[key] = random_color
        else:
            material_kwargs[key] = rng.uniform(0, 1)
    return material_kwargs
