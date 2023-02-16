import numpy as np
from typing import Dict, List
from .textures import get_texture
from .materials import get_material
from .utils import get_quaternion


KUBASIC_IDS = (
    "cube", 
    "cylinder", 
    "sphere", 
    "cone", 
    "torus", 
    "gear",
    "torus_knot", 
    "sponge", 
    "spot", 
    "suzanne"
)

TEXTURES = [
    'NONE',
    'IMAGE',
    'CLOUDS',
    'DISTORTED_NOISE',
    'MAGIC',
    'MARBLE',
    'MUSGRAVE',
    'STUCCI',
    'VORONOI',
    'WOOD'
]


def latent_dataset(
    num_scenes: int = 100,
    resolution: List[int] = [256, 144],
    min_num_objects: int = 3,
    max_num_objects: int = 6,
    spawn_region: List[List[float]] = [[-2.5, -3.0, 0.2], [2.5, 3.0, 1.5]],
    sun_position: List[float] = [0.0, 0.0, 7.0],
    camera_position: List[float] = [0.0, -8.0, 3.6],
    camera_look_at: List[float] = [0.0, 0.0, 0.5],
    camera_focal_length: float = 32.0,
    camera_sensor_width: float = 30.0,
    floor_scale: List[float] = [20.0, 40.0, 0.01],
    floor_position: List[float] = [0.0, 0.0, 0.0],
    background_type: str = "mixed"
) -> List[Dict]:
    
    """
    A dataset returns a list of dictionaries, each dictionary is the config for a single scene.
    default values are set for mouse data.
    for monkey data, use:
        resolution = [256, 256]
        spawn_region = [[-2.5, -3.0, 0.2], [2.5, 3.0, 1.5]]
        sun_position = [0.0, 0.0, 7.0]
        camera_position = [0.0, -6.0, 4.0]
        camera_look_at = [0.0, 0.0, 0.0]
        floor_scale = [30.0, 30.0, 0.01]


    The dataset thus contains all the scenes that will be subsequently generated.
    The list of config dictionaries will be passed to the ImageConfig table, and from there it will be rendered.
    So this function will not generate scenes yet, but it will create the configs that will generate the scenes.

    Args:
        num_scenes: number of scenes
        resolution: (height, width)
        min_num_objects: minimum number of objects in a scene
        max_num_objects: maximum number of objects in a scene
        spawn_region: [[min_x, min_y, min_z], [max_x, max_y, max_z]]
        sun_position: [x, y, z]
        camera_position: [x, y, z]
        camera_look_at: [x, y, z]
        camera_focal_length: focal length of the camera
        camera_sensor_width: sensor width of the camera
        floor_scale: [x, y, z]
        floor_position: [x, y, z]
        background_type: "mixed" or "realistic"

    Returns:
        A list of dictionaries, each dictionary is the config for a single image.
    """

    if len(resolution) != 2:
        raise ValueError(
            "resolution should be a list of ints of length=2, e.g., [256, 256]"
        )

    if len(spawn_region) != 2:
        raise ValueError(
            "spawn region should be a list of lists of length 3, e.g., [[-2.5, -3.0, 0.2], [2.5, 3.0, 1.5]]"
        )

    for sr in spawn_region:
        if len(sr) != 3:
            raise ValueError(
                "spawn region should be a list of 2 lists of length 3, e.g., [[-2.5, -3.0, 0.2], [2.5, 3.0, 1.5]]"
            )

    if len(sun_position) != 3:
        raise ValueError(
            "sun position should be a list of length 3, e.g., [0.0, 0.0, 7.0]"
        )

    if len(camera_position) != 3:
        raise ValueError(
            "camera position should be a list of length 3, e.g., [0.0, -8.0, 3.6]"
        )

    if len(camera_look_at) != 3:
        raise ValueError(
            "camera look at should be a list of length 3, e.g., [0.0, 0.0, 0.5]"
        )

    if len(floor_scale) != 3:
        raise ValueError(
            "floor scale should be a list of length 3, e.g., [20.0, 40.0, 0.01]"
        )

    if len(floor_position) != 3:
        raise ValueError(
            "floor position should be a list of length 3, e.g., [0.0, 0.0, 0.0]"
        )
        
    rng = np.random.default_rng()
    seeds = rng.choice(
        low=0, 
        high=2147483647, 
        size=num_scenes, 
        replace=False
    )
    scenes = []
    
    for seed in range(seeds):
        latents = {}

        rng = np.random.RandomState(seed)
        latents["seed"] = seed

        # set resolution
        latents["resolution"] = resolution

        # set spawn region
        latents["spawn_region"] = spawn_region

        # set sun position
        latents["sun_position"] = sun_position
        latents["sun_position"][0] = rng.uniform(-1, 1)
        latents["sun_position"][1] = rng.uniform(-1, 1)

        # set camera position
        latents["camera_position"] = camera_position

        # set camera look at
        latents["camera_look_at"] = camera_look_at

        # set camera focal length
        latents["camera_focal_length"] = camera_focal_length

        # set camera sensor width
        latents["camera_sensor_width"] = camera_sensor_width

        # set floor scale
        latents["floor_scale"] = floor_scale

        # set floor position
        latents["floor_position"] = floor_position

        # set background type
        if background_type == "mixed":
            latents["bg_texture"] = get_texture(
                rng.choice(TEXTURES), rng, True
            )
        elif background_type == "realistic":
            latents["bg_texture"] = get_texture(
                "IMAGE", rng, True
            )
        else:
            raise ValueError("Invalid background type: background_type can be either 'mixed' or 'realistic'")

        # set the background material
        latents["bg_material"] = get_material(rng)
        
        # set ambient illumination
        latents["ambient_illumination"] = rng.uniform(0.4, 0.7)
        
        # object properties
        # number of objects in the scene 
        # visibility and overlap depend on camera position and spawn region
        latents["num_objects"] = rng.randint(min_num_objects, max_num_objects + 1)
        
        # choose #num_objects KuBasic shapes
        latents["object_shapes"] = rng.choice(KUBASIC_IDS, size=latents["num_objects"])
        
        # set #num_objects scales
        latents["object_scales"] = rng.uniform(0.6, 1.2, size=latents["num_objects"])
        
        # set #num_objects angles of rotation in (0, 2pi)
        latents["object_angles_of_rotation"] = rng.uniform(0, 2*np.pi, size=latents["num_objects"])
        
        # choose axes of rotation for the objects
        latents["object_axes_of_rotation"] = rng.choice(["x", "y", "z"], size=latents["num_objects"])
        
        # get object quaternions
        latents["object_quaternions"] = [
            get_quaternion(
                latents["object_axes_of_rotation"][k],
                latents["object_angles_of_rotation"][k]
            ) for k in range(latents["num_objects"])
        ]
        
        # set object textures
        latents["object_textures"] = [
            get_texture(
                rng.choice(TEXTURES), 
                rng, 
                False
            ) for _ in range(latents["num_objects"])
        ]
        
        # set object materials
        latents["object_materials"] = [get_material(rng) for _ in range(latents["num_objects"])]
        
        # append to dataset
        scenes.append(latents)

    return scenes