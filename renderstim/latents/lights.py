from kubric import core

def get_scene_lights(position):
    sun = core.DirectionalLight(
        name="sun",
        color=core.color.Color.from_name("white"), 
        shadow_softness=0.1,
        intensity=0.9, 
        position=position
    )
    lights = [sun]
    for light in lights:
        light.look_at((0, 0, 0))
    return lights