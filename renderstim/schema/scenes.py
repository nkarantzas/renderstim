from .templates.rendered_scenes import RenderedScenesBase
from .main import LatentDataset
from . import schema


@schema
class RenderedScenes(RenderedScenesBase):
    scene_config_table = LatentDataset.SceneConfig

