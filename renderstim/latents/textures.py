import bpy
from glob import glob

bg_textures = glob("/mnt/bg_textures/*.png")
obj_textures = glob("/mnt/obj_textures/*.png")

def get_texture(type, rng, background=False):
    if background: size = 3192
    else: size = 256
    TEXTURE_IMAGES = obj_textures + bg_textures
    
    if type == 'CLOUDS':
        cloud_noise_basis = [
            'IMPROVED_PERLIN',
            'VORONOI_F1',
            'VORONOI_F2',
            'VORONOI_F3',
            'VORONOI_F2_F1',
            'VORONOI_CRACKLE'
        ]
        return {
            'type': 'CLOUDS',
            'nabla': rng.uniform(0.001, 0.1),
            'noise_depth': rng.randint(0, 5),
            'noise_scale': rng.randint(10, 30),
            'noise_basis': rng.choice(cloud_noise_basis),
            'size': size
        }
    elif type == 'DISTORTED_NOISE':
        distorted_noise_basis = [
            'BLENDER_ORIGINAL', 
            'ORIGINAL_PERLIN',
            'VORONOI_F2',
            'VORONOI_F4',
            'VORONOI_CRACKLE', 
            'CELL_NOISE'
        ]
        return {
            'type': 'DISTORTED_NOISE',
            'nabla': rng.uniform(0.001, 0.1),
            'distortion': rng.randint(1, 10),
            'noise_basis': rng.choice(distorted_noise_basis),
            'noise_scale': rng.randint(10, 30),
            'noise_distortion': rng.choice(distorted_noise_basis),
            'size': size
        }
    elif type == 'MAGIC':
        return {
            'type': 'MAGIC',
            'noise_depth': rng.randint(0, 5),
            'turbulence': rng.randint(5, 10),
            'size': size
        }

    elif type == 'MARBLE':
        marble_noise_basis = [
            'BLENDER_ORIGINAL', 
            'VORONOI_F2',
            'VORONOI_CRACKLE', 
            'CELL_NOISE'
        ]
        return {
            'type': 'MARBLE',
            'nabla': rng.uniform(0.001, 0.1),
            'noise_depth': rng.randint(0, 5),
            'noise_scale': rng.randint(10, 30),
            'noise_basis': rng.choice(marble_noise_basis),
            'marble_type': rng.choice(['SOFT', 'SHARP']),
            'turbulence': rng.randint(5, 15),
            'size': size
        }
    elif type == 'MUSGRAVE':
        musgrave_noise_basis = [
            'BLENDER_ORIGINAL', 
            'VORONOI_F1',   
            'VORONOI_F2_F1',
            'VORONOI_CRACKLE', 
            'CELL_NOISE'
        ]

        musgrave_types = [
            'MULTIFRACTAL',
            'RIDGED_MULTIFRACTAL',
            'FBM'
        ]

        return {
            "type": "MUSGRAVE",
            "dimension_max": rng.uniform(0.001, 2),
            "gain": rng.randint(1, 6),
            "lacunarity": rng.randint(1, 6),
            "musgrave_type": rng.choice(musgrave_types),
            "nabla": rng.uniform(0.001, 0.1),
            "noise_basis": rng.choice(musgrave_noise_basis),
            "noise_intensity": rng.randint(1, 10),
            "noise_scale": rng.randint(10, 30),
            "octaves": rng.randint(1, 8),
            "offset": 1,
            "size": size
        }
    elif type == 'STUCCI':
        stucci_noise_basis = [
            'BLENDER_ORIGINAL', 
            'VORONOI_F1',   
            'VORONOI_F2_F1',
            'VORONOI_CRACKLE', 
            'CELL_NOISE'
        ]

        stucci_types = [
            'PLASTIC',
            'WALL_IN',
            'WALL_OUT'
        ]

        return {
            "type": "STUCCI",
            "noise_basis": rng.choice(stucci_noise_basis),
            "noise_scale": rng.randint(10, 30),
            "noise_type": 'HARD_NOISE',
            "stucci_type": rng.choice(stucci_types),
            "turbulence": rng.randint(5, 15),
            "size": size
        }
    elif type == 'VORONOI':
        voronoi_distance_metric = [
            'DISTANCE',
            'DISTANCE_SQUARED',
            'MANHATTAN',
            'CHEBYCHEV',
            'MINKOVSKY_HALF',
            'MINKOVSKY_FOUR',
            'MINKOVSKY'
        ]

        return {
            "type": "VORONOI",
            "color_mode": "INTENSITY",
            "distance_metric": rng.choice(voronoi_distance_metric),
            "minkovsky_exponent": rng.randint(1, 10),
            "nabla": rng.uniform(0.001, 0.1),
            "noise_scale": rng.randint(10, 30),
            "size": size
        }
    elif type == 'WOOD':
        wood_noise_basis = [
            'BLENDER_ORIGINAL',
            'VORONOI_F1',
            'VORONOI_CRACKLE',
            'CELL_NOISE'
        ]

        return {
            "type": "WOOD",
            "nabla": rng.uniform(0.001, 0.1),
            "noise_scale": rng.randint(10, 30),
            "turbulence": rng.randint(5, 15),
            "wood_type": 'BANDNOISE',
            "noise_basis": rng.choice(wood_noise_basis),
            "size": size
        }
    elif type == 'IMAGE':
        return {
            'type': 'IMAGE',
            'image_path': rng.choice(TEXTURE_IMAGES),
        }
    else:
        return {'type': 'NONE'}

def texture_pixels(texture=None, x=512, y=512):
    pixels = []
    final_pixels = []
    for rangex in range(x):
        for rangey in range(y):
            pixels.append(texture.evaluate(value=(rangex, rangey, 0)))
    for p in pixels:
        for fl in p:
            final_pixels.append(fl)
    return final_pixels

def apply_texture(obj_name, material_name, texture=None):

    if texture['type'] == 'NONE':
        return None
    
    elif texture['type'] == 'CLOUDS':
        tex = bpy.data.textures.new(
            name="clouds_texture", 
            type="CLOUDS"
        )
        tex.cloud_type = "GRAYSCALE"
        tex.noise_type = 'HARD_NOISE'
        tex.use_color_ramp = True
        tex.nabla = texture['nabla']
        tex.noise_depth = texture['noise_depth']
        tex.noise_scale = texture['noise_scale']
        tex.noise_basis = texture['noise_basis']

    elif texture['type'] == 'DISTORTED_NOISE':
        tex = bpy.data.textures.new(
            name="distorted_noise_texture", 
            type="DISTORTED_NOISE"
        )
        tex.use_color_ramp = True
        tex.nabla = texture['nabla']
        tex.distortion = texture['distortion']
        tex.noise_basis = texture['noise_basis']
        tex.noise_scale = texture['noise_scale']
        tex.noise_distortion = texture['noise_distortion']

    elif texture['type'] == 'MAGIC':
        tex = bpy.data.textures.new(
            name="magic_texture", 
            type="MAGIC"
        )
        tex.use_color_ramp = True
        tex.noise_depth = texture['noise_depth']
        tex.turbulence = texture['turbulence']

    elif texture['type'] == 'MARBLE':
        tex = bpy.data.textures.new(
            name="marble_texture", 
            type="MARBLE"
        )
        tex.use_color_ramp = True
        tex.noise_type = 'HARD_NOISE'
        tex.nabla = texture['nabla']
        tex.noise_depth = texture['noise_depth']
        tex.noise_scale = texture['noise_scale']
        tex.noise_basis = texture['noise_basis']
        tex.marble_type = texture['marble_type']
        tex.turbulence = texture['turbulence']
    
    elif texture['type'] == 'MUSGRAVE':
        tex = bpy.data.textures.new(
            name="musgrave_texture", 
            type="MUSGRAVE"
        )
        tex.use_color_ramp = True
        tex.dimension_max = texture['dimension_max']
        tex.gain = texture['gain']
        tex.lacunarity = texture['lacunarity']
        tex.musgrave_type = texture['musgrave_type']
        tex.nabla = texture['nabla']
        tex.noise_basis = texture['noise_basis']
        tex.noise_intensity = texture['noise_intensity']
        tex.noise_scale = texture['noise_scale']
        tex.octaves = texture['octaves']
        tex.offset = texture['offset']

    elif texture['type'] == 'STUCCI':
        tex = bpy.data.textures.new(
            name="stucci_texture", 
            type="STUCCI"
        )
        tex.use_color_ramp = True
        tex.noise_type = 'HARD_NOISE'
        tex.noise_scale = texture['noise_scale']
        tex.noise_basis = texture['noise_basis']
        tex.stucci_type = texture['stucci_type']
        tex.turbulence = texture['turbulence']
    
    elif texture['type'] == 'VORONOI':
        tex = bpy.data.textures.new(
            name="voronoi_texture", 
            type="VORONOI"
        )
        tex.use_color_ramp = True
        tex.weight_1 = 1
        tex.weight_2 = 0
        tex.weight_3 = 0
        tex.weight_4 = 0
        tex.color_mode = texture['color_mode']
        tex.distance_metric = texture['distance_metric']
        tex.minkovsky_exponent = texture['minkovsky_exponent']
        tex.nabla = texture['nabla']
        tex.noise_scale = texture['noise_scale']

    elif texture['type'] == 'WOOD':
        tex = bpy.data.textures.new(
            name="wood_texture", 
            type="WOOD"
        )
        tex.use_color_ramp = True
        tex.noise_type = 'HARD_NOISE'
        tex.nabla = texture['nabla']
        tex.noise_scale = texture['noise_scale']
        tex.noise_basis = texture['noise_basis']
        tex.wood_type = texture['wood_type']
        tex.turbulence = texture['turbulence']
    
    # select the object
    obj = bpy.data.objects[obj_name]

    # create a new material    
    mat = bpy.data.materials.new(material_name)

    # get the nodes
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    # create the nodes
    node_principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    node_tex = nodes.new('ShaderNodeTexImage')

    # create the links  
    mat.node_tree.links.new(
        node_tex.outputs["Color"], 
        node_principled.inputs["Base Color"]
    )
    mat.node_tree.links.new(
        node_principled.outputs["BSDF"], 
        node_output.inputs["Surface"]
    )
    
    # set the texture
    if 'size' in texture.keys():
        node_tex.image = bpy.data.images.new(
            material_name, 
            texture['size'], 
            texture['size'], 
            alpha=True
        )
        node_tex.image.pixels = texture_pixels(
            tex, 
            x=node_tex.image.size[0], 
            y=node_tex.image.size[1]
        )

    elif texture['type'] == 'IMAGE':
        node_tex.image = bpy.data.images.load(texture['image_path'])

    obj.active_material = mat

    # Assign it to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)